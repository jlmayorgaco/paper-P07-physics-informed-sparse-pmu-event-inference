"""Verify sealed episode scores and calculate a paired trajectory-bootstrap difference."""
import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np
from evaluate import evaluate

HERE = Path(__file__).resolve().parent


def read(name):
    return json.loads((HERE / name).read_text(encoding="utf8"))


def sha(name):
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()


def main():
    manifest = read("test_manifest.json")
    if sha("test_truth.json") != manifest["truth"]:
        raise ValueError("Test labels differ from simulation manifest")
    truth = read("test_truth.json")
    if len(truth) != manifest["records"]:
        raise ValueError("Incomplete test schedule")
    for prefix, cfg in [("", "freeze.json"), ("robust_", "robust_freeze.json"), ("phasor_", "phasor_freeze.json")]:
        seal = read(prefix + "seal.json")
        if seal != dict(predictions=sha(prefix+"predictions.json"), freeze=sha(cfg), manifest=sha("test_manifest.json")):
            raise ValueError("Prediction or configuration differs from its seal")
    predictions = read("predictions.json")
    predictions["student"] = read("robust_predictions.json")
    predictions["phasor"] = read("phasor_predictions.json")
    archived = read("scores.json")
    archived["student"] = read("robust_scores.json")
    archived["phasor"] = read("phasor_scores.json")
    for method, alarms in predictions.items():
        if evaluate(truth, alarms, bootstrap=True) != archived[method]:
            raise ValueError(f"Cannot reproduce {method} scores")
    primary = read("phasor_freeze.json")["primary"]
    contributions = []
    timing = Counter()
    preceding = Counter()
    for i, events in enumerate(truth):
        cases = [evaluate([events], [predictions[m][i]]) for m in (primary, "trees")]
        a, b = cases
        contributions.append((len(events), a["joint"]-b["joint"], a["extras"]-b["extras"]))
        alarms = predictions[primary][i]
        unused = list(alarms)
        for event in events:
            match = next((alarm for alarm in unused if 0 <= alarm["detected"]-event["onset"] <= 45), None)
            if match is not None:
                unused.remove(match)
        for alarm in unused:
            tick = alarm["detected"]
            previous = [e for e in events if e["onset"] <= tick]
            if not previous:
                timing["before_first_onset"] += 1
            elif tick < previous[-1]["end"]:
                timing["during_active_intervention"] += 1
            else:
                timing["after_restoration"] += 1
                preceding[str(previous[-1]["code"])] += 1
    rows = np.array(contributions)
    rng = np.random.default_rng(618004)
    bootstrap = rows[rng.integers(len(rows), size=(10000, len(rows)))].sum(axis=1)
    result = dict(comparison=f"{primary} minus trees",
                  joint_percentage_points=float(100*rows[:, 1].sum()/rows[:, 0].sum()),
                  joint_difference_ci95_pp=np.quantile(100*bootstrap[:, 1]/bootstrap[:, 0], [.025,.975]).tolist(),
                  extra_alarm_difference=int(rows[:, 2].sum()), extras_by_timing=dict(timing),
                  extras_after_restoration_by_previous_family=dict(preceding))
    assert sum(timing.values()) == archived[primary]["extras"]
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

"""Reproduce episode metrics and paired recovery controls from the sealed JSON reports."""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from evaluate import evaluate


def read(name):
    return json.loads((HERE / name).read_text(encoding="utf8"))


def check(name, expected):
    data = (HERE / name).read_bytes()
    # Study digests are native Windows bytes. Git checkouts can normalize JSON newlines.
    if expected not in {hashlib.sha256(b).hexdigest() for b in
                        (data, data.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))}:
        raise ValueError(f"Invalid hash for {name}")


def controls(truth, alarms, groups):
    paired = {}
    for i, name in enumerate(groups):
        if name.startswith("pair-"):
            paired.setdefault(name, {})[len(truth[i])] = i
    clean_controls = exact_seconds = both = 0
    by_prior = {name: [0, 0] for name in ("fault", "line", "generation", "load")}
    for rows in paired.values():
        control, intervention = rows[1], rows[2]
        first, second = truth[intervention]
        if truth[control] != [first]:
            raise ValueError("Pair does not share its first intervention")
        # A late first-event detection is scored with the same one-to-one deadline.
        first_index = next((i for i, a in enumerate(alarms[control])
                            if 0 <= a["detected"] - first["onset"] <= 45), None)
        clean = not any(i != first_index and a["detected"] >= first["end"]
                        for i, a in enumerate(alarms[control]))
        a = next((a for a in alarms[intervention] if 0 <= a["detected"] - second["onset"] <= 45), None)
        correct = bool(a and a["published"] is not None and a["published"] - second["onset"] <= 45
                       and (a["code"], a["source"]) == (second["code"], second["source"]))
        clean_controls += clean
        exact_seconds += correct
        both += clean and correct
        family = ("fault", "line", "generation", "load")[first["code"] - 1]
        by_prior[family][0] += correct
        by_prior[family][1] += 1
    return dict(pairs=len(paired), clean_recovery_controls=clean_controls,
                correct_second_events=exact_seconds, both_in_pair=both, seconds_by_prior_family=by_prior)


if __name__ == "__main__":
    seal, f1_seal = read("seal.json"), read("f1_seal.json")
    for name, expected in [("test_truth.json", read("test_manifest.json")["truth"]),
                           ("test_manifest.json", seal["manifest"]), ("test_manifest.json", f1_seal["manifest"]),
                           ("predictions.json", seal["predictions"]), ("freeze.json", seal["development"]),
                           ("f1_point.json", f1_seal["point"]), ("f1_predictions.json", f1_seal["predictions"])]:
        check(name, expected)
    labels = read("test_truth.json")
    groups = read("test_manifest.json")["clusters"]
    forecasts, archived = read("predictions.json"), read("scores.json")
    forecasts["f1"], archived["f1"] = read("f1_predictions.json"), read("f1_scores.json")
    for name, records in forecasts.items():
        metrics = evaluate(labels, records)
        if any(v != archived[name][k] for k, v in metrics.items()):
            raise ValueError(f"Cannot reproduce {name}")
        print(name, json.dumps(controls(labels, records, groups)))

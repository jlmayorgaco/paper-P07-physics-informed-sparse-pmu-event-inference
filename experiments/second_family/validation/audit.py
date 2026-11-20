"""Independently recount the sealed primary endpoint; optionally repeat two raw PMU trials."""

import argparse
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from shared import RESULT, RUN, digest, read


def audit():
    labels = read(RESULT / "truth.json")
    obs = read(RESULT / "observations.json")
    assert digest(RESULT / "truth.json") == obs["truth_sha"]
    for k, v in read(RESULT / "prediction_seal.json").items():
        assert digest(RESULT / (k + ".json")) == v
    pred = read(RESULT / "predictions.json")
    scores = read(RESULT / "scores.json")
    extras = 0
    hits = {k: 0 for k in scores["summaries"]}
    for truth in labels:
        first, second = truth["events"]
        rows = pred["events"][truth["id"]]
        assigned = 0
        for e, end in [(first, second["onset_s"]), (second, 40 + 1 / 30)]:
            valid = [a for a in rows if e["onset_s"] <= a["report"] / 30 < end]
            assert not valid or valid == sorted(valid, key=lambda a: a["report"])
            assigned += bool(valid)
            if e is second and valid:
                a = valid[0]
                for arm in hits:
                    deadline = a["report"] if arm == "native" else a.get("readout")
                    label = a.get("original" if arm == "native" else arm)
                    if deadline is not None and deadline / 30 < e["off_s"] and label == e["family"]:
                        hits[arm] += 1
        extras += len(rows) - assigned
    assert extras == scores["event_extras"]
    assert hits == {k: s["correct"] for k, s in scores["summaries"].items()}
    for arm, records in pred["normal"].items():
        assert len(records) == 36 and sum(r["alarms"] for r in records) == scores["quiet"][arm]["alarms"]
    print("Verified seals, matched alarms, seven endpoint counts and normal exposure.")


def replay():
    import simulate_pairs as simulator
    import predict
    from freeze import verify

    verify()
    simulator.initialize()
    templates = sorted(
        (r for r in read(RUN / "truth_private/TEST.json") if r["kind"] == "normal"), key=lambda r: r["id"]
    )
    pairs = [("load", "load"), ("load", "line"), ("line", "load"), ("line", "line")] * 9
    np.random.default_rng(869147).shuffle(pairs)
    obs = read(RESULT / "observations.json")["records"]
    orig = {r["id"]: r["files"]["nominal"] for r in read(RUN / "OBSERVATIONS_P2_TEST.json")}
    pred = read(RESULT / "predictions.json")["events"]
    predict.init()
    for i in (0, 35):
        with TemporaryDirectory() as folder:
            simulator.TMP = Path(folder)
            (simulator.TMP / "pmu").mkdir()
            rec, _ = simulator.new_test((i, templates[i], pairs[i]))
            assert rec == obs[i]
            pid = rec["id"]
            task = (
                pid,
                simulator.TMP / "pmu" / (pid + ".npz"),
                RUN / "work/P2/TEST" / (pid + "_nominal") / "nominal",
                rec["observation_sha"],
                orig[pid],
            )
            _, events = predict.record(task)
            assert events == pred[pid]
    print("Reproduced two fresh trajectories byte for byte and all associated alarm outputs.")


if __name__ == "__main__":
    cli = argparse.ArgumentParser()
    cli.add_argument("--replay", action="store_true")
    args = cli.parse_args()
    audit()
    if args.replay:
        replay()

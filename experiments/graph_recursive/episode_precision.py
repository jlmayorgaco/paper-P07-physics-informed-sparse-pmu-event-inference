"""Second frozen operating point for the same candidate generator and logistic coefficients."""
import argparse

import numpy as np

from episode_gate import ConfirmedMonitor, Signatures
from episode_trial import (DATA, FREEZE, OUT, arrays, candidates, digest, filtered, intervals,
                           read, summarize, truth, verify, write_json)
from phasors import MODEL
from study import HERE


POINT = OUT / "f1_point.json"
PRED = OUT / "f1_predictions.json"
SEAL = OUT / "f1_seal.json"


def select():
    if POINT.exists() or (DATA / "test").exists():
        raise FileExistsError("Select the second operating point before generating the test cohort")
    primary = verify()
    options = [row for row in primary["selection"] if row["proposal"] == primary["proposal"]]
    best = max(options, key=lambda row: (row["macro_f1"], row["joint"], -row["extras"]))
    threshold = best["threshold"]
    write_json(POINT, dict(threshold=threshold, cut=float(np.log(threshold / (1-threshold))),
                           development=best, primary=digest(FREEZE), source=digest(HERE / "episode_precision.py")))


def config():
    point = read(POINT)
    if point["primary"] != digest(FREEZE) or point["source"] != digest(HERE / "episode_precision.py"):
        raise ValueError("F1 operating point changed")
    return dict(verify(), cut=point["cut"], threshold=point["threshold"])


class F1Monitor(ConfirmedMonitor):
    def __init__(self):
        super().__init__()
        self.config = config()


def seal():
    if PRED.exists():
        raise FileExistsError("F1 predictions already sealed")
    operating = config()
    records, traces = arrays("test")
    with np.load(MODEL) as archive:
        graph = dict(archive)
    rows = candidates(records, traces, Signatures(), graph, operating["proposal"])
    write_json(PRED, filtered(rows, operating))
    write_json(SEAL, dict(predictions=digest(PRED), point=digest(POINT),
                          manifest=digest(OUT / "test_manifest.json")))


def score():
    config()
    if read(SEAL) != dict(predictions=digest(PRED), point=digest(POINT),
                          manifest=digest(OUT / "test_manifest.json")):
        raise ValueError("F1 seal changed")
    labels = truth("test")
    forecasts = read(OUT / "predictions.json")
    if digest(OUT / "predictions.json") != read(OUT / "seal.json")["predictions"]:
        raise ValueError("Comparator predictions changed")
    forecasts["confirmed"] = read(PRED)
    result = summarize(labels, forecasts["confirmed"])
    result["paired_difference_ci95"] = intervals(labels, forecasts, read(OUT / "test_manifest.json")["clusters"])
    write_json(OUT / "f1_scores.json", result)
    print(result["joint"], result["macro_f1"], result["extras"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("select","seal","score"))
    stage = parser.parse_args().stage
    {"select": select, "seal": seal, "score": score}[stage]()

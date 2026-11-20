"""Compute causal graph traces once per stream for all episode-decision rules."""
import argparse
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from episode_cohort import DATA, OUT
from phasors import MODEL
from robust import trace_student
from study import HERE, digest, read


def initialize(split):
    global observer, streams
    with np.load(MODEL, allow_pickle=False) as model:
        observer = dict(model)
    streams = np.load(DATA / split / "pmu.npy", mmap_mode="r", allow_pickle=False)


def run_one(index):
    return trace_student(observer, streams[index])


def trace_path(split):
    return DATA / split / "graph_trace.npy"


def evidence(split, workers=6):
    import json
    from study import write_json
    manifest = read(OUT / f"{split}_manifest.json")
    data_hash = digest(DATA / split / "pmu.npy")
    if data_hash != manifest["observations"]:
        raise ValueError("Invalid PMU data")
    inputs = {"observations": data_hash, "model": digest(MODEL),
              "source": [digest(HERE / p) for p in ("robust.py", "physical.py", "estimator.py", "episode_trace.py")]}
    path = trace_path(split)
    receipt = path.with_suffix(".json")
    if receipt.exists():
        saved = json.loads(receipt.read_text())
        if saved["inputs"] != inputs or saved["output"] != digest(path):
            raise ValueError("Invalid trace cache")
        return
    with ProcessPoolExecutor(workers, initializer=initialize, initargs=(split,)) as pool:
        traces = list(pool.map(run_one, range(manifest["records"])))
    np.save(path, np.asarray(traces))
    write_json(receipt, dict(inputs=inputs, output=digest(path)))
    print("traced", split, len(traces), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("split", choices=("train", "dev", "test"))
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()
    evidence(args.split, args.workers)

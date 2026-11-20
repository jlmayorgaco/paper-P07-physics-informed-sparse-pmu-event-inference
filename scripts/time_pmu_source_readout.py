"""Measure the incremental CPU-path wall time after frames and family are available."""

import argparse
import json
from pathlib import Path
from time import perf_counter
import numpy as np
from competition_response_bank import frames_from
from pmu_source_readout import localize


def run(root, model_dir):
    bank = dict(np.load(model_dir / "bank.npz", allow_pickle=False))
    records = json.loads((root / "predictions.json").read_text())
    times = []
    # Frozen earlier cohort, deterministically select at most eight cases per physical prediction.
    counts = {}
    for key, row in sorted(records.items()):
        family = row["successor"][0]
        if f"sites{family}" not in bank or counts.get(family, 0) >= 8:
            continue
        counts[family] = counts.get(family, 0) + 1
        frames = frames_from(root / "observations" / key)
        localize(frames, row["successor"], bank)
        start = perf_counter()
        localize(frames, row["successor"], bank)
        times.append(1000 * (perf_counter() - start))
    result = dict(
        cases=len(times),
        counts=counts,
        median_ms=float(np.median(times)),
        p95_ms=float(np.quantile(times, 0.95)),
    )
    (model_dir / "readout_timing.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("root", type=Path)
    p.add_argument("model_dir", type=Path)
    a = p.parse_args()
    run(a.root, a.model_dir)

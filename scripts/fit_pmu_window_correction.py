"""Select graph attenuation lengths using only prior M9 cohorts, balanced by asset."""

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from pmu_window_correction import (
    distance_signatures,
    spatial_estimate,
    physical_evidence,
    electrical,
)


def fit(roots, data, out):
    circuit = electrical.network_signatures(data)
    graph = distance_signatures(data)
    lengths = [0.025, 0.05, 0.1, 0.2]
    cases = defaultdict(list)
    for root in roots:
        truth = json.loads((root / "truth.json").read_text())
        for key, row in truth.items():
            family = row["code"]
            if family not in (1, 2, 3, 4, 6) or row.get("end", 120) != 120:
                continue
            frames = electrical.prior.bank.frames_from(root / "observations" / key)
            volts = physical_evidence(frames)[0]
            original = electrical.rank_source(frames, [family, "none"], circuit)[1]
            guesses = [original] + [
                spatial_estimate(volts, family, graph, v) for v in lengths
            ]
            cases[(family, row["source"])].append([s == row["source"] for s in guesses])
    scores, selected = {}, {}
    for family in (1, 2, 3, 4, 6):
        by_asset = [
            np.mean(rows, axis=0) for (c, _), rows in cases.items() if c == family
        ]
        means = np.mean(by_asset, axis=0)
        best = int(np.argmax(means))
        scores[family] = dict(assets=len(by_asset), rates=means.tolist())
        if best and means[best] > means[0]:
            selected[family] = lengths[best - 1]
    out.write_text(
        json.dumps(
            dict(selected=selected, lengths=lengths, development=scores), indent=2
        )
        + "\n"
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("data", type=Path)
    p.add_argument("out", type=Path)
    p.add_argument("roots", nargs="+", type=Path)
    a = p.parse_args()
    fit(a.roots, a.data, a.out)

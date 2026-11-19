"""Report before/after differences on the common successor blind replay."""

import argparse
import json
from pathlib import Path
from score_paired_m9_stream import score, METHODS


def report(root, out):
    methods = dict(METHODS, successor="Revised hybrid")
    score(root, out, methods=methods, repetitions=6)
    metrics = json.loads((out / "metrics.json").read_text())
    pred = json.loads((root / "predictions.json").read_text())
    truth = json.loads((root / "truth.json").read_text())
    for cond in ("isolated", "consecutive"):
        keys = [
            k for k, t in truth.items() if t["end"] == 120 and t["condition"] == cond
        ]
        for m in methods:
            r = metrics[cond][m]
            for group, codes in (
                ("physical", (1, 2, 3, 4, 6, 8)),
                ("instrument", (5, 7)),
            ):
                kg = [k for k in keys if truth[k]["code"] in codes]
                r[group + "_exact"] = sum(
                    pred[k][m][1] == truth[k]["source"] for k in kg
                )
                r[group + "_events"] = len(kg)
            r["joint_hits"] = sum(
                pred[k][m] == [truth[k]["code"], truth[k]["source"]]
                for k in keys
                if truth[k]["code"]
            )
        delta = {}
        for endpoint in ("family", "source"):
            gained, lost = 0, 0
            for k in keys:
                if endpoint == "source" and not truth[k]["code"]:
                    continue
                j, field = (0, "code") if endpoint == "family" else (1, "source")
                old, new = [
                    pred[k][m][j] == truth[k][field]
                    for m in ("electrical", "successor")
                ]
                gained += int(new and not old)
                lost += int(old and not new)
            delta[endpoint] = dict(gained=gained, lost=lost)
        metrics.setdefault("paired_method_changes", {})[cond] = delta
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("root", type=Path)
    p.add_argument("out", type=Path)
    a = p.parse_args()
    report(a.root, a.out)

"""Report before/after differences on the common successor blind replay."""

import argparse
import json
from pathlib import Path
import numpy as np
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
        # Keep all nine true classes represented in each paired bootstrap.
        by_class = [
            [k for k in sorted(keys) if truth[k]["code"] == c] for c in range(9)
        ]
        draws = np.random.default_rng(120261).integers(0, 6, (5000, 9, 6))
        samples = {}
        for method in ("electrical", "successor"):
            predictions = np.array(
                [[pred[k][method][0] for k in group] for group in by_class]
            )
            sampled = predictions[np.arange(9)[None, :, None], draws]
            correct = (sampled == np.arange(9)[None, :, None]).sum(axis=2)
            called = np.array([(sampled == c).sum(axis=(1, 2)) for c in range(9)]).T
            samples[method] = (2 * correct / (6 + called)).mean(axis=1)
        delta["macro_f1_paired_interval"] = np.quantile(
            samples["successor"] - samples["electrical"], [0.025, 0.975]
        ).tolist()
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
    lines = [r"\begin{tabular}{lrrrrr}\toprule",
             r"Method & Macro-F1 & Family & Detected & Source & Physical\\",
             r"\midrule"]
    for cond in ("isolated", "consecutive"):
        title = "Isolated target" if cond == "isolated" else "Target after a fault"
        lines.append(r"\multicolumn{6}{l}{\emph{" + title + r"}}\\")
        for method, name in methods.items():
            r = metrics[cond][method]
            lines.append(
                f"{name} & {r['macro_f1']:.3f} & {r['family_hits']} & "
                f"{r['detections']} & {r['exact_hits']} & {r['physical_exact']}" + r"\\"
            )
    lines.append(r"\bottomrule\end{tabular}")
    (out / "table.tex").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("root", type=Path)
    p.add_argument("out", type=Path)
    a = p.parse_args()
    report(a.root, a.out)

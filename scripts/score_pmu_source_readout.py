"""Score exact sources and test every invariant against the released window classifier."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from score_paired_m9_stream import summarize

FAMILIES = (
    "Normal",
    "Fault",
    "Line",
    "Generation",
    "Load",
    "Missing",
    "Mixed",
    "Bad data",
    "Composite",
)
METHODS = ("baseline", "registered")


def assess(root, out):
    blob = (root / "predictions.json").read_bytes()
    assert hashlib.sha256(blob).hexdigest() == json.loads(
        (root / "seal.json").read_text()
    )
    pred = json.loads(blob)
    truth = json.loads((root / "truth.json").read_text())
    assert truth.keys() == pred.keys() and len(truth) == 288
    assert all(r["baseline"][0] == r["registered"][0] for r in pred.values())
    assert all(
        r["baseline"] == r["registered"]
        for r in pred.values()
        if r["baseline"][0] in (0, 5, 7)
    )
    assert len({(r["pair"], r["end"], r["condition"]) for r in truth.values()}) == 288
    for pair in {r["pair"] for r in truth.values()}:
        targets = [r for r in truth.values() if r["pair"] == pair and r["end"] == 120]
        assert (
            len(targets) == 2
            and len({(r["code"], r["source"], r["onset"]) for r in targets}) == 1
        )
    stats = {}
    fig, axes = plt.subplots(
        1, 2, sharey=True, figsize=(7.1, 3.3), layout="constrained"
    )
    for condition in ("isolated", "consecutive", "all_windows"):
        keys = [
            k
            for k, v in truth.items()
            if condition == "all_windows"
            or (v["end"] == 120 and v["condition"] == condition)
        ]
        results = {m: summarize(keys, truth, pred, m) for m in METHODS}
        old, new = results.values()
        assert all(old[k] == new[k] for k in old if k != "exact_hits")
        for method in METHODS:

            def hits(ks):
                return sum(pred[k][method][1] == truth[k]["source"] for k in ks)

            row = results[method]
            ev = [k for k in keys if truth[k]["code"]]
            physical = [k for k in ev if truth[k]["code"] not in (5, 7)]
            row.update(
                physical_hits=hits(physical),
                physical_events=len(physical),
                joint_hits=sum(
                    pred[k][method] == [truth[k]["code"], truth[k]["source"]]
                    for k in ev
                ),
            )
        stats[condition] = results
        if condition == "all_windows":
            continue
        assert Counter(truth[k]["code"] for k in keys) == Counter(
            {c: 8 for c in range(9)}
        )
        classes = []
        changes = {}
        for code in range(1, 9):
            subset = [k for k in keys if truth[k]["code"] == code]
            hit = np.array(
                [[pred[k][m][1] == truth[k]["source"] for m in METHODS] for k in subset]
            )
            classes.append(hit)
            a, b = hit.T
            changes[code] = dict(
                baseline=int(a.sum()),
                registered=int(b.sum()),
                gained=int((~a & b).sum()),
                lost=int((a & ~b).sum()),
            )
        stats[condition]["by_class"] = changes
        # Paired within each of eight target classes, conditional on the simulated design.
        diff = np.array([h[:, 1].astype(int) - h[:, 0].astype(int) for h in classes])
        ix = np.random.default_rng(88152).integers(0, 8, size=(10000, 8, 8))
        bootstrap = diff[np.arange(8)[None, :, None], ix].mean(axis=(1, 2))
        stats[condition]["paired_gain_interval"] = np.quantile(
            bootstrap, [0.025, 0.975]
        ).tolist()
        ax = axes[int(condition == "consecutive")]
        for idx, (key, label, color, marker) in enumerate(
            (
                ("baseline", "Previous hybrid", "#be702d", "s"),
                ("registered", "Calibrated readout", "#12695e", "o"),
            )
        ):
            x = [c[key] for c in changes.values()]
            ax.scatter(
                x,
                np.arange(8) + (0.12 if idx else -0.12),
                label=label,
                c=color,
                marker=marker,
                s=28,
            )
        ax.set_title("Isolated target" if condition == "isolated" else "After a fault")
        ax.set_xlabel("Exact locations out of eight")
        ax.set_xlim(-0.4, 8.4)
        ax.set_xticks(range(0, 9, 2))
        ax.grid(axis="x", alpha=0.25)
    axes[0].set_yticks(range(8), FAMILIES[1:])
    axes[0].invert_yaxis()
    handles, labels = axes[1].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside lower center", ncol=2, frameon=False)
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / "locations.pdf", metadata={"CreationDate": None, "ModDate": None})
    plt.close(fig)
    (out / "results.json").write_text(json.dumps(stats, indent=2) + "\n")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("root", type=Path)
    p.add_argument("out", type=Path)
    a = p.parse_args()
    assess(a.root, a.out)

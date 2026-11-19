"""Verify sealed paired predictions and publish metrics and six confusion matrices."""

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import numpy as np
from sklearn.metrics import confusion_matrix, f1_score

METHODS = {
    "submitted": "Submission",
    "physical": "Attributor II",
    "electrical": "Electrical hybrid",
}


def summarize(keys, truth, preds, method):
    y = np.array([truth[k]["code"] for k in keys])
    p = np.array([preds[k][method][0] for k in keys])
    assert np.isin(p, range(9)).all()
    alarm, event = p != 0, y != 0
    detected = alarm & event
    delays = [
        truth[k]["end"] - truth[k]["onset"] for k, hit in zip(keys, detected) if hit
    ]
    negatives = int((~event).sum())
    false = int((alarm & ~event).sum())
    return dict(
        windows=len(keys),
        events=int(event.sum()),
        detections=int(detected.sum()),
        normal=negatives,
        false_alarms=false,
        normal_hours=negatives / 120,
        false_alarms_per_hour=false * 120 / negatives if negatives else None,
        median_delay_s=float(np.median(delays)) if delays else None,
        macro_f1=float(
            f1_score(y, p, labels=list(range(9)), average="macro", zero_division=0)
        ),
        family_hits=int((p == y).sum()),
        exact_hits=sum(
            bool(truth[k]["code"] and truth[k]["source"] == preds[k][method][1])
            for k in keys
        ),
        confusion=confusion_matrix(y, p, labels=list(range(9))).tolist(),
    )


def score(root, out, *, methods=METHODS, repetitions=3):
    raw = (root / "predictions.json").read_bytes()
    assert sha256(raw).hexdigest() == json.loads((root / "seal.json").read_text())
    preds, truth = json.loads(raw), json.loads((root / "truth.json").read_text())
    assert preds.keys() == truth.keys() and len(truth) == 36 * repetitions
    assert all(
        len(rows) == len(methods) and rows.keys() == methods.keys()
        for rows in preds.values()
    )
    assert set(Counter((v["pair"], v["end"]) for v in truth.values()).values()) == {2}
    assert (
        len({(v["pair"], v["end"], v["condition"]) for v in truth.values()})
        == 36 * repetitions
    )
    metrics = {}
    fig, axes = plt.subplots(
        2,
        len(methods),
        figsize=(7.1, 4.65),
        layout="constrained",
        sharex=True,
        sharey=True,
    )
    for i, condition in enumerate(("isolated", "consecutive")):
        keys = [
            k
            for k, t in truth.items()
            if t["condition"] == condition and t["end"] == 120
        ]
        assert Counter(truth[k]["code"] for k in keys) == Counter(
            {c: repetitions for c in range(9)}
        )
        metrics[condition] = {}
        for j, (method, title) in enumerate(methods.items()):
            result = summarize(keys, truth, preds, method)
            metrics[condition][method] = result
            matrix = np.array(result["confusion"])
            ax = axes[i, j]
            ax.imshow(matrix, cmap="Blues", norm=Normalize(0, repetitions))
            for (r, c), value in np.ndenumerate(matrix):
                if value:
                    ax.text(
                        c,
                        r,
                        str(value),
                        ha="center",
                        va="center",
                        fontsize=7,
                        color="white" if value > repetitions / 2 else "black",
                    )
            ax.set_xticks(range(9))
            ax.set_yticks(range(9))
            ax.tick_params(labelsize=7, length=0)
            if i == 0:
                ax.set_title(title, fontsize=9)
            if i == 1:
                ax.set_xlabel("Predicted class", fontsize=8)
            if j == 0:
                ax.set_ylabel(condition.capitalize() + "\nTrue class", fontsize=8)
    for label, end in (("first_window", 90), ("all_windows", None)):
        keys = [k for k, t in truth.items() if end is None or t["end"] == end]
        metrics[label] = {m: summarize(keys, truth, preds, m) for m in methods}
    quiet_keys = [
        k for k, t in truth.items() if t["code"] == 0 and t["condition"] == "isolated"
    ]
    assert len(quiet_keys) == 10 * repetitions
    metrics["quiet_only"] = {m: summarize(quiet_keys, truth, preds, m) for m in methods}
    pairs = {}
    for key, target in truth.items():
        if target["end"] == 120:
            pairs.setdefault(target["pair"], {})[target["condition"]] = key
    metrics["paired_family_changes"] = {}
    for method in methods:
        counts = Counter()
        for pair in pairs.values():
            first, second = pair["isolated"], pair["consecutive"]
            assert all(
                truth[first][field] == truth[second][field]
                for field in ("code", "source", "onset")
            )
            before, after = preds[first][method][0], preds[second][method][0]
            label = truth[first]["code"]
            if before != after:
                counts["changed"] += 1
                counts["became_correct"] += int(after == label)
                counts["became_incorrect"] += int(before == label)
        metrics["paired_family_changes"][method] = dict(counts)
    out.mkdir(parents=True, exist_ok=True)
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
    fig.savefig(out / "confusion.pdf", metadata={"CreationDate": None, "ModDate": None})
    plt.close(fig)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("root", type=Path)
    p.add_argument("out", type=Path)
    args = p.parse_args()
    score(args.root, args.out)

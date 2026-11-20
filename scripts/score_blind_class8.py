"""Score sealed nine-class decisions and paired class-8 source changes."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

import numpy as np
from score_paired_m9_stream import summarize


def score(root, out):
    raw = (root / "predictions.json").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == json.loads(
        (root / "seal.json").read_text()
    )
    preds = json.loads(raw)
    extra = (root / "current_predictions.json").read_bytes()
    assert hashlib.sha256(extra).hexdigest() == json.loads(
        (root / "current_seal.json").read_text()
    )
    secondary = json.loads(extra)
    assert secondary.keys() == preds.keys()
    for k, r in preds.items():
        r["joint_current"] = secondary[k]
        assert r["joint_current"][0] == r["joint"][0]
        if r["joint"][0] != 8:
            assert r["joint_current"] == r["joint"]
    truth = json.loads((root / "truth.json").read_text())
    assert len(preds) == 288 and preds.keys() == truth.keys()
    assert all(r["registered"][0] == r["joint"][0] for r in preds.values())
    assert all(
        r["registered"] == r["joint"] for r in preds.values() if r["joint"][0] != 8
    )
    for r in preds.values():
        if "probability" in r:
            p = r["probability"]
            assert (
                len(p) == 39
                and np.isclose(sum(p.values()), 1)
                and max(p, key=p.get) == r["joint"][1]
            )
    result = {}
    for context in ("isolated", "consecutive", "all_windows"):
        keys = [
            k
            for k, t in truth.items()
            if context == "all_windows" or t["condition"] == context and t["end"] == 120
        ]
        if context != "all_windows":
            assert Counter(truth[k]["code"] for k in keys) == {c: 8 for c in range(9)}
        paired = {
            m: summarize(keys, truth, preds, m)
            for m in ("registered", "joint", "joint_current")
        }
        old = paired["registered"]
        for new in paired.values():
            assert all(old[k] == new[k] for k in old if k != "exact_hits")
        c8 = [k for k in keys if truth[k]["code"] == 8]
        by_method = {}
        for m in paired:
            by_method[m] = dict(
                n=len(c8),
                detected_as_composite=sum(preds[k][m][0] == 8 for k in c8),
                exact=sum(preds[k][m][1] == truth[k]["source"] for k in c8),
            )
        gains, losses = 0, 0
        for k in keys:
            if not truth[k]["code"]:
                continue
            a, b = (
                preds[k][m][1] == truth[k]["source"] for m in ("registered", "joint")
            )
            gains += int(b and not a)
            losses += int(a and not b)
        paired["class8"] = by_method
        paired["source_changes"] = dict(gained=gains, lost=losses)
        result[context] = paired
    out.mkdir(parents=True, exist_ok=True)
    (out / "blind_results.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("root", type=Path)
    p.add_argument("out", type=Path)
    a = p.parse_args()
    score(a.root, a.out)

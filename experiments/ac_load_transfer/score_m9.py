"""Check both prediction seals and score the secondary load-only readout on target windows."""

import argparse
from hashlib import sha256
import json
from pathlib import Path


def score(root, out):
    for pred_dir, prefix in ((root, ""), (out, "ac_m9_")):
        raw = (pred_dir / (prefix + "predictions.json")).read_bytes()
        assert sha256(raw).hexdigest() == json.loads(
            (pred_dir / (prefix + "seal.json")).read_text()
        )
    baseline = json.loads((root / "predictions.json").read_text())
    ac = json.loads((out / "ac_m9_predictions.json").read_text())
    truth = json.loads((root / "truth.json").read_text())
    assert baseline.keys() == ac.keys() == truth.keys()
    assert all(
        ac[k] == p["successor"] or ac[k][0] == p["successor"][0] == 4
        for k, p in baseline.items()
    )
    results = {}
    for condition in ("isolated", "consecutive"):
        keys = [
            k
            for k, t in truth.items()
            if t["condition"] == condition and t["end"] == 120 and t["code"]
        ]
        result = {}
        for group, subset in (
            ("all", keys),
            ("load", [k for k in keys if truth[k]["code"] == 4]),
        ):
            result[group] = dict(
                events=len(subset),
                previous=sum(
                    baseline[k]["successor"][1] == truth[k]["source"] for k in subset
                ),
                ac=sum(ac[k][1] == truth[k]["source"] for k in subset),
            )
        results[condition] = result
    (out / "ac_m9_results.json").write_text(json.dumps(results, indent=2) + "\n")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("root", type=Path)
    p.add_argument("out", type=Path)
    a = p.parse_args()
    score(a.root, a.out)

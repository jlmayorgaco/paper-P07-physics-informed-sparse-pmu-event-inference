"""Audit case pairing, physical site disjointness and angle agreement after sealing."""
from collections import Counter
import json
from pathlib import Path
import sys

from competition_held_locations import METHODS, score, save
from prepare_held_locations import SITES


def audit(root):
    results = score(root)
    assert results == json.loads((root / "results.json").read_text())
    labels = json.loads((root / "primary/truth.json").read_text())
    predictions = json.loads((root / "predictions.json").read_text())
    old = json.loads(Path("experiments/competition_spatial_264/primary/truth.json").read_text())
    details = {}
    for family in range(9):
        cases = [k for k in labels if labels[k]["code"] == family]
        sites = Counter(labels[k]["source"] for k in cases)
        if family in SITES:
            prior = {r["source"] for r in old.values() if r["code"] == family}
            assert len(sites) == 3 and set(sites).isdisjoint(prior)
            assert set(sites.values()) == {4}
        details[family] = dict(sites=sites, methods={})
        for method in METHODS:
            details[family]["methods"][method] = dict(
                family=sum(predictions[k][method][0] == family for k in cases),
                exact=sum(predictions[k][method][1] == labels[k]["source"] for k in cases))
    admission = [v for split in ("primary","quiet") for v in
                 json.loads((root/split/"dynamic_admission.json").read_text()).values()]
    return dict(per_family=details,
                identical_under_turn=sum(r["residual"]==r["residual_shifted"] for r in predictions.values()),
                total=len(predictions),
                startup_angle_rejections=sum(v.startswith("Noise estimate outside support: voltage_angle ") for v in admission))


if __name__ == "__main__":
    root = Path(sys.argv[1])
    save(root/"audit.json", audit(root))

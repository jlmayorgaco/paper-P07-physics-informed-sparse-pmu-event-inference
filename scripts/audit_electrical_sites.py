"""Recount paired site-level hits and check that all physical truths were eligible."""
import argparse
from collections import Counter
import json
from pathlib import Path

import numpy as np

from competition_electrical_localizer import METHODS, PHYSICAL, network_signatures
from benchmark_competition_windows import save
from prepare_electrical_sites import CATALOG, NEW, SITES


def audit(root, submitted):
    signatures = network_signatures(submitted/"data")
    read = lambda name: json.loads((root/name).read_text())
    truth = read("primary/truth.json")
    rows = read("predictions.json")
    assert all(r["residual"][0] == r["electrical"][0] for r in rows.values())
    old = {s for table in (CATALOG,SITES) for group in table.values() for s in group}
    per_class = {}
    for family in range(9):
        cases = [k for k in truth if truth[k]["code"] == family]
        sites = Counter(truth[k]["source"] for k in cases)
        if family in PHYSICAL:
            expected = {s.replace("BUS","") if "-" in s else s for s in NEW[family]}
            expected = {"LINE"+s if "-" in s else s for s in expected}
            assert set(sites)==expected and set(sites.values())=={4}
            assert set(sites)<=set(signatures[family]) and set(NEW[family]).isdisjoint(old)
        per_class[family] = dict(true_sites=sites,methods={})
        for m in METHODS:
            per_class[family]["methods"][m] = dict(
                family=sum(rows[k][m][0]==family for k in cases),
                exact=sum(rows[k][m][1]==truth[k]["source"] for k in cases))
    physical = [k for k in truth if truth[k]["code"] in PHYSICAL]
    changes = Counter()
    for k in physical:
        before = rows[k]["residual"][1] == truth[k]["source"]
        after = rows[k]["electrical"][1] == truth[k]["source"]
        changes[(before, after)] += 1
    # Identifiability check under the linear model itself: unknown common
    # component and complex amplitude, noiseless observations at all eight PMUs.
    indistinguishable = {}
    for family,templates in signatures.items():
        matrix = np.array(list(templates.values()))
        matrix -= matrix.mean(axis=1,keepdims=True)
        matrix /= np.linalg.norm(matrix,axis=1,keepdims=True)
        matches = np.abs(matrix @ matrix.conj().T) >= 1-1e-10
        names = list(templates)
        indistinguishable[family] = [[names[a],names[b]] for a,b in zip(*np.where(np.triu(matches,1)))]
    admissions = [v for split in ("primary","quiet") for v in read(split+"/dynamic_admission.json").values()]
    return dict(per_class=per_class, physical_records=len(physical), locations_gained=changes[False,True],
                locations_lost=changes[True,False], identical_family_calls=len(rows),
                startup_noise_rejections=sum(v.startswith("Noise estimate outside support: voltage_angle ") for v in admissions),
                indistinguishable_candidate_pairs=indistinguishable)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("root",type=Path)
    p.add_argument("submitted",type=Path)
    a = p.parse_args()
    save(a.root/"audit.json",audit(a.root,a.submitted))

"""IEEE-39 equivalent-network source ranking for the frozen PMU window classifier."""
import argparse
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
import re

import numpy as np
import pandas as pd

import competition_held_locations as prior
from benchmark_competition_windows import save

METHODS = ("submitted", "residual", "electrical")
PHYSICAL = (1, 2, 3, 4, 6, 8)


def network_signatures(data):
    # RAW internal indices differ from physical BUS names.
    raw = (data/"metadata/IEEE_39_Bus_Power_System.raw").read_text().splitlines()[3:]
    ids, loads, gens = {}, [], []
    v0 = np.empty(39, dtype=complex)
    section = 0
    for line in raw:
        if line.strip().startswith("0 /end"):
            section += 1
            if section == 3:
                break
            continue
        fields = line.split("/")[0].split(",")
        internal = int(fields[0])
        if section == 0:
            bus = int(re.search(r"BUS(\d+)", fields[1])[1])
            ids[internal] = bus
            v0[bus-1] = float(fields[8])*np.exp(1j*np.deg2rad(float(fields[9])))
        elif section == 1 and float(fields[5]) > 0:
            loads.append(ids[internal])
        elif section == 2:
            gens.append(ids[internal])
    assert len(set(ids.values())) == 39 and len(gens) == 10
    topo = data/"topology/ieee39"
    matrix = pd.read_csv(topo/"ybus_full_complex.csv")
    y = np.zeros((39,39), dtype=complex)
    y[matrix.from_bus-1, matrix.to_bus-1] = matrix.real + 1j*matrix.imag
    # Norton generator equivalents behind a common assumed transient reactance.
    g = np.array(gens)-1
    y[g,g] += 1/(.2j)
    z = np.linalg.inv(y)
    observed = np.array(prior.bank.BUSES)-1
    bus_families = {1: range(1,40), 3: gens, 4: loads, 6: gens, 8: range(1,40)}
    bank = {fam: {f"BUS{k}": z[observed,k-1]/v0[observed] for k in sorted(set(sites))}
            for fam,sites in bus_families.items()}
    lines = {}
    for b in pd.read_csv(topo/"branches_physical.csv").itertuples():
        a, c = b.from_bus, b.to_bus
        yseries = 1/complex(b.r,b.x)
        tap = b.tap*np.exp(1j*np.deg2rad(b.shift_deg))
        diag = yseries + .5j*b.b
        stamp = np.array([[diag/abs(tap)**2, -yseries/tap.conjugate()],[-yseries/tap, diag]])
        terminals = np.array([a,c])-1
        post = y.copy()
        post[np.ix_(terminals,terminals)] -= stamp
        rhs = np.zeros(39, complex)
        rhs[terminals] = stamp @ v0[terminals]
        dv = np.linalg.lstsq(post,rhs,rcond=1e-10)[0]
        lines[f"LINE{min(a,c)}-{max(a,c)}"] = dv[observed]/v0[observed]
    assert len(lines) == 46
    bank[2] = lines
    return bank


def rank_source(frames, decision, signatures):
    family = decision[0]
    if family not in signatures:
        return decision
    data = prior.spatial.channels(frames)
    voltage = data[:,::4] + 1j*np.deg2rad(data[:,1::4])
    scale = np.maximum(np.nanstd(voltage[:1800],axis=0), 1e-6)
    pulse = prior.residual_pulse(frames) if family == 8 else None
    if family == 1:
        # Short fault: select the three-report excursion with greatest quiet-scaled energy.
        centered = voltage[1800:] - np.nanmean(voltage[:1800],axis=0)
        smooth = (centered[:-2]+centered[1:-1]+centered[2:])/3
        dx = smooth[np.nanargmax(np.nansum(abs(smooth/scale)**2,axis=1))]
    else:
        dx4 = prior.spatial.contrast(data,pulse)
        dx = dx4[::4] + 1j*np.deg2rad(dx4[1::4])
    valid = np.isfinite(dx) & np.isfinite(scale)
    if valid.sum() < 3:
        return [family, "none"]
    # Profile a common offset and unknown complex event strength by weighted LS.
    weights = 1/scale[valid]**2
    def centered(x):
        x = x[...,valid]
        return (x - np.average(x,axis=-1,weights=weights)[...,None])*np.sqrt(weights)
    templates = signatures[family]
    s = centered(np.array(list(templates.values())))
    obs = centered(dx)
    energy = np.sum(abs(s)**2,axis=1)
    gain = abs(s.conj() @ obs)**2 / np.maximum(energy,1e-18)
    return [family, list(templates)[int(np.argmax(gain))]]


def init(submitted, admissions):
    global signatures
    prior.spatial.initialize(submitted, Path("experiments/competition_response_156/bank.json"),
                             admissions, Path("experiments/competition_spatial_264/spatial.json"))
    signatures = network_signatures(submitted/"data")


def infer(folder):
    frames = prior.native.api._load_frames(folder)
    api = prior.native.api
    start, end = api._window_bounds(frames,30)[-1]
    assert start == 60 and end < 90
    features = api._build_feature_rows(api._slice_frames(frames,start,end,True))
    pred = prior.native.model.predict_from_features(*features).iloc[0]
    original = [int(pred.pred_event), str(pred.pred_location)]
    frames = prior.canonical(frames)
    _, hybrid = prior.pipeline(frames, prior.bank.startup[folder.name], prior.residual_pulse)
    return folder.name, dict(submitted=original, residual=hybrid,
                             electrical=rank_source(frames,hybrid,signatures))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("stage",choices=["predict","score","verify"])
    p.add_argument("root",type=Path)
    p.add_argument("--submitted",type=Path)
    a = p.parse_args()
    if a.stage == "predict":
        admissions = {}
        for split in ("primary","quiet"):
            admissions.update(json.loads((a.root/split/"dynamic_admission.json").read_text()))
        with ProcessPoolExecutor(max_workers=8,initializer=init,
                                 initargs=(a.submitted.resolve(),admissions)) as pool:
            rows = dict(pool.map(infer, sorted(a.root.glob("*/observations/*"))))
        save(a.root/"predictions.json", rows)
        save(a.root/"seal.json",prior.digest(a.root/"predictions.json"))
    else:
        results = prior.score(a.root,methods=METHODS)
        if a.stage == "score":
            save(a.root/"results.json",results)
        else:
            assert results == json.loads((a.root/"results.json").read_text())
            print("Verified sealed results for all three methods.")

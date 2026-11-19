"""Paired synthetic test of a masked, prefix-scaled PMU response bank."""
import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from benchmark_competition_windows import prepare, save
import competition_integrity_successor as baseline


BUSES = (2, 5, 6, 10, 19, 22, 29, 39)
GENERATORS = ("BUS2", "BUS32", "BUS39")
CATALOG = {1: ("BUS39", "BUS16", "BUS7"), 2: ("BUS23-BUS24", "BUS16-BUS17", "BUS3-BUS4"),
           3: GENERATORS, 4: ("BUS7", "BUS20", "BUS39"), 6: GENERATORS,
           8: ("BUS19", "BUS7", "BUS39")}
SPAN = 10


def measurements(frames):
    channels = []
    for bus in BUSES:
        d = frames[bus]
        valid = d.DATA_PRESENT.eq(1)
        prefix = d.TIMESTAMP < 60
        mag = d[[f"BUS{bus}_V{p}_MAG" for p in "ABC"]].where(valid, axis=0)
        mag = mag.div(mag[prefix].median()).mean(axis=1)
        ang = d[[f"BUS{bus}_V{p}_ANG" for p in "ABC"]].where(valid, axis=0)
        # Each phase has its own reference and can wrap at +/-180 degrees.
        ref = np.rad2deg(np.angle(np.exp(1j*np.deg2rad(ang[prefix])).mean(axis=0)))
        ang = ((ang - ref + 180) % 360 - 180).mean(axis=1)
        channels.extend((mag, ang, d[f"BUS{bus}_Freq"].where(valid)))
    matrix = pd.concat(channels, axis=1)
    blocks = matrix.groupby(frames[BUSES[0]].TIMESTAMP.astype(int))
    return blocks.mean().where(blocks.count() >= 15).to_numpy()


def paths(x, starts):
    # Each candidate onset uses the preceding five seconds as its local reference.
    return np.stack([x[t:t+SPAN] - np.nanmean(x[t-5:t], axis=0) for t in starts])


def scores(x, templates, starts):
    scale = np.maximum(np.nanstd(x[:60], axis=0), 1e-8)
    y = paths(x, starts) / scale
    s = templates / scale
    mask = np.isfinite(y).reshape(len(y), -1)
    y = np.nan_to_num(y).reshape(len(y), -1)
    s = s.reshape(len(s), -1)
    inner = y @ s.T
    energy = mask.astype(float) @ (s*s).T
    # Twice the diagonal-Gaussian log likelihood gain, profiling positive
    # amplitude over a bounded range. A missing report contributes zero.
    amplitude = np.clip(inner / np.maximum(energy, 1e-9), 0, 2)
    gain = 2*amplitude*inner - amplitude**2*energy
    return gain.max(axis=0)


def frames_from(folder):
    return {b: pd.read_csv(folder / f"Bus{b}_Competition_Data_nanmask.csv") for b in BUSES}


def fit(dev, target):
    truth = json.loads((dev/"truth.json").read_text())
    series, groups = {}, {}
    for case, label in truth.items():
        x = measurements(frames_from(dev/"observations"/case))
        series[case] = x
        if label["code"] in (1,2,3,4,8):
            key = (label["code"], label["source"])
            groups.setdefault(key, []).append(paths(x,[round(label["onset_s"])])[0])
    keys = sorted(groups)
    templates = np.array([np.mean(groups[k],axis=0) for k in keys])
    # Protect the quiet class and isolated instrumentation problems.
    null_scores = [scores(x,templates,range(5,51)).max() for x in series.values()]
    null_scores.extend(scores(series[i],templates,range(60,81)).max()
                       for i,r in truth.items() if r["code"] in (0,5,7))
    save(target,dict(keys=keys, templates=templates.tolist(), threshold=1.1*max(null_scores)))


def classify(x, current, bank, frames):
    if current[0] not in (0,1,5,6,7):
        return current, "keep"
    gain = scores(x, np.asarray(bank["templates"]), range(60,81))
    best = int(np.argmax(gain))
    if gain[best] <= bank["threshold"]:
        return current, "keep"
    family, source = bank["keys"][best]
    if (current[0]==1 and family!=1) or (current[0]==7 and family!=8):
        return current, "keep"
    gap = any(((d.TIMESTAMP >= 60) & d.DATA_PRESENT.eq(0)).sum() >= 12 for d in frames.values())
    return [6 if gap else family, source], "response"


def init(submitted, model, admissions):
    global bank, startup
    baseline.init_model(submitted)
    bank = json.loads(model.read_text())
    startup = admissions


def infer(folder):
    case, old = baseline.infer(folder)
    if not startup[case].startswith("Noise estimate outside support: voltage_angle "):
        return case, dict(current=old["successor"], response=old["successor"], route="keep")
    frames = baseline.api._load_frames(folder)
    result, which = classify(measurements(frames),old["successor"],bank,frames)
    return case, dict(current=old["successor"], response=result, route=which)


def score(root):
    from sklearn.metrics import confusion_matrix, f1_score
    raw = (root/"predictions.json").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == json.loads((root/"seal.json").read_text())
    pred = json.loads(raw)
    results = {}
    truth = json.loads((root/"primary/truth.json").read_text())
    normals = json.loads((root/"quiet/truth.json").read_text())
    assert not truth.keys() & normals.keys() and pred.keys() == truth.keys() | normals.keys()
    ids = sorted(truth)
    codes = [truth[i]["code"] for i in ids]
    assert np.array_equal(np.bincount(codes),np.full(9,12))
    assert len(normals)==48 and all(v["code"]==0 for v in normals.values())
    all_quiet = list(normals) + [i for i in ids if truth[i]["code"]==0]
    for method in ("current","response"):
        called = [pred[i][method][0] for i in ids]
        events = [i for i in ids if truth[i]["code"]]
        results[method] = dict(macro_f1=f1_score(codes,called,average="macro",labels=range(9)),
            family_correct=sum(a==b for a,b in zip(codes,called)), windows=len(ids),
            source_correct=sum(pred[i][method][1]==truth[i]["source"] for i in events),
            joint=sum(pred[i][method]==[truth[i]["code"],truth[i]["source"]] for i in events),
            events=len(events), false_alarms=sum(pred[i][method][0]!=0 for i in all_quiet),
            normal_windows=len(all_quiet), confusion=confusion_matrix(codes,called,labels=range(9)).tolist())
    save(root/"results.json",results)
    print(json.dumps(results))


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("stage",choices=["fit","prepare","predict","score"])
    p.add_argument("root",type=Path)
    p.add_argument("--dev",type=Path)
    p.add_argument("--archive",type=Path)
    p.add_argument("--submitted",type=Path)
    a=p.parse_args()
    a.root.mkdir(parents=True,exist_ok=True)
    model=a.root/"bank.json"
    if a.stage=="fit":
        fit(a.dev,model)
    elif a.stage=="prepare":
        prepare(a.root/"primary",a.archive.resolve(),seed=12437713,repetitions=12,
                move_integrity=True,asset_catalog=CATALOG,vary_physical=True)
        prepare(a.root/"quiet",a.archive.resolve(),seed=23099417,repetitions=48,normal_only=True)
    elif a.stage=="predict":
        folders=sorted(a.root.glob("*/observations/*"))
        admissions={}
        for split in ("primary","quiet"):
            admissions.update(json.loads((a.root/split/"dynamic_admission.json").read_text()))
        with ProcessPoolExecutor(max_workers=4,initializer=init,initargs=(a.submitted.resolve(),model,admissions)) as pool:
            predictions=dict(pool.map(infer,folders))
        save(a.root/"predictions.json",predictions)
        save(a.root/"seal.json",hashlib.sha256((a.root/"predictions.json").read_bytes()).hexdigest())
    else:
        score(a.root)

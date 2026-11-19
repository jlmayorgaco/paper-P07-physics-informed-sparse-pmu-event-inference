"""Development-calibrated integrity correction and prospective synthetic comparison."""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from hashlib import sha256
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

from benchmark_competition_windows import prepare, save


def excursion(signal, initial, window):
    """Peak 12-report average relative to quiet fluctuations on the same channel."""
    reference = signal[initial].rolling(12).mean().dropna()
    current = signal[window].rolling(12).mean().dropna()
    if reference.empty or current.empty:
        return np.nan
    center = reference.median()
    scale = (reference - center).abs().quantile(.995)
    if not np.isfinite(scale) or scale <= 1e-10:
        return np.nan
    return float((current - center).abs().max() / scale)


def correct(frames, original):
    parity, missing, frequency, voltage = {}, {}, [], []
    for bus, df in frames.items():
        initial, window = df.TIMESTAMP < 60, df.TIMESTAMP >= 60
        valid = df.DATA_PRESENT.eq(1)
        missing[bus] = int((window & ~valid).sum())
        frequency.append(excursion(df[f"BUS{bus}_Freq"].where(valid), initial, window))
        mag = df[[f"BUS{bus}_V{p}_MAG" for p in "ABC"]].where(valid, axis=0)
        relative = mag.div(mag[initial].median().replace(0, np.nan))
        voltage.append(excursion(relative.mean(axis=1, skipna=False), initial, window))
        residuals = relative.sub(relative.mean(axis=1, skipna=False), axis=0)
        parity[bus] = max(excursion(residuals[col], initial, window) for col in residuals)
    # Require adequate PMU coverage before issuing an integrity-only correction.
    if min(np.isfinite(frequency).sum(), np.isfinite(voltage).sum()) < 5:
        return original, "fallback"
    coherent = np.nanmedian(frequency) >= 2.5 or np.nanmedian(voltage) >= 2.5
    gaps = [bus for bus, count in missing.items() if count >= 12]
    if len(gaps) == 1 and not coherent and original[0] in (0,5,6):
        return [5, f"PMU{gaps[0]}"], "missing"
    isolated = [b for b, val in parity.items() if np.isfinite(val) and val >= 2.5]
    if not gaps and not coherent and len(isolated) == 1 and original[0] in (0,7):
        return [7, f"PMU{isolated[0]}"], "phase_imbalance"
    return original, "fallback"


def init_model(submitted):
    global model, api
    sys.path.insert(0, str(submitted))
    from src.models import hybrid_submission as api
    model = api.SGSMAFinalModel(submitted / "models")


def infer(folder):
    frames = api._load_frames(folder)
    start, end = api._window_bounds(frames, 30)[-1]
    assert start == 60 and end < 90
    features = api._build_feature_rows(api._slice_frames(frames, start, end, True))
    native = model.predict_from_features(*features).iloc[0]
    original = [int(native.pred_event), str(native.pred_location)]
    successor, reason = correct(frames, original)
    return folder.name, dict(original=original, successor=successor, route=reason)


def score(root):
    from sklearn.metrics import confusion_matrix, f1_score
    raw = (root / "predictions.json").read_bytes()
    assert sha256(raw).hexdigest() == json.loads((root / "seal.json").read_text())
    pred = json.loads(raw)
    truth = json.loads((root / "truth.json").read_text())
    assert pred.keys() == truth.keys()
    ids = sorted(truth)
    labels = [truth[i]["code"] for i in ids]
    assert Counter(labels) == {c: 7 for c in range(9)}
    positive = [i for i in ids if truth[i]["code"]]
    results = {}
    for method in ("original", "successor"):
        codes = [pred[i][method][0] for i in ids]
        results[method] = dict(macro_f1=f1_score(labels,codes,average="macro",labels=range(9)),
            correct=sum(a == b for a,b in zip(labels,codes)),
            exact=sum(pred[i][method][1] == truth[i]["source"] for i in positive),
            joint=sum(pred[i][method] == [truth[i]["code"],truth[i]["source"]] for i in positive),
            events=len(positive), confusion=confusion_matrix(labels,codes,labels=range(9)).tolist())
    results["routes"] = dict(Counter(v["route"] for v in pred.values()))
    save(root / "results.json", results)
    print(json.dumps(results))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("stage", choices=["prepare","predict","score","parity"])
    p.add_argument("root", type=Path)
    p.add_argument("archive", type=Path)
    p.add_argument("submitted", type=Path)
    args = p.parse_args()
    if args.stage == "prepare":
        prepare(args.root,args.archive.resolve(),seed=89324577,repetitions=7,move_integrity=True)
    elif args.stage == "score":
        score(args.root)
    else:
        with ProcessPoolExecutor(max_workers=4,initializer=init_model,
                                 initargs=(args.submitted.resolve(),)) as pool:
            pred = dict(pool.map(infer, sorted((args.root/"observations").iterdir())))
        if args.stage == "parity":
            old = json.loads((args.root/"predictions.json").read_text())
            assert old.keys() == pred.keys() and all(old[i]["original"] == p["original"] for i,p in pred.items())
            print(f"Original ZIP decision parity on {len(pred)} development windows")
        else:
            save(args.root/"predictions.json",pred)
            save(args.root/"seal.json",sha256((args.root/"predictions.json").read_bytes()).hexdigest())

"""Frozen comparison of submitted, spatial and residual rules at held-out sites."""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from pathlib import Path

import numpy as np
from sklearn.metrics import confusion_matrix, f1_score

import competition_spatial_contrast as spatial
from benchmark_competition_windows import save

bank = spatial.previous
native = bank.baseline
METHODS = ("submitted", "spatial", "residual")


def canonical(frames, turns=0):
    normalized = {}
    for bus, original in frames.items():
        d = original.copy()
        cols = [c for c in d if c.endswith("_ANG")]
        angles = d[cols].to_numpy()
        # Quantize below the precision of the input to remove modulo roundoff.
        wrap = lambda a: np.round((a + 180) % 360 - 180, 8)
        d[cols] = wrap(angles + 360 * turns)
        normalized[bus] = d
    return normalized


def residual_pulse(frames):
    """Local equivalent-admittance innovation relative to the other PMUs."""
    innovations = []
    for bus in bank.BUSES:
        d = frames[bus]
        quiet = (d.TIMESTAMP < 60) & d.DATA_PRESENT.eq(1)
        def phasor(q):
            mag = d[[f"BUS{bus}_{q}{p}_MAG" for p in "ABC"]].to_numpy()
            deg = d[[f"BUS{bus}_{q}{p}_ANG" for p in "ABC"]].to_numpy()
            return mag * np.exp(1j * np.deg2rad(deg))
        v, i = phasor("V"), phasor("I")
        # Least-squares complex I = Y V fit, separately for each phase.
        admittance = np.nansum(i[quiet] * v[quiet].conj(), axis=0) / np.nansum(abs(v[quiet])**2, axis=0)
        errors = abs(i - v * admittance) / np.maximum(np.nanmedian(abs(i[quiet]), axis=0), 1e-10)
        level = np.median(errors, axis=1)
        level[d.DATA_PRESENT != 1] = np.nan
        innovations.append(level)
    r = np.stack(innovations, axis=1)
    r -= np.nanmedian(r, axis=1, keepdims=True)
    time = d.TIMESTAMP.to_numpy()
    quiet = time < 60
    threshold = np.maximum(.12, 3 * np.nanquantile(r[quiet], .995, axis=0))
    pulses = []
    for col, bus in enumerate(bank.BUSES):
        idx = np.flatnonzero((~quiet) & (r[:, col] > threshold[col]))
        for run in np.split(idx, np.flatnonzero(np.diff(idx) > 1) + 1):
            if 12 <= len(run) <= 150 and run[-1] + 12 < len(time):
                pulses.append((float(np.mean(r[run, col])), int(run[0]), int(run[-1])+1, bus))
    return max(pulses)[1:] if pulses else None


def pipeline(frames, admission, detector):
    api = native.api
    start, stop = api._window_bounds(frames, 30)[-1]
    assert start == 60 and stop < 90
    feat = api._build_feature_rows(api._slice_frames(frames, start, stop, True))
    row = native.model.predict_from_features(*feat).iloc[0]
    original = [int(row.pred_event), str(row.pred_location)]
    current, _ = native.correct(frames, original)
    family = current[0]
    if admission.startswith("Noise estimate outside support: voltage_angle "):
        x = bank.measurements(frames)
        current, route = bank.classify(x, current, bank.bank, frames)
        family = current[0]
        if family == 6 and route == "response":
            gains = bank.scores(x, np.array(bank.bank["templates"]), range(60,81))
            family = bank.bank["keys"][int(np.argmax(gains))][0]
    pulse = detector(frames)
    if pulse is not None and current[0] in (0,7,8):
        current = [8, spatial.localize(spatial.contrast(spatial.channels(frames), pulse), spatial.models["8"])]
    elif family in (3,4):
        current = [current[0], spatial.localize(spatial.contrast(spatial.channels(frames)), spatial.models[str(family)])]
    return original, current


def infer(folder):
    frames = native.api._load_frames(folder)
    admission = bank.startup[folder.name]
    original, prior = pipeline(frames, admission, spatial.pulse_bounds)
    _, revised = pipeline(canonical(frames), admission, residual_pulse)
    _, shifted = pipeline(canonical(frames, turns=1), admission, residual_pulse)
    return folder.name, dict(submitted=original, spatial=prior, residual=revised,
                             residual_shifted=shifted)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def score(root):
    path = root/"predictions.json"
    assert digest(path) == json.loads((root/"seal.json").read_text())
    pred = json.loads(path.read_text())
    truth, quiet = (json.loads((root/s/"truth.json").read_text()) for s in ("primary","quiet"))
    assert Counter(r["code"] for r in truth.values()) == {i:12 for i in range(9)}
    assert len(quiet) == 48 and all(r["code"]==0 for r in quiet.values())
    assert not truth.keys() & quiet.keys() and pred.keys() == truth.keys() | quiet.keys()
    positives = [k for k,r in truth.items() if r["code"]]
    normals = [*quiet, *(k for k,r in truth.items() if not r["code"])]
    results = {}
    for method in METHODS:
        y = [r["code"] for r in truth.values()]
        called = [pred[k][method][0] for k in truth]
        results[method] = dict(macro_f1=f1_score(y,called,average="macro",labels=range(9),zero_division=0),
            family=sum(a==b for a,b in zip(y,called)), records=len(y),
            exact=sum(pred[k][method][1]==truth[k]["source"] for k in positives),
            joint=sum(pred[k][method]==[truth[k]["code"],truth[k]["source"]] for k in positives),
            events=len(positives), false_alarms=sum(pred[k][method][0]!=0 for k in normals),
            quiet=len(normals), confusion=confusion_matrix(y,called,labels=range(9)).tolist())
    return results


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("stage", choices=["predict","score","verify"])
    p.add_argument("root",type=Path)
    p.add_argument("--submitted",type=Path)
    args = p.parse_args()
    root = args.root
    if args.stage == "predict":
        admissions = {}
        for s in ("primary","quiet"):
            admissions.update(json.loads((root/s/"dynamic_admission.json").read_text()))
        args_init = (args.submitted.resolve(), Path("experiments/competition_response_156/bank.json"),
                     admissions, Path("experiments/competition_spatial_264/spatial.json"))
        with ProcessPoolExecutor(max_workers=6,initializer=spatial.initialize,initargs=args_init) as pool:
            rows = dict(pool.map(infer, sorted(root.glob("*/observations/*"))))
        save(root/"predictions.json",rows)
        save(root/"seal.json",digest(root/"predictions.json"))
    elif args.stage == "score":
        save(root/"results.json",score(root))
    else:
        assert score(root) == json.loads((root/"results.json").read_text())
        print("Verified all metrics and confusion matrices from sealed predictions.")

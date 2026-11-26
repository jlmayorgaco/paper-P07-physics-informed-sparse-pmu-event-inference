"""Evaluate static attributor and learned baselines on the second-plant records (PLAN.md).  python evaluate.py"""
from __future__ import annotations
import hashlib, json, sys, time
from pathlib import Path
import numpy as np
from sklearn.ensemble import ExtraTreesClassifier

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "fair_baselines"))
import baselines as bl                                       # noqa: E402
import importlib
integrity = importlib.import_module("integrity"); attribute_v2 = bl.attribute_v2; sim_io = bl.sim_io
from score_sim import score_record, summarize                # noqa: E402
sys.path.insert(0, str(bl.B01 / "run/engine_clean/reference"))
from noise import NoiseStream, apply_noise                   # noqa: E402

DET = bl.B01 / "run/data/truth_private/deterministic"
NOISE = json.loads((bl.B01 / "run/engine_clean/reference/stochastic_model.json").read_text())
CENT = {f: np.array(v["normalization_center"]) for f, v in NOISE["families"].items()}
FIELDS = ["voltage_magnitude", "voltage_angle", "current_magnitude", "current_angle", "frequency", "rocof"]


def as_record(d, truth):
    raw, ph = bl.features(d)
    return dict(id=truth["id"], t=d["t"], raw=raw, ph=ph, dur=truth["duration_s"], truth=truth)


def second_plant_records():
    out = []
    for p in sorted((HERE / "data").glob("P*.npz")):
        truth = json.loads((HERE / "data" / (p.stem + ".truth.json")).read_text())
        out.append((sim_io.load(p), as_record(sim_io.load(p), truth)))
    return out


def renoised_train(train_recs, k_seeds=4):
    out = []
    for r in train_recs:
        z = np.load(DET / f"{r['id']}.npz"); det = {f: z[f] for f in FIELDS}; n = len(z["time_s"])
        for s in range(k_seeds):
            eps = NoiseStream(NOISE, 770000 + 1000 * int(r["id"][1:]) + s).generate(n)
            nz = apply_noise(det, eps)
            V = nz["voltage_magnitude"] * np.exp(1j * np.deg2rad(nz["voltage_angle"])); I = nz["current_magnitude"] * np.exp(1j * np.deg2rad(nz["current_angle"]))
            d = dict(t=z["time_s"], V=V, I=I, present=np.isfinite(V) & np.isfinite(I))
            raw, ph = bl.features(d); raw, ph = raw.astype(np.float32), ph.astype(np.float32); out.append(dict(id=r["id"], t=d["t"], raw=raw, ph=ph, dur=r["dur"], truth=r["truth"]))
    return out


def train_set(recs, key, ratio=10, seed=0):
    rng = np.random.default_rng(seed); X, Y = [], []
    for r in recs:
        y = bl.labels(r); idx = np.arange(bl.K0, len(y)); pos = idx[y[idx] > 0]; neg = idx[y[idx] == 0]
        neg = rng.choice(neg, size=min(len(neg), ratio * max(len(pos), 1)), replace=False)
        sel = np.r_[pos, neg]; X.append(r[key][sel]); Y.append(y[sel])
    return np.vstack(X), np.concatenate(Y)


def fit_tau_and_score(name, mk, key, tr, cal, targets):
    """same rule as the baselines study: tau for zero normal alarms on CAL, best CAL Top-1"""
    X, Y = train_set(tr, key, ratio=(5 if len(tr) > 30 else 10)); mdl = mk().fit(X, Y)
    def proba(r):
        p = mdl.predict_proba(r[key]); full = np.zeros((len(p), len(bl.CLS)))
        for j, c in enumerate(mdl.classes_): full[:, c] = p[:, j]
        return full
    best = None
    for tau in np.arange(0.05, 0.96, 0.05):
        recs = [score_record(r["truth"]["events"], bl.episodes(r, proba(r), tau, bl.CLS), r["dur"]) for r in cal]
        s = summarize(recs)
        if (s["fa_per_normal_h"] or 0) == 0:
            sc = (s["top1"], s["detected"], -(s["extras_per_event_h"] or 0))
            if best is None or sc > best[0]: best = (sc, float(tau))
    tau = best[1] if best else 0.95
    res = {}
    for label, recs_ in targets.items():
        sc = [score_record(r["truth"]["events"], bl.episodes(r, proba(r), tau, bl.CLS), r["dur"]) for r in recs_]
        res[label] = dict(summary=summarize(sc), per_record=[all(x["detected"] and x["top1"] for x in s["rows"]) for s in sc if s["rows"]],
                          normal_alarms=int(sum(s["extras"] for s in sc if not s["rows"])))
    print(name, "tau", tau, {k: (v["summary"]["detected"], v["summary"]["top1"], v["summary"]["extras_per_event_h"]) for k, v in res.items()}, flush=True)
    return dict(tau=tau, **res)


def main():
    t0 = time.perf_counter()
    tr, cal, te = bl.load_split("TRAIN"), bl.load_split("CAL"), bl.load_split("TEST")
    sp = second_plant_records(); sp_recs = [r for _, r in sp]
    print("loaded", len(sp_recs), "second-plant records", round(time.perf_counter() - t0, 1), flush=True)
    # static attributor
    att = attribute_v2.AttributorV2(catalog=bl.SRC); srecs = []
    for d, r in sp:
        fl = integrity.flags(d, att.net); _, eps = att.run(d, fl, startup_s=bl.K0 / bl.FS)
        srecs.append(score_record(r["truth"]["events"], eps, r["dur"]))
    out = dict(static=dict(summary=summarize(srecs), per_record=[all(x["detected"] and x["top1"] for x in s["rows"]) for s in srecs if s["rows"]],
                           normal_alarms=int(sum(s["extras"] for s in srecs if not s["rows"]))))
    print("static", out["static"]["summary"]["detected"], out["static"]["summary"]["top1"], flush=True)
    rich = renoised_train(tr); print("re-noised training records", len(rich), round(time.perf_counter() - t0, 1), flush=True)
    mk_small = lambda: ExtraTreesClassifier(300, class_weight="balanced_subsample", n_jobs=1, random_state=0)
    mk_rich = lambda: ExtraTreesClassifier(60, min_samples_leaf=3, class_weight="balanced_subsample", n_jobs=1, random_state=0, max_features="sqrt")
    targets = {"f01_test": te, "second_plant": sp_recs}
    out["ML"] = fit_tau_and_score("ML", mk_small, "raw", tr, cal, targets)
    out["FIS"] = fit_tau_and_score("FIS", mk_small, "ph", tr, cal, targets)
    out["ML+"] = fit_tau_and_score("ML+", mk_rich, "raw", tr + rich, cal, targets)
    out["FIS+"] = fit_tau_and_score("FIS+", mk_rich, "ph", tr + rich, cal, targets)
    (HERE / "results.json").write_text(json.dumps(dict(results=out, plan_sha256=hashlib.sha256((HERE / "PLAN.md").read_bytes()).hexdigest(),
                                                       code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()), indent=1, default=float))
    print("wall", round(time.perf_counter() - t0, 1))


if __name__ == "__main__":
    main()

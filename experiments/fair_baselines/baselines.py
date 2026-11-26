"""Learned baselines on the bank's simulated cohort, same scorer (see PLAN.md).  python baselines.py"""
from __future__ import annotations
import hashlib, json, os, sys, time
from pathlib import Path
import numpy as np
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

HERE = Path(__file__).resolve().parent
SCI = HERE.parents[2] / "SGSMA26-Physics-Informed-AD/experiments"
V2 = SCI / "PAPER_ALLEVENTS_V1/frozen_v2"
B01 = SCI / "PAPER_CALIBRATION_B01"
sys.path.insert(0, str(V2)); sys.path.insert(0, str(SCI / "PAPER_ALLEVENTS_V1/eval"))
import attribute, attribute_v2, sim_io                      # noqa: E402
from score_sim import score_record, summarize                # noqa: E402

CFG = attribute.CFG; REF = attribute.REF
FS = 30; K0 = 10 * FS; W1, W2 = 15, 45; B_LO, B_HI = 120, 45
SRC = [a["id"] for a in json.loads((B01 / "run/runtime/model/assets.json").read_text())]
CLS = ["normal", "off"] + SRC
FAMC = {"line": 2, "load": 4}
fam_of = {a["id"]: a["family"] for a in json.loads((B01 / "run/runtime/model/assets.json").read_text())}
ATT = attribute_v2.AttributorV2(catalog=SRC)
SIGS = np.array([s for _, nm, s, _ in ATT.sig]); SIGN = [nm for _, nm, _, _ in ATT.sig]
assert SIGN == [n for n in SIGN] and set(SIGN) == set(SRC)


def zc(d):
    V = d["V"] / CFG["vbase"]; I = d["I"] / CFG["ibase"]
    bad = ~d["present"]
    rot = np.exp(-1j * np.angle(V[:, [REF]]))
    return np.c_[np.where(bad, np.nan, V) * rot, np.where(bad, np.nan, I) * rot]


def wmean(Z, w):
    ok = np.isfinite(Z); X = np.where(ok, Z, 0); c = np.cumsum(np.r_[np.zeros((1, Z.shape[1]), complex), X], 0)
    n = np.cumsum(np.r_[np.zeros((1, Z.shape[1])), ok.astype(float)], 0)
    k = np.arange(len(Z)); lo = np.maximum(k + 1 - w, 0)
    return (c[k + 1] - c[lo]) / np.maximum(n[k + 1] - n[lo], 1)


def features(d):
    """per-report causal features (n, F_raw), (n, F_phys); rows before K0-ish are filled but unused"""
    Z = zc(d); n = len(Z)
    base_m = wmean(Z, B_LO - B_HI + 1)                       # mean over [k-B_LO, k-B_HI]
    k = np.arange(n); bi = k - B_HI
    base = np.where((bi >= B_LO - B_HI)[:, None], base_m[np.clip(bi, 0, n - 1)], np.nan)
    m1, m2 = wmean(Z, W1), wmean(Z, W2)
    d1, d2 = m1 - base, m2 - base
    sd = np.sqrt(np.nanmean(np.abs(d1[B_LO:K0]) ** 2, 0)); sd[~(sd > 0)] = 1.0
    d1, d2 = np.nan_to_num(d1 / sd), np.nan_to_num(d2 / sd)
    raw = np.c_[d1.real, d1.imag, d2.real, d2.imag]
    S = SIGS / sd
    nrm = np.sum(np.abs(S) ** 2, 1)
    ph = []
    for dd in (d1, d2):
        p = np.real(dd @ S.conj().T)                         # (n, 18) Re <s, d>
        ph += [p * np.abs(p) / nrm, p / nrm]                  # signed gain, amplitude
    return raw, np.hstack(ph)


def load_split(split):
    meta = json.loads((B01 / f"run/data/PRIVATE_RECORD_META_{split}.json").read_text())
    truth = {r["id"]: r for r in json.loads((B01 / f"execution_request/truth_private/by_split/{split}.json").read_text())}
    out = []
    for m in meta:
        d = sim_io.load(B01 / "run/data/observed" / f"{m['id']}.npz")
        raw, ph = features(d)
        out.append(dict(id=m["id"], t=d["t"], raw=raw, ph=ph, dur=m["duration_s"], truth=truth[m["id"]]))
    return out


def labels(rec):
    t = rec["t"]; y = np.zeros(len(t), int)
    for e in rec["truth"]["events"]:
        y[(t >= e["onset_s"]) & (t < e["onset_s"] + 1.0)] = CLS.index(e["source"])
        y[(t >= e["off_s"]) & (t < e["off_s"] + 1.0)] = 1
    return y


def train_set(recs, key, seed=0):
    rng = np.random.default_rng(seed); X, Y = [], []
    for r in recs:
        y = labels(r); idx = np.arange(K0, len(y)); pos = idx[y[idx] > 0]; neg = idx[y[idx] == 0]
        neg = rng.choice(neg, size=min(len(neg), 10 * max(len(pos), 1)), replace=False)
        sel = np.r_[pos, neg]; X.append(r[key][sel]); Y.append(y[sel])
    return np.vstack(X), np.concatenate(Y)


def episodes(rec, P, tau, classes):
    t = rec["t"]; pev = 1 - P[:, 0] - P[:, 1]
    eps, k, n = [], K0, len(t)
    while k < n - 2:
        if pev[k] >= tau and pev[k + 1] >= tau and pev[k + 2] >= tau:
            s = k; e = k + 2
            while e + 1 < n and pev[e + 1] >= tau / 2: e += 1
            blk = P[s:min(s + 30, e + 1), 2:].mean(0); order = np.argsort(-blk)
            loc = classes[2 + order[0]]
            eps.append(dict(onset_s=float(t[s]), detect_s=float(t[s + 2]), cls=FAMC[fam_of[loc]], location=loc,
                            top3=[classes[2 + j] for j in order[:3]]))
            k = e + 15
        else:
            k += 1
    return eps


def run_model(name, mk, key, tr, cal, te):
    X, Y = train_set(tr, key); mdl = mk().fit(X, Y); cl = [CLS[c] for c in mdl.classes_]
    def proba(r):
        p = mdl.predict_proba(r[key]); full = np.zeros((len(p), len(CLS)))
        for j, c in enumerate(mdl.classes_): full[:, c] = p[:, j]
        return full
    Pc = {r["id"]: proba(r) for r in cal}
    best = None
    for tau in np.arange(0.05, 0.96, 0.05):
        recs = []
        for r in cal:
            eps = episodes(r, Pc[r["id"]], tau, CLS)
            sc = score_record(r["truth"]["events"], eps, r["dur"]); recs.append(sc)
        s = summarize(recs)
        if (s["fa_per_normal_h"] or 0) == 0:
            score = (s["top1"], s["detected"], -(s["extras_per_event_h"] or 0))
            if best is None or score > best[0]: best = (score, float(tau), s)
    if best is None: best = (None, 0.95, None)
    tau = best[1]
    recs = []; preds = {}
    for r in te:
        eps = episodes(r, proba(r), tau, CLS); preds[r["id"]] = eps
        sc = score_record(r["truth"]["events"], eps, r["dur"]); sc.update(id=r["id"], condition=r["truth"]["condition"]); recs.append(sc)
    summ = summarize(recs)
    for c in ("MATCH", "IN_SUPPORT", "OUT_SUPPORT"):
        summ["by_condition_" + c] = summarize([x for x in recs if x["condition"] == c])
    return dict(name=name, tau=tau, cal=best[2], test=summ, preds=preds)


def main():
    t0 = time.perf_counter()
    smoke = os.environ.get("SMOKE") == "1"          # development: TEST is never read
    tr, cal = load_split("TRAIN"), load_split("CAL"); te = cal if smoke else load_split("TEST")
    print("features", round(time.perf_counter() - t0, 1), "s", flush=True)
    models = [("ML", lambda: ExtraTreesClassifier(300, class_weight="balanced_subsample", n_jobs=1, random_state=0), "raw"),
              ("FIS", lambda: ExtraTreesClassifier(300, class_weight="balanced_subsample", n_jobs=1, random_state=0), "ph"),
              ("LR", lambda: make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, C=1.0)), "ph")]
    only = sys.argv[1:] 
    res = {}
    for nm, mk, key in models:
        if only and nm not in only: continue
        r = run_model(nm, mk, key, tr, cal, te); res[nm] = r
        s = r["test"]; print(nm, "tau", r["tau"], "TEST det", s["detected"], "/", s["events"], "class", s["class_ok"], "top1", s["top1"], "top3", s["top3"],
              "FA/h", s["fa_per_normal_h"], "extras/h", s["extras_per_event_h"], flush=True)
    out = HERE / "results" / (("SMOKE_" if smoke else "") + "BASELINES_" + ("_".join(only) if only else "ALL") + ".json")
    out.write_text(json.dumps(dict(results=res, code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                                   plan_sha256=hashlib.sha256((HERE / "PLAN.md").read_bytes()).hexdigest()), indent=1, default=float))


if __name__ == "__main__":
    main()

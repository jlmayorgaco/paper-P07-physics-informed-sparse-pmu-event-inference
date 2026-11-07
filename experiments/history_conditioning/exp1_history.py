"""Decisive experiment: does conditioning on the previous event's state improve source attribution?

Scenario (fixed schedule): load p ON at 2 s, OFF at 5 s (severity A, unknown to the estimator), a second, weak load c ON at
6.5 s (severity b) while the network is still recovering.  The estimator knows p and the ON/OFF times (the history cause is
retained by the bank), estimates A from the reports before 6.5 s, and ranks the new source c over the other loads.
Noise covariance: empirical covariance of RAW0001 first differences (quiet window), optionally scaled.

Methods (same observations, priors, onset, horizon):
  N   nominal signature   mu = baseline(A_hat) + b * s_c(rest)
  Q   bilinear signature  mu = N + b * A_hat * Q_pc            (Q from offline mixed differences)
  R1  relinearized        mu = baseline(A_hat) + b * s_c(A_hat) (first order in b, history-conditioned)
  F   fixed history       mu = nonlinear plant at A_hat, covariance R
  M   marginalized (Woodbury)  F with covariance R + J P_A J^T, J = d mu / dA at A_hat (rank one)
  QA  quadrature over A   reference marginalization: 7 Gauss-Hermite nodes on A ~ N(A_hat, P_A), nonlinear plant
"""
from __future__ import annotations

import hashlib, json, sys, time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import dynamics as dyn

import os
T_ON, T_OFF = 2.0, 5.0
T_NEW = float(os.environ.get('H_TNEW', 6.5))     # onset of the new source (default: protocol H01)
BGRID = np.array([0.02, 0.03, 0.04, 0.05, 0.06])
B0 = 0.04
DA = 0.01
A_PRIOR = tuple(float(v) for v in os.environ.get('H_APRIOR', '0.08,0.16').split(','))
A_CLIP = float(os.environ.get('H_ACLIP', 0.4))
B_TRUE = (0.02, 0.06)
GH_Z, GH_W = np.polynomial.hermite_e.hermegauss(7)
GH_W = GH_W / GH_W.sum()
LOADS = dyn.CAND_LOADS


def noise_cov() -> np.ndarray:
    z = np.load(HERE / "results/raw_windows.npz"); v = z["quiet"].astype(complex)
    lm = np.log(np.abs(v)); an = np.unwrap(np.angle(v), axis=0)
    d = np.c_[np.diff(lm, axis=0), np.diff(an, axis=0)] / np.sqrt(2)
    return np.cov(d.T)


class Study:
    def __init__(self, W: float, scale: float, th: float = 99.0, mism: float = 0.0) -> None:
        self.pt = dyn.Plant()                                            # truth plant
        self.p = dyn.Plant(1 + mism, 1 + 2 * mism) if mism else self.pt   # estimator plant (mismatched inertia and damping)
        self.W = W; self.n = int(round(W * 30)); self.nh = int(round(min(th, T_NEW) * 30))
        R = noise_cov() * scale ** 2
        self.R = R; self.Lc = np.linalg.cholesky(R)
        Li = np.linalg.inv(self.Lc); self.Wh = Li                       # whitening
        self.x0 = self.p.init_state()
        self._hist: dict = {}
        self._cont: dict = {}
        self.sims = 0
        self.eq_sig = {}
        self.base0 = self.cont(self.x0, ())[0]                          # rest, no event (constant)
        for c in LOADS:
            self.eq_sig[c] = (self.cont(self.x0, ((c, B0),))[0] - self.base0) / B0

    # ---- plant helpers (cached)
    def hist(self, pbus: int, A: float):
        key = (pbus, round(A, 9))
        h = self._hist.get(key)
        if h is None:
            ev = [(T_ON, T_OFF, pbus, A)]
            y, x, _ = self.p.run(self.x0, 0.0, T_NEW, dyn.sched(ev)); self.sims += 1
            h = (y, x); self._hist[key] = h
        return h

    def cont(self, x, cfg, key=None):
        k = None if key is None else (key, cfg)
        if k is not None and k in self._cont:
            return self._cont[k]
        y, xf, _ = self.p.run(x, T_NEW, T_NEW + self.W, lambda t: cfg); self.sims += 1
        out = (y, xf)
        if k is not None: self._cont[k] = out
        return out

    # ---- history estimation (Gauss-Newton on the scalar severity)
    def estimate_A(self, pbus: int, y_hist: np.ndarray):
        A = 0.5 * sum(A_PRIOR)
        for _ in range(3):
            m = self.hist(pbus, A)[0]; mj = self.hist(pbus, A + DA)[0]
            J = ((mj - m) / DA)
            r = (y_hist[-self.nh:] - m[-self.nh:]) @ self.Wh.T; Jw = J[-self.nh:] @ self.Wh.T
            den = float((Jw * Jw).sum()); A = float(np.clip(A + (Jw * r).sum() / den, 0.02, A_CLIP))
        m = self.hist(pbus, A)[0]; mj = self.hist(pbus, A + DA)[0]
        Jw = ((mj - m) / DA)[-self.nh:] @ self.Wh.T
        return A, 1.0 / float((Jw * Jw).sum())

    # ---- Gaussian log-likelihood helpers (whitened)
    def ll_white(self, y, mu):
        r = (y - mu) @ self.Wh.T
        return -0.5 * float((r * r).sum()), r

    def ll_rank1(self, y, mu, J, P):
        r = (y - mu) @ self.Wh.T; j = J @ self.Wh.T
        jj = float((j * j).sum()); rj = float((r * j).sum())
        quad = float((r * r).sum()) - P * rj * rj / (1 + P * jj)
        return -0.5 * quad - 0.5 * np.log1p(P * jj)

    # ---- one scenario
    def run_one(self, rng: np.random.Generator, tables) -> dict:
        pbus = int(rng.choice(LOADS)); cands = [c for c in LOADS if c != pbus]
        c_true = int(rng.choice(cands)); A_true = float(rng.uniform(*A_PRIOR)); b_true = float(rng.uniform(*B_TRUE))
        ev = [(T_ON, T_OFF, pbus, A_true), (T_NEW, T_NEW + self.W + 1, c_true, b_true)]
        y_all, _, _ = self.pt.run(self.x0, 0.0, T_NEW + self.W, dyn.sched(ev))
        y_all = y_all + (rng.standard_normal(y_all.shape) @ self.Lc.T)
        yh, yn = y_all[: int(round(T_NEW * 30))], y_all[int(round(T_NEW * 30)):]
        A_hat, P_A = self.estimate_A(pbus, yh)
        xh = self.hist(pbus, A_hat)[1]
        base = self.cont(xh, ())[0]
        out = dict(p=pbus, c=c_true, A=A_true, b=b_true, A_hat=A_hat, P_A=P_A, cands=cands)
        L = {k: {} for k in ("N", "Q", "R1", "F", "M", "QA")}
        cost = {k: 0.0 for k in L}
        mu_cache: dict = {}
        s_hat_c: dict = {}
        for c in cands:
            lN, lQ, lR, lF, lM, lQA = [], [], [], [], [], []
            t0 = time.perf_counter()
            # N
            for b in BGRID:
                lN.append(self.ll_white(yn, base + b * self.eq_sig[c])[0])
            cost["N"] += time.perf_counter() - t0
            t0 = time.perf_counter()
            Q = tables[(pbus, c)]
            for b in BGRID:
                lQ.append(self.ll_white(yn, base + b * self.eq_sig[c] + b * A_hat * Q)[0])
            cost["Q"] += time.perf_counter() - t0
            t0 = time.perf_counter()
            s_hat = (self.cont(xh, ((c, B0),))[0] - base) / B0
            s_hat_c[c] = s_hat
            for b in BGRID:
                lR.append(self.ll_white(yn, base + b * s_hat)[0])
            cost["R1"] += time.perf_counter() - t0
            t0 = time.perf_counter()
            mus = {}
            for b in BGRID:
                mus[b] = self.cont(xh, ((c, float(b)),))[0]
                lF.append(self.ll_white(yn, mus[b])[0])
            cost["F"] += time.perf_counter() - t0
            mu_cache[c] = mus
            t0 = time.perf_counter()
            xo = self.hist(pbus, A_hat + DA)[1]
            for b in BGRID:
                J = (self.cont(xo, ((c, float(b)),))[0] - mus[b]) / DA
                lM.append(self.ll_rank1(yn, mus[b], J, P_A))
            cost["M"] += time.perf_counter() - t0 + (time.perf_counter() - t0) * 0   # + F sims reused
            t0 = time.perf_counter()
            for b in BGRID:
                parts = []
                for z, w in zip(GH_Z, GH_W):
                    xa = self.hist(pbus, A_hat + np.sqrt(P_A) * z)[1]
                    parts.append(np.log(w) + self.ll_white(yn, self.cont(xa, ((c, float(b)),))[0])[0])
                m = max(parts); lQA.append(m + np.log(np.sum(np.exp(np.array(parts) - m))))
            cost["QA"] += time.perf_counter() - t0
            for k, v in (("N", lN), ("Q", lQ), ("R1", lR), ("F", lF), ("M", lM), ("QA", lQA)):
                a = np.array(v); m = a.max()
                L[k][c] = float(m + np.log(np.mean(np.exp(a - m))))
        res = {}
        for k in L:
            lv = np.array([L[k][c] for c in cands]); post = np.exp(lv - lv.max()); post /= post.sum()
            res[k] = dict(top=int(cands[int(np.argmax(lv))]), nll=float(-np.log(max(post[cands.index(c_true)], 1e-300))),
                          p_true=float(post[cands.index(c_true)]), margin=float(np.sort(lv)[-1] - np.sort(lv)[-2]))
        # computable certificate of the approximate methods relative to the plug-in nonlinear plant F
        cert = {}
        for k in ("N", "Q", "R1"):
            rho = {}
            for c in cands:
                worst = 0.0
                for bi, b in enumerate(BGRID):
                    mu_k = {"N": base + b * self.eq_sig[c], "Q": base + b * self.eq_sig[c] + b * A_hat * tables[(pbus, c)],
                            "R1": base + b * s_hat_c[c]}[k]
                    d = ((mu_cache[c][b] - mu_k) @ self.Wh.T); dn = float(np.sqrt((d * d).sum()))
                    e = ((yn - mu_cache[c][b]) @ self.Wh.T); en = float(np.sqrt((e * e).sum()))
                    worst = max(worst, dn * en + 0.5 * dn * dn)
                rho[c] = worst
            lv = np.array([L[k][c] for c in cands]); order = np.argsort(lv)[::-1]
            w, r2 = cands[int(order[0])], cands[int(order[1])]
            cert[k] = dict(bound=float(rho[w] + rho[r2]), margin=res[k]["margin"],
                           certified=bool(res[k]["margin"] > rho[w] + rho[r2]))
        out.update(res=res, cert=cert, cost=cost)
        return out


def offline_tables(st: Study) -> dict:
    """Mixed differences Q_pc at the reference A1 (one set per history load and candidate)."""
    A1 = 0.12; tab = {}
    for pb in LOADS:
        xA = st.hist(pb, A1)[1]; baseA = st.cont(xA, ())[0]
        for c in LOADS:
            if c == pb: continue
            muAb = st.cont(xA, ((c, B0),))[0]
            Q = ((muAb - baseA) - (st.eq_sig[c] * B0)) / (A1 * B0)
            tab[(pb, c)] = Q
    return tab


def main(seeds: list[int], W: float, scale: float, th: float, mism: float, tag: str) -> None:
    out = HERE / "results" / tag; out.mkdir(parents=True, exist_ok=False)
    st = Study(W, scale, th, mism)
    t0 = time.perf_counter(); tab = offline_tables(st); off_s = time.perf_counter() - t0
    rows = []
    for s in seeds:
        rng = np.random.default_rng(s); t1 = time.perf_counter()
        r = st.run_one(rng, tab); r["seed"] = s; r["wall"] = time.perf_counter() - t1; rows.append(r)
        if len(rows) % 10 == 0: print(tag, len(rows), "/", len(seeds), flush=True)
    meta = dict(W=W, scale=scale, th=th, mism=mism, tag=tag, seeds=[seeds[0], seeds[-1], len(seeds)], offline_s=off_s, sims=st.sims,
                code_sha=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (out / "ROWS.json").write_text(json.dumps(dict(meta=meta, rows=rows), default=float))
    print("done", tag, meta)


if __name__ == "__main__":
    a = sys.argv
    main(list(range(int(a[1]), int(a[2]))), float(a[3]), float(a[4]), float(a[5]), float(a[6]), a[7])

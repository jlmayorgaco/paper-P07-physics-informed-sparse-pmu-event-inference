"""RAW0001 validation of the reduced plant (read-only; nothing is fitted to RAW0001 except one load severity).

The label-free onset of the sustained load change comes from the attributor's own episode list.  Observed deviations
(log-magnitude, angle relative to PMU 39) in the quasi-steady window are compared with the plant response of every
load bus, with a free non-negative amplitude per candidate (profile likelihood).
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import dynamics as dyn

ONSET = 3877.766                                   # attributor episode onset (label-free)
T0W, T1W = 10.0, 60.0                              # quasi-steady window after onset [s]
B0 = 0.10


def feats(v: np.ndarray) -> np.ndarray:
    lm = np.log(np.abs(v)); an = np.unwrap(np.angle(v), axis=0)
    return np.c_[lm, (an[:, :7] - an[:, 7:8])]


def main() -> None:
    z = np.load(HERE / "results/raw_windows.npz")
    q = feats(z["quiet"].astype(complex)); dq = np.diff(q, axis=0) / np.sqrt(2)
    R = np.cov(dq.T)
    t = z["t_load"]; v = z["load"].astype(complex)
    f = feats(v)
    pre = f[(t >= 3800) & (t < ONSET - 5)].mean(0)
    w = (t >= ONSET + T0W) & (t < ONSET + T1W)
    blocks = f[w][: (w.sum() // 30) * 30].reshape(-1, 30, 15).mean(1) - pre           # 1-s block means
    nb = len(blocks); Rb = R / 30
    L = np.linalg.cholesky(Rb); Li = np.linalg.inv(L)

    pl = dyn.Plant(); x0 = pl.init_state()
    base, _, _ = pl.run(x0, 0.0, T1W + 1, lambda t: ())
    loads = [b for b in sorted(pl.base_load) if b not in dyn.GEN and pl.base_load[b].real > 0.5]
    # plant features: same columns
    def plant_feats(y):
        return np.c_[y[:, :8], (y[:, 8:15] - y[:, 15:16])]
    res = {}
    for c in loads:
        y, _, _ = pl.run(x0, 0.0, T1W + 1, dyn.sched([(1.0, 1e9, c, B0)]))
        d = plant_feats(y) - plant_feats(base)
        sel = d[int(round((1.0 + T0W) * 30)): int(round((1.0 + T1W) * 30))]
        pb = sel[: (len(sel) // 30) * 30].reshape(-1, 30, 15).mean(1)[:nb]
        r0 = blocks @ Li.T; s = pb @ Li.T
        a = max(float((r0 * s).sum() / (s * s).sum()), 0.0)
        chi = float(((r0 - a * s) ** 2).sum())
        res[c] = dict(a=a, severity=a * B0, chi2=chi, chi2_zero=float((r0 ** 2).sum()))
    order = sorted(res, key=lambda c: res[c]["chi2"])
    bank = [3, 4, 7, 15, 16, 20, 24, 26]
    ob = sorted([c for c in bank], key=lambda c: res[c]["chi2"]) if all(c in res for c in bank) else None
    out = dict(onset_s=ONSET, n_blocks=nb, window_s=[T0W, T1W], loads=len(loads),
               rank_all=order[:6], chi2_all={str(c): round(res[c]["chi2"], 1) for c in order[:6]},
               chi2_null=round(res[order[0]]["chi2_zero"], 1), severity_fit={str(c): round(res[c]["severity"], 4) for c in order[:3]},
               rank_bank=ob[:4] if ob else None, bus7_rank_all=order.index(7) + 1, bus7_rank_bank=(ob.index(7) + 1) if ob else None,
               delta_chi2_bus7_vs_next=round(res[order[1]]["chi2"] - res[order[0]]["chi2"], 1) if order[0] == 7 else None)
    (HERE / "results/RAW0001_VALIDATION.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()

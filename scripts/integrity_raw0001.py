"""Physics-based measurement-integrity monitor evaluated on the competition record RAW0001.

Integrity mechanisms of the SGSMA 2026 guide are examined without training,
using three checks with distinct scopes:

1. Availability: the received-frame flag and finite values identify a missing
   PMU exactly (labels 5 and 6).
2. Sequence parity: ideal balanced phasors have no negative- or zero-sequence
   voltage or current.  The check is sensitive to per-phase corruption, but
   the ideal relation does not include report-window transients or estimator
   imbalance.  Its threshold is a nominal single-statistic tail point; the
   implemented report statistic takes the maximum of voltage and current.
3. Network coupling: only the modeled single-bolted-fault set implies the
   ratio c_p computed from the network impedance matrix
   (scripts/integrity_coupling.py).  A change above 10 % at p with less than
   c_p/4 of it elsewhere is flagged as inconsistent with that set, not with
   all possible physical events.

While the network shows a coupling-consistent disturbance (a modeled fault),
sequence parity is suspended, because phasor estimation during fast transients
is not a balanced steady-state quantity.  Labels are used only for evaluation.
The prespecified threshold assumes Gaussian per-phase noise and known scale;
the implementation estimates scale from a startup prefix.  A second, post hoc
operating point doubles the threshold after inspection of the heavier tails.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT.parent / "SGSMA26-Physics-Informed-AD/data/RAW0001"
OUT = ROOT / "generated/revision_20261104"
PMUS = [2, 5, 6, 10, 19, 22, 29, 39]
PREFIX = 90
PFA = 1e-9          # nominal marginal tail probability for one statistic
A = np.exp(2j * np.pi / 3)
BIG = 0.10          # balanced excursion considered (fraction of nominal)
MARGIN = 0.25       # fraction of the network coupling bound
REF = 30            # causal reference window (reports) for balanced changes


def phasors(df: pd.DataFrame, b: int, q: str) -> np.ndarray:
    cols = [(f"BUS{b}_{q}{ph}_MAG", f"BUS{b}_{q}{ph}_ANG") for ph in "ABC"]
    return np.stack([df[m].to_numpy() * np.exp(1j * np.deg2rad(df[a].to_numpy())) for m, a in cols], axis=1)


def sequences(x: np.ndarray):
    a, b, c = x[:, 0], x[:, 1], x[:, 2]
    return (a + b + c) / 3, (a + A * b + A * A * c) / 3, (a + A * A * b + A * c) / 3


def gamma2_threshold(pfa: float) -> float:
    xs = np.linspace(1, 80, 800001)
    return float(xs[np.argmin(np.abs(np.log1p(xs) - xs - np.log(pfa)))])


def episodes(mask: np.ndarray, gap: int = 1):
    idx = np.flatnonzero(mask)
    if not len(idx):
        return []
    out, s, p = [], idx[0], idx[0]
    for i in idx[1:]:
        if i - p > gap + 1:
            out.append((s, p)); s = i
        p = i
    out.append((s, p))
    return out


def main(inflation: float = 1.0, tag: str = "") -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    coupling = json.loads((OUT / "integrity_coupling.json").read_text())["per_pmu"]
    frames = {b: pd.read_csv(RAW / f"Bus{b}_Competition_Data_nanmask.csv") for b in PMUS}
    t = frames[PMUS[0]].TIMESTAMP.to_numpy()
    n, m = len(t), len(PMUS)
    stat = np.full((n, m), np.nan); phase = np.full((n, m), -1); v1n = np.full((n, m), np.nan)
    missing = np.zeros((n, m), bool); label = np.zeros((n, m), int)
    for j, b in enumerate(PMUS):
        df = frames[b]
        label[:, j] = df.Event.to_numpy()
        missing[:, j] = (df.DATA_PRESENT.to_numpy() == 0) | ~np.isfinite(df[f"BUS{b}_VA_MAG"].to_numpy())
        s = []
        for q in ("V", "I"):
            x = phasors(df, b, q)
            x0, x1, x2 = sequences(x)
            e = np.abs(x2) ** 2 + np.abs(x0) ** 2
            s.append(2 * e / np.nanmean(e[:PREFIX]))          # ~Gamma(2,1)
            if q == "V":
                v1n[:, j] = np.abs(x1) / np.nanmedian(np.abs(x1[:PREFIX]))
                ap = np.abs(np.real(np.conj(x) * x0[:, None]) / np.abs(x))
                ok = np.isfinite(ap).all(axis=1)
                phase[ok, j] = np.argmax(ap[ok], axis=1)
        stat[:, j] = np.fmax(s[0], s[1])
    tau = inflation * gamma2_threshold(PFA)
    # causal balanced change relative to the median of the previous REF reports
    ref = pd.DataFrame(v1n).rolling(REF, min_periods=10).median().shift(1).to_numpy()
    dv = np.abs(v1n - ref)
    c = np.array([coupling[str(b)]["coupling"] for b in PMUS])
    others_max = np.array([np.nanmax(np.delete(dv, j, axis=1), axis=1) for j in range(m)]).T
    big = dv > BIG
    coupling_flag = big & (others_max < MARGIN * c[None, :] * dv)
    physical_disturbance = (big & ~coupling_flag).any(axis=1)          # coupling-consistent sag somewhere
    dist = pd.Series(physical_disturbance).rolling(2 * REF, min_periods=1).max().to_numpy().astype(bool)
    parity_flag = (stat > tau) & ~dist[:, None]
    corrupt = (parity_flag | coupling_flag) & ~missing
    corrupt[:PREFIX] = False                                           # monitoring starts after the prefix
    mechanism = np.where(coupling_flag, "network coupling", "sequence parity")

    truth_corrupt = label == 7
    truth_missing = np.isin(label, [5, 6])
    physical_onsets = [float(t[k]) for k in np.flatnonzero(np.diff(np.isin(label[:, 0], [1, 2, 3, 4]).astype(int)) == 1) + 1]

    rows = []
    for j, b in enumerate(PMUS):
        for s, e in episodes(corrupt[:, j]):
            sl = slice(s, e + 1)
            lab = truth_corrupt[sl, j].any()
            near = [o for o in physical_onsets if 0 <= t[s] - o < 1.0]
            ph = phase[sl, j][phase[sl, j] >= 0]
            rows.append(dict(pmu=b, start_s=float(t[s]), end_s=float(t[e]), reports=int(e - s + 1),
                             mechanism=str(mechanism[s, j]), labeled_corruption=bool(lab),
                             after_physical_onset_s=None if not near else float(t[s] - near[0]),
                             phase="ABC"[int(np.bincount(ph).argmax())] if len(ph) else None,
                             max_statistic=float(np.nanmax(stat[sl, j])), max_balanced_change=float(np.nanmax(dv[sl, j]))))
    det = pd.DataFrame(rows)
    # labeled episodes: detection delay, location, phase
    lab_rows = []
    for j, b in enumerate(PMUS):
        for kind, true, pred in [("corrupted", truth_corrupt, corrupt), ("missing", truth_missing, missing)]:
            for s, e in episodes(true[:, j], gap=0):
                hit = pred[s:e + 1].any(axis=1)
                first = s + int(np.argmax(hit)) if hit.any() else None
                row = dict(kind=kind, pmu=b, start_s=float(t[s]), duration_s=float(t[e] - t[s] + 1 / 30),
                           detected=first is not None, delay_reports=None if first is None else int(first - s),
                           located=[PMUS[k] for k in np.flatnonzero(pred[first])] if first is not None else [],
                           reports_flagged=int(pred[s:e + 1, j].sum()), reports=int(e - s + 1))
                if kind == "corrupted":
                    cols = {k: frames[b][f"BUS{b}_V{k}_MAG"].to_numpy() for k in "ABC"}
                    pre = {k: np.nanmedian(v[max(0, s - 30):s]) for k, v in cols.items()}
                    dev = {k: np.nanmedian(cols[k][s:e + 1]) / pre[k] - 1 for k in "ABC"}
                    tp = max(dev, key=lambda k: abs(dev[k]))
                    ph = phase[s:e + 1, j][phase[s:e + 1, j] >= 0]
                    row.update(true_phase=tp, relative_step=float(dev[tp]),
                               identified_phase="ABC"[int(np.bincount(ph).argmax())] if len(ph) else None)
                lab_rows.append(row)
    lab = pd.DataFrame(lab_rows)
    unl = det[~det.labeled_corruption & det.after_physical_onset_s.isna()]
    trans = det[~det.labeled_corruption & det.after_physical_onset_s.notna()]
    mon_min = float((n - PREFIX) / 30 / 60)
    normal_min = float((((label == 0).all(axis=1))[PREFIX:]).sum() / 30 / 60)
    res = dict(variance_inflation=inflation, threshold_gamma2=tau, per_report_false_alarm_probability=PFA, monitored_minutes=mon_min,
               normal_minutes=normal_min,
               labeled=lab.to_dict("records"),
               detections=det.to_dict("records"),
               n_labeled_corruption=int((lab.kind == "corrupted").sum()),
               n_labeled_corruption_detected=int(((lab.kind == "corrupted") & lab.detected).sum()),
               n_labeled_missing=int((lab.kind == "missing").sum()),
               n_labeled_missing_detected=int(((lab.kind == "missing") & lab.detected).sum()),
               missing_reports=int(truth_missing.sum()), missing_reports_flagged=int((missing & truth_missing).sum()),
               missing_false_reports=int((missing & ~truth_missing).sum()),
               n_unlabeled_detections=int(len(unl)), n_switching_transients=int(len(trans)),
               switching_false_alarms_per_min=float(len(trans) / mon_min))
    (OUT / f"integrity_raw0001{tag}.json").write_text(json.dumps(res, indent=2, default=float))
    # compact series around the labeled and unlabeled episodes for the figure
    keep = np.zeros(n, bool)
    for a, b_ in [(2.5, 13.0), (333.5, 338.5), (1172.5, 1179.0), (2776.0, 2779.5), (5378.0, 5380.0)]:
        keep |= (t >= a) & (t < b_)
    ser = pd.DataFrame({"time_s": t[keep]})
    for j, b in enumerate(PMUS):
        ser[f"stat_{b}"] = stat[keep, j]; ser[f"dv_{b}"] = dv[keep, j]
        ser[f"flag_{b}"] = corrupt[keep, j]; ser[f"label_{b}"] = label[keep, j]
    ser["tau"] = tau
    ser.to_csv(OUT / f"integrity_raw0001{tag}_series.csv", index=False)
    print(lab.to_string()); print(det.to_string())
    print({k: v for k, v in res.items() if k not in ("labeled", "detections")})


if __name__ == "__main__":
    main()                                  # nominal single-statistic tail, Gaussian per-phase noise
    main(2.0, "_inflated")                  # post hoc: variance inflation 2 for heavier-than-Gaussian tails

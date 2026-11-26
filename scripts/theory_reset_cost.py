"""Predicted cost of forgetting the physical state at inferred closure (A01 reset arm).

For every A01 continuous intervention (C01 MATCH parents, noise 1) the noise-free
truth is propagated with the frozen operators through ON, the active interval,
OFF and the post-restoration gap.  At the inferred closure time (carry-arm
restoration emission) two filters continue on the same truth:

  carry: conditional mean equals the true augmented state  -> innovation 0;
  reset: the first 114 physical-state coordinates are set to zero, all
         instrument/discrepancy coordinates retained (exactly the A01 reset).

The reset filter's innovation is the deterministic free recovery response
C0 Phi0 dx(kappa) seen through the filter.  A spurious alarm requires a
birth hypothesis j to explain that bias better than the null history:

  G_j(k) = Lambda_null(k) - Lambda_j(k),  births at closure, b profiled.

Predicted extra alarm:  max_{j,k} G_j(k) + log prior_cell >= log(0.99/0.01).
Prediction is compared event by event with the A01 reset-arm extras.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from theory_isolability import Bank, op_index, profiled_energy, SCI, ASSETS, PROTOCOL, CASES, OUT

A01 = SCI / "PAPER_ABLATION_A01/run/results"
POST_REGIME = 3   # recovery regime used while recovering after closure


def main() -> None:
    cfg = json.loads(PROTOCOL.read_text())
    assets = json.loads(ASSETS.read_text())
    names = [a["id"] for a in assets]
    fam = [a["family"] for a in assets]
    idx = {n: k for k, n in enumerate(names)}
    bank = Bank(Path(str(SCI / "PAPER_CALIBRATION_B01/run/particles/C025/nominal/bank.npz")))
    d = np.load(SCI / "PAPER_CALIBRATION_B01/run/particles/C025/nominal/bank.npz")
    bank.K, bank.Sinv = d["K"][POST_REGIME], d["Sinv"][POST_REGIME]
    birth = 1 - np.exp(-cfg["birth_hazard_per_s"] / 30)
    log_prior_cell = np.log(birth / len(assets))
    log_threshold = np.log(cfg["alarm_probability"] / (1 - cfg["alarm_probability"]))

    cases = {c["parent_schedule"]: c for c in json.loads(CASES.read_text()) if c["condition"] == "MATCH"}
    ev = pd.read_csv(A01 / "EVENTS.csv")
    ex = pd.read_csv(A01 / "EXTRAS.csv")
    carry = ev[(ev.method == "BAYES_MEMORY") & (ev.lane == "continuous")]
    reset = ev[(ev.method == "BAYES_NO_CARRY") & (ev.lane == "continuous")].set_index("event")
    rx = ex[(ex.method == "BAYES_NO_CARRY") & (ex.lane == "continuous")]

    rows = []
    for parent, g in carry.groupby("parent"):
        events = cases[parent]["events"]
        for n_e, e in enumerate(events):
            row = carry[carry.event == e["id"]].iloc[0]
            c = idx[e["source"]]
            amp = e["amplitude"] if e["amplitude"] is not None else 0.0
            closure = e["off_s"] + (row.off_delay_s if row.off_delay_s == row.off_delay_s else 0.5)
            nxt = events[n_e + 1]["onset_s"] if n_e + 1 < len(events) else e["off_s"] + 8.0
            k_on, k_off = round(e["onset_s"] * 30), round(e["off_s"] * 30)
            k_cl, k_end = round(closure * 30), round(nxt * 30)
            if k_end <= k_cl + 2:
                continue
            # truth path from onset to the next onset
            path = [op_index(c, "on0")] + [op_index(c, "stay")] * (k_off - k_on - 1) + [op_index(c, "off0")] + \
                   [0] * (k_end - k_off - 1)
            x = np.zeros(bank.n)
            zs, xs = [], []
            for o in path:
                gr = bank.group[o]
                zs.append(bank.J[gr] @ x + bank.j[o] + bank.v[o] * amp)
                xs.append(x.copy())
                x = bank.T[gr] @ x + bank.g[o] + bank.u[o] * amp
            j0 = k_cl - k_on                                   # first report scored after closure
            z = np.array(zs[j0:])
            m_reset = xs[j0].copy()
            m_reset[:114] = 0.0                               # A01 reset: physical deviations only
            # null history from the reset state (normal mode throughout)

            def run(cell, m0):
                m = m0.copy()
                dd = np.zeros(bank.n)
                EE = ES = SS = 0.0
                out = []
                for k in range(len(z)):
                    o = 0 if cell is None else (op_index(cell, "on0") if k == 0 else op_index(cell, "stay"))
                    gr = bank.group[o]
                    Si = bank.Sinv[gr]
                    ee = z[k] - bank.J[gr] @ m - bank.j[o]
                    s = bank.J[gr] @ dd + bank.v[o]
                    EE += ee @ Si @ ee
                    ES += s @ Si @ ee
                    SS += s @ Si @ s
                    out.append((EE, ES, SS))
                    K = bank.K[gr]
                    m = bank.T[gr] @ m + bank.g[o] + K @ ee
                    dd = bank.T[gr] @ dd + bank.u[o] - K @ s
                return np.array(out)

            null = run(None, m_reset)
            lam_null = 0.5 * null[:, 0]
            gains = []
            for j in range(len(assets)):
                t = run(j, m_reset)
                lam_j = profiled_energy(t[:, 0], t[:, 1], t[:, 2], fam[j] == "load")
                gains.append(lam_null - lam_j)
            gains = np.array(gains)
            best = gains.max(axis=0)
            jbest = int(np.argmax(gains.max(axis=1)))
            observed = rx[(rx.parent == parent) & (rx.alarm_s > e["off_s"]) & (rx.alarm_s < nxt)]
            r_reset = reset.loc[e["id"]] if e["id"] in reset.index else None
            nextid = events[n_e + 1]["id"] if n_e + 1 < len(events) else None
            rows.append(dict(event=e["id"], parent=parent, source=e["source"], family=e["family"],
                             amplitude=e["amplitude"], duration_s=e["off_s"] - e["onset_s"],
                             gap_after_closure_s=(k_end - k_cl) / 30,
                             lambda_reset_null=float(lam_null[-1]),
                             max_spurious_gain=float(best.max()),
                             predicted_extra=bool(best.max() + log_prior_cell >= log_threshold),
                             predicted_spurious_source=names[jbest],
                             observed_extras_after=int(len(observed)),
                             observed_extra_sources=";".join(observed.source.astype(str)),
                             next_event=nextid,
                             next_event_timely_reset=bool(reset.loc[nextid].timely) if nextid in reset.index else None))
            print(e["id"], e["source"], "Lambda_reset=%.3g gain=%.3g pred=%s obs=%d" % (
                lam_null[-1], best.max(), rows[-1]["predicted_extra"], len(observed)), flush=True)
    res = pd.DataFrame(rows)
    res.to_csv(OUT / "reset_cost_prediction.csv", index=False)
    tab = pd.crosstab(res.predicted_extra, res.observed_extras_after > 0)
    print(tab)
    from sklearn.metrics import roc_auc_score
    y = (res.observed_extras_after > 0).astype(int)
    auc = float(roc_auc_score(y, res.max_spurious_gain)) if 0 < y.sum() < len(y) else None
    summary = dict(events=len(res), predicted_extra=int(res.predicted_extra.sum()),
                   observed_events_with_extra=int(y.sum()), observed_extras_total=int(res.observed_extras_after.sum()),
                   agreement=float((res.predicted_extra == (y > 0)).mean()), auc_gain_vs_observed=auc,
                   post_closure_regime=POST_REGIME, log_threshold=float(log_threshold),
                   log_prior_cell=float(log_prior_cell))
    (OUT / "reset_cost_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

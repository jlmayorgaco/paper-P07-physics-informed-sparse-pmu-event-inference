"""Physics-derived detectability/isolability from the frozen switched-DAE operators.

For each catalog source i, a noise-free trajectory is generated with the SAME
discrete operators used by inference (onset at report 0, half-phase 0).  Every
candidate conditional filter j (null, 9 loads, 9 lines) is run on it.  Because
all hypotheses are linear-Gaussian given the mode path, the expected
log-likelihood ratio of the true hypothesis against j after k reports is the
whitened innovation energy (Willsky--Jones signatures):

    Lambda_ij(k) = 1/2 * min_b sum_{r<=k} || e_j(r) - s_j(r) b ||^2_{S_j^{-1}},

with b profiled for load candidates (no b for lines) and e_i == 0 for the truth.
Lambda_i0 (null) is the detection information, min_{j!=i} Lambda_ij the
isolation information.  Detection uses the exact Gaussian marginal over the
load amplitude prior (sd 0.15) so that the Occam factor is included.

Read-only inputs: one nominal bank built by the C01-identical runtime (B01 CAL
record), the C01 truth and C01 evaluated events.  Nothing is written outside
generated/revision_20261104/.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCI = ROOT.parent / "SGSMA26-Physics-Informed-AD" / "experiments"
BANK = SCI / "PAPER_CALIBRATION_B01/run/particles/C025/nominal/bank.npz"
PROTOCOL = SCI / "PAPER_CONFIRMATORY_C01/run/runtime/PROTOCOL.json"
ASSETS = SCI / "PAPER_CONFIRMATORY_C01/run/runtime/model/assets.json"
CASES = SCI / "PAPER_CONFIRMATORY_C01/run/data/truth_private/cases.json"
EVENTS = SCI / "PAPER_CONFIRMATORY_C01/run/results/EVENTS.csv"
OUT = ROOT / "generated/revision_20261104"

HORIZON = 90  # reports (3 s); event durations are 2-5 s
REGIME = 0    # quiet regime: the regime in force before an alarm


def op_index(cell: int, kind: str) -> int:
    return 1 + 5 * cell + {"stay": 0, "on0": 1, "off0": 2, "on1": 3, "off1": 4}[kind]


class Bank:
    def __init__(self, path: Path):
        d = np.load(path)
        self.T, self.J, self.K = d["T"], d["J"], d["K"][REGIME]
        self.Sinv, self.g, self.u, self.j, self.v = d["Sinv"][REGIME], d["g"], d["u"], d["j"], d["v"]
        self.group = d["group"]
        self.n = self.T.shape[1]

    def path(self, cell: int | None, horizon: int) -> list[int]:
        if cell is None:
            return [0] * horizon
        return [op_index(cell, "on0")] + [op_index(cell, "stay")] * (horizon - 1)

    def simulate(self, cell: int, amplitude: float, horizon: int) -> np.ndarray:
        """Noise-free reports z_k for hypothesis (cell, amplitude), zero pre-event deviation."""
        x = np.zeros(self.n)
        z = np.empty((horizon, self.J.shape[1]))
        for k, o in enumerate(self.path(cell, horizon)):
            gr = self.group[o]
            z[k] = self.J[gr] @ x + self.j[o] + self.v[o] * amplitude
            x = self.T[gr] @ x + self.g[o] + self.u[o] * amplitude
        return z

    def filter_terms(self, cell: int | None, z: np.ndarray):
        """Per-report whitened sufficient statistics of candidate filter on z."""
        m = np.zeros(self.n)
        d = np.zeros(self.n)
        EE, ES, SS = [], [], []
        for k, o in enumerate(self.path(cell, len(z))):
            gr = self.group[o]
            Si = self.Sinv[gr]
            e = z[k] - self.J[gr] @ m - self.j[o]
            s = self.J[gr] @ d + self.v[o]
            EE.append(e @ Si @ e)
            ES.append(s @ Si @ e)
            SS.append(s @ Si @ s)
            K = self.K[gr]
            m = self.T[gr] @ m + self.g[o] + K @ e
            d = self.T[gr] @ d + self.u[o] - K @ s
        return np.cumsum(EE), np.cumsum(ES), np.cumsum(SS)


def profiled_energy(EE, ES, SS, is_load: bool, lo=-0.2, hi=0.2):
    if not is_load:
        return 0.5 * EE
    with np.errstate(divide="ignore", invalid="ignore"):
        b = np.clip(np.where(SS > 0, ES / SS, 0.0), lo, hi)
    return 0.5 * (EE - 2 * b * ES + b * b * SS)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cfg = json.loads(PROTOCOL.read_text())
    assets = json.loads(ASSETS.read_text())
    names = [a["id"] for a in assets]
    fam = [a["family"] for a in assets]
    bank = Bank(BANK)
    v0 = cfg["amplitude_prior_sd"] ** 2
    birth = 1 - np.exp(-cfg["birth_hazard_per_s"] / 30)
    log_prior_cell = np.log(birth / len(assets))
    log_threshold = np.log(cfg["alarm_probability"] / (1 - cfg["alarm_probability"]))

    # ---------- 1. Unit signatures: detection information per unit amplitude -------------
    rows = []
    null_terms = {}
    for i, a in enumerate(assets):
        amp = 0.1 if fam[i] == "load" else 1.0
        z = bank.simulate(i, amp, HORIZON)
        EE0, ES0, SS0 = bank.filter_terms(None, z)
        null_terms[i] = (EE0, amp)
        # isolation information against every other candidate
        iso = np.full((len(assets), HORIZON), np.inf)
        for j in range(len(assets)):
            if j == i:
                continue
            EE, ES, SS = bank.filter_terms(j, z)
            iso[j] = profiled_energy(EE, ES, SS, fam[j] == "load")
        # truth filter sanity: residual must vanish at the true amplitude
        EEt, ESt, SSt = bank.filter_terms(i, z)
        resid = 0.5 * (EEt - 2 * amp * ESt + amp * amp * SSt) if fam[i] == "load" else 0.5 * EEt
        nearest = int(np.argmin(iso[:, 29]))
        for k in [2, 5, 14, 29, 89]:
            rows.append(dict(source=names[i], family=fam[i], reports=k + 1,
                             detection_info=0.5 * EE0[k], isolation_info=float(np.min(iso[:, k])),
                             nearest_competitor=names[int(np.argmin(iso[:, k]))],
                             truth_residual=float(resid[k]), reference_amplitude=amp))
        print(names[i], "det(1s)=%.3g iso(1s)=%.3g nearest=%s truth_resid=%.2e" % (
            0.5 * EE0[29], iso[nearest, 29], names[nearest], resid[29]), flush=True)
    sig = pd.DataFrame(rows)
    sig.to_csv(OUT / "isolability_signatures.csv", index=False)

    # ---------- 2. Predicted alarm report per C01 event, vs observed ----------------------
    def predicted_alarm_report(i: int, amplitude: float) -> int | None:
        if fam[i] == "load":
            EE0, ref = null_terms[i]
            info = EE0 * (amplitude / ref) ** 2       # whitened energy scales with a^2
            # exact Gaussian marginal over b ~ N(0, v0): log BF = 1/2 G v0 /(1+G v0) * a^2 G ... use quadratic form
            # with e = a s (null filter), BF = 1/2 * (a G)^2/(G+1/v0) - 1/2 log(1+v0 G); G = info*2/a^2
            G = 2 * EE0 / ref ** 2
            logbf = 0.5 * (amplitude * G) ** 2 / (G + 1 / v0) - 0.5 * np.log1p(v0 * G)
        else:
            logbf = 0.5 * null_terms[i][0]
        post = logbf + log_prior_cell
        hit = np.flatnonzero(post >= log_threshold)
        if not len(hit):
            return None
        return int(hit[0]) + cfg["confirmation_frames"] - 1

    cases = json.loads(CASES.read_text())
    truth = {e["id"]: e for c in cases if c["condition"] == "MATCH" for e in c["events"]}
    ev = pd.read_csv(EVENTS)
    ev = ev[(ev.method == "R11_NOMINAL") & (ev.condition == "MATCH") & (ev.lane == "continuous")].copy()
    ev["amplitude"] = ev.event.map(lambda e: truth[e]["amplitude"])
    idx = {n: k for k, n in enumerate(names)}
    ev["predicted_alarm_delay_s"] = [
        (lambda r: np.nan if r is None else (r + 1) / 30)(predicted_alarm_report(idx[s], a if a == a else 1.0))
        for s, a in zip(ev.source, ev.amplitude)]
    ev["observed_alarm_delay_s"] = ev.alarm_s - ev.onset_s
    ev[["event", "source", "family", "amplitude", "noise", "predicted_alarm_delay_s",
        "observed_alarm_delay_s", "timely"]].to_csv(OUT / "predicted_vs_observed_delay.csv", index=False)

    # ---------- 3. Minimum detectable load change (MW) within one second -----------------
    loads = pd.read_csv(SCI.parent / "SIM0001_JuliaPD_F01/runtime/reference/data/load.csv")
    md = []
    for i in range(len(assets)):
        if fam[i] != "load":
            continue
        bus = int(names[i].replace("BUS", ""))
        p_mw = -100 * float(loads.loc[loads.bus == bus, "Pset"].iloc[0])
        EE0, ref = null_terms[i]
        G1 = 2 * EE0[29] / ref ** 2   # whitened information per unit amplitude^2 in 1 s
        need = 2 * (log_threshold - log_prior_cell)  # required 2*logLR (ignoring Occam term)
        for alpha in [1, 2, 5, 10, 20]:
            a_min = np.sqrt(need / (G1 / alpha ** 2))
            md.append(dict(source=names[i], load_MW=p_mw, noise_multiplier=alpha,
                           min_fraction_1s=a_min, min_MW_1s=a_min * p_mw,
                           test_min_fraction=0.03, detectable_at_test_min=a_min <= 0.03))
    pd.DataFrame(md).to_csv(OUT / "minimum_detectable_load.csv", index=False)

    summary = dict(bank=str(BANK.relative_to(SCI.parent)), regime="quiet", horizon_reports=HORIZON,
                   log_threshold=float(log_threshold), log_prior_cell=float(log_prior_cell),
                   max_truth_residual=float(sig.truth_residual.abs().max()))
    (OUT / "isolability_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    sys.exit(main())

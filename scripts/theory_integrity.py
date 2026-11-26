"""Information left for physical attribution when one PMU is missing or corrupted.

Proposition (integrity isolation): with Gaussian noise independent across PMUs,
profiling an unrestricted corruption sequence on the channels of PMU p is the
orthogonal projection that deletes those channels.  Hence the information that
separates a physical source from 'arbitrary corruption of PMU p' equals the
detection information of that source on the other seven PMUs, Lambda_i^(-p),
which is also the information available when PMU p is missing (guide labels 6
and 7 share one quantity).

Numerically, for each held-out calibration event (12 load, 12 line), the
deterministic PMU trajectory gives the change of voltage/current magnitudes
(relative) and angles in the first second after onset, relative to the
pre-onset mean.  Angles are centered across the available PMUs (common-mode
error removed).  With independent white per-PMU noise of standard deviation sigma
per relative-magnitude and radian-angle component, the matched-filter information is
    I = 1/2 * sum (change / sigma)^2,
computed with all PMUs and with each PMU deleted.  Output:
generated/revision_20261104/integrity_information.csv
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
B01 = ROOT.parent / "SGSMA26-Physics-Informed-AD/experiments/PAPER_CALIBRATION_B01"
REV = ROOT / "generated/revision_20261104"
PMUS = [2, 5, 6, 10, 19, 22, 29, 39]
NEED = 15.0
SIGMA = 0.0005


def info(z, t, onset, keep):
    pre = (t >= onset - 0.5) & (t < onset)
    win = (t >= onset) & (t < onset + 1.0)
    total = 0.0
    for f in ("voltage_magnitude", "current_magnitude"):
        x = z[f][:, keep]
        d = x[win] / x[pre].mean(axis=0) - 1
        total += float(np.sum(d ** 2))
    for f in ("voltage_angle", "current_angle"):
        a = np.unwrap(np.deg2rad(z[f][:, keep]), axis=0)
        d = a[win] - a[pre].mean(axis=0)
        d = d - d.mean(axis=1, keepdims=True)
        total += float(np.sum(d ** 2))
    return 0.5 * total / SIGMA ** 2


def main() -> None:
    truth = json.loads((B01 / "execution_request/truth_private/by_split/CAL.json").read_text())
    rows = []
    for case in [c for c in truth if c["condition"] == "MATCH" and c["kind"] == "event"]:
        with np.load(B01 / f"run/data/truth_private/deterministic/{case['id']}.npz") as zz:
            z = {k: zz[k] for k in zz.files}
        t = z["time_s"]
        for e in case["events"]:
            full = info(z, t, e["onset_s"], list(range(8)))
            row = dict(event=e["id"], family=e["family"], source=e["source"], amplitude=e["amplitude"], full=full)
            for p in range(8):
                row[f"without_{PMUS[p]}"] = info(z, t, e["onset_s"], [k for k in range(8) if k != p])
            rows.append(row)
    df = pd.DataFrame(rows)
    w = [c for c in df if c.startswith("without_")]
    df["worst_missing_pmu"] = df[w].idxmin(axis=1).str.replace("without_", "")
    df["worst_information"] = df[w].min(axis=1)
    df["worst_fraction"] = df.worst_information / df.full
    df["worst_over_alarm"] = df.worst_information / NEED
    df.to_csv(REV / "integrity_information.csv", index=False)
    summary = dict(sigma_tve=SIGMA, events=len(df),
                   min_worst_over_alarm=float(df.worst_over_alarm.min()),
                   median_worst_fraction=float(df.worst_fraction.median()),
                   min_worst_fraction=float(df.worst_fraction.min()),
                   all_above_alarm=bool((df.worst_information >= NEED).all()),
                   worst_case=df.loc[df.worst_fraction.idxmin(), ["source", "worst_missing_pmu", "worst_fraction"]].to_dict())
    (REV / "integrity_information.json").write_text(json.dumps(summary, indent=2, default=str))
    print(df[["source", "family", "amplitude", "full", "worst_missing_pmu", "worst_fraction", "worst_over_alarm"]].round(3).to_string())
    print(json.dumps(summary, indent=1, default=str))


if __name__ == "__main__":
    main()

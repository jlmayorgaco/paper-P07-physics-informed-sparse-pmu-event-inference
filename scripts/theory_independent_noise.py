"""Oracle information of the noise-stress load events under independent per-PMU phasor noise.

For each CAL load event, the deterministic (noise-free) PMU trajectory gives the
change of the voltage and current angles in the first second after onset,
relative to the pre-onset mean.  Removing the cross-PMU mean of each angle family
cancels any common-mode error (clock, frequency drift).  With independent white
angle noise of standard deviation sigma per PMU and report, a matched filter that
knows the signal shape has expected log-likelihood ratio
    I = 1/2 * sum_k sum_ch (dtheta_ch(k)/sigma)^2   (after mean removal),
an upper bound on what the angle channels can deliver.  Comparing I with the
alarm evidence (15 nats) separates a physical information limit from a
mis-specified noise model in the implemented filter.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
B01 = ROOT.parent / "SGSMA26-Physics-Informed-AD/experiments/PAPER_CALIBRATION_B01"
REV = ROOT / "generated/revision_20261104"
NEED = 15.0


def main() -> None:
    truth = json.loads((B01 / "execution_request/truth_private/by_split/CAL.json").read_text())
    rows = []
    for case in [c for c in truth if c["condition"] == "MATCH" and c["kind"] == "event"]:
        with np.load(B01 / f"run/data/truth_private/deterministic/{case['id']}.npz") as z:
            t = z["time_s"]
            ang = {f: np.unwrap(np.deg2rad(z[f]), axis=0) for f in ("voltage_angle", "current_angle")}
        for e in case["events"]:
            pre = (t >= e["onset_s"] - 0.5) & (t < e["onset_s"])
            win = (t >= e["onset_s"]) & (t < e["onset_s"] + 1.0)
            info = {}
            for f, a in ang.items():
                d = a[win] - a[pre].mean(axis=0)
                d = d - d.mean(axis=1, keepdims=True)          # cancel common-mode error
                info[f] = float(np.sum(d ** 2))                 # in rad^2; divide by sigma^2 below
            for tve in (0.0005, 0.001):
                total = 0.5 * (info["voltage_angle"] + info["current_angle"]) / tve ** 2
                vonly = 0.5 * info["voltage_angle"] / tve ** 2
                rows.append(dict(event=e["id"], family=e["family"], source=e["source"], amplitude=e["amplitude"],
                                 tve=tve, oracle_info_angles=total, oracle_info_voltage_angles=vonly,
                                 above_alarm=total >= NEED))
    df = pd.DataFrame(rows)
    df.to_csv(REV / "independent_noise_oracle.csv", index=False)
    print(df.groupby(["tve", "family"]).agg(events=("event", "size"), above=("above_alarm", "sum"),
                                            median_info=("oracle_info_angles", "median"),
                                            min_info=("oracle_info_angles", "min")).round(1).to_string())
    print(df[(df.family == "load")][["tve", "source", "amplitude", "oracle_info_angles",
                                       "oracle_info_voltage_angles"]].round(2).to_string())


if __name__ == "__main__":
    main()

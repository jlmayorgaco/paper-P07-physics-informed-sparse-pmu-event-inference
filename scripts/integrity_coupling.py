"""Network-coupling bound for balanced single-PMU excursions (IEEE 39-bus).

A balanced physical disturbance that lowers the positive-sequence voltage of
PMU p must also lower the voltage of the other PMUs through the network.  With
the network admittance matrix, constant-impedance loads and generator transient
reactances, a bolted fault at bus f changes bus voltages in proportion to
column f of Z = Y^{-1}, so the sag ratio between PMUs j and p is
|Z_jf / Z_pf|.  For each PMU p we compute

    c_p = min over fault buses f where p is the most affected PMU of
          max_{j != p} |Z_jf / Z_pf|,

the smallest possible coupling of a p-dominant physical sag to the rest of the
PMUs.  A balanced excursion at p whose largest sag elsewhere is far below
c_p * (sag at p) cannot be produced by the network and is an integrity event.

Generator transient reactances are the standard New England values on 100 MVA
(Pai, 1989); loads are constant impedance at the base-case voltage.
Output: generated/revision_20261104/integrity_coupling.json
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCI = ROOT.parent / "SGSMA26-Physics-Informed-AD"
OUT = ROOT / "generated/revision_20261104"
PMUS = [2, 5, 6, 10, 19, 22, 29, 39]
XD = {39: 0.006, 31: 0.0697, 32: 0.0531, 33: 0.0436, 34: 0.132, 35: 0.05, 36: 0.049, 37: 0.057, 38: 0.057,
      30: 0.031}


def main() -> None:
    y = pd.read_csv(SCI / "data/topology/ieee39/ybus_full_complex.csv")
    Y = np.zeros((39, 39), complex)
    Y[y.from_bus - 1, y.to_bus - 1] = y.real + 1j * y.imag
    raw = (SCI / "data/metadata/IEEE_39_Bus_Power_System.raw").read_text().splitlines()
    names, volt = {}, {}
    k = 3
    while not raw[k].strip().startswith("0 /"):
        f = [s.strip() for s in raw[k].split(",")]
        num, name = int(f[0]), int(re.search(r"BUS(\d+)", f[1]).group(1))
        names[num] = name
        volt[name] = float(f[8])
        k += 1
    k += 1
    while not raw[k].strip().startswith("0 /"):
        f = [s.strip() for s in raw[k].split("/")[0].split(",")]
        b = names[int(f[0])]
        p, q = float(f[5]), float(f[6])
        Y[b - 1, b - 1] += (p - 1j * q) / 100 / volt[b] ** 2
        k += 1
    for b, x in XD.items():
        Y[b - 1, b - 1] += 1 / (1j * x)
    Z = np.linalg.inv(Y)
    pm = [b - 1 for b in PMUS]
    res = {}
    for i, p in enumerate(PMUS):
        ratios = []
        for f in range(39):
            col = np.abs(Z[pm, f])
            if np.argmax(col) != i:
                continue
            others = np.delete(col, i) / col[i]
            ratios.append((f + 1, float(others.max()), PMUS[[j for j in range(8) if j != i][int(np.argmax(others))]]))
        if ratios:
            f, c, j = min(ratios, key=lambda r: r[1])
            res[p] = dict(coupling=c, worst_fault_bus=f, most_coupled_pmu=j, dominant_fault_buses=len(ratios))
    # prediction for the RAW0001 bolted fault at bus 39
    col = np.abs(Z[pm, 38])
    pred39 = {PMUS[j]: float(col[j] / col[7]) for j in range(8)}
    out = dict(per_pmu=res, predicted_sag_ratio_fault_bus39=pred39,
               note="ratio of voltage change at PMU j to change at the faulted PMU bus for a bolted fault")
    (OUT / "integrity_coupling.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()

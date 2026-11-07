"""Extract positive-sequence voltage windows of RAW0001 (one file at a time, low memory).  Labels are not read."""
from __future__ import annotations
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[2].parent / "SGSMA26-Physics-Informed-AD"
PMUS = [2, 5, 6, 10, 19, 22, 29, 39]
A = np.exp(2j * np.pi / 3)
WIN = {"quiet": (100.0, 300.0), "startup": (0.0, 3.0), "load": (3800.0, 4250.0), "line": (2330.0, 2430.0)}


def main() -> None:
    out = {k: [] for k in WIN}; ts = {}
    for b in PMUS:
        cols = ["TIMESTAMP"] + [f"BUS{b}_V{p}_{q}" for p in "ABC" for q in ("MAG", "ANG")] + ["DATA_PRESENT"]
        d = pd.read_csv(ROOT / f"data/RAW0001/Bus{b}_Competition_Data_nanmask.csv", usecols=cols)
        t = d.TIMESTAMP.to_numpy(); t = t - t[0]
        ph = [d[f"BUS{b}_V{p}_MAG"].to_numpy() * np.exp(1j * np.deg2rad(d[f"BUS{b}_V{p}_ANG"].to_numpy())) for p in "ABC"]
        v = (ph[0] + A * ph[1] + A * A * ph[2]) / 3
        v[d.DATA_PRESENT.to_numpy() != 1] = np.nan
        for k, (a, c) in WIN.items():
            m = (t >= a) & (t < c); out[k].append(v[m].astype(np.complex64)); ts[k] = t[m]
        del d, ph, v
    np.savez_compressed(Path(__file__).parent / "results/raw_windows.npz",
                        **{k: np.stack(out[k], 1) for k in WIN}, **{f"t_{k}": ts[k] for k in WIN})
    print({k: np.stack(out[k], 1).shape for k in WIN})


if __name__ == "__main__":
    main()

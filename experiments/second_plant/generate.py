"""Second, independent plant: re-simulate the B01 TEST schedules with classical machines, droop governors and
constant-impedance loads (experiments/history_conditioning/dynamics.py), then pass the result through the same
PMU operator and the same instrumental noise as the original cohort.  The bank and every baseline see records
whose physics they were not built on.   python generate.py [limit]
"""
from __future__ import annotations
import importlib.util, json, sys
from pathlib import Path
import numpy as np, pandas as pd

HERE = Path(__file__).resolve().parent
SCI = HERE.parents[2] / "SGSMA26-Physics-Informed-AD/experiments"
B01 = SCI / "PAPER_CALIBRATION_B01"
ENG = B01 / "run/engine_clean"
sys.path.insert(0, str(HERE.parent / "history_conditioning")); sys.path.insert(0, str(ENG / "reference"))
import dynamics as dyn                                   # noqa: E402
from pmu_operator import report                          # noqa: E402
from noise import NoiseStream, apply_noise               # noqa: E402

BR = pd.read_csv(SCI.parent / "data/topology/ieee39/branches_physical.csv")
PMUS = [2, 5, 6, 10, 19, 22, 29, 39]


class Plant2(dyn.Plant):
    """Adds line outages: cfg entries are (bus, level) for loads or ('L', i, j) for a removed branch."""

    def zg(self, cfg):
        z = self._zc.get(cfg)
        if z is None:
            Y = self.Y0 + self.Yg
            for e in cfg:
                if e[0] == "L":
                    r = BR[((BR.from_bus == e[1]) & (BR.to_bus == e[2])) | ((BR.from_bus == e[2]) & (BR.to_bus == e[1]))].iloc[0]
                    i, j = int(r.from_bus) - 1, int(r.to_bus) - 1; y = 1 / complex(r.r, r.x); bc = 1j * r.b / 2
                    t = r.tap * np.exp(1j * np.deg2rad(r.shift_deg))
                    Y = Y.copy(); Y[i, i] -= (y + bc) / abs(t) ** 2; Y[j, j] -= y + bc; Y[i, j] -= -y / np.conj(t); Y[j, i] -= -y / t
                else:
                    b, a = e; s = self.base_load[b]; Y = Y.copy(); Y[b - 1, b - 1] += np.conj(a * s) / self.net.vbase[b] ** 2
            z = np.linalg.inv(Y)[:, self.gi]; self._zc[cfg] = z
        return z

    def run_full(self, x, n, schedule):
        """n reports at 30/s from t=0; returns complex V at all 39 buses in per unit (the network model is already per unit)."""
        out = np.zeros((n, 39), complex); t = 0.0
        for r in range(n):
            for _ in range(dyn.REPORT_EVERY):
                x = self.step(x, self.zg(schedule(t + 0.5 * dyn.DT))); t += dyn.DT
            Zg = self.zg(schedule(t - 0.5 * dyn.DT))
            out[r] = (Zg @ (self.yg * (self.mag * np.exp(1j * x[:10]))))
        return out


def schedule_from(events):
    items = []
    for e in events:
        if e["family"] == "load":
            items.append((e["onset_s"], e["off_s"], (int(e["source"][3:]), float(e["amplitude"]))))
        else:
            i, j = (int(v) for v in e["source"][4:].split("-")); items.append((e["onset_s"], e["off_s"], ("L", i, j)))
    def f(t):
        return tuple(sorted((k for a, b, k in items if a <= t < b), key=str))
    return f


def main(limit=None):
    p = Plant2()
    truth = json.loads((B01 / "execution_request/truth_private/by_split/TEST.json").read_text())
    meta = {m["id"]: m for m in json.loads((B01 / "run/data/PRIVATE_RECORD_META_TEST.json").read_text())}
    ref = ENG / "reference"
    mapping = pd.read_csv(ref / "terminal_mapping.csv"); kv = pd.read_csv(ref / "data/bus.csv").base_kv.to_numpy()
    measure = json.loads((ref / "reporting_config.json").read_text()); noise = json.loads((ref / "stochastic_model.json").read_text())
    centers = {f: np.array(v["normalization_center"]) for f, v in noise["families"].items()}
    net = json.loads((B01 / "run/runtime/model/dae/measurement_network.json").read_text())
    B = np.array(net["B_real"]) + 1j * np.array(net["B_imag"])
    spec = importlib.util.spec_from_file_location("frozen_export", ENG / "export_pmu.py"); ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
    chosen = [r for r in truth if r["events"]][: (limit or 99)] + [r for r in truth if not r["events"]][:4]
    for r in chosen:
        dur = 120 if r["events"] else 120
        n = int(dur * 30) + 1
        V = p.run_full(p.init_state(), n, schedule_from(r["events"]))
        t = np.arange(n) / 30.0
        cur = -(V @ B.T)                                     # native current: minus the outward current B v (see pmu_operator)
        z = report(t, V, cur, mapping, kv, measure)
        det = dict(voltage_magnitude=abs(z["voltage_pu"]) * 345e3 / np.sqrt(3), voltage_angle=np.angle(z["voltage_pu"], deg=True),
                   current_magnitude=abs(z["current_A"]), current_angle=np.angle(z["current_A"], deg=True),
                   frequency=z["frequency_hz"], rocof=z["rocof_hz_s"])
        seed = meta[r["id"]]["noise_seed"]
        eps = NoiseStream(noise, seed).generate(n)
        noisy = apply_noise(det, eps)
        rid = "P" + r["id"][1:]
        np.savez_compressed(HERE / "data" / f"{rid}.npz", time_s=t, **noisy)
        ex.export(t, noisy, HERE / "data" / "observations" / rid, PMUS)
        (HERE / "data" / f"{rid}.truth.json").write_text(json.dumps(dict(r, id=rid, source_record=r["id"], duration_s=dur)))
        print("done", rid, len(r["events"]), "events", flush=True)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else None)

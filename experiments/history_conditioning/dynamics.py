"""Reduced electromechanical IEEE-39 plant for the history-conditioning study.

Classical machines (constant EMF behind transient reactance, swing equation with damping), constant-impedance
loads, network from the competition .raw (same admittance as the attributor).  Load changes are admittance steps,
so the network is exactly algebraic and the only nonlinearity is the sine of the rotor angle differences.
Inertias are the New England values on the 100 MVA base (sum 782.7 s, the system value used elsewhere).

This plant is NOT the research simulator used for the bank; it is an independent, cheaper plant used to test
whether conditioning on the previous event's state helps attribution (see PLAN.md).
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SCI = HERE.parents[2] / "SGSMA26-Physics-Informed-AD"          # science repository (network, topology, RAW0001)
_sp = importlib.util.spec_from_file_location("network", SCI / "experiments/PAPER_ALLEVENTS_V1/physics/network.py")
network = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(network)

GEN = [30, 31, 32, 33, 34, 35, 36, 37, 38, 39]
H = np.array([42.0, 30.3, 35.8, 28.6, 26.0, 34.8, 26.4, 24.3, 34.5, 500.0])
D = 4.0                      # pu on 100 MVA per pu speed (inter-machine damping)
DROOP = 0.05                 # governor droop (pu speed per pu power)
TG = 0.5                     # governor lag [s]
W0 = 2 * np.pi * 60.0
PMU = network.PMUS
CAND_LOADS = [3, 4, 7, 15, 16, 20, 24, 26]          # nonzero loads of the bank catalog (BUS31 has no load in the .raw)
DT = 1.0 / 120.0
REPORT_EVERY = 4                                     # 30 reports/s


class Plant:
    def __init__(self, hscale: float = 1.0, dscale: float = 1.0) -> None:
        self.H = H * hscale; self.D = D * dscale
        net = network.Network()
        self.net = net
        gi = [g - 1 for g in GEN]
        self.gi = gi
        self.yg = np.array([1 / (1j * network.XD[g]) for g in GEN])
        Yg = np.zeros((39, 39), complex)
        for k, g in enumerate(gi):
            Yg[g, g] = self.yg[k]
        self.Y0 = net.Y - Yg                              # network with base loads, without generators
        self.Yg = Yg
        V0 = net.V0
        Ig = (self.Y0 @ V0)[gi]
        self.E0 = V0[gi] + Ig / self.yg                   # E = V + I / y
        self.mag = np.abs(self.E0)
        self.d0 = np.angle(self.E0)
        self.pm = [p - 1 for p in PMU]
        self.base_load = net.load
        self._zc: dict = {}
        Zg0 = self.zg(())
        Veq = Zg0 @ (self.yg * self.E0)
        self.Pm = np.real(self.E0 * np.conj(self.yg * (self.E0 - Veq[gi])))

    # ---- network configuration: tuple of (bus, level) with level = fractional change of the base load
    def zg(self, cfg: tuple) -> np.ndarray:
        z = self._zc.get(cfg)
        if z is None:
            Y = self.Y0 + self.Yg
            for b, a in cfg:
                s = self.base_load[b]
                Y = Y.copy(); Y[b - 1, b - 1] += np.conj(a * s) / self.net.vbase[b] ** 2
            Z = np.linalg.inv(Y)
            z = Z[:, self.gi]
            self._zc[cfg] = z
        return z

    def init_state(self) -> np.ndarray:
        return np.r_[self.d0, np.zeros(10), self.Pm]

    def _f(self, x, Zg):
        d, w, pt = x[:10], x[10:20], x[20:]
        E = self.mag * np.exp(1j * d)
        V = Zg @ (self.yg * E)
        Ig = self.yg * (E - V[self.gi])
        Pe = np.real(E * np.conj(Ig))
        gov = (self.Pm - (self.Pm / DROOP) * w - pt) / TG
        return np.r_[W0 * w, (pt - Pe - self.D * w) / (2 * self.H), gov], V

    def step(self, x, Zg):
        k1, _ = self._f(x, Zg)
        k2, _ = self._f(x + 0.5 * DT * k1, Zg)
        k3, _ = self._f(x + 0.5 * DT * k2, Zg)
        k4, _ = self._f(x + DT * k3, Zg)
        return x + DT / 6 * (k1 + 2 * k2 + 2 * k3 + k4)

    def run(self, x, t0: float, t1: float, schedule) -> tuple[np.ndarray, np.ndarray, float]:
        """Integrate from t0 to t1 (multiples of 1/30 s); schedule(t) -> cfg.  Returns reports (n,16) and final state.

        A report is [log|V| (8), angle (8)] at the PMU buses, sampled at each 1/30 s boundary after t0."""
        n = int(round((t1 - t0) * 30))
        out = np.zeros((n, 16))
        t = t0
        for r in range(n):
            for _ in range(REPORT_EVERY):
                x = self.step(x, self.zg(schedule(t + 0.5 * DT)))
                t += DT
            Zg = self.zg(schedule(t - 0.5 * DT))
            E = self.mag * np.exp(1j * x[:10])
            V = (Zg @ (self.yg * E))[self.pm]
            out[r, :8] = np.log(np.abs(V)); out[r, 8:] = np.unwrap(np.angle(V))
        return out, x, t


def sched(events):
    """events: list of (t_on, t_off, bus, level).  Returns schedule function t -> config tuple."""
    def f(t):
        return tuple(sorted((b, a) for t_on, t_off, b, a in events if t_on <= t < t_off))
    return f


if __name__ == "__main__":
    import time
    p = Plant()
    x0 = p.init_state()
    t0 = time.perf_counter()
    y, x1, _ = p.run(x0, 0.0, 10.0, lambda t: ())
    print("equilibrium drift (max |dx|) over 10 s:", float(np.abs(x1 - x0).max()), "wall", round(time.perf_counter() - t0, 2))
    ev = [(1.0, 4.0, 7, 0.15)]
    y, x1, _ = p.run(x0, 0.0, 10.0, sched(ev))
    print("BUS7 +15% pulse: max d(log|V|) per PMU", np.round(np.abs(y[:, :8] - y[0, :8]).max(0), 5))
    print("angle swing (deg) per PMU", np.round(np.degrees(np.ptp(y[:, 8:], axis=0)), 4))
    print("Pm sum (pu)", float(p.Pm.sum()), "E mag", np.round(p.mag, 3))

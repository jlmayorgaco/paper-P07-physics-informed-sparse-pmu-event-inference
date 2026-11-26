"""Localize a signed load change from sparse voltages at two AC equilibria."""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import sys

import numpy as np
import pandas as pd
from scipy.optimize import root

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from competition_electrical_localizer import network_signatures
from competition_response_bank import BUSES

OBS = np.array(BUSES) - 1


class PowerFlow:
    def __init__(self, data):
        raw = (
            (data / "metadata/IEEE_39_Bus_Power_System.raw")
            .read_text()
            .splitlines()[3:]
        )
        v = np.zeros(39, complex)
        self.load = np.zeros(39, complex)
        types = np.zeros(39, int)
        ids = {}
        section = 0
        for line in raw:
            if line.strip().startswith("0 /end"):
                section += 1
                if section == 2:
                    break
                continue
            f = line.split("/")[0].split(",")
            key = int(f[0])
            if section == 0:
                bus = int(re.search(r"BUS(\d+)", f[1])[1]) - 1
                ids[key] = bus
                v[bus] = float(f[8]) * np.exp(1j * np.radians(float(f[9])))
                types[bus] = int(f[3])
            elif int(f[2]) and float(f[5]) > 0:
                self.load[ids[key]] += complex(float(f[5]), float(f[6])) / 100
        matrix = pd.read_csv(data / "topology/ieee39/ybus_full_complex.csv")
        self.y = np.zeros((39, 39), complex)
        self.y[matrix.from_bus - 1, matrix.to_bus - 1] = matrix.real + 1j * matrix.imag
        self.active = types != 3
        self.pq = types == 1
        assert self.active.sum() == 38 and self.pq.sum() == 29
        self.v0 = v
        self.x0 = np.r_[np.angle(v[self.active]), np.log(abs(v[self.pq]))]
        self.injection = self.power(self.x0)
        self.sites = np.flatnonzero(self.load.real > 0)
        assert len(self.sites) == 18

    def voltage(self, x):
        angles = np.angle(self.v0)
        logmag = np.log(abs(self.v0))
        angles[self.active] = x[: self.active.sum()]
        logmag[self.pq] = x[self.active.sum() :]
        return np.exp(logmag + 1j * angles)

    def project(self, s):
        return np.r_[s.real[self.active], s.imag[self.pq]]

    def power(self, x):
        v = self.voltage(x)
        return self.project(v * (self.y @ v).conj())

    def solve(self, load_delta, initial):
        target = self.injection - self.project(load_delta)
        sol = root(lambda x: self.power(x) - target, initial, tol=1e-10)
        error = np.max(abs(self.power(sol.x) - target))
        if not sol.success or error > 1e-7:
            raise ArithmeticError(f"nonconverged equilibrium, mismatch {error}")
        return sol.x, error

    def dictionary(self, *, full=False):
        h = 1e-5
        eye = np.eye(len(self.x0)) * h
        jac = np.column_stack(
            [
                (self.power(self.x0 + dx) - self.power(self.x0 - dx)) / (2 * h)
                for dx in eye
            ]
        )
        columns = []
        for site in self.sites:
            d = np.zeros(39, complex)
            d[site] = self.load[site]
            dx = np.linalg.solve(jac, -self.project(d))
            slope = (
                self.voltage(self.x0 + h * dx) - self.voltage(self.x0 - h * dx)
            ) / (2 * h * self.v0)
            # Compare the tangent with a one-sided nonlinear perturbation at nominal load.
            state, _ = self.solve(d * h, self.x0)
            exact = (self.voltage(state) / self.v0 - 1) / h
            assert np.max(abs(slope - exact)) < 2e-4
            columns.append(slope if full else slope[OBS])
        return np.array(columns)


def estimate(y, atoms, sites, real_scale):
    # Profile the common offset, then the step magnitude.
    centered = atoms - atoms.mean(axis=1, keepdims=True)
    products = centered.conj() @ (y - y.mean())
    power = products.real**2 if real_scale else abs(products) ** 2
    norm = (abs(centered) ** 2).sum(axis=1)
    assert np.all(norm > 1e-18)
    return int(sites[np.argmax(power / norm)] + 1)


def run(data, out):
    plant = PowerFlow(data)
    ac = plant.dictionary()
    lookup = network_signatures(data)[4]
    z = np.array([lookup[f"BUS{k+1}"] for k in plant.sites])
    rng = np.random.default_rng(694031)
    rows = []
    max_error = 0
    for op in range(16):
        operating = plant.load * rng.uniform(-0.05, 0.05, 39)
        x, err = plant.solve(operating, plant.x0)
        max_error = max(max_error, err)
        before = plant.voltage(x)
        for bus in plant.sites:
            frac = rng.choice([-1, 1]) * rng.uniform(0.05, 0.2)
            demand = operating.copy()
            demand[bus] += frac * plant.load[bus]
            after, err = plant.solve(demand, x)
            max_error = max(max_error, err)
            diff = (plant.voltage(after) / before - 1)[OBS]
            noise = (rng.normal(size=8) + 1j * rng.normal(size=8)) / np.sqrt(2)
            for rms in (0, 0.0005):
                measured = diff + rms * noise
                rows.append(
                    dict(
                        operating_point=op,
                        bus=int(bus + 1),
                        fraction=frac,
                        noise=rms,
                        impedance=estimate(measured, z, plant.sites, False),
                        ac_complex=estimate(measured, ac, plant.sites, False),
                        ac_real=estimate(measured, ac, plant.sites, True),
                    )
                )
    out.mkdir(parents=True, exist_ok=True)
    with (out / "predictions.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)
    summary = {}
    for noise in (0, 0.0005):
        group = [r for r in rows if r["noise"] == noise]
        assert len(group) == 288
        summary[str(noise)] = {
            method: sum(r["bus"] == r[method] for r in group)
            for method in ("impedance", "ac_complex", "ac_real")
        }
    files = [
        "metadata/IEEE_39_Bus_Power_System.raw",
        "topology/ieee39/ybus_full_complex.csv",
        "topology/ieee39/branches_physical.csv",
    ]
    report = dict(
        hits=summary,
        cases_per_condition=288,
        max_equilibrium_mismatch=float(max_error),
        inputs={
            name: hashlib.sha256((data / name).read_bytes()).hexdigest()
            for name in files
        },
    )
    (out / "summary.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("data", type=Path)
    p.add_argument("out", type=Path)
    a = p.parse_args()
    run(a.data, a.out)

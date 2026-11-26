"""Paired test of six terminal currents added to eight voltage changes."""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from run import OBS, PowerFlow, estimate

TERMINALS = (
    (2, 3, 3),
    (6, 7, 6),
    (10, 11, 11),
    (16, 19, 19),
    (21, 22, 22),
    (28, 29, 29),
)


def terminal_matrix(data):
    branches = pd.read_csv(data / "topology/ieee39/branches_physical.csv")
    matrix = np.zeros((len(TERMINALS), 39), complex)
    for k, (left, right, end) in enumerate(TERMINALS):
        matches = branches[
            ((branches.from_bus == left) & (branches.to_bus == right))
            | ((branches.from_bus == right) & (branches.to_bus == left))
        ]
        assert len(matches) == 1
        row = matches.iloc[0]
        a, b = int(row.from_bus), int(row.to_bus)
        y = 1 / complex(row.r, row.x)
        tap = row.tap * np.exp(1j * np.radians(row.shift_deg))
        diagonal = y + 0.5j * row.b
        weights = (
            (diagonal / abs(tap) ** 2, -y / tap.conjugate())
            if end == a
            else (-y / tap, diagonal)
        )
        matrix[k, [a - 1, b - 1]] = weights
    return matrix


def whiten(x, rms):
    return (x - x.mean(axis=-1, keepdims=True)) / rms


def run(data, out):
    plant = PowerFlow(data)
    terminal = terminal_matrix(data)
    tangent = plant.dictionary(full=True)
    base_i = terminal @ plant.v0
    currents = ((tangent * plant.v0) @ terminal.T) / base_i
    voltage_atoms = whiten(tangent[:, OBS], 0.0005)
    joint_atoms = np.column_stack([voltage_atoms, whiten(currents, 0.005)])
    rng = np.random.default_rng(879221)

    def noise(n, rms):
        return rms * (rng.normal(size=n) + 1j * rng.normal(size=n)) / np.sqrt(2)

    rows = []
    for op in range(16):
        delta = plant.load * rng.uniform(-0.05, 0.05, 39)
        state, _ = plant.solve(delta, plant.x0)
        before = plant.voltage(state)
        for bus in plant.sites:
            change = delta.copy()
            frac = rng.choice([-1, 1]) * rng.uniform(0.05, 0.2)
            change[bus] += frac * plant.load[bus]
            state_after, _ = plant.solve(change, state)
            after = plant.voltage(state_after)
            voltage = (after / before - 1)[OBS] + noise(8, 0.0005)
            current = (terminal @ after) / (terminal @ before) - 1 + noise(6, 0.005)
            assert np.isfinite(current).all()
            v = whiten(voltage, 0.0005)
            vi = np.r_[v, whiten(current, 0.005)]
            rows.append(
                dict(
                    operating_point=op,
                    bus=int(bus + 1),
                    fraction=frac,
                    voltage=estimate(v, voltage_atoms, plant.sites, True),
                    joint=estimate(vi, joint_atoms, plant.sites, True),
                )
            )
    df = pd.DataFrame(rows)
    out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "current_predictions.csv", index=False)
    va, vi = df.voltage == df.bus, df.joint == df.bus
    result = dict(
        n=len(df),
        voltage=int(va.sum()),
        joint=int(vi.sum()),
        gained=int((~va & vi).sum()),
        lost=int((va & ~vi).sum()),
    )
    (out / "current_summary.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("data", type=Path)
    p.add_argument("out", type=Path)
    a = p.parse_args()
    run(a.data, a.out)

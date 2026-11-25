"""Condition a physical load-source dictionary on the sparse pre-event phasors."""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import logsumexp

from joint_current import terminal_matrix, whiten
from run import OBS, PowerFlow, estimate


def normalized(z):
    return np.concatenate(
        [whiten(z[..., :8], 0.0005), whiten(z[..., 8:], 0.005)], axis=-1
    )


def read(v, terminal):
    return np.r_[v[OBS], terminal @ v]


def updated_responses(plant, terminal, prior, nominal, atoms):
    z = normalized(prior / nominal - 1)
    forward = np.vstack([atoms.real.T, atoms.imag.T])
    # Circular errors are specified by complex RMS; real components have half the variance.
    rhs = forward.T @ np.r_[z.real, z.imag]
    frac = np.linalg.solve(
        forward.T @ forward + np.eye(len(plant.sites)) / (2 * 0.05**2), rhs
    )
    base = np.zeros(39, complex)
    base[plant.sites] = plant.load[plant.sites] * frac
    state, _ = plant.solve(base, plant.x0)
    center = read(plant.voltage(state), terminal)
    slopes = []
    curves = []
    for bus in plant.sites:
        offsets = []
        for size in (-0.1, 0.1):
            step = base.copy()
            step[bus] += size * plant.load[bus]
            x, _ = plant.solve(step, state)
            offsets.append(normalized(read(plant.voltage(x), terminal) / center - 1))
        slopes.append((offsets[1] - offsets[0]) / 0.2)
        curves.append((offsets[1] + offsets[0]) / 0.02)
    return np.array(slopes), np.array(curves)


def run(data, out):
    plant = PowerFlow(data)
    terminal = terminal_matrix(data)
    nominal = read(plant.v0, terminal)
    tangent = plant.dictionary(full=True)
    atoms = normalized(
        np.column_stack(
            [tangent[:, OBS], ((tangent * plant.v0) @ terminal.T) / nominal[8:]]
        )
    )
    rms = np.r_[np.full(8, 0.0005), np.full(6, 0.005)]
    seed = 712490
    rng = np.random.default_rng(seed)

    def noise():
        return rms * (rng.normal(size=14) + 1j * rng.normal(size=14)) / np.sqrt(2)

    # Equal-width midpoint quadrature gives equal mass to increases and decreases.
    positive = 0.02 + (np.arange(512) + 0.5) * (0.28 / 512)
    sizes = np.r_[-positive, positive]
    rows = []
    for op in range(24):
        base = plant.load * rng.uniform(-0.075, 0.075, 39)
        x, _ = plant.solve(base, plant.x0)
        before = read(plant.voltage(x), terminal)
        prior = before * (1 + noise())
        slope, curve = updated_responses(plant, terminal, prior, nominal, atoms)
        expected = (
            sizes[None, :, None] * slope[:, None, :]
            + sizes[None, :, None] ** 2 * curve[:, None, :]
        )
        for bus in plant.sites:
            step = base.copy()
            frac = rng.choice([-1, 1]) * rng.uniform(0.04, 0.22)
            step[bus] += frac * complex(
                plant.load[bus].real, plant.load[bus].imag * rng.uniform(0.9, 1.1)
            )
            state, _ = plant.solve(step, x)
            y = normalized(read(plant.voltage(state), terminal) / before - 1 + noise())
            likelihood = -np.sum(abs(expected - y) ** 2, axis=-1)
            rows.append(
                dict(
                    op=op,
                    bus=int(bus + 1),
                    nominal=estimate(y, atoms, plant.sites, True),
                    profile=int(plant.sites[likelihood.max(axis=1).argmax()] + 1),
                    marginal=int(
                        plant.sites[logsumexp(likelihood, axis=1).argmax()] + 1
                    ),
                )
            )
    df = pd.DataFrame(rows)
    assert len(df) == 432
    out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "operating_predictions.csv", index=False)
    old = df.nominal == df.bus
    stats = {}
    for key in ("nominal", "profile", "marginal"):
        hit = df[key] == df.bus
        stats[key] = dict(
            hits=int(hit.sum()),
            gained=int((hit & ~old).sum()),
            lost=int((~hit & old).sum()),
        )
    (out / "operating_summary.json").write_text(json.dumps(stats, indent=2) + "\n")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("data", type=Path)
    p.add_argument("out", type=Path)
    a = p.parse_args()
    run(a.data, a.out)

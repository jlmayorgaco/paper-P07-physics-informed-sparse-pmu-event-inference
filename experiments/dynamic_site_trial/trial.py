"""Paired location readouts on independently generated classical-machine trajectories."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments/history_conditioning"))
import dynamics as dyn

N = 90
ONSETS = np.arange(3, 13)
SIGMA = .001


def simulate(plant, family, bus, strength, onset):
    """Integrate the nonlinear plant, measuring relative phasors at eight PMUs."""
    z0 = plant.zg(())
    z1 = z0
    torque = np.zeros(10)
    if family == "generation":
        torque[dyn.GEN.index(bus)] = .1 * strength
    else:
        demand = .01 if family == "weak" else .1 * plant.base_load[bus]
        y = plant.Y0 + plant.Yg
        y[bus-1, bus-1] += np.conj(demand * strength) / plant.net.vbase[bus]**2
        z1 = np.linalg.inv(y)[:, plant.gi]
    x = plant.init_state()
    baseline = (z0 @ (plant.yg * plant.E0))[plant.pm]
    response = np.zeros((N, 16))
    direct = np.zeros_like(response)

    def observe(v):
        ratio = v[plant.pm] / baseline
        return np.r_[np.log(abs(ratio)), np.angle(ratio)]

    for t in range(onset, N):
        active = t < onset + 30
        z = z1 if active else z0
        acceleration = torque / (2 * plant.H) if active else 0

        def derivative(state):
            dx, _ = plant._f(state, z)
            dx[10:20] += acceleration
            return dx

        for _ in range(dyn.REPORT_EVERY):
            dt = dyn.DT
            a = derivative(x)
            b = derivative(x + dt*a/2)
            c = derivative(x + dt*b/2)
            d = derivative(x + dt*c)
            x += dt * (a + 2*b + 2*c + d) / 6
        response[t] = observe(z @ (plant.yg * plant.mag * np.exp(1j*x[:10])))
        if active:
            direct[t] = observe(z1 @ (plant.yg * plant.E0))
    return response, direct


def template_bank(plant, family, sites):
    banks = [[], []]
    for bus in sites:
        for bank, signal in zip(banks, simulate(plant, family, bus, 1., 0)):
            shifted = np.zeros((len(ONSETS), N, 16))
            for j, onset in enumerate(ONSETS):
                shifted[j, onset:] = signal[:-onset]
            bank.append(shifted)
    return [np.array(bank) for bank in banks]


def rank(data, bank, sites, onset, strength, known, channels):
    signatures = bank[..., channels]
    cross = np.einsum("sutj,tj->su", signatures, data[:, channels])
    energy = np.einsum("sutj,sutj->su", signatures, signatures)
    scale = strength if known else np.clip(cross / np.maximum(energy, 1e-24), .7, 1.3)
    score = 2 * scale * cross - scale**2 * energy
    best = score[:, onset - ONSETS[0]] if known else score.max(axis=1)
    # A tie between indistinguishable assets supplies no exact prediction.
    winners = np.flatnonzero(best >= best.max() - 1e-16)
    return sites[winners[0]] if len(winners) == 1 else -1


def predict(split, folder):
    plant = dyn.Plant()
    rng = np.random.default_rng(84721 if split == "dev" else 59803)
    sites_by_family = dict(weak=list(range(1, 40)), generation=dyn.GEN,
                           load=sorted(b for b,s in plant.base_load.items() if s.real > 0))
    predictions, truths = [], []
    for family, sites in sites_by_family.items():
        dynamic, static = template_bank(plant, family, sites)
        for index, bus in enumerate(sites):
            if (index % 3 == 0) != (split == "blind"):
                continue
            for _ in range(6):
                strength = rng.uniform(.7, 1.3)
                onset = int(rng.choice(ONSETS))
                plant.H = dyn.H * rng.uniform(.8, 1.2)
                plant.D = dyn.D * rng.uniform(.8, 1.2)
                signal, _ = simulate(plant, family, bus, strength, onset)
                observed = signal + rng.normal(0, SIGMA, signal.shape)
                row = dict(case=len(predictions), family=family)
                for name, bank, known, channels in (
                    ("static", static, False, slice(None)),
                    ("static_known", static, True, slice(None)),
                    ("dynamic", dynamic, False, slice(None)),
                    ("dynamic_known", dynamic, True, slice(None)),
                    ("magnitude", dynamic, False, slice(0, 8)),
                    ("angle", dynamic, False, slice(8, 16)),
                ):
                    row[name] = rank(observed, bank, sites, onset, strength, known, channels)
                predictions.append(row)
                truths.append(dict(case=row["case"], bus=bus))
        plant.H, plant.D = dyn.H.copy(), dyn.D
    dest = folder / f"{split}_predictions.csv"
    pd.DataFrame(predictions).to_csv(dest, index=False)
    (folder / f"{split}.sha256").write_text(hashlib.sha256(dest.read_bytes()).hexdigest())
    pd.DataFrame(truths).to_csv(folder / f"{split}_truth.csv", index=False)


def score(split, folder):
    dest = folder / f"{split}_predictions.csv"
    assert hashlib.sha256(dest.read_bytes()).hexdigest() == (folder / f"{split}.sha256").read_text()
    frame = pd.read_csv(dest).merge(pd.read_csv(folder / f"{split}_truth.csv"), validate="one_to_one")
    rng = np.random.default_rng(985)
    rows = []
    for family, group in frame.groupby("family"):
        hits = group.iloc[:, 2:-1].eq(group.bus, axis=0)
        delta = hits.dynamic.astype(int) - hits.static.astype(int)
        cluster = delta.groupby(group.bus).mean().to_numpy()
        ci = np.quantile(rng.choice(cluster, (5000, len(cluster))).mean(axis=1), [.025, .975])
        rows.append(dict(family=family, n=len(group), **hits.sum().to_dict(),
                         gained=int(sum(delta == 1)), lost=int(sum(delta == -1)),
                         delta_ci=ci.tolist()))
    (folder / f"{split}_scores.json").write_text(json.dumps(rows, indent=2))
    print(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["predict", "score"])
    parser.add_argument("split", choices=["blind", "dev"])
    args = parser.parse_args()
    (predict if args.mode == "predict" else score)(args.split, Path(__file__).resolve().parent)

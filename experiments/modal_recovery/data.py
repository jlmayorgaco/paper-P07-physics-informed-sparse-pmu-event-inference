"""Generate independent simulated recoveries with matched no-second-switch controls."""
import argparse
from concurrent.futures import ProcessPoolExecutor
from hashlib import sha256
import json
import os
from pathlib import Path
import sys

for var in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS"):
    os.environ[var] = "1"

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments/second_family"))
import simulate_pairs as sim

TMP = ROOT / "tmp/modal_recovery"
SEEDS = {"fit": 345771, "cal": 861571, "test": 710533}


def channels(raw):
    return np.column_stack((raw["voltage_magnitude"] * (np.sqrt(3) / 345000), raw["current_magnitude"]))


def nominal_modes():
    plant = sim.plant
    x = plant.init_state()
    network = plant.zg(())
    steps = np.maximum(1, abs(x)) * 1e-6
    def derivative(delta):
        return plant._f(x + delta, network)[0]
    columns = [(derivative(d) - derivative(-d)) / (2 * dt) for d, dt in zip(np.diag(steps), steps)]
    modes = np.linalg.eigvals(np.stack(columns, axis=1)).imag / (2 * np.pi)
    return np.sort(modes[modes > 1e-6])


def template(arg):
    source, amplitude = arg
    asset = next(a for a in sim.assets if a["id"] == source)
    e = sim.event(np.random.default_rng(0), asset, 120, 120)
    e["amplitude"] = amplitude
    _, raw = sim.physical(dict(duration_s=4.5, events=[e]))
    y = channels(raw)
    baseline = y[5:60].mean(axis=0)
    np.testing.assert_allclose(y[5:60], np.broadcast_to(baseline,(55,16)), rtol=1e-8, atol=1e-7)
    return (source, asset["family"], y[60:90] - baseline)


def parent(arg):
    split, idx = arg
    rng = np.random.default_rng([SEEDS[split], idx])
    families = ("load", "line")
    first_family = families[idx % 2]
    second_family = families[(idx // 2) % 2]
    def choose(family, exclude=None):
        eligible = [a for a in sim.assets if a["family"] == family and a["id"] != exclude]
        return eligible[int(rng.integers(len(eligible)))]
    first = sim.event(rng, choose(first_family), 2 * int(rng.integers(52, 69)), 2 * int(rng.integers(60,121)))
    clearance = first["off_tick"] // 2
    end = clearance / 30 + 9
    noise_seed = int(rng.integers(1, 2**31))
    variants = [None]
    if split == "test":
        asset = choose(second_family, first["source"])
        variants.append(sim.event(rng, asset, first["off_tick"] + int(rng.integers(75, 241)),
                                  int(rng.integers(120, 241))))
    noise = sim.sim.NoiseStream(sim.sim.NOISE, noise_seed).generate(round(end * 30) + 1)
    targets = {}
    for second in variants:
        identity = rng.bytes(12).hex()
        active = [first] if second is None else [first, second]
        t, raw = sim.physical(dict(duration_s=end, events=active))
        y = channels(sim.sim.apply_noise(raw, noise))
        path = TMP / split / (identity + ".npz")
        with path.open("xb") as stream:
            np.savez_compressed(stream, y=y, t=t, clearance=np.int32(clearance))
        targets[identity] = dict(parent=idx, first=first["source"], clearance=clearance,
                                 family=second["family"] if second else "none",
                                 source=second["source"] if second else None,
                                 on=second["onset_s"] if second else None, off=second["off_s"] if second else None)
    return targets


def generate(split, workers):
    work = TMP / split
    work.mkdir(parents=True, exist_ok=False)
    if split == "test":
        from study import verify
        verify()
    size = {"fit": 48, "cal": 80, "test": 96}[split]
    with ProcessPoolExecutor(workers, initializer=sim.initialize) as pool:
        if split == "fit":
            sim.initialize()
            tasks = [(a["id"], amp) for a in sim.assets for amp in
                     ((-.14, -.09, -.04, .04, .09, .14) if a["family"] == "load" else (None,))]
            result = list(pool.map(template, tasks))
            ids, families, signatures = zip(*result)
            np.savez(TMP / "templates.npz", ids=ids, families=families, signatures=np.array(signatures), modes_hz=nominal_modes())
        targets = {}
        for i, rows in enumerate(pool.map(parent, ((split, i) for i in range(size))), 1):
            targets.update(rows)
            if i % 16 == 0:
                print(split, i, "/", size, flush=True)
    assert len(targets) == (2 * size if split == "test" else size)
    content = (json.dumps(targets, sort_keys=True, indent=2) + "\n").encode()
    (TMP / (split + "_truth.json")).write_bytes(content)
    if split == "test":
        (TMP / "test_truth.sha256").write_text(sha256(content).hexdigest(), encoding="ascii")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("split", choices=SEEDS)
    p.add_argument("--workers", type=int, default=6)
    args = p.parse_args()
    generate(args.split, args.workers)

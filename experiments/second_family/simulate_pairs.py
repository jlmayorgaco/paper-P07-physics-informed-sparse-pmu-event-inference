"""Generate isolated training events and blinded prospective second-event streams."""

import argparse
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from shared import RESULT, RUN, TMP, FIELDS, archive_imports, digest, read, save


def initialize():
    global sim, plant, assets
    archive_imports()
    import simulate as sim
    import plant2

    plant = plant2.build()
    assets = read(RUN / "dependencies/runtime/model/assets.json")


def physical(row):
    t, v, i, status = plant.simulate(row, sim.MAP)
    if not status["valid"]:
        raise ValueError(status)
    z = sim.report(t, v, i, sim.MAP, sim.KV, sim.REPORT)
    return t, dict(
        voltage_magnitude=abs(z["voltage_pu"]) * 345e3 / np.sqrt(3),
        voltage_angle=np.angle(z["voltage_pu"], deg=True),
        current_magnitude=abs(z["current_A"]),
        current_angle=np.angle(z["current_A"], deg=True),
        frequency=z["frequency_hz"],
        rocof=z["rocof_hz_s"],
    )


def event(rng, asset, start, length):
    amp = float(rng.choice([-1, 1]) * rng.uniform(0.03, 0.14)) if asset["family"] == "load" else None
    return dict(
        source=asset["id"],
        family=asset["family"],
        amplitude=amp,
        onset_tick=start,
        off_tick=start + length,
        onset_s=start / 60,
        off_s=(start + length) / 60,
    )


def isolated(task):
    from spectral import features, channels

    seed, idx = task
    rng = np.random.default_rng([seed, idx])
    a = assets[idx % 18]
    e = event(rng, a, 120, 120)
    t, raw = physical(dict(duration_s=5.0, events=[e]))
    noise = sim.NoiseStream(sim.NOISE, int(rng.integers(2**31))).generate(len(t))
    pmu = sim.apply_noise(raw, noise)
    x = channels(pmu, slice(5, 58))
    k = 60 + int(rng.integers(13))
    return *features(x[k : k + 30]), int(a["family"] == "line")


def train_data(workers):
    TMP.mkdir(parents=True, exist_ok=True)
    with ProcessPoolExecutor(workers, initializer=initialize) as pool:
        for split, seed, n in (("train", 869141, 360), ("val", 869143, 108)):
            data = list(pool.map(isolated, [(seed, i) for i in range(n)], chunksize=3))
            eigen, singular, y = map(np.stack, zip(*data))
            np.savez(TMP / (split + ".npz"), eigen=eigen, singular=singular, y=y)
            print(split, n, flush=True)


def new_test(task):
    index, template, families = task
    rng = np.random.default_rng([869147, index])
    row = []
    start = int(rng.integers(900, 1141))
    for family in families:
        pool = [a for a in assets if a["family"] == family and all(a["id"] != e["source"] for e in row)]
        e = event(rng, pool[int(rng.integers(len(pool)))], start, int(rng.integers(120, 301)))
        row.append(e)
        start = e["off_tick"] + int(rng.integers(30, 181))
    t, raw = physical(dict(duration_s=40, events=row))
    pid = template["id"]
    noise = sim.NoiseStream(sim.NOISE, template["noise_seed"])
    prefix = noise.generate(360)
    for name, child in zip(noise.order, np.random.SeedSequence([869149, index]).spawn(len(noise.order))):
        noise.family[name]["rng"] = np.random.default_rng(child)
    future = noise.generate(len(t) - 360)
    d = sim.apply_noise(raw, {k: np.concatenate((prefix[k], future[k])) for k in prefix})
    base = RUN / "observations/P2/TEST" / (pid + "_nominal.npz")
    with np.load(base, allow_pickle=False) as z:
        for key in FIELDS:
            np.testing.assert_allclose(d[key][:360], z[key][:360], rtol=2e-6, atol=1e-6, equal_nan=True)
            d[key] = d[key].astype(z[key].dtype)
            d[key][:360] = z[key][:360]
        t = t.astype(z["time_s"].dtype)
    path = TMP / "pmu" / (pid + ".npz")
    np.savez_compressed(path, time_s=t, **d)
    return dict(id=pid, observation_sha=digest(path)), dict(id=pid, events=row)


def test_data(workers):
    from freeze import verify

    verify()
    if (RESULT / "observations.json").exists():
        raise FileExistsError("Test observations already sealed")
    (TMP / "pmu").mkdir(parents=True, exist_ok=True)
    templates = sorted(
        (r for r in read(RUN / "truth_private/TEST.json") if r["kind"] == "normal"), key=lambda r: r["id"]
    )
    patterns = [("load", "load"), ("load", "line"), ("line", "load"), ("line", "line")] * 9
    np.random.default_rng(869147).shuffle(patterns)
    assert len(templates) == len(patterns) == 36
    with ProcessPoolExecutor(workers, initializer=initialize) as pool:
        results = list(pool.map(new_test, zip(range(36), templates, patterns)))
    obs, truth = map(list, zip(*results))
    save(TMP / "truth.json", truth)
    save(RESULT / "observations.json", dict(records=obs, truth_sha=digest(TMP / "truth.json")))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("stage", choices=["training", "test"])
    p.add_argument("--workers", type=int, default=8)
    args = p.parse_args()
    (train_data if args.stage == "training" else test_data)(args.workers)

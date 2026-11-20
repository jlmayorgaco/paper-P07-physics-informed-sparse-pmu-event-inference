"""Matched trajectories with the same first event, machine parameters and PMU noise."""
import argparse
from pathlib import Path

import numpy as np

from physical import Generator, ROOT
from study import digest, read, write_json


OUT = Path(__file__).resolve().parent / "episode_confirmation"
DATA = ROOT / "tmp/graph_episode_confirmation"
DESIGN = {"train": (4, 485179), "dev": (2, 138709), "test": (2, 605937)}
SPANS = {1: (5, 13), 2: (22, 59), 3: (27, 66), 4: (27, 66)}


def generate(split):
    if split == "test":
        from episode_trial import verify
        verify()
    blocks, seed = DESIGN[split]
    rng = np.random.default_rng(seed)
    sim = Generator()
    sites = {code: [s for i, s in enumerate(sorted(sim.catalog[code]))
                    if (i % 3 == 0) == (split == "test")] for code in SPANS}
    rows = []
    def event(code, onset):
        return dict(code=int(code), source=str(rng.choice(sites[code])), onset=int(onset),
                    end=int(onset + rng.integers(*SPANS[code])), strength=float(rng.uniform(.7, 1.3)),
                    sensors=[2, 5])

    for block in range(blocks):
        for j in range(12):
            rows.append((f"quiet-{block}-{j}", [], int(rng.integers(2**60))))
        for code in SPANS:
            first = event(code, rng.integers(65, 316))
            rows.append((f"single-{block}-{code}", [first], int(rng.integers(2**60))))
        # A full crossing gives four matched recovery controls per ordered pair across four blocks.
        for code in SPANS:
            for next_code in SPANS:
                key = f"pair-{block}-{code}-{next_code}"
                first = event(code, rng.integers(65, 316))
                second = event(next_code, max(first["end"] + rng.integers(30, 121), first["onset"] + 46))
                noise_seed = int(rng.integers(2**60))
                rows.extend([(key, [first], noise_seed), (key, [first, second], noise_seed)])
    folder = DATA / split
    folder.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(exist_ok=True)
    manifest = OUT / f"{split}_manifest.json"
    if manifest.exists() and (folder / "pmu.npy").exists():
        raise FileExistsError(f"{split} already generated")
    observations = np.lib.format.open_memmap(folder / "pmu.npy", mode="w+", dtype="float32",
                                              shape=(len(rows), 720, 8, 5))
    labels, clusters = [], []
    for i, position in enumerate(rng.permutation(len(rows))):
        cluster, events, noise_seed = rows[position]
        observations[i] = sim.simulate(events, np.random.default_rng(noise_seed))
        labels.append(events)
        clusters.append(cluster)
    observations.flush()
    write_json(folder / "truth.json", labels)
    info = dict(seed=seed, records=len(rows), sites=sites, clusters=clusters,
                observations=digest(folder / "pmu.npy"), truth=digest(folder / "truth.json"))
    if manifest.exists() and info != read(manifest):
        raise ValueError("Regenerated data differ from archived hashes")
    write_json(manifest, info)
    print(split, len(rows), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("split", choices=DESIGN)
    generate(parser.parse_args().split)

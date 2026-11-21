"""Disjoint simulations for fitting, calibration and paired comparison."""
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import argparse
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import data
import study

TMP = study.ROOT / "tmp/conditional_switch"
SPLITS = {"fit": (8204613, 256), "cal": (6721831, 320), "test": (9316879, 240)}


def initialize(split):
    data.TMP = TMP
    data.SEEDS[split] = SPLITS[split][0]
    data.sim.initialize()


def generate(split, workers):
    if split == "test":
        from run import verify
        verify()
    seed, size = SPLITS[split]
    folder = TMP / split
    folder.mkdir(exist_ok=True, parents=True)
    if (TMP / (split+"_manifest.json")).exists():
        raise FileExistsError("Split is already complete")
    if any(folder.iterdir()):
        raise FileExistsError("Existing partial split needs inspection")
    truth = {}
    with ProcessPoolExecutor(workers, initializer=initialize, initargs=(split,)) as pool:
        for i, rows in enumerate(pool.map(data.parent, [(split,i) for i in range(size)]), 1):
            truth.update(rows)
            if i % 80 == 0:
                print(split,i,flush=True)
    assert len(truth) == size * (2 if split == "test" else 1)
    label_path = TMP / (split+"_truth.json")
    study.save(label_path, truth)
    observations = {p.stem: study.digest(p) for p in sorted(folder.glob("*.npz"))}
    assert observations.keys() == truth.keys()
    study.save(TMP / (split+"_manifest.json"), dict(seed=seed, parents=size, hashes=observations,
                                                    targets_sha=study.digest(label_path)))


if __name__ == "__main__":
    cli = argparse.ArgumentParser()
    cli.add_argument("split", choices=SPLITS)
    cli.add_argument("--workers", type=int, default=8)
    args = cli.parse_args()
    generate(args.split,args.workers)

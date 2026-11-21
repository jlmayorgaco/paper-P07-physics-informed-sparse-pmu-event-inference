"""Matched nonlinear P2 simulations using the upstream reporting and noise models."""
import argparse
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent/"conditional_switch"))
sys.path.insert(0, str(HERE.parent))
import data
import study
import numpy as np

TMP = study.ROOT/"tmp/relative_phase"
RESULT = HERE/"results"
SPLITS = {"fit":(8204613,256), "cal":(6721831,320), "dev":(9316879,240), "test":(20977153,240)}


def channels(raw):
    # Store the measured angles in degrees to preserve the PMU reporting convention.
    return np.column_stack((raw["voltage_magnitude"]*(np.sqrt(3)/345000),raw["current_magnitude"],
                            raw["voltage_angle"],raw["current_angle"]))


def angular(y):
    """Relative quadrature components using only the initial quiet reporting second."""
    v, i = np.deg2rad(y[:,16:24]), np.deg2rad(y[:,24:32])
    phase = np.column_stack((v[:,1:]-v[:,:1],i-v))
    reference = np.angle(np.exp(1j*phase[:30]).mean(axis=0))
    return np.sin(phase-reference)*np.column_stack((y[:,1:8],y[:,8:16]))


def initialize(split):
    data.TMP = TMP
    data.channels = channels
    name = "test" if split in ("dev","test") else split
    data.SEEDS[name] = SPLITS[split][0]
    data.sim.initialize()


def parent(task):
    split, index = task
    # Upstream writes into a directory named by its split. Isolate each run.
    data.TMP = TMP/split
    name = "test" if split in ("dev","test") else split
    return data.parent((name,index))


def folder(split):
    return TMP/split/("test" if split in ("dev","test") else split)


def generate(split, workers):
    if split=="test":
        from campaign import verify_freeze
        verify_freeze()
    target = folder(split)
    target.mkdir(exist_ok=False,parents=True)
    seed, n = SPLITS[split]
    truth = {}
    with ProcessPoolExecutor(workers,initializer=initialize,initargs=(split,)) as pool:
        for entry in pool.map(parent,[(split,i) for i in range(n)],chunksize=2):
            truth.update(entry)
    assert len(truth)==n*(2 if split in ("dev","test") else 1)
    truth_path = TMP/split/"targets.json"
    study.save(truth_path,truth)
    files = {p.stem:study.digest(p) for p in sorted(target.glob("*.npz"))}
    assert files.keys()==truth.keys()
    if split!="test":
        old_split = "test" if split=="dev" else split
        old = study.ROOT/"tmp/conditional_switch"
        assert study.read(old/(old_split+"_truth.json"))==truth
        for key in files:
            y,c = study.unpack(target/(key+".npz"))
            previous,old_c = study.unpack(old/old_split/(key+".npz"))
            assert c==old_c and np.array_equal(y[:,:16],previous)
    study.save(TMP/split/"manifest.json",dict(seed=seed,parents=n,hashes=files,targets_sha=study.digest(truth_path)))
    print(split,n,len(files),flush=True)


if __name__=="__main__":
    cli=argparse.ArgumentParser()
    cli.add_argument("split",choices=SPLITS)
    cli.add_argument("--workers",type=int,default=8)
    a=cli.parse_args()
    generate(a.split,a.workers)

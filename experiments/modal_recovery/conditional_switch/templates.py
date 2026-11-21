"""Generate isolated electrical responses and integrate over unknown load size."""
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import data
import numpy as np
TMP = data.ROOT / "tmp/conditional_switch"


def simulate_response(task):
    asset, size = task
    event = data.sim.event(np.random.default_rng(0),asset,120,190)
    event["amplitude"] = size
    _, raw = data.sim.physical(dict(duration_s=5.5, events=[event]))
    y = data.channels(raw)
    return y[60:150]-y[5:60].mean(axis=0)


def build():
    data.sim.initialize()
    nodes, weights = np.polynomial.legendre.leggauss(5)
    sizes = .085 + .055*nodes
    tasks, ids, prior = [], [], []
    for asset in data.sim.assets:
        amps = [None] if asset["family"]=="line" else np.r_[-sizes,sizes].tolist()
        mass = [1.] if len(amps)==1 else np.tile(weights/4.,2)
        for amp, p in zip(amps,mass):
            tasks.append((asset,amp))
            ids.append(asset["id"])
            prior.append(p/18.)
    with ProcessPoolExecutor(8,initializer=data.sim.initialize) as pool:
        responses = list(pool.map(simulate_response,tasks))
    assert np.isclose(sum(prior),1.)
    TMP.mkdir(exist_ok=True,parents=True)
    with (TMP/"templates.npz").open("xb") as stream:
        np.savez_compressed(stream,signals=responses,ids=ids,probabilities=prior)


if __name__ == "__main__":
    build()

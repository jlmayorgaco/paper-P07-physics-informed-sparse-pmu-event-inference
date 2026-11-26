"""New balanced four-family streams; reserve entire assets across physical families."""
import argparse
import numpy as np

from common import DATA, FREEZE, HELD, RESULT, load, save, sha, verify
from physical import Generator


DESIGN = {"train": (40,80,64,7832149), "dev": (24,40,32,4217081),
          "test": (192,80,64,9148053)}
SPANS = {1:(5,13), 2:(22,59), 3:(27,66), 4:(27,66)}


def generate(split):
    if split == "test":
        verify()
    elif FREEZE.exists():
        raise FileExistsError("Development is closed")
    folder = DATA/split
    folder.mkdir(parents=True,exist_ok=True)
    manifest = RESULT/f"{split}_manifest.json"
    if manifest.exists():
        raise FileExistsError(str(manifest))
    n0,n1,n2,seed = DESIGN[split]
    sequence, physical = np.random.SeedSequence(seed).spawn(2)
    rng = np.random.default_rng(sequence)
    gen = Generator()
    sites = {c:sorted(s for s in gen.catalog[c] if (s in HELD)==(split=="test")) for c in SPANS}
    sizes = rng.permutation([0]*n0+[1]*n1+[2]*n2)
    total = n1+2*n2
    codes = iter(rng.permutation(np.tile(np.arange(1,5),total//4)))
    # Cover every reserved source; shuffle a complete catalogue before starting another pass.
    sources = {c:iter(np.concatenate([rng.permutation(s) for _ in range(total//(4*len(s))+1)]))
               for c,s in sites.items()}
    array = np.lib.format.open_memmap(folder/"pmu.npy", mode="w+", dtype="float32",
                                      shape=(len(sizes),720,8,5))
    truth = []
    for i,(count,child) in enumerate(zip(sizes,physical.spawn(len(sizes)),strict=True)):
        events = []
        onset = int(rng.integers(65,316))
        for _ in range(count):
            code = int(next(codes))
            end = onset+int(rng.integers(*SPANS[code]))
            events.append(dict(code=code,source=str(next(sources[code])),onset=onset,end=end,
                               strength=float(rng.uniform(.7,1.3)),sensors=[2,5]))
            onset = max(onset+46, end+int(rng.integers(30,121)))
        array[i] = gen.simulate(events,np.random.default_rng(child))
        truth.append(events)
    array.flush()
    save(folder/"truth.json", truth)
    save(manifest, dict(records=len(truth),seed=seed,events=total,sites=sites,quiet=n0,
                        singles=n1,doubles=n2,observations=sha(folder/"pmu.npy"),truth=sha(folder/"truth.json")))
    print(split,len(truth),total,flush=True)


def readings(split):
    name = DATA/split/"pmu.npy"
    if load(RESULT/f"{split}_manifest.json")["observations"]!=sha(name):
        raise ValueError("Measurements changed")
    return np.load(name,mmap_mode="r")


def labels(split):
    name = DATA/split/"truth.json"
    if sha(name)!=load(RESULT/f"{split}_manifest.json")["truth"]:
        raise ValueError("Labels changed")
    return load(name)


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("split",choices=DESIGN)
    generate(parser.parse_args().split)

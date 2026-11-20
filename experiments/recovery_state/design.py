"""Prospective four-family evaluation on paired recovery and intervention branches."""
import argparse
from pathlib import Path
import subprocess
import sys
import tempfile

import numpy as np

HERE = Path(__file__).resolve().parent
PREVIOUS = HERE.parent/"graph_intervention"
sys.path.insert(0,str(PREVIOUS))
import common
from common import ROOT, sha, load, save
from cohort import SPANS
from physical import Generator

DATA = ROOT/"tmp/recovery_state"
RESULT = HERE/"results"
MODEL = HERE/"model.npz"
DISC = HERE/"discrepancy.npz"
TREES = HERE/"trees_refit.joblib"
LOCK = RESULT/"freeze.json"
DESIGN = {"train":(6,48,6524381),"dev":(4,48,5784103),"test":(8,192,2390751)}


def held_sites():
    rng = np.random.default_rng(8172109)
    old = set(load(PREVIOUS/"results/freeze.json")["held"])
    with np.load(common.GRAPH/"model.npz") as f:
        codes,sites = f["code"],f["site"]
    held = set()
    for code,count in ((3,3),(4,4),(1,2),(2,8)):
        choices = sorted(set(sites[codes==code])-old-held)
        held.update(map(str,rng.choice(choices,size=count,replace=False)))
    return held


def generate(split,replay=False):
    if split=="test":
        subprocess.run([sys.executable,str(HERE/"study_recovery.py"),"verify"],check=True)
    elif LOCK.exists():
        raise FileExistsError("Development closed")
    path = RESULT/f"{split}_manifest.json"
    if replay and (split!="test" or not path.is_file()):
        raise ValueError("Replay requires the sealed test manifest")
    if path.exists() and not replay:
        raise FileExistsError(path)
    blocks,nquiet,seed=DESIGN[split]
    rng=np.random.default_rng(seed)
    sim=Generator()
    held=held_sites()
    sites={c:sorted(s for s in sim.catalog[c] if (s in held)==(split=="test")) for c in SPANS}
    pools={c:[] for c in SPANS}
    def event(c,start):
        if not pools[c]:
            pools[c]=list(rng.permutation(sites[c]))
        return dict(code=c,source=str(pools[c].pop()),onset=int(start),end=int(start+rng.integers(*SPANS[c])),
                    strength=float(rng.uniform(.7,1.3)),sensors=[2,5])
    rows=[]
    for i in range(nquiet):
        rows.append((f"quiet-{i}",[],int(rng.integers(2**60))))
    for block in range(blocks):
        for c in SPANS:
            e=event(c,rng.integers(65,316))
            rows.append((f"single-{block}-{c}",[e],int(rng.integers(2**60))))
            for d in SPANS:
                first=event(c,rng.integers(65,316))
                second=event(d,max(first["end"]+rng.integers(30,121),first["onset"]+46))
                cluster=f"pair-{block}-{c}-{d}"
                noise=int(rng.integers(2**60))
                rows.extend(((cluster,[first],noise),(cluster,[first,second],noise)))
    if replay and (DATA/split).exists():
        arrays(split)
        arrays(split,True)
        print("Held observations and labels agree with the published hashes.")
        return
    folder=Path(tempfile.mkdtemp(dir=DATA)) if replay else DATA/split
    folder.mkdir(exist_ok=True,parents=True)
    array=np.lib.format.open_memmap(folder/"pmu.npy",mode="w+",dtype="float32",shape=(len(rows),720,8,5))
    names,labels=[],[]
    for i,j in enumerate(rng.permutation(len(rows))):
        name,events,noise=rows[j]
        array[i]=sim.simulate(events,np.random.default_rng(noise))
        names.append(name)
        labels.append(events)
    array.flush()
    del array
    save(folder/"truth.json",labels)
    manifest=dict(seed=seed,records=len(rows),events=sum(map(len,labels)),clusters=names,
                  sites=sites,observations=sha(folder/"pmu.npy"),truth=sha(folder/"truth.json"))
    if replay:
        if manifest!=load(path):
            raise ValueError("Regenerated observations differ from published manifest")
        folder.rename(DATA/split)
    else:
        save(path,manifest)
    print(split,len(rows),sum(map(len,labels)),flush=True)


def arrays(split,truth=False):
    folder=DATA/split
    manifest=load(RESULT/f"{split}_manifest.json")
    path=folder/("truth.json" if truth else "pmu.npy")
    if sha(path)!=manifest["truth" if truth else "observations"]:
        raise ValueError("Input differs from manifest")
    return load(path) if truth else np.load(path,mmap_mode="r",allow_pickle=False)


def bind():
    """Direct the unchanged legacy numerical routines to this trial's independent model artifacts."""
    import operators,discrepancy,intervention_monitor
    common.DATA=DATA
    operators.MODEL=MODEL
    discrepancy.MODEL=MODEL
    discrepancy.FILE=DISC
    intervention_monitor.FILE=DISC
    intervention_monitor.DATA=DATA
    return operators,discrepancy


def train():
    if LOCK.exists() or (DATA/"test").exists():
        raise FileExistsError("Cannot fit after the freeze")
    operators,discrepancy=bind()
    records,events=arrays("train"),arrays("train",True)
    save(RESULT/"calibration.json",operators.fit(records,events))
    discrepancy.fit(records,events)
    operators.cache_bank()


def trees():
    import refit
    refit.DATA,refit.FREEZE,refit.HELD,refit.REFIT,refit.RESULT=DATA,LOCK,held_sites(),TREES,RESULT
    refit.fit()


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage",choices=("train","dev","test","replay-test","model","trees"))
    stage=parser.parse_args().stage
    if stage=="replay-test":
        generate("test",replay=True)
    elif stage in DESIGN:
        generate(stage)
    elif stage=="model":
        train()
    else:
        trees()

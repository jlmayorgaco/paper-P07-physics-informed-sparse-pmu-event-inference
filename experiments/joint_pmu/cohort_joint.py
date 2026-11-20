"""Independent IEEE-39 records with untouched test sources and an isolated simulation process."""
import argparse
import itertools
from pathlib import Path
import subprocess
import sys
import numpy as np

HERE=Path(__file__).resolve().parent
REC=HERE.parent/"recovery_state"
sys.path.insert(0,str(REC))
import design
from design import common,load,save,sha,ROOT,SPANS

DATA=ROOT/"tmp/joint_pmu"
RESULT=HERE/"results"
MODEL=HERE/"model.npz"
DISC=HERE/"discrepancy.npz"
TREES=HERE/"trees_refit.joblib"
LOCK=RESULT/"freeze.json"
SPLITS={"train":(6,48,73019123),"dev":(4,48,40872161),"test":(8,192,91872601)}


def held():
    old=set(load(REC/"results/freeze.json")["held"])|set(load(design.PREVIOUS/"results/freeze.json")["held"])
    rng=np.random.default_rng(1147729)
    result=set()
    with np.load(common.GRAPH/"model.npz") as f:
        for code,count in ((3,3),(4,4),(1,2),(2,8)):
            choices=sorted(set(f["site"][f["code"]==code])-old-result)
            result.update(map(str,rng.choice(choices,count,replace=False)))
    return result


def bind():
    design.DATA,design.RESULT,design.MODEL,design.DISC,design.TREES,design.LOCK=DATA,RESULT,MODEL,DISC,TREES,LOCK
    return design.bind()


def generate(split):
    bind()
    if split=="test":
        subprocess.run([sys.executable,str(HERE/"run_joint.py"),"verify"],check=True)
    elif LOCK.exists() or (DATA/"test").exists():
        raise FileExistsError("Development closed")
    path=RESULT/f"{split}_manifest.json"
    if path.exists():
        raise FileExistsError(path)
    blocks,nquiet,seed=SPLITS[split]
    rng=np.random.default_rng(seed)
    sim=design.Generator()
    reserved=held()
    sites={c:sorted(s for s in sim.catalog[c] if (s in reserved)==(split=="test")) for c in SPANS}
    pools={c:[] for c in SPANS}
    families=[(c,) for c in SPANS]+list(itertools.product(SPANS,repeat=2))
    families+=list(itertools.product((1,2),(1,2),(3,4)))
    schedules=[[] for _ in range(nquiet)]
    for _ in range(blocks):
        for pattern in families:
            row=[]
            onset=int(rng.integers(65,241))
            for c in pattern:
                if not pools[c]:
                    pools[c]=list(rng.permutation(sites[c]))
                end=onset+int(rng.integers(*SPANS[c]))
                row.append(dict(code=c,source=str(pools[c].pop()),onset=onset,end=end,
                                strength=float(rng.uniform(.7,1.3)),sensors=[2,5]))
                onset=max(onset+46,end+int(rng.integers(30,121)))
            schedules.append(row)
    folder=DATA/split
    folder.mkdir(exist_ok=True,parents=True)
    names=rng.permutation(len(schedules))
    truth=[schedules[j] for j in names]
    children=np.random.SeedSequence([seed,392716]).spawn(len(truth))
    arr=np.lib.format.open_memmap(folder/"pmu.npy",mode="w+",dtype="float32",shape=(len(truth),720,8,5))
    for i,(row,child) in enumerate(zip(truth,children,strict=True)):
        arr[i]=sim.simulate(row,np.random.default_rng(child))
    arr.flush()
    del arr
    save(folder/"truth.json",truth)
    save(path,dict(seed=seed,sites=sites,records=len(truth),events=sum(map(len,truth)),
                   observations=sha(folder/"pmu.npy"),truth=sha(folder/"truth.json")))
    print(split,len(truth),sum(map(len,truth)),flush=True)


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("stage",choices=[*SPLITS,"model","trees"])
    stage=p.parse_args().stage
    bind()
    if stage=="model":
        design.train()
    elif stage=="trees":
        import refit
        refit.DATA,refit.FREEZE,refit.HELD,refit.REFIT,refit.RESULT=DATA,LOCK,held(),TREES,RESULT
        refit.fit()
    else:
        generate(stage)

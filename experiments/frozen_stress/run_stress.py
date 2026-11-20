"""Register the design, generate paired observations, seal frozen predictions, then score."""
import argparse
from concurrent.futures import ProcessPoolExecutor,as_completed
from dataclasses import asdict
import hashlib
import os
import subprocess
import sys
import numpy as np
from design_stress import c,HERE,DATA,RESULT,CONDITIONS,SEED,cases,change_timing

LOCK=RESULT/"registration.json"
MANIFEST=RESULT/"observations.json"
PRED=RESULT/"predictions.json"
TRUTH=DATA/"truth.json"


def artifacts():
    files=[*HERE.glob("*.py"),HERE/"PROTOCOL.md",c.LOCK,c.TREES,c.common.FROZEN_TREES]
    return {p.relative_to(c.ROOT).as_posix():c.sha(p) for p in files}


def verify():
    if c.load(LOCK)["files"]!=artifacts():
        raise ValueError("Stress protocol or frozen model changed")
    subprocess.run([sys.executable,str(c.HERE/"run_joint.py"),"verify"],check=True)


def register():
    if LOCK.exists() or MANIFEST.exists() or DATA.exists():
        raise FileExistsError("Design already registered or generated")
    c.save(LOCK,dict(seed=SEED,conditions=[asdict(s) for s in CONDITIONS],files=artifacts()))
    verify()


def init_sim():
    global simulator,maps
    from threadpoolctl import threadpool_limits
    from stress_plant import StressPlant
    threadpool_limits(1)
    simulator=StressPlant()
    maps={s.name:np.load(DATA/(s.name+".npy"),mmap_mode="r+") for s in CONDITIONS}


def simulate(task):
    i,events=task
    opened,rejections=simulator.outages(events,i)
    seed=np.random.SeedSequence([SEED,6719,i])
    results={}
    local={}
    for s in CONDITIONS:
        current=opened[:s.outages]
        row=change_timing(events,s.timing)
        key=(s.outages,s.load,tuple(e["onset"] for e in row))
        if key not in local:
            local[key]=simulator.simulate(row,s.load,current,seed)
        maps[s.name][i]=local[key]
        eq=simulator.equilibrium(s.load,current)
        results[s.name]=[eq.error,float(min(abs(eq.voltage))),float(max(abs(eq.voltage)))]
    if i<5:
        np.testing.assert_array_equal(local[(0,1.,tuple(e["onset"] for e in events))],
                                      simulator.sim.simulate(events,np.random.default_rng(seed)))
    return dict(opened=opened,rejected=rejections,equilibria=results)


def generate(workers):
    verify()
    if MANIFEST.exists() or PRED.exists():
        raise FileExistsError("Observations already sealed")
    DATA.mkdir(exist_ok=True,parents=True)
    rows=cases()
    for s in CONDITIONS:
        mem=np.lib.format.open_memmap(DATA/(s.name+".npy"),mode="w+",dtype="float32",shape=(len(rows),720,8,5))
        del mem
    with ProcessPoolExecutor(workers,initializer=init_sim) as pool:
        logs=list(pool.map(simulate,enumerate(rows),chunksize=2))
    truth={t:[change_timing(r,t) for r in rows] for t in sorted({s.timing for s in CONDITIONS})}
    c.save(TRUTH,truth)
    c.save(RESULT/"equilibria.json",logs)
    c.save(MANIFEST,dict(records=len(rows),events=sum(map(len,rows)),truth=c.sha(TRUTH),
                         registration=c.sha(LOCK),equilibria=c.sha(RESULT/"equilibria.json"),
                         observations={s.name:c.sha(DATA/(s.name+".npy")) for s in CONDITIONS}))
    print("Generated",len(CONDITIONS),"conditions of",len(rows),"records",flush=True)


def init_monitor():
    global first,cfg,trees,arrays
    import joblib
    from threadpoolctl import threadpool_limits
    from apply_joint import frozen_observer
    threadpool_limits(1)
    first=frozen_observer()
    cfg=c.load(c.LOCK)["config"]
    trees=[joblib.load(p) for p in (c.common.FROZEN_TREES,c.TREES)]
    arrays={s.name:np.load(DATA/(s.name+".npy"),mmap_mode="r") for s in CONDITIONS}


def run_one(task):
    from joint_observer import JointObserver
    from study import supervised
    name,i=task
    raw=arrays[name][i]
    obs=JointObserver(first.bank,first.model,cfg,first.physics)
    return dict(joint=[a for frame in raw for a in obs.step(frame)],
                trees=supervised(raw,trees[0]),trees_refit=supervised(raw,trees[1]))


def predict(workers):
    verify()
    receipt=c.load(MANIFEST)
    if receipt["registration"]!=c.sha(LOCK) or PRED.exists():
        raise ValueError("Invalid observation manifest or predictions already sealed")
    by_digest={}
    for s in CONDITIONS:
        path=DATA/(s.name+".npy")
        if c.sha(path)!=receipt["observations"][s.name]:
            raise ValueError("Observation mismatch")
        raw=np.load(path,mmap_mode="r")
        for i,row in enumerate(raw):
            key=hashlib.sha256(row).hexdigest()
            by_digest.setdefault(key,[]).append((s.name,i))
    # Cache only exact PMU matches. No schedule, condition identity or index
    # is passed into any estimator, including on records with identical inputs.
    cache=DATA/("cache_"+c.sha(LOCK)[:12])
    cache.mkdir(exist_ok=True)
    jobs=[(k,v[0]) for k,v in by_digest.items() if not (cache/(k+".json")).exists()]
    np.random.default_rng(743144).shuffle(jobs)
    with ProcessPoolExecutor(workers,initializer=init_monitor) as pool:
        futures={pool.submit(run_one,item):key for key,item in jobs}
        for n,future in enumerate(as_completed(futures),1):
            key=futures[future]
            temp=cache/(key+".partial")
            c.save(temp,future.result())
            temp.replace(cache/(key+".json"))
            if n%150==0:
                print("PMU replay",n,"/",len(jobs),flush=True)
    result={s.name:{m:[None]*receipt["records"] for m in ("joint","trees","trees_refit")} for s in CONDITIONS}
    for key,items in by_digest.items():
        predictions=c.load(cache/(key+".json"))
        for arm,i in items:
            for m,p in predictions.items():
                result[arm][m][i]=p
    c.save(PRED,result)
    c.save(RESULT/"seal.json",dict(registration=c.sha(LOCK),observations=c.sha(MANIFEST),predictions=c.sha(PRED),
                                  unique_pmu_records=len(by_digest)))
    print("Prediction seal",c.sha(PRED),flush=True)


def score():
    from score_stress import bootstrap,intervals,summary
    verify()
    seal=c.load(RESULT/"seal.json")
    if (seal["registration"],seal["observations"],seal["predictions"])!=(c.sha(LOCK),c.sha(MANIFEST),c.sha(PRED)):
        raise ValueError("Prediction seal mismatch")
    if c.sha(TRUTH)!=c.load(MANIFEST)["truth"]:
        raise ValueError("Truth mismatch")
    labels=c.load(TRUTH)
    pred=c.load(PRED)
    w=bootstrap(labels["reference"])
    totals={}
    for s in CONDITIONS:
        data,boot={},{}
        for name,p in pred[s.name].items():
            data[name],boot[name]=summary(labels[s.timing],p,w)
        if s.name=="reference":
            reference=boot["joint"]
        data["joint"]["delta_vs_reference_ci95"]=intervals(boot["joint"]-reference)
        data["joint"]["delta_vs_trees_ci95"]={k:intervals(boot["joint"]-boot[k]) for k in ("trees","trees_refit")}
        totals[s.name]=data
    c.save(RESULT/"test_truth.json",labels)
    c.save(RESULT/"scores.json",totals)


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage",choices=("register","verify","generate","predict","score"))
    parser.add_argument("--workers",type=int,default=10)
    args=parser.parse_args()
    if args.stage in ("generate","predict"):
        {"generate":generate,"predict":predict}[args.stage](args.workers)
    else:
        {"register":register,"verify":verify,"score":score}[args.stage]()

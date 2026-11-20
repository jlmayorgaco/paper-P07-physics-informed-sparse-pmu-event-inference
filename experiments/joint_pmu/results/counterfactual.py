"""After unsealing, remove the last intervention and replay the frozen PMU-only monitor."""
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import sys
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
import cohort_joint as c
from apply_joint import frozen_observer
from joint_observer import JointObserver


def init():
    global sim,first,config,original
    from threadpoolctl import threadpool_limits
    threadpool_limits(1)
    sim=c.design.Generator()
    first=frozen_observer()
    config=c.load(c.LOCK)["config"]
    original=np.load(c.DATA/"test/pmu.npy",mmap_mode="r")


def replay(task):
    i,events,child,previous=task
    cut=events[-1]["onset"]
    raw=sim.simulate(events[:-1],np.random.default_rng(child))
    if raw[:cut].tobytes()!=original[i,:cut].tobytes():
        raise ValueError("Twin PMU prefix differs")
    obs=JointObserver(first.bank,first.model,config,first.physics)
    alerts=[a for frame in raw for a in obs.step(frame)]
    if [a for a in previous if a["detected"]<cut]!=[a for a in alerts if a["detected"]<cut]:
        raise ValueError("Causal alarm prefix differs")
    return i,alerts


if __name__=="__main__":
    manifest=c.load(HERE/"test_manifest.json")
    truth=c.load(HERE/"test_truth.json")
    if c.sha(HERE/"test_truth.json")!=manifest["truth"] or c.sha(c.DATA/"test/pmu.npy")!=manifest["observations"]:
        raise ValueError("Unverified input")
    published=c.load(HERE/"predictions.json")["joint"]
    children=np.random.SeedSequence([manifest["seed"],392716]).spawn(len(truth))
    selected=[i for i,r in enumerate(truth) if len(r)==3 or
              (len(r)==2 and r[0]["code"] in (1,2) and r[1]["code"] in (3,4))]
    with ProcessPoolExecutor(8,initializer=init) as pool:
        pred=dict(pool.map(replay,((i,truth[i],children[i],published[i]) for i in selected)))
    from trial import metrics
    strata={}
    for n in (2,3):
        ids=[i for i in selected if len(truth[i])==n]
        strata[str(n)]=metrics([truth[i][:-1] for i in ids],[pred[i] for i in ids])
    c.save(HERE/"counterfactual.json",dict(results=strata,predictions=pred,freeze=c.sha(c.LOCK)))
    print({k:(s["events"],s["joint"],s["extras"]) for k,s in strata.items()})

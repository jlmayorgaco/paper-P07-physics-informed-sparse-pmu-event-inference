"""Paired development experiment with oracle prior histories and genuine third interventions."""
from concurrent.futures import ProcessPoolExecutor
import argparse
from pathlib import Path
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
import diagnose
from diagnose import design,SensorAblation,classify
from intervention_monitor import Observer
from operators import TAIL,stream


def scenarios():
    sites=design.load(design.RESULT/"train_manifest.json")["sites"]
    rng=np.random.default_rng(53869201)
    def event(code,t):
        return dict(code=code,source=str(rng.choice(sites[str(code)])),onset=t,
                    end=t+int(rng.integers(*design.SPANS[code])),strength=float(rng.uniform(.7,1.3)),sensors=[2,5])
    tasks=[]
    for block in range(4):
        for code1 in (1,2):
            for code2 in (1,2):
                for code3 in (3,4):
                    e1=event(code1,int(rng.integers(65,145)))
                    e2=event(code2,e1["end"]+int(rng.integers(35,91)))
                    gap=rng.integers(30,61) if block%2==0 else rng.integers(155,186)
                    e3=event(code3,e2["end"]+int(gap))
                    tasks.append(([e1,e2,e3],int(rng.integers(2**60))))
    return tasks


def init():
    global plant,bank,model,config
    from threadpoolctl import threadpool_limits
    threadpool_limits(1)
    plant=design.Generator()
    first=diagnose.frozen_observer()
    bank,model=first.bank,first.model
    config=design.load(design.LOCK)["config"]
    config=dict(config,log_gate=config["post_gate"])


def scan(z,start):
    # The three arms get identical side information. Only their no-new-event
    # forecast differs. Detection reuses the frozen innovation likelihood.
    observer=Observer(bank,model,config)
    alarms=[]
    for k in range(start,len(z)):
        observer.k=k
        alarms.extend(observer._scan(z[k],1.))
    return alarms


def experiment(task):
    events,seed=task
    e1,e2,e3=events
    def simulate(episodes,clean=False):
        rng=np.random.default_rng(seed)
        if clean:
            rng=SensorAblation(rng.bit_generator.state)
        return plant.simulate(episodes,rng)
    def innovations(episodes):
        return stream(simulate(episodes,True),model)[0]
    z1=innovations([e1])
    z2=innovations([e2])
    both=innovations([e1,e2])
    truncated=z2.copy()
    truncated[e2["onset"]+TAIL:]=0.
    means={"separate_truncated":z1+truncated,"separate_full":z1+z2,"joint_full":both}
    control=simulate(events[:2])
    case=simulate(events)
    if control[:e3["onset"]].tobytes()!=case[:e3["onset"]].tobytes():
        raise ValueError("Branches differ before the third intervention")
    zc,za=stream(control,model)[0],stream(case,model)[0]
    start=e2["onset"]+3
    results={}
    for name,mean in means.items():
        quiet=scan(zc-mean,start)
        positive=scan(za-mean,start)
        if [a for a in quiet if a["detected"]<e3["onset"]]!=[a for a in positive if a["detected"]<e3["onset"]]:
            raise ValueError("Alarm before the split differs")
        results[name]=dict(control=classify(quiet,[]),case=classify(positive,[e3]),
                           rms_control=float(np.mean((zc[start:]-mean[start:])**2)**.5))
    return dict(events=events,seed=seed,results=results)


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers",type=int,default=6)
    args=parser.parse_args()
    tasks=scenarios()
    with ProcessPoolExecutor(args.workers,initializer=init) as pool:
        rows=list(pool.map(experiment,tasks))
    totals={}
    for name in rows[0]["results"]:
        results=[r["results"][name] for r in rows]
        totals[name]=dict(pairs=len(rows),control_extras=sum(len(r["control"]["extras"]) for r in results),
                          case_extras=sum(len(r["case"]["extras"]) for r in results),
                          third_joint=sum(r["case"]["joint"][0] for r in results),
                          third_joint_by_code={str(c):sum(r["results"][name]["case"]["joint"][0]
                                for r in rows if r["events"][2]["code"]==c) for c in (3,4)})
    design.save(diagnose.HERE/"feasibility.json",dict(seed=53869201,totals=totals,rows=rows))
    print(totals,flush=True)

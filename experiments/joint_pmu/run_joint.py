"""Fit operating points on development, freeze, predict from PMUs, then unseal truth."""
import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import joblib
import numpy as np
import cohort_joint as c
from joint_observer import JointObserver
from joint_physics import Physics
from intervention_monitor import Bank
from recovery import RecoveryObserver,Dynamics
from study import supervised
from trial import metrics
from score_recovery import draws


def initialize(split):
    global records,model,bank,physics,older,trees,archived_recovery
    from threadpoolctl import threadpool_limits
    threadpool_limits(1)
    c.bind()
    records=np.load(c.DATA/split/"pmu.npy",mmap_mode="r",allow_pickle=False)
    with np.load(c.MODEL) as f:
        model=dict(f)
    bank=Bank()
    physics=Physics(model)
    older=Dynamics(model)
    trees=None
    archived_recovery=None


def worker(task):
    global trees,archived_recovery
    idx,name,cfg=task
    if name=="trees":
        if trees is None:
            trees=[joblib.load(p) for p in (c.common.FROZEN_TREES,c.TREES)]
        return [supervised(records[idx],m) for m in trees]
    if name=="archived":
        if archived_recovery is None:
            from unittest.mock import patch
            import intervention_monitor as im
            with patch.object(im,"DATA",c.ROOT/"tmp/recovery_state"),patch.object(im,"FILE",c.REC/"discrepancy.npz"):
                archived_bank=Bank()
            with np.load(c.REC/"model.npz") as arc:
                archived_model=dict(arc)
            archived_recovery=(archived_bank,archived_model,Dynamics(archived_model))
        b,m,p=archived_recovery
        obs=RecoveryObserver(b,m,cfg,p)
    elif name=="previous":
        obs=RecoveryObserver(bank,model,cfg,older)
    else:
        obs=JointObserver(bank,model,cfg,physics)
    return [a for row in records[idx] for a in obs.step(row)]


def predict_set(split,options):
    c.bind()
    n=len(c.design.arrays(split))
    results={}
    with ProcessPoolExecutor(int(os.environ.get("P07_WORKERS","8")),initializer=initialize,
                             initargs=(split,)) as pool:
        for name,cfg in options.items():
            inputs=[c.sha(c.RESULT/(split+"_manifest.json")),cfg,c.sha(c.MODEL),c.sha(c.DISC),c.sha(c.TREES)]
            if name not in ("previous","trees","archived"):
                inputs.extend(c.sha(p) for p in (c.HERE/"joint_observer.py",c.HERE/"joint_physics.py"))
            token=hashlib.sha256(json.dumps(inputs,sort_keys=True).encode()).hexdigest()[:16]
            cache=c.DATA/f"dev_{name}_{token}.json"
            if split=="dev" and cache.exists():
                rows=c.load(cache)
            else:
                rows=list(pool.map(worker,((i,name,cfg) for i in range(n)),chunksize=1))
                if split=="dev":
                    c.save(cache,rows)
            if name=="trees":
                results["trees"],results["trees_refit"]=map(list,zip(*rows))
            else:
                results[name]=rows
            print(split,name,n,flush=True)
    return results


def report(truth,pred):
    out=metrics(truth,pred)
    target={str(c):[0,0] for c in (3,4)}
    third=[0,0]
    seconds=[0,0]
    for row,alarms in zip(truth,pred,strict=True):
        for j,event in enumerate(row[1:],1):
            a=next((a for a in alarms if 0<=a["detected"]-event["onset"]<=45),None)
            good=bool(a and a["published"] is not None and a["published"]<=event["onset"]+45
                      and (a["code"],a["source"])==(event["code"],event["source"]))
            group=seconds if j==1 else third
            group[0]+=good
            group[1]+=1
            if j==1 and row[0]["code"] in (1,2) and event["code"] in (3,4):
                counts=target[str(event["code"])]
                counts[0]+=good
                counts[1]+=1
    out.update(target=target,all_second=seconds,all_third=third)
    return out


def hashes():
    # Register the common simulator, scorer, and archive input revisions from the
    # preceding trial, independently of any thresholds or learned weights in it.
    old=c.load(c.REC/"results/freeze.json")["files"]
    archive=Path(os.environ["P07_SCIENCE_ARCHIVE"])
    sources={}
    for name in old:
        if name.startswith("archive/"):
            sources[name]=c.sha(archive/name.removeprefix("archive/"))
        elif name.endswith(".py") or name in (c.common.GRAPH.relative_to(c.ROOT).as_posix()+"/model.npz",
                                               c.common.FROZEN_TREES.relative_to(c.ROOT).as_posix()):
            sources[name]=c.sha(c.ROOT/name)
    fixed=[*c.HERE.glob("*.py"),c.HERE/"PROTOCOL.md",c.MODEL,c.DISC,c.TREES,
           c.REC/"results/freeze.json",c.REC/"model.npz",c.REC/"discrepancy.npz",
           c.ROOT/"tmp/recovery_state/bank/inputs.json",c.design.PREVIOUS/"results/freeze.json",
           *[c.RESULT/p for p in ("development.json","tree_fit.json","train_manifest.json","dev_manifest.json","calibration.json")],
           c.DATA/"bank/inputs.json"]
    sources.update({p.relative_to(c.ROOT).as_posix():c.sha(p) for p in fixed})
    return sources


def verify():
    operators,_=c.bind()
    operators.cache_bank()
    old_bank=c.ROOT/"tmp/recovery_state/bank"
    if not (old_bank/"inputs.json").exists():
        subprocess.run([sys.executable,str(c.REC/"study_recovery.py"),"verify"],check=True)
    f=c.load(c.LOCK)
    if f["files"]!=hashes():
        raise ValueError("Freeze verification failed")
    for name,digest in c.load(old_bank/"inputs.json")["arrays"].items():
        if c.sha(old_bank/(name+".npy"))!=digest:
            raise ValueError("Historical comparator bank changed")
    return f


def develop(freeze):
    c.bind()
    if c.LOCK.exists() or (c.DATA/"test").exists():
        raise FileExistsError("Development closed")
    y=c.design.arrays("dev",True)
    train=c.design.arrays("train",True)
    refit=c.load(c.RESULT/"tree_fit.json")
    seen=set().union(*refit["labels_by_family"].values())|{e["source"] for row in train+y for e in row}
    if c.held() & seen:
        raise ValueError("Reserved site in training or development labels")
    base=dict(c.load(c.REC/"results/freeze.json")["config"],hazard=sum(map(len,train))/(690*len(train)))
    configs={f"J{g}":dict(base,log_gate=g,post_gate=g) for g in (15,35,75,130,200)}
    opts=dict(trees=None,previous=base,**configs)
    scores={k:report(y,p) for k,p in predict_set("dev",opts).items()}
    budget=min(scores[name]["extras"] for name in ("trees","trees_refit"))
    def rank(name):
        s=scores[name]
        floor=min(s["macro_f1"],s["family"]/s["events"],s["exact_site"]/s["events"])
        target=sum(a for a,b in s["target"].values())
        return (max(0,s["extras"]-budget),-target,-floor,-s["macro_f1"],s["extras"])
    best=min(configs,key=rank)
    c.save(c.RESULT/"development.json",scores)
    print("Development",best,{k:(round(s["macro_f1"],4),s["exact_site"],s["extras"],s["target"])
                               for k,s in scores.items()},flush=True)
    if freeze:
        c.save(c.LOCK,dict(chosen=best,config=configs[best],previous=base,held=sorted(c.held()),
                           budget=budget,files=hashes()))


def predict():
    f=verify()
    path=c.RESULT/"predictions.json"
    if path.exists():
        raise FileExistsError("Predictions already sealed")
    old_cfg=c.load(c.REC/"results/freeze.json")["config"]
    result=predict_set("test",dict(joint=f["config"],previous=f["previous"],trees=None,archived=old_cfg))
    c.save(path,result)
    c.save(c.RESULT/"seal.json",dict(predictions=c.sha(path),freeze=c.sha(c.LOCK),manifest=c.sha(c.RESULT/"test_manifest.json")))


def score():
    f=verify()
    path=c.RESULT/"predictions.json"
    man=c.RESULT/"test_manifest.json"
    if c.load(c.RESULT/"seal.json")!=dict(predictions=c.sha(path),freeze=c.sha(c.LOCK),manifest=c.sha(man)):
        raise ValueError("Invalid seal")
    truth=c.design.arrays("test",True)
    if {e["source"] for row in truth for e in row}!=set(f["held"]):
        raise ValueError("Missing held assets")
    predictions=c.load(path)
    n=len(truth)
    weights=np.random.default_rng(230721).multinomial(n,np.full(n,1/n),size=4000)
    out,boot={},{}
    for name,p in predictions.items():
        out[name]=report(truth,p)
        boot[name]=draws(truth,p,np.arange(n),weights)
    keys=["macro_f1","family_fraction","site_fraction","joint_fraction","extras"]
    def ci(sample):
        return dict(zip(keys,np.quantile(sample,[.025,.975],axis=0).T.tolist()))
    out["joint"]["ci95"]=ci(boot["joint"])
    out["joint"]["paired_ci95"]={k:ci(boot["joint"]-v) for k,v in boot.items() if k!="joint"}
    c.save(c.RESULT/"test_truth.json",truth)
    c.save(c.RESULT/"scores.json",out)
    print({k:(s["macro_f1"],s["family"],s["exact_site"],s["extras"],s["target"],s["all_third"]) for k,s in out.items()})


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("stage",choices=["dev","freeze","verify","predict","score"])
    stage=p.parse_args().stage
    if stage in ("dev","freeze"):
        develop(stage=="freeze")
    else:
        {"verify":verify,"predict":predict,"score":score}[stage]()

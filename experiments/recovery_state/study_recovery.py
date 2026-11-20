"""Freeze development selection before generation. Predict on PMUs before opening labels."""
import argparse
from concurrent.futures import ProcessPoolExecutor
import os
import hashlib
import json
from pathlib import Path
import numpy as np
import joblib
import design
from design import HERE, PREVIOUS, DATA, RESULT, MODEL, TREES, DISC, LOCK, ROOT, load, save, sha
from common import GRAPH, SUP, FROZEN_TREES
from intervention_monitor import Bank, run
from recovery import Dynamics, monitor
from study import supervised
from trial import metrics


def worker_init(split):
    global bank,model,physics,records,tree_models,threads
    from threadpoolctl import threadpool_limits
    threads=threadpool_limits(limits=1)
    design.bind()
    bank=Bank()
    with np.load(MODEL) as f:
        model=dict(f)
    physics=Dynamics(model)
    records=np.load(DATA/split/"pmu.npy",mmap_mode="r")
    tree_models=None


def worker(task):
    global tree_models
    i,name,cfg=task
    if name=="trees":
        if tree_models is None:
            tree_models=[joblib.load(p) for p in (FROZEN_TREES,TREES)]
        return [supervised(records[i],t) for t in tree_models]
    if name=="previous":
        return run(records[i],bank,model,cfg)
    return monitor(records[i],bank,model,cfg,physics)


def paths():
    names=[*HERE.glob("*.py"),HERE/"PROTOCOL.md",MODEL,TREES,DISC,GRAPH/"model.npz",FROZEN_TREES,
           *PREVIOUS.glob("*.py"),PREVIOUS/"operating/freeze.json",PREVIOUS/"results/freeze.json",
           GRAPH/"physical.py",GRAPH/"estimator.py",GRAPH/"evaluate.py",GRAPH/"study.py",
           SUP/"plant.py",SUP/"larger.py",SUP/"learner.py",SUP/"online.py",
           HERE.parent/"branch_current_trial/run.py",HERE.parent/"history_conditioning/dynamics.py",
           HERE.parent/"dynamic_site_trial/trial.py",
           *[RESULT/p for p in ("tree_fit.json","train_manifest.json","dev_manifest.json","calibration.json",
                                "development.json")],DATA/"bank/inputs.json"]
    files={p.relative_to(ROOT).as_posix():sha(p) for p in names}
    archive=Path(os.environ["P07_SCIENCE_ARCHIVE"])
    run=archive/"experiments/PAPER_CALIBRATION_B01/run"
    reference=run/"engine_clean/reference"
    external=[archive/"experiments/PAPER_ALLEVENTS_V1/physics/network.py",
              archive/"data/topology/ieee39/ybus_full_complex.csv",
              archive/"data/topology/ieee39/branches_physical.csv",
              archive/"data/metadata/IEEE_39_Bus_Power_System.raw",
              run/"runtime/model/dae/measurement_network.json",
              *[reference/p for p in ("terminal_mapping.csv","reporting_config.json","data/bus.csv",
                 "data/branch.csv","stochastic_model.json","noise.py","pmu_operator.py")]]
    files.update({"archive/"+p.relative_to(archive).as_posix():sha(p) for p in external})
    return files


def verify():
    frozen=load(LOCK)
    if not (DATA/"bank/inputs.json").is_file():
        operators,_=design.bind()
        operators.cache_bank()
    if paths()!=frozen["files"]:
        raise ValueError("Frozen inputs or code changed")
    for key,digest in load(DATA/"bank/inputs.json")["arrays"].items():
        if sha(DATA/"bank"/(key+".npy"))!=digest:
            raise ValueError("Template bank changed: "+key)
    return frozen


def predictions(split,options):
    n=len(design.arrays(split))
    outputs={}
    with ProcessPoolExecutor(int(os.environ.get("P07_WORKERS","8")),initializer=worker_init,
                             initargs=(split,)) as pool:
        for name,cfg in options.items():
            deps=[MODEL,DISC,PREVIOUS/"intervention_monitor.py",PREVIOUS/"operators.py"]
            if name=="trees":
                deps=[TREES,FROZEN_TREES,GRAPH/"study.py"]
            elif name!="previous":
                deps.append(HERE/"recovery.py")
            identity=[sha(RESULT/"dev_manifest.json"),cfg,*[sha(p) for p in deps]]
            token=hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()[:16]
            partial=DATA/f"dev_{name}_{token}.json"
            if split=="dev" and partial.exists():
                outputs[name]=load(partial)
                continue
            p=list(pool.map(worker,((i,name,cfg) for i in range(n)),chunksize=2))
            outputs[name]=p
            if split=="dev":
                save(partial,p)
            print(split,name,n,flush=True)
    outputs["trees"],outputs["trees_refit"]=map(list,zip(*outputs["trees"]))
    return outputs


def fit():
    if LOCK.exists() or (DATA/"test").exists():
        raise FileExistsError("Development closed")
    y=design.arrays("dev",True)
    train=design.arrays("train",True)
    held=design.held_sites()
    seen=set().union(*load(RESULT/"tree_fit.json")["labels_by_family"].values())
    if held & (seen|{e["source"] for row in y+train for e in row}|set(load(PREVIOUS/"results/freeze.json")["held"])):
        raise ValueError("Held labels overlap training or previous test")
    base=dict(load(PREVIOUS/"operating/freeze.json")["config"],hazard=sum(map(len,train))/(len(train)*690))
    candidates={f"R{g}":dict(base,post_gate=g) for g in (50,100,200)}
    p=predictions("dev",dict(trees=None,previous=base,**candidates))
    scores={k:metrics(y,v) for k,v in p.items()}
    budget=min(scores[k]["extras"] for k in ("trees","trees_refit"))
    quiet=min(scores[k]["quiet_extras"] for k in ("trees","trees_refit"))
    def priority(k):
        s=scores[k]
        worst=min(s["macro_f1"],s["family"]/s["events"],s["exact_site"]/s["events"])
        return max(0,s["quiet_extras"]-quiet),max(0,s["extras"]-budget),-worst,-s["macro_f1"],-s["joint"]
    best=min(candidates,key=priority)
    save(RESULT/"development.json",scores)
    save(LOCK,dict(chosen=best,config=candidates[best],previous=base,budget=budget,quiet_budget=quiet,
                   held=sorted(held),files=paths()))
    print("Development:",best,{k:(s["macro_f1"],s["family"],s["exact_site"],s["extras"])
                               for k,s in scores.items()},flush=True)


def predict():
    f=verify()
    path=RESULT/"predictions.json"
    if path.exists():
        raise FileExistsError("Blind predictions sealed")
    pred=predictions("test",dict(recovery=f["config"],previous=f["previous"],trees=None))
    save(path,pred)
    save(RESULT/"seal.json",dict(predictions=sha(path),freeze=sha(LOCK),manifest=sha(RESULT/"test_manifest.json")))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage",choices=["fit","verify","predict","score"])
    stage=parser.parse_args().stage
    if stage=="verify":
        verify()
    elif stage=="score":
        from score_recovery import score
        score()
    elif stage=="fit":
        fit()
    else:
        predict()

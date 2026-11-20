"""Extend the decision threshold on development before any blind stream exists."""
import argparse
from concurrent.futures import ProcessPoolExecutor
import os
from pathlib import Path
import sys

import numpy as np

OUT = Path(__file__).resolve().parent
sys.path.insert(0,str(OUT.parent))
from common import DATA, FREEZE, RESULT, load, save, sha, verify
from cohort import labels, readings
from operators import cache_bank
from trial import draws, metrics, worker, worker_init

POINT = OUT/"freeze.json"


def forecasts(split,configs):
    n = len(readings(split))
    cache_bank()
    result = {}
    with ProcessPoolExecutor(int(os.environ.get("P07_WORKERS","8")),initializer=worker_init,
                             initargs=(split,)) as pool:
        for name,cfg in configs.items():
            result[name] = list(pool.map(worker,((i,cfg) for i in range(n)),chunksize=2))
            print(split,name,flush=True)
    return result


def select():
    if POINT.exists() or (DATA/"test").exists():
        raise FileExistsError("Decision calibration must precede test generation")
    base = verify()
    configs = {f"L{t}":dict(base["config"],log_gate=t) for t in (130.,160.,200.,250.,320.,400.)}
    y = labels("dev")
    dev = {k:metrics(y,v) for k,v in forecasts("dev",configs).items()}
    dev["initial"]=load(RESULT/"development.json")[base["chosen"]]
    configs["initial"]=base["config"]
    def preference(k):
        s = dev[k]
        return (max(0,s["quiet_extras"]-base["quiet_budget"]),max(0,s["extras"]-base["budget"]),
                -s["macro_f1"],-s["joint"],configs[k]["log_gate"])
    primary = min(dev,key=preference)
    save(OUT/"development.json",dev)
    save(POINT,dict(primary=primary,config=configs[primary],base=sha(FREEZE),source=sha(Path(__file__)),
                    protocol=sha(OUT/"PROTOCOL.md"),development=sha(OUT/"development.json")))
    print("primary",primary,dev[primary]["macro_f1"],dev[primary]["exact_site"],dev[primary]["extras"])


def frozen():
    verify()
    p = load(POINT)
    if (p["base"],p["source"],p["protocol"],p["development"])!=(
            sha(FREEZE),sha(Path(__file__)),sha(OUT/"PROTOCOL.md"),sha(OUT/"development.json")):
        raise ValueError("Publication rule or protocol differs from freeze")
    return p


def predict():
    point=frozen()
    path=OUT/"predictions.json"
    if path.exists():
        raise FileExistsError("Primary already sealed")
    result=forecasts("test",{"graph":point["config"]})
    save(path,result["graph"])
    save(OUT/"seal.json",dict(primary=sha(POINT),manifest=sha(RESULT/"test_manifest.json"),predictions=sha(path)))


def score():
    frozen()
    path=OUT/"predictions.json"
    if load(OUT/"seal.json")!=dict(primary=sha(POINT),manifest=sha(RESULT/"test_manifest.json"),predictions=sha(path)):
        raise ValueError("Primary seal changed")
    if sha(RESULT/"predictions.json")!=load(RESULT/"seal.json")["predictions"]:
        raise ValueError("Comparator seal changed")
    y=labels("test")
    alarms=load(path)
    ref=load(RESULT/"predictions.json")
    r=metrics(y,alarms)
    indices=np.random.default_rng(652951).integers(len(y),size=(4000,len(y)))
    proposed=draws(y,alarms,indices)
    r["paired_ci95"]={other:dict(zip(("macro_f1","exact_site_fraction","joint_fraction","extra_count"),
                 np.quantile(proposed-draws(y,ref[other],indices),[.025,.975],axis=0).T.tolist()))
                 for other in ("trees","trees_refit")}
    save(OUT/"scores.json",r)
    print("primary",r["macro_f1"],r["exact_site"],r["extras"])


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage",choices=("fit","predict","score"))
    stage=parser.parse_args().stage
    {"fit":select,"predict":predict,"score":score}[stage]()

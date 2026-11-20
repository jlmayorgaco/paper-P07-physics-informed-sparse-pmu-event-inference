"""Development selection, independent predictions, and paired scoring for intervention evidence."""
import argparse
from concurrent.futures import ProcessPoolExecutor
import os

import joblib
import numpy as np

from common import DATA, FREEZE, FROZEN_TREES, GRAPH, HELD, MODEL, REFIT, RESULT, artifacts, load, save, sha, verify
from cohort import labels, readings
from evaluate import evaluate
from intervention_monitor import Bank, run
from operators import cache_bank
from study import supervised


def worker_init(split):
    global bank,model,streams,tree_models,threads
    from threadpoolctl import threadpool_limits
    threads = threadpool_limits(limits=1)
    bank = Bank()
    with np.load(MODEL) as f:
        model = dict(f)
    streams = np.load(DATA/split/"pmu.npy",mmap_mode="r")
    tree_models = None


def worker(task):
    global tree_models
    i,cfg = task
    if cfg is None:
        if tree_models is None:
            tree_models = (joblib.load(FROZEN_TREES),joblib.load(REFIT))
        return [supervised(streams[i],t) for t in tree_models]
    return run(streams[i],bank,model,cfg)


def predictions(split,configs):
    n = len(readings(split))
    cache_bank()
    result = {}
    with ProcessPoolExecutor(int(os.environ.get("P07_WORKERS","8")),initializer=worker_init,
                             initargs=(split,)) as workers:
        ref = list(workers.map(worker,((i,None) for i in range(n)),chunksize=2))
        result["trees"], result["trees_refit"] = map(list,zip(*ref))
        for name,cfg in configs.items():
            result[name] = list(workers.map(worker,((i,cfg) for i in range(n)),chunksize=2))
            print(split,name,n,flush=True)
    return result


def tally(truth,alarms):
    # [site alone, both, events, extras, completely quiet extras, second both, second events]
    out = np.zeros(7,dtype=int)
    for events,row in zip(truth,alarms,strict=True):
        used = set()
        for j,e in enumerate(events):
            found = next((i for i,a in enumerate(row) if i not in used and
                          0<=a["detected"]-e["onset"]<=45),None)
            out[2]+=1
            out[6]+=j==1
            if found is None:
                continue
            used.add(found)
            a = row[found]
            right = a["published"] is not None and a["published"]-e["onset"]<=45 and a["source"]==e["source"]
            both = right and a["code"]==e["code"]
            out[0]+=right
            out[1]+=both
            out[5]+=bool(j==1 and both)
        out[3]+=len(row)-len(used)
        out[4]+=len(row) if not events else 0
    return out


def metrics(truth,alarms):
    res = evaluate(truth,alarms)
    site,joint,n,extras,quiet,second,total = tally(truth,alarms).tolist()
    if (joint,n,extras,quiet)!=(res["joint"],res["events"],res["extras"],res["quiet_extras"]):
        raise ValueError("Inconsistent episode matching")
    return dict(**res,exact_site=site,second_joint=[second,total])


def select():
    if FREEZE.exists() or (DATA/"test").exists():
        raise FileExistsError("Test must follow development freeze")
    dev,train = labels("dev"),labels("train")
    history = load(RESULT/"tree_fit.json")
    seen = set().union(*history["labels_by_family"].values())
    if HELD & (seen|{e["source"] for r in dev+train for e in r}):
        raise ValueError("Held-out source labels used for fitting")
    old = load(GRAPH/"episode_confirmation/test_truth.json")
    if HELD & {e["source"] for r in old for e in r}:
        raise ValueError("Selection overlaps the preceding test sites")
    hazard = sum(map(len,train))/(len(train)*690)
    configs = {f"L{level}_P{int(prob*100)}":dict(log_gate=level,identify=prob,hazard=hazard)
               for level in (6.,16.,35.,65.,100.) for prob in (.60,.95)}
    pred = predictions("dev",configs)
    scored = {k:metrics(dev,v) for k,v in pred.items()}
    budget = min(scored[k]["extras"] for k in ("trees","trees_refit"))
    quiet_budget = min(scored[k]["quiet_extras"] for k in ("trees","trees_refit"))
    def preference(name):
        s = scored[name]
        return (max(0,s["quiet_extras"]-quiet_budget), max(0,s["extras"]-budget),
                -s["macro_f1"],-s["joint"],s["extras"])
    chosen = min(configs,key=preference)
    best_f1 = max(configs,key=lambda k:(scored[k]["macro_f1"],scored[k]["joint"],-scored[k]["extras"]))
    save(RESULT/"development.json",scored)
    save(FREEZE,dict(chosen=chosen,config=configs[chosen],f1_name=best_f1,f1_config=configs[best_f1],
                     budget=budget,quiet_budget=quiet_budget,held=sorted(HELD),
                     dev_exceeds_budget=scored[chosen]["extras"]>budget,
                     files=artifacts(),development=sha(RESULT/"development.json")))
    print("selected",chosen,best_f1,budget,scored[chosen]["macro_f1"],scored[chosen]["extras"],flush=True)


def predict():
    cfg = verify()
    path = RESULT/"predictions.json"
    if path.exists():
        raise FileExistsError("Blind predictions already sealed")
    options = {"graph":cfg["config"]}
    if cfg["config"]!=cfg["f1_config"]:
        options["graph_f1"]=cfg["f1_config"]
    pred = predictions("test",options)
    save(path,pred)
    save(RESULT/"seal.json",dict(predictions=sha(path),freeze=sha(FREEZE),manifest=sha(RESULT/"test_manifest.json")))


def draws(truth,alerts,indices):
    tables,rows = [],[]
    for events,alarms in zip(truth,alerts,strict=True):
        tables.append(evaluate([events],[alarms])["confusion"])
        rows.append(tally([events],[alarms]))
    tab = np.asarray(tables)[indices].sum(axis=1)
    x = np.asarray(rows)[indices].sum(axis=1)
    f1 = [2*tab[:,c,c]/np.maximum(1,tab[:,c,:].sum(axis=1)+tab[:,:,c].sum(axis=1)) for c in range(1,5)]
    return np.column_stack((np.mean(f1,axis=0),x[:,0]/x[:,2],x[:,1]/x[:,2],x[:,3]))


def score():
    cfg = verify()
    path = RESULT/"predictions.json"
    if load(RESULT/"seal.json")!=dict(predictions=sha(path),freeze=sha(FREEZE),manifest=sha(RESULT/"test_manifest.json")):
        raise ValueError("Invalid blind seal")
    y=labels("test")
    observed = {e["source"] for row in y for e in row}
    if observed!=HELD or set(cfg["held"])!=observed:
        raise ValueError("Test source coverage differs from the registered holdout")
    save(RESULT/"test_truth.json",y)
    result = {}
    indices = np.random.default_rng(652951).integers(len(y),size=(4000,len(y)))
    sampled = {}
    for k,p in load(path).items():
        result[k]=metrics(y,p)
        sampled[k]=draws(y,p,indices)
    for k in ("graph","graph_f1"):
        if k in result:
            result[k]["paired_ci95"] = {other:dict(zip(("macro_f1","exact_site_fraction","joint_fraction","extra_count"),
                np.quantile(sampled[k]-sampled[other],[.025,.975],axis=0).T.tolist())) for other in ("trees","trees_refit")}
    save(RESULT/"scores.json",result)
    print({k:(v["macro_f1"],v["exact_site"],v["joint"],v["extras"]) for k,v in result.items()})


if __name__=="__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage",choices=("fit","predict","score"))
    stage=parser.parse_args().stage
    {"fit":select,"predict":predict,"score":score}[stage]()

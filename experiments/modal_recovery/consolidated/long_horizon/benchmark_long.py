"""Run a predeclared trajectory-extension check, then freeze and score a new 30 s trial."""
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import sys
from model_long import HERE,OUT,WORK,RESULT,TMP,inputs,load,phase_data,study
from metrics import outcomes
from adjudicate import tally,paired,site_id,CODE
import numpy as np


def initialize():
    global weights
    weights=load()


def infer(task):
    path,key,meta=task
    predictions={}
    for name,raw,c in inputs(path,meta):
        predictions[name]={arm:est.predict(raw,c) for arm,est in zip(("short_curve","graph"),weights)}
        early={k:v[:c+271] for k,v in raw.items()}
        assert weights[0].predict(early,c)==weights[1].predict(early,c)
    return key,predictions


def compute(folder,manifest,workers):
    records=manifest["records"]
    tasks=[(folder/(k+".npz"),k,v) for k,v in sorted(records.items())]
    with ProcessPoolExecutor(workers,initializer=initialize) as pool:
        return dict(pool.map(infer,tasks,chunksize=2))


def metrics(keys,truth,calls,setting,arm):
    vectors={m:[] for m in ("detection","family","exact","early","control_alarm")}
    pairs=[]
    fp_times=[]
    for key in keys:
        t=truth[key]
        v=calls[key][setting][arm]
        for m,value in outcomes(t,v).items():
            vectors[m].append(value)
        b,label=v["alarm"],v["label"]
        if t["on"] is None:
            code=(CODE[label[0]] if label else -1) if b is not None else 0
            if b is not None:
                fp_times.append((b-t["clearance"])/30)
        else:
            timely=b is not None and 2*b>=round(60*t["on"]) and 2*(b+29)<round(60*t["off"])
            code=CODE[label[0]] if timely and label else 0
        pairs.append((CODE[t["family"]],code))
    total={m:sum(a) for m,a in vectors.items()}
    total.update(tally(pairs),false_after_clear_s=fp_times)
    return vectors,total


def development():
    old=study.read(RESULT/"inputs.json")
    truth=study.read(RESULT/"truth.json")
    old["records"]={k:m for k,m in old["records"].items() if m["long"]}
    data=compute(TMP/"pmu",old,3)
    out={s:{arm:metrics(sorted(data),truth,data,s,arm)[1] for arm in ("short_curve","graph")}
         for s in ("native","joint")}
    study.save(OUT/"development.json",out)
    print({s:{a:(r["exact"],r["control_alarm"]) for a,r in rows.items()} for s,rows in out.items()})


def seal():
    dev=study.read(OUT/"development.json")
    files={p.name:study.digest(p) for p in HERE.iterdir() if p.is_file() and p.name!="RESULTS.md"}
    model={p.name:study.digest(p) for p in OUT.iterdir() if p.is_file()}
    assert not (WORK/"pmu").exists() and not (OUT/"inputs.json").exists()
    study.save(OUT/"freeze.json",dict(sources=files,weights=model,earlier=study.digest(RESULT/"freeze.json"),
        fixed_before_generation=True,seed=94026173,dev_summary={s:{a:[v["exact"],v["control_alarm"]]
        for a,v in r.items()} for s,r in dev.items()}))


def verify():
    f=study.read(OUT/"freeze.json")
    for name,base in (("sources",HERE),("weights",OUT)):
        for k,v in f[name].items():
            assert study.digest(base/k)==v,k
    assert f["earlier"]==study.digest(RESULT/"freeze.json")


def predict():
    verify()
    manifest=study.read(OUT/"inputs.json")
    assert len(manifest["records"])==192
    data=compute(WORK/"pmu",manifest,4)
    study.save(OUT/"predictions.json",data)


def score():
    from adjudicate import committed
    for name in ("inputs.json","zip_predictions.json","predictions.json"):
        committed(OUT/name)
    man=study.read(OUT/"inputs.json")
    labels_path=OUT/"truth.json" if (OUT/"truth.json").exists() else WORK/"targets.json"
    assert study.digest(labels_path)==man["targets_sha"]
    t=study.read(labels_path)
    calls=study.read(OUT/"predictions.json")
    zip_p=study.read(OUT/"zip_predictions.json")["cases"]
    assert set(t)==set(calls)==set(man["records"]) and len(t)==192 and len(zip_p)==96
    grouped={"all":sorted(t),"early":[k for k in sorted(t) if t[k]["parent"]<48],
            "late":[k for k in sorted(t) if t[k]["parent"]>=48]}
    timely={}
    for g,keys in grouped.items():
        timely[g]={}
        for s in ("native","joint"):
            a,ra=metrics(keys,t,calls,s,"graph"); b,rb=metrics(keys,t,calls,s,"short_curve")
            timely[g][s]=dict(graph=ra,short_curve=rb,paired={m:paired(a[m],b[m]) for m in a})
    win={}
    for s in ("native","joint"):
        win[s]={}
        for arm in ("graph","short_curve","hackathon","minirocket"):
            cls=[]; fa=exact=family=detected=0
            for k in sorted(zip_p):
                target=t[k]
                if arm=="hackathon":
                    zipcall=zip_p[k][s]["zip"]
                    code,where=zipcall["event_code"],zipcall["site"]
                elif arm=="minirocket":
                    ref=zip_p[k][s]["minirocket"]
                    code,where=CODE.get(ref["class"],-1),ref["site"]
                else:
                    decision=calls[k][s][arm]
                    lbl=decision["label"]
                    code=CODE[lbl[0]] if lbl else (0 if decision["alarm"] is None else -1)
                    where=lbl[1] if lbl else None
                true=CODE[target["family"]]
                cls.append((true,code if code in (0,2,4) else -1))
                if true:
                    detected+=code!=0
                    family+=code==true
                    exact+=code==true and site_id(where)==site_id(target["source"])
                else:
                    fa+=code!=0
            win[s][arm]=dict(**tally(cls),exact=exact,family=family,detection=detected,control_alarm=fa)
    result=dict(timely=timely,window=win,truth_sha=man["targets_sha"])
    if not (OUT/"truth.json").exists():
        import shutil
        shutil.copyfile(labels_path,OUT/"truth.json")
    if (OUT/"summary.json").exists():
        assert result==study.read(OUT/"summary.json")
    else:
        study.save(OUT/"summary.json",result)
    print({s:{a:(r["exact"],r["control_alarm"]) for a,r in v.items()} for s,v in win.items()})


if __name__=="__main__":
    {"dev":development,"freeze":seal,"predict":predict,"score":score}[sys.argv[1]]()

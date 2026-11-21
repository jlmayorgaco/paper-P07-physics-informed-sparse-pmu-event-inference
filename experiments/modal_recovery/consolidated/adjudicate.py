"""Score commitments for control alarms, detection and source decisions on paired streams."""
from collections import Counter
from hashlib import sha256
import subprocess
import shutil
import sys
import numpy as np
from scipy.stats import beta, binomtest
from robust import RESULT, TMP, CONDITIONS, study
from metrics import outcomes

ARMS=("graph","angular","magnitude","minirocket","li_wang","hydra")
CLASSES=(0,2,4)
CODE={"none":0,"line":2,"load":4}
FILES=("predictions.json","window_predictions.json","zip_predictions.json","inputs.json")


def committed(path):
    rel=path.relative_to(study.ROOT).as_posix()
    content=subprocess.check_output(["git","cat-file","blob",f"HEAD:{rel}"],cwd=study.ROOT)
    assert content==path.read_bytes(),f"Uncommitted change in {rel}"


def tally(pairs):
    confusion=Counter(pairs)
    f1=[]
    for k in CLASSES:
        tp=confusion[k,k]
        denominator=sum(n*((int(i==k))+(int(j==k))) for (i,j),n in confusion.items())
        f1.append(2*tp/denominator if denominator else 0.)
    return dict(macro_f1=sum(f1)/3,confusion={str(i):{str(j):confusion[i,j] for j in (0,2,4,-1)} for i in CLASSES})


def bounds(k,n):
    return [float(beta.ppf(.05,k,n-k+1)) if k else 0.,
            float(beta.ppf(.95,k+1,n-k)) if k<n else 1.]


def site_id(site):
    if site and str(site).upper().startswith("LINE"):
        a,b=sorted(map(int,str(site).upper()[4:].split("-")))
        return f"LINE{a}-{b}"
    return site


def paired(left,right):
    a=np.asarray(left,bool)
    b=np.asarray(right,bool)
    wins=int(sum(a&~b))
    losses=int(sum(b&~a))
    return dict(graph_only=wins,other_only=losses,
                p=float(binomtest(wins,wins+losses).pvalue) if wins+losses else 1.)


def primary(keys,truth,preds,setting):
    pos=[k for k in keys if truth[k]["on"] is not None]
    neg=[k for k in keys if truth[k]["on"] is None]
    values,totals={},{}
    for arm in ARMS:
        observed={m:[] for m in ("detection","family","exact","early","control_alarm")}
        labels=[]
        eligible=0
        for k in pos+neg:
            t=truth[k]
            p=preds[k][setting][arm]
            v=outcomes(t,p)
            for m,matched in v.items():
                observed[m].append(matched)
            b=p["alarm"]
            timely=t["on"] is not None and v["detection"] and b is not None and 2*(b+29)<round(60*t["off"])
            eligible+=int(timely)
            label=p["label"]
            if arm in ("li_wang","hydra"):
                assert b==preds[k][setting]["graph"]["alarm"]
            # Missed, early or late positive decisions count as missed events.
            # Controls with an alarm but no published class fall outside E0/E2/E4.
            code=0
            if (t["on"] is None and b is not None) or timely:
                code=CODE.get(label[0],-1) if label else -1
            labels.append((CODE[t["family"]],code))
        values[arm]=observed
        totals[arm]={k:int(sum(v)) for k,v in observed.items()}
        totals[arm].update(eligible=eligible,**tally(labels))
        totals[arm]["bounds95_one_sided"]={k:bounds(int(sum(v)),len(v)) for k,v in observed.items()}
        if arm=="li_wang":
            totals[arm]["exact"]=None
            del totals[arm]["bounds95_one_sided"]["exact"]
    comparisons={arm:{m:paired(values["graph"][m],values[arm][m]) for m in values[arm]
                      if arm!="li_wang" or m=="family"} for arm in ARMS[1:]}
    return dict(positives=len(pos),controls=len(neg),arms=totals,paired=comparisons)


def fixed(truth,preds,official,setting):
    keys=sorted(preds)
    assert set(keys)==set(official)
    pairs=Counter(truth[k]["parent"] for k in keys)
    assert set(pairs)==set(range(48)) and set(pairs.values())=={2}
    numbers={}
    flags={}
    for arm in ("graph","minirocket","hackathon"):
        classes=[]; positives=[]; families=[]; exact=[]; negatives=[]
        for k in keys:
            t=truth[k]
            rec=official[k][setting] if arm=="hackathon" else preds[k][setting][arm]
            code=int(rec["event"])
            target=CODE[t["family"]]
            classes.append((target,code if code in CLASSES else -1))
            if target:
                positives.append(code!=0)
                families.append(code==target)
                exact.append(code==target and site_id(rec["site"])==site_id(t["source"]))
            else:
                negatives.append(code!=0)
        flags[arm]=dict(detection=positives,family=families,exact=exact,control_alarm=negatives)
        numbers[arm]={k:sum(v) for k,v in flags[arm].items()}
        numbers[arm].update(**tally(classes),all_class_accuracy=sum(a==b for a,b in classes)/len(keys))
    return dict(positives=len(positives),controls=len(negatives),arms=numbers,
                paired={arm:{m:paired(flags["graph"][m],v) for m,v in row.items()} for arm,row in flags.items() if arm!="graph"})


def score():
    for f in FILES:
        committed(RESULT/f)
    manifest=study.read(RESULT/"inputs.json")
    source=RESULT/"truth.json" if (RESULT/"truth.json").exists() else TMP/"targets.json"
    assert study.digest(source)==manifest["targets_sha"]
    t=study.read(source)
    pred=study.read(RESULT/"predictions.json")
    assert set(t)==set(pred)==set(manifest["records"])
    assert len(t)==600
    for group,n in (("catalog",240),("bus31",60)):
        parents=Counter((v["parent"],v["on"] is None) for v in t.values() if v["panel"]==group)
        assert len(parents)==2*n and set(parents.values())=={1}
    window=study.read(RESULT/"window_predictions.json")
    old=study.read(RESULT/"zip_predictions.json")
    result=dict(primary={group:{s:primary([k for k,v in t.items() if v["panel"]==group],t,pred,s)
                                for s in CONDITIONS} for group in ("catalog","bus31")},
                window={s:fixed(t,window,old,s) for s in ("native","joint")},
                files={f:study.digest(RESULT/f) for f in FILES},truth_sha=manifest["targets_sha"])
    if source!=RESULT/"truth.json":
        shutil.copyfile(source,RESULT/"truth.json")
    if (RESULT/"summary.json").exists():
        assert result==study.read(RESULT/"summary.json")
    else:
        study.save(RESULT/"summary.json",result)


if __name__=="__main__":
    score()

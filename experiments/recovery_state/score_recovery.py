"""One-to-one episode scoring with matched recovery controls and a paired cluster bootstrap."""
from collections import defaultdict
import numpy as np
from design import DATA, LOCK, RESULT, arrays, load, save, sha
from trial import metrics


def pairs(truth, records, names, expected):
    groups=defaultdict(list)
    for i,name in enumerate(names):
        groups[name].append(i)
    matched=[]
    for name,ids in groups.items():
        if name.startswith("pair-"):
            control,case=sorted(ids,key=lambda i:len(truth[i]))
            events=truth[case]
            if len(events)!=2 or truth[control]!=events[:1]:
                raise ValueError("Inconsistent paired schedules")
            tick=events[1]["onset"]
            if records[control,:tick].tobytes()!=records[case,:tick].tobytes():
                raise ValueError("Twin streams disagree before intervention")
            matched.append((control,case))
    if len(matched)!=expected:
        raise ValueError("Incomplete twin evaluation")
    return matched


def second_counts(truth,pred,matched):
    counts={str(c):dict(events=0,detected=0,family=0,site=0,joint=0,control_extras=0) for c in (3,4)}
    for control,case in matched:
        first,event=truth[case]
        t=event["onset"]
        if [a for a in pred[control] if a["detected"]<t]!=[a for a in pred[case] if a["detected"]<t]:
            raise ValueError("Alarm prefix depends on future reports")
        if first["code"] not in (1,2) or event["code"] not in (3,4):
            continue
        row=counts[str(event["code"])]
        row["events"]+=1
        row["control_extras"]+=metrics([truth[control]],[pred[control]])["extras"]
        alarm=next((a for a in pred[case] if 0<=a["detected"]-t<=45),None)
        if alarm is None:
            continue
        row["detected"]+=1
        if alarm["published"] is not None and alarm["published"]<=t+45:
            family=alarm["code"]==event["code"]
            site=alarm["source"]==event["source"]
            row["family"]+=family
            row["site"]+=site
            row["joint"]+=family and site
    return counts


def draws(truth,pred,groups,weights):
    # 30 confusion cells (extra/4 true x late/4 reported/other), then 4 counts.
    stats=np.zeros((weights.shape[1],34),dtype=float)
    for g,events,alerts in zip(groups,truth,pred,strict=True):
        row=metrics([events],[alerts])
        stats[g]+=np.r_[np.ravel(row["confusion"]),row["events"],row["exact_site"],row["joint"],row["extras"]]
    aggregate=weights@stats
    conf=aggregate[:,:30].reshape(-1,5,6)
    diag=np.diagonal(conf[:,1:,1:5],axis1=1,axis2=2)
    den=conf[:,1:,:].sum(axis=2)+conf[:,:,1:5].sum(axis=1)
    f1=np.mean(2*diag/np.maximum(den,1),axis=1)
    n,site,joint,extras=aggregate[:,30:].T
    return np.column_stack([f1,diag.sum(axis=1)/n,site/n,joint/n,extras])


def score():
    from study_recovery import verify
    frozen=verify()
    path=RESULT/"predictions.json"
    manifest=RESULT/"test_manifest.json"
    if load(RESULT/"seal.json")!=dict(predictions=sha(path),freeze=sha(LOCK),manifest=sha(manifest)):
        raise ValueError("Invalid blind seal")
    predictions=load(path)
    if set(predictions)!={"recovery","previous","trees","trees_refit"}:
        raise ValueError("Missing comparator")
    truth=arrays("test",True)
    if {e["source"] for r in truth for e in r}!=set(frozen["held"]):
        raise ValueError("Incorrect held-out asset coverage")
    names=load(manifest)["clusters"]
    matched=pairs(truth,arrays("test"),names,128)
    labels,groups=np.unique(names,return_inverse=True)
    n=len(labels)
    weights=np.random.default_rng(652951).multinomial(n,np.full(n,1/n),size=4000)
    result={}
    boot={}
    keys=["macro_f1","family_fraction","exact_site_fraction","joint_fraction","extra_count"]
    def interval(a):
        return dict(zip(keys,np.quantile(a,[.025,.975],axis=0).T.tolist()))
    for k,pred in predictions.items():
        s=metrics(truth,pred)
        s["target_second"]=second_counts(truth,pred,matched)
        s["all_matched_control_extras"]=sum(metrics([truth[c]],[pred[c]])["extras"] for c,_ in matched)
        boot[k]=draws(truth,pred,groups,weights)
        s["cluster_ci95"]=interval(boot[k])
        result[k]=s
    result["recovery"]["delta_ci95"]={k:interval(boot["recovery"]-v) for k,v in boot.items() if k!="recovery"}
    save(RESULT/"test_truth.json",truth)
    save(RESULT/"scores.json",result)
    print({k:(s["macro_f1"],s["family"],s["exact_site"],s["extras"],s["target_second"])
           for k,s in result.items()})

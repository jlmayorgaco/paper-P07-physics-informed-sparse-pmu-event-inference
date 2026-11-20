"""Score timestamped alarms one-to-one, preserving negative records and missed events."""
import hashlib
import json
import shutil
from collections import Counter

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score

from plant import DATA, FRAMES, FS, HERE


def score():
    path=HERE/"predictions.json"
    assert hashlib.sha256(path.read_bytes()).hexdigest()==(HERE/"prediction_seal.txt").read_text()
    pred=json.loads(path.read_text())
    truthpath=DATA/"test/truth.json"
    assert hashlib.sha256(truthpath.read_bytes()).hexdigest()==json.loads((HERE/"test_manifest.json").read_text())["sha256_truth"]
    truth=json.loads(truthpath.read_text())
    assert len(pred)==len(truth)==300
    ledger=[]
    delays=[]
    totals=[]
    for rid,(events,alarms) in enumerate(zip(truth,pred)):
        matched=set()
        claimed=set()
        success=0
        for i,e in enumerate(events):
            candidates=[j for j,a in enumerate(alarms) if j not in claimed and 0<=a["published"]-e["onset"]<=45]
            row=dict(record=rid,onset=e["onset"]/FS,true_class=e["code"],true_site=e["source"],
                     published=None,pred_class=0,pred_site="",kind="miss")
            if candidates:
                j=min(candidates,key=lambda k:alarms[k]["published"])
                a=alarms[j]
                matched.add(i)
                claimed.add(j)
                delay=(a["published"]-e["onset"])/FS
                delays.append(delay)
                row.update(published=a["published"]/FS,pred_class=a["code"],pred_site=a["source"],kind="matched")
                success+=int(a["code"]==e["code"] and a["source"]==e["source"])
            ledger.append(row)
        for j,a in enumerate(alarms):
            if j not in claimed:
                ledger.append(dict(record=rid,onset=None,true_class=0,true_site="",published=a["published"]/FS,
                                   pred_class=a["code"],pred_site=a["source"],kind="extra"))
        # Eligible quiet seconds contain no active intervention or publication.
        occupied={t//FS for e in events for t in range(e["onset"],e["end"])}
        occupied.update(a["published"]//FS for a in alarms)
        quiet_bins=len(set(range(FRAMES//FS))-occupied)
        totals.append(dict(record=rid,true=len(events),pred=len(alarms),detected=len(matched),joint=success,
                           extras=len(alarms)-len(claimed),quiet_bins=quiet_bins,
                           normal=int(not events),normal_ok=int(not events and not alarms),
                           perfect=int(success==len(events)==len(alarms))))
    ledger=pd.DataFrame(ledger)
    ledger.to_csv(HERE/"event_ledger.csv",index=False)
    counts=pd.DataFrame(totals)
    t=counts.sum()
    confusion=np.zeros((9,9),int)
    np.add.at(confusion,(ledger.true_class,ledger.pred_class),1)
    confusion[0,0]+=t.quiet_bins
    class_f1=2*confusion.diagonal()/np.maximum(1,confusion.sum(0)+confusion.sum(1))
    events=ledger.query("true_class>0").copy()
    events["family_hit"]=events.true_class==events.pred_class
    events["site_hit"]=events.true_site==events.pred_site
    events["joint"]=events.family_hit&events.site_hit
    table=events.groupby("true_class").agg(events=("true_class","size"),matched=("published","count"),
                    family=("family_hit","sum"),site=("site_hit","sum"),joint=("joint","sum"))
    table.to_csv(HERE/"per_family.csv")
    bootstrap=np.random.default_rng(5221).integers(300,size=(5000,300))
    intervals={}
    for metric,num,den in [("joint","joint","true"),("recall","detected","true"),("precision","detected","pred"),
                           ("quiet_records","normal_ok","normal")]:
        samples=counts[num].to_numpy()[bootstrap].sum(1)/counts[den].to_numpy()[bootstrap].sum(1)
        intervals[metric]=np.quantile(samples,[.025,.975]).tolist()
    result=dict(records=len(counts),events=int(t.true),alarms=int(t.pred),matched=int(t.detected),
        precision=t.detected/t.pred,recall=t.detected/t.true,correct_family=int(events.family_hit.sum()),
        correct_site=int(events.site_hit.sum()),joint=int(t.joint),joint_rate=t.joint/t.true,
        macro_f1_9=class_f1.mean(),per_class_f1=class_f1.tolist(),confusion=confusion.tolist(),
        extras=int(t.extras),quiet_records=int(t.normal),quiet_records_without_alarm=int(t.normal_ok),
        extras_on_normal=int(counts.loc[counts.normal==1,"extras"].sum()),perfect_records=int(t.perfect),
        test_hours=len(counts)*FRAMES/FS/3600,delay_median_p95_s=np.quantile(delays,[.5,.95]).tolist(),
        bootstrap95=intervals,records_by_event_count=dict(Counter(map(len,truth))))
    (HERE/"scores.json").write_text(json.dumps(result,indent=2))
    shutil.copyfile(truthpath,HERE/"test_truth.json")
    print({k:v for k,v in result.items() if k not in ("confusion","per_class_f1")})
    print(table)


if __name__=="__main__":
    score()

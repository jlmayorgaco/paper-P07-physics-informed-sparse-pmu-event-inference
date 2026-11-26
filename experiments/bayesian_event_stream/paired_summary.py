"""Paired interval and error breakdown for a sealed stream comparison."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


def summarize(folder, candidate, baseline):
    path=folder/"predictions.csv"
    assert hashlib.sha256(path.read_bytes()).hexdigest()==(folder/"seal.sha256").read_text()
    truth=pd.read_csv(folder/"truth.csv")
    truth["previous"]=truth.groupby("record")["mode"].shift().fillna("quiet")
    pred=pd.read_csv(path).merge(truth,validate="many_to_one")
    event=pred["mode"]!="quiet"
    pred["hit"]=(pred["mode"]==pred.pred)&(pred.bus==pred.asset)
    pivot=pred[event].pivot(index=["record","window"],columns="method",values="hit")
    gain=pivot[candidate]&~pivot[baseline]
    loss=pivot[baseline]&~pivot[candidate]
    # Bootstrap whole records, including those without events.
    totals=(gain.astype(int)-loss.astype(int)).groupby(level=0).agg(["sum","count"])
    totals=totals.reindex(truth.record.unique(),fill_value=0).to_numpy()
    rng=np.random.default_rng(11952)
    samples=totals[rng.integers(len(totals),size=(10000,len(totals)))].sum(axis=1)
    ci=np.quantile(samples[:,0]/samples[:,1],[.025,.975]).tolist()
    g=pred[pred.method==candidate].copy()
    false=g[(g["mode"]=="quiet")&(g.pred!="quiet")]
    summary=dict(candidate=candidate,baseline=baseline,gains=int(gain.sum()),losses=int(loss.sum()),
                 paired_joint_delta_ci=ci,perfect_records=int(g.groupby("record").hit.all().sum()),
                 false_alarms_previous=false.previous.value_counts().to_dict(),
                 exact_per_family=g.groupby("mode").hit.sum().to_dict())
    observed=folder.parents[1]/"tmp" if folder.name!="successor" else folder.parents[2]/"tmp"
    seed=643271 if folder.name=="successor" else 476209
    obs=observed/f"bayes_stream_{seed}"/"observations.npy"
    summary["observations_sha256"]=hashlib.sha256(obs.read_bytes()).hexdigest()
    print(summary)
    (folder/"paired_summary.json").write_text(json.dumps(summary,indent=2))


if __name__=="__main__":
    here=Path(__file__).resolve().parent
    summarize(here,"history","bayes")
    summarize(here/"successor","ensemble","history")

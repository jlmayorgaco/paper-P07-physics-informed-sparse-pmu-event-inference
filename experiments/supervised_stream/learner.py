"""Fit a causal trigger, event classifier and physics-template source ranker."""
import hashlib
import json
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import ExtraTreesClassifier, ExtraTreesRegressor
from sklearn.metrics import f1_score

from plant import DATA, FRAMES, FS, HERE, Generator, PMUS

TICKS=np.arange(30,FRAMES,3)
WAIT=24
REFRACTORY=72


def forest(n,depth,leaf=2):
    return ExtraTreesClassifier(n_estimators=n,max_depth=depth,min_samples_leaf=leaf,
                                max_features=.5,n_jobs=4,random_state=3608)


def normalized(obs,scales):
    center=np.median(obs[:30,:,:4],axis=0)
    values=obs[:,:,:4]-center
    values[:,:,3]=(values[:,:,3]+180)%360-180
    values/=scales
    # Zero is the neutral imputation; missingness stays an explicit sensor feature.
    values*=obs[:,:,4,None]
    return np.concatenate((values,obs[:,:,4,None]-1),axis=2).astype("float32")


def gate_features(z):
    flat=z.reshape(FRAMES,-1)
    sums=np.vstack((np.zeros(flat.shape[1]),np.cumsum(flat,axis=0,dtype=np.float64)))
    def avg(start,end):
        return (sums[end]-sums[start])/(end-start)[:,None]
    end=TICKS+1
    parts=[]
    for w in (3,9,18):
        recent=avg(end-w,end)
        earlier=avg(end-w-12,end-w)
        diff=recent-earlier
        parts.extend((diff,np.max(abs(diff.reshape(-1,8,5)),axis=1)))
    return np.column_stack(parts).astype("float32")


def patch(z,start):
    # 24 reports of local evidence and 15 preceding reports for a linear trend.
    ids=np.arange(start-15,start+24)
    x=z[ids.clip(0,len(z)-1)].astype("float64")
    base=x[:15].mean(axis=0)
    trend=(x[8:15].mean(axis=0)-x[:7].mean(axis=0))/8
    raw=x[15:]-base
    return raw,raw-np.arange(8,32)[:,None,None]*trend


def event_features(z,start):
    raw,adj=patch(z,start)
    parts=[]
    for block in (raw,adj):
        for segment in np.array_split(block,4):
            parts.append(segment.mean(axis=0).ravel())
        parts.append(np.max(abs(block),axis=0).ravel())
    return np.concatenate(parts).astype("float32")


def template_bank(sim,scales):
    bank={}
    for code,sites in sim.catalog.items():
        templates=[]
        for site in sites:
            event=dict(code=3 if code==6 else code,source=site,onset=60,end=68 if code==1 else 100,
                       strength=1.,sensors=[2,5])
            obs=sim.simulate([event],np.random.default_rng(1),nominal=True)
            z=normalized(obs,scales)
            templates.append(patch(z,60)[0])
        bank[code]=np.array(templates)
    return bank


def rank_features(z,start,code,bank):
    # Compare local time/PMU signatures at three alignments. For each channel
    # group retain its fit improvement, normalized correlation and scale mismatch.
    templates=bank[code]
    all_offsets=[]
    for offset in (-3,0,3):
        raw,adj=patch(z,start+offset)
        # Later alignments may only consume reports available by publication.
        length=24-max(0,offset)
        parts=[]
        for obs in (raw[:length],adj[:length]):
            for c in range(5):
                target=obs[:,:,c]
                t=templates[:,:length,:,c]
                dot=np.einsum("ntb,tb->n",t,target)
                energy=np.sum(t*t,axis=(1,2))
                strength=np.clip(dot/np.maximum(energy,1e-12),.5,1.5)
                fit=2*strength*dot-strength**2*energy
                corr=dot/np.sqrt(np.maximum(energy*np.sum(target**2),1e-20))
                parts.extend((np.sign(fit)*np.log1p(abs(fit)),corr,strength))
        all_offsets.append(np.column_stack(parts))
    return np.column_stack(all_offsets).astype("float32")


def subset_training(zs,truth,ids):
    features,labels,delays=[],[],[]
    for rid in ids:
        label=np.zeros(len(TICKS),int)
        delay=np.zeros(len(TICKS),int)
        for event in truth[rid]:
            dt=TICKS-event["onset"]
            mask=(dt>=0)&(dt<=15)
            label[mask]=1
            delay[mask]=dt[mask]
        # Keep every positive and a systematic fifth of negative examples.
        take=(label==1)|((np.arange(len(TICKS))+rid)%5==0)
        features.append(gate_features(zs[rid])[take])
        labels.extend(label[take])
        delays.extend(delay[take])
    return np.vstack(features),np.array(labels),np.array(delays)


def gates(z,trigger,clock,threshold):
    x=gate_features(z)
    prob=trigger.predict_proba(x)[:,1]
    possible=np.flatnonzero(prob>=threshold)
    if not len(possible):
        return []
    lag=clock.predict(x[possible])
    found=[]
    available=0
    for j,late in zip(possible,lag):
        t=int(TICKS[j])
        if t<available:
            continue
        start=max(0,t-int(np.clip(round(late),0,15)))
        publish=max(t,start+WAIT-1)
        if publish<len(z):
            found.append((start,publish))
            available=t+REFRACTORY
    return found


def gate_counts(truth,detected):
    claimed=set()
    for _,when in detected:
        for i,e in enumerate(truth):
            if i not in claimed and 0<=when-e["onset"]<=45:
                claimed.add(i)
                break
    return len(claimed),len(detected)-len(claimed),len(truth)-len(claimed)


def train():
    sim=Generator()
    scales=np.column_stack((np.full(8,.001),np.full(8,.001),sim.exp.mag.sd,sim.exp.ang.sd))
    truth=json.loads((DATA/"train/truth.json").read_text())
    raw=np.load(DATA/"train/observations.npy",mmap_mode="r")
    zs=[normalized(r,scales) for r in raw]
    ids=np.random.default_rng(341).permutation(len(zs))
    fit,cal=ids[:560],ids[560:]
    x,y,d=subset_training(zs,truth,fit)
    trigger=forest(64,18)
    trigger.fit(x,y)
    clock=ExtraTreesRegressor(n_estimators=48,max_depth=12,min_samples_leaf=3,random_state=663,n_jobs=4)
    clock.fit(x[y==1],d[y==1])
    # One calibration pass per record; threshold selection uses training-side records only.
    grid=(.20,.35,.50,.65,.80)
    counts={k:np.zeros(3,int) for k in grid}
    for rid in cal:
        xcal=gate_features(zs[rid])
        probs=trigger.predict_proba(xcal)[:,1]
        delays=clock.predict(xcal)
        for tau in grid:
            found=[]
            available=0
            for j in np.flatnonzero(probs>=tau):
                t=int(TICKS[j])
                if t<available:
                    continue
                start=t-int(np.clip(round(delays[j]),0,15))
                end=max(t,start+WAIT-1)
                if end<FRAMES:
                    found.append((start,end))
                    available=t+REFRACTORY
            counts[tau]+=gate_counts(truth[rid],found)
    def objective(key):
        a,b,c=counts[key]
        return 2*a/max(1,2*a+b+c),-b
    threshold=max(grid,key=objective)
    x,y,d=subset_training(zs,truth,range(len(zs)))
    trigger.fit(x,y)
    clock.fit(x[y==1],d[y==1])
    bank=template_bank(sim,scales)
    fx,fy=[],[]
    rx,ry={},{}
    for rid,events in enumerate(truth):
        for event in events:
            c=event["code"]
            for jitter in (-4,0,4):
                anchor=event["onset"]+jitter
                fx.append(event_features(zs[rid],anchor))
                fy.append(c)
                rx.setdefault(c,[]).append(rank_features(zs[rid],anchor,c,bank))
                ry.setdefault(c,[]).extend(site==event["source"] for site in sim.catalog[c])
    family=forest(100,20,1).fit(fx,fy)
    rankers={}
    for c in rx:
        rankers[c]=forest(80,16,2).fit(np.vstack(rx[c]),ry[c])
    model=dict(scales=scales,trigger=trigger,clock=clock,threshold=threshold,
               bank=bank,family=family,rankers=rankers,catalog=sim.catalog)
    for estimator in [trigger,clock,family,*rankers.values()]:
        estimator.n_jobs=1
    path=HERE/"model.joblib"
    joblib.dump(model,path,compress=3)
    metadata=dict(model_sha256=hashlib.file_digest(open(path,"rb"),"sha256").hexdigest(),
                  threshold=threshold,calibration={k:v.tolist() for k,v in counts.items()},
                  fit_ids=fit.tolist(),calibration_ids=cal.tolist(),final_fit=700)
    (HERE/"model_freeze.json").write_text(json.dumps(metadata))
    print("Frozen model",metadata["model_sha256"],"threshold",threshold,"training records",len(zs),flush=True)


def predict():
    path=HERE/"model.joblib"
    seal=json.loads((HERE/"model_freeze.json").read_text())
    assert hashlib.file_digest(open(path,"rb"),"sha256").hexdigest()==seal["model_sha256"]
    m=joblib.load(path)
    obs=np.load(DATA/"test/observations.npy",mmap_mode="r")
    alarms=[]
    for r in obs:
        z=normalized(r,m["scales"])
        sequence=[]
        for start,when in gates(z,m["trigger"],m["clock"],m["threshold"]):
            # Supply a physically truncated prefix to both downstream estimators.
            prefix=z[:when+1]
            code=int(m["family"].predict(event_features(prefix,start)[None,:])[0])
            rx=rank_features(prefix,start,code,m["bank"])
            proba=m["rankers"][code].predict_proba(rx)[:,1]
            sequence.append(dict(onset_est=start,published=when,code=code,
                                 source=m["catalog"][code][int(np.argmax(proba))]))
        alarms.append(sequence)
    path=HERE/"predictions.json"
    path.write_text(json.dumps(alarms))
    (HERE/"prediction_seal.txt").write_text(hashlib.sha256(path.read_bytes()).hexdigest())

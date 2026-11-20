"""Larger independent run with a learned no-event confirmation and source ranking."""
import argparse
import hashlib
import json
from pathlib import Path

import joblib
import numpy as np
from scipy.linalg import solve_triangular
from sklearn.ensemble import ExtraTreesRegressor

import learner as first
from plant import DATA, HERE, FRAMES, Generator, PMUS, generate
from score import score

OUT=HERE/"successor"
STORE=DATA/"larger"
WAIT=36
TICKS=first.TICKS
TAUS=(.12,.20,.28,.36)
CONF=(.35,.50,.65)


def patch(z,start):
    ids=np.arange(start-18,start+WAIT)
    x=z[ids.clip(0,len(z)-1)].astype(float)
    base=x[:18].mean(axis=0)
    slope=(x[10:18].mean(axis=0)-x[:8].mean(axis=0))/10
    raw=x[18:]-base
    return raw,raw-(np.arange(WAIT)+9.5)[:,None,None]*slope


def family_features(z,start):
    raw,adj=patch(z,start)
    vec=[]
    for signal in (raw,adj):
        for seg in np.array_split(signal,6):
            mean=seg.mean(axis=0)
            vec.extend([mean.ravel(),np.sort(abs(mean),axis=0)[-3:].ravel()])
        vec.append(np.abs(signal).max(axis=0).ravel())
    return np.concatenate(vec).astype("float32")


def gate_features(z):
    a=first.gate_features(z)
    sums=np.vstack([np.zeros((1,40)),np.cumsum(z.reshape(FRAMES,40),axis=0,dtype=float)])
    end=TICKS+1
    def avg(left,right):
        return ((sums[right]-sums[left])/(right-left)[:,None]).reshape(-1,8,5)
    parts=[a]
    for w in (3,9):
        current=avg(end-w,end)
        last=avg(end-2*w,end-w)
        older=avg(end-3*w,end-2*w)
        for val in (current,last,current-2*last+older):
            parts.extend([np.sort(abs(val),axis=1)[:,-3:].reshape(len(end),-1),
                          np.sqrt((val**2).mean(axis=1))])
    return np.column_stack(parts).astype("float32")


def gate_fit(zs,labels,ids):
    features,targets,delay=[],[],[]
    for i in ids:
        y=np.zeros(len(TICKS),int)
        dt=y.copy()
        for e in labels[i]:
            lag=TICKS-e["onset"]
            m=(lag>=0)&(lag<=15)
            y[m],dt[m]=1,lag[m]
        take=(y==1)|((np.arange(len(y))+i)%6==0)
        features.append(gate_features(zs[i])[take])
        targets.extend(y[take])
        delay.extend(dt[take])
    x=np.vstack(features)
    y=np.array(targets)
    trigger=first.forest(64,18).fit(x,y)
    clock=ExtraTreesRegressor(n_estimators=48,max_depth=12,min_samples_leaf=3,n_jobs=4,
                              random_state=663).fit(x[y==1],np.asarray(delay)[y==1])
    trigger.n_jobs=clock.n_jobs=1
    return trigger,clock


def telemetry(z,trigger,clock):
    x=gate_features(z)
    p=trigger.predict_proba(x)[:,1]
    idx=np.flatnonzero(p>=min(TAUS))
    return [(int(TICKS[j]),float(p[j]),int(TICKS[j]-np.clip(round(dt),0,15)))
            for j,dt in zip(idx,clock.predict(x[idx]) if len(idx) else [])]


def candidates(tele,tau):
    available=0
    for tick,prob,start in tele:
        if tick<available or prob<tau or start+WAIT>FRAMES:
            continue
        yield start,start+WAIT-1
        available=tick+first.REFRACTORY


def fit_family(zs,truth,ids,tele):
    x,y=[],[]
    rng=np.random.default_rng(95413)
    for i in ids:
        events=truth[i]
        anchors=np.array([e["onset"] for e in events])
        for e in events:
            for jitter in (-5,-2,1,4):
                x.append(family_features(zs[i],e["onset"]+jitter))
                y.append(e["code"])
        negatives=list(rng.integers(40,FRAMES-45,size=2))
        for e in events:
            negatives.extend((e["end"]+3,e["end"]+20))
        negatives.extend(start for start,_ in candidates(tele[i],min(TAUS)))
        for start in set(negatives):
            if start+WAIT<=FRAMES and np.all(abs(start-anchors)>25):
                x.append(family_features(zs[i],start))
                y.append(0)
    clf=first.forest(96,20,1).fit(x,y)
    clf.n_jobs=1
    return clf


def bank_for(sim,scales):
    bank={}
    for code,sites in sim.catalog.items():
        rows=[]
        for site in sites:
            e=dict(code=3 if code==6 else code,source=site,onset=60,end=68 if code==1 else 110,
                   strength=1.,sensors=[2,5])
            obs=sim.simulate([e],np.random.default_rng(1),nominal=True)
            if code==8:
                obs[66:110,0,2]/=1.3
            z=first.normalized(obs,scales)
            rows.append(patch(z,60)[0])
        bank[code]=np.array(rows)
    return bank


def spatial_noise(model):
    factor=model.chol[:16,:16]
    cov=factor@factor.T
    sd=np.tile(model.sd,2)
    cov=cov/(sd[:,None]*sd)
    transition=np.linalg.solve(cov[:8,:8],cov[:8,8:]).T
    innov=cov[8:,8:]-transition@cov[:8,8:]
    return transition.T,np.linalg.inv(np.linalg.cholesky(innov)).T


def ranking(z,start,code,model):
    bank=model["bank"][code]
    stats=[]
    for shift in (-3,0,3):
        raw,adj=patch(z,start+shift)
        n=WAIT-max(0,shift)
        for obs in (raw[:n],adj[:n]):
            for c in range(5):
                sig=bank[:,:n,:,c]
                target=obs[:,:,c]
                data=[(sig,target)]
                if c in (2,3):
                    ar,white=model["spatial"][c-2]
                    data.append(((sig[:,1:]-sig[:,:-1]@ar)@white,
                                 (target[1:]-target[:-1]@ar)@white))
                for s,v in data:
                    dot=np.einsum("itb,tb->i",s,v)
                    energy=np.einsum("itb,itb->i",s,s)
                    a=np.clip(dot/np.maximum(energy,1e-12),.5,1.5)
                    val=2*dot*a-energy*a*a
                    corr=dot/np.sqrt(np.maximum(energy*np.sum(v*v),1e-20))
                    stats.extend((np.sign(val)*np.log1p(abs(val)),corr,a))
    return np.column_stack(stats).astype("float32")


def train():
    sim=Generator()
    scales=np.column_stack((np.full(8,.001),np.full(8,.001),sim.exp.mag.sd,sim.exp.ang.sd))
    truth=json.loads((STORE/"train/truth.json").read_text())
    obs=np.load(STORE/"train/observations.npy",mmap_mode="r")
    zs=[first.normalized(r,scales) for r in obs]
    ids=np.random.default_rng(4711).permutation(len(zs))
    fit,cal=ids[:1680],ids[1680:]
    trigger,clock=gate_fit(zs,truth,fit)
    tele=[telemetry(z,trigger,clock) for z in zs]
    family=fit_family(zs,truth,fit,tele)
    counts={(tau,cf):np.zeros(3,int) for tau in TAUS for cf in CONF}
    for i in cal:
        cache={}
        for tau in TAUS:
            actions=list(candidates(tele[i],tau))
            for start,_ in actions:
                if start not in cache:
                    cache[start]=family.predict_proba(family_features(zs[i],start)[None,:])[0,0]
            for cf in CONF:
                actions_ok=[a for a in actions if 1-cache[a[0]]>=cf]
                counts[tau,cf]+=first.gate_counts(truth[i],actions_ok)
    def objective(pair):
        tp,fp,fn=counts[pair]
        return 2*tp/max(1,2*tp+fp+fn),-fp
    best=max(counts,key=objective)
    print("calibrated",best,counts[best],flush=True)
    family=fit_family(zs,truth,ids,tele)
    trigger,clock=gate_fit(zs,truth,ids)
    model=dict(scales=scales,bank=bank_for(sim,scales),catalog=sim.catalog,
               spatial=[spatial_noise(sim.exp.mag),spatial_noise(sim.exp.ang)],
               trigger=trigger,clock=clock,family=family,thresholds=best,rankers={})
    for code in sim.catalog:
        features,labels=[],[]
        for i,events in enumerate(truth):
            for e in events:
                if e["code"]!=code:
                    continue
                for jitter in (-3,0,3):
                    features.append(ranking(zs[i],e["onset"]+jitter,code,model))
                    labels.extend(site==e["source"] for site in sim.catalog[code])
        estimator=first.forest(64,18,2).fit(np.vstack(features),labels)
        estimator.n_jobs=1
        model["rankers"][code]=estimator
    path=OUT/"model.joblib"
    joblib.dump(model,path,compress=3)
    meta=dict(model_sha256=hashlib.file_digest(open(path,"rb"),"sha256").hexdigest(),
              thresholds=best,calibration={str(k):v.tolist() for k,v in counts.items()},
              fit_ids=fit.tolist(),calibration_ids=cal.tolist(),final_fit=len(ids))
    (OUT/"model_freeze.json").write_text(json.dumps(meta))
    print("frozen",meta["model_sha256"],flush=True)


def predict():
    path=OUT/"model.joblib"
    assert hashlib.file_digest(open(path,"rb"),"sha256").hexdigest()==json.loads((OUT/"model_freeze.json").read_text())["model_sha256"]
    model=joblib.load(path)
    tau,cf=model["thresholds"]
    results=[]
    for obs in np.load(STORE/"test/observations.npy",mmap_mode="r"):
        z=first.normalized(obs,model["scales"])
        alarms=[]
        for start,pub in candidates(telemetry(z,model["trigger"],model["clock"]),tau):
            prefix=z[:pub+1]
            p=model["family"].predict_proba(family_features(prefix,start)[None,:])[0]
            if 1-p[0]<cf:
                continue
            code=int(np.argmax(p[1:])+1)
            rank=model["rankers"][code].predict_proba(ranking(prefix,start,code,model))[:,1]
            alarms.append(dict(onset_est=start,published=pub,code=code,
                               source=model["catalog"][code][int(np.argmax(rank))]))
        results.append(alarms)
    path=OUT/"predictions.json"
    path.write_text(json.dumps(results))
    (OUT/"prediction_seal.txt").write_text(hashlib.sha256(path.read_bytes()).hexdigest())


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("stage",choices=["train","generate_train","generate_test","predict","score"])
    a=p.parse_args()
    if a.stage=="train":
        train()
    elif a.stage=="predict":
        predict()
    elif a.stage=="score":
        score(OUT,STORE,900)
    else:
        split=a.stage.split("_")[1]
        if split=="test":
            assert (OUT/"model_freeze.json").is_file()
        generate(split,2100 if split=="train" else 900,830711 if split=="train" else 660137,STORE,OUT)

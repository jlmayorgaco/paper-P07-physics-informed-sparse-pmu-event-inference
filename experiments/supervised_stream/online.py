"""Online monitor for the trained physical nine-state stream model.

Call step once per synchronized 30 Hz report. Rows follow PMUS and columns
are log-voltage-magnitude residual, voltage-angle residual (rad), terminal
current magnitude (A), current-angle residual (deg), and presence (0/1).
The first 30 reports provide the quiet operating baseline. Start a new instance
for a distinct trajectory. An alarm is returned at its actual publication time.
"""
from collections import deque
import hashlib
import json

import joblib
import numpy as np
from larger import OUT, WAIT, family_features, ranking


def gate_vector(z):
    x=z[-30:]
    parts=[]
    for w in (3,9,18):
        recent=x[-w:].mean(axis=0,dtype=float)
        earlier=x[-w-12:-w].mean(axis=0,dtype=float)
        diff=recent-earlier
        parts.extend([diff.ravel(),np.max(abs(diff),axis=0)])
    for w in (3,9):
        cur=x[-w:].mean(axis=0,dtype=float)
        prev=x[-2*w:-w].mean(axis=0,dtype=float)
        old=x[-3*w:-2*w].mean(axis=0,dtype=float)
        for value in (cur,prev,cur-2*prev+old):
            parts.extend([np.sort(abs(value),axis=0)[-3:].ravel(),np.sqrt((value**2).mean(axis=0))])
    return np.concatenate(parts).astype("float32")[None,:]


def load_model(folder=OUT):
    file=folder/"model.joblib"
    meta=json.loads((folder/"model_freeze.json").read_text())
    if hashlib.file_digest(open(file,"rb"),"sha256").hexdigest()!=meta["model_sha256"]:
        raise ValueError("Model checksum mismatch")
    return joblib.load(file)


class Monitor:
    def __init__(self,model):
        self.model=model
        self.frames=deque(maxlen=96)
        self.prefix=[]
        self.center=None
        self.tick=-1
        self.pending=None
        self.available=0

    def normalize(self,obs):
        values=np.asarray(obs[:,:4],dtype="float32")-self.center
        values[:,3]=(values[:,3]+180)%360-180
        values/=self.model["scales"]
        values*=obs[:,4,None]
        return np.column_stack((values,obs[:,4]-1)).astype("float32")

    def step(self,obs):
        obs=np.asarray(obs,dtype="float32")
        if obs.shape!=(8,5) or not np.isfinite(obs).all():
            raise ValueError("Expected one finite 8 PMU by 5 field report; use the presence field for missing data")
        self.tick+=1
        if self.center is None:
            self.prefix.append(obs.copy())
            if len(self.prefix)==30:
                self.center=np.median(np.array(self.prefix)[:,:,:4],axis=0)
                self.frames.extend(self.normalize(item) for item in self.prefix)
                self.prefix.clear()
            return None
        self.frames.append(self.normalize(obs))
        if self.tick%3==0 and self.tick>=self.available:
            x=gate_vector(np.array(self.frames))
            if self.model["trigger"].predict_proba(x)[0,1]>=self.model["thresholds"][0]:
                lag=int(np.clip(round(self.model["clock"].predict(x)[0]),0,15))
                self.pending=self.tick-lag
                self.available=self.tick+72
        if self.pending is None or self.tick!=self.pending+WAIT-1:
            return None
        start=self.pending
        self.pending=None
        z=np.array(self.frames)
        local=len(z)-WAIT
        p=self.model["family"].predict_proba(family_features(z,local)[None,:])[0]
        if 1-p[0]<self.model["thresholds"][1]:
            return None
        code=int(np.argmax(p[1:])+1)
        f=ranking(z,local,code,self.model)
        ix=np.argmax(self.model["rankers"][code].predict_proba(f)[:,1])
        return dict(onset_est=start,published=self.tick,code=code,source=self.model["catalog"][code][ix])

if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser(description="Monitor a synchronized (frames,8,5) NumPy PMU stream at 30 Hz.")
    parser.add_argument("measurements")
    args=parser.parse_args()
    instance=Monitor(load_model())
    for report in np.load(args.measurements,mmap_mode="r",allow_pickle=False):
        alarm=instance.step(report)
        if alarm:
            print(json.dumps(dict(alarm,time_s=alarm["published"]/30)))

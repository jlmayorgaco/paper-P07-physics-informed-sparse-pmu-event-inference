"""Conditional Gaussian recovery on a sealed independent stream."""
import argparse
from functools import lru_cache
import hashlib
import itertools

import numpy as np
import pandas as pd
from scipy.special import logsumexp

from run_stream import (Experiment, Filter, HERE, N, PARTICLES, SCRATCH, STARTS,
                        dyn, generate, log_interval, score, trajectory)

OUT = HERE / "successor"
DATA = SCRATCH.with_name("bayes_stream_643271")


class Recovery:
    def __init__(self, exp, bank):
        self.exp, self.bank = exp, bank

    @lru_cache(maxsize=67)
    def ensemble(self, key):
        mode,bus = key
        curves = []
        for a,h,d in itertools.product((.7,1.3),(.8,1.,1.2),(.8,1.2)):
            self.exp.plant.H = dyn.H*h
            self.exp.plant.D = dyn.D*d
            curves.append(trajectory(self.exp,[(mode,bus,0,a)]))
        return np.array(curves)

    def components(self,k):
        onset = STARTS[k%len(STARTS)]
        curves = self.ensemble(self.bank.keys[k])
        shifted = np.pad(curves,((0,0),(onset,0),(0,0)))[:,:2*N]
        whiten = self.exp.whiten
        past = whiten(shifted[:,:N]).reshape(len(curves),-1)
        future = whiten(shifted[:,N:]).reshape(len(curves),-1)
        scale = np.sqrt(len(curves)-1)
        return past.mean(0),future.mean(0),(past-past.mean(0))/scale,(future-future.mean(0))/scale

    def conditional(self,k,previous,current):
        m,n,x,z = self.components(k)
        post = np.eye(len(x))+x@x.T
        mean = n+z.T@np.linalg.solve(post,x@(previous-m))
        total = post+z@z.T
        residual = current-mean
        projected = z@residual
        logdet = np.linalg.slogdet(total)[1]-np.linalg.slogdet(post)[1]
        common = -.5*(residual@residual-projected@np.linalg.solve(total,projected)+logdet)
        templates = self.bank.front
        projection = templates@z.T
        c = templates@residual-projection@np.linalg.solve(total,projected)
        energy = self.bank.energy-np.sum(projection*np.linalg.solve(total,projection.T).T,axis=1)
        assert np.min(energy)>0
        root = np.sqrt(energy)
        a = c/energy
        evidence = (.5*c*a+.5*np.log(2*np.pi)-np.log(.6*root)
                    +log_interval((.7-a)*root,(1.3-a)*root))
        return common+np.r_[-np.log(4),evidence+self.bank.priors]

    def decide(self,old,previous,current,rng):
        cdf = np.exp(old-logsumexp(old)).cumsum()
        cdf[-1] = 1.
        sample = np.searchsorted(cdf,(np.arange(PARTICLES)+rng.random(PARTICLES))/PARTICLES)
        scores = []
        for j,count in zip(*np.unique(sample,return_counts=True)):
            if j:
                row = self.conditional(j-1,previous,current)
            else:
                row = self.bank.likelihood(current)[0]-.5*(current@current)
            scores.append(row+np.log(count))
        return self.bank.decide(logsumexp(scores,axis=0))


def predict():
    exp = Experiment()
    bank = Filter(exp)
    recovery = Recovery(exp,bank)
    hist_rng,ensemble_rng = map(np.random.default_rng,(91283,19394))
    records = []
    for rid,record in enumerate(np.load(DATA/"observations.npy")):
        for w,obs in enumerate(np.split(record,2)):
            y = exp.whiten(obs).ravel()
            evidence,means = bank.likelihood(y)
            bayes = bank.decide(evidence)
            decisions = dict(profile=bank.profile(y),bayes=bayes,history=bayes,ensemble=bayes)
            if w:
                decisions["history"] = bank.carry(y,old,old_means,hist_rng)
                decisions["ensemble"] = recovery.decide(old,previous,y,ensemble_rng)
            for name,(mode,bus) in decisions.items():
                records.append(dict(record=rid,window=w,method=name,pred=mode,asset=bus))
            old,old_means,previous = evidence,means,y
    path = OUT/"predictions.csv"
    pd.DataFrame(records).to_csv(path,index=False)
    (OUT/"seal.sha256").write_text(hashlib.sha256(path.read_bytes()).hexdigest())


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("stage",choices=("generate","predict","score"))
    a=p.parse_args()
    OUT.mkdir(exist_ok=True)
    if a.stage=="generate":
        generate(643271,OUT,DATA)
    elif a.stage=="predict":
        predict()
    else:
        score(OUT)

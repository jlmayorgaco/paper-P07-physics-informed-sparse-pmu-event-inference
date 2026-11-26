"""Generate continuous nonlinear records, infer from sensors only, then score seals."""
import argparse
import hashlib
import itertools
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import log_ndtr, logsumexp
from scipy.stats import truncnorm
from sklearn.metrics import confusion_matrix, f1_score

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "branch_current_trial"))
from run import Experiment, N, SIGMA, dyn

MODES = ("quiet", "weak", "generation", "load")
STARTS = np.arange(3, 25, 3)
PARTICLES = 16
SCRATCH = HERE.parents[1] / "tmp/bayes_stream_476209"


def catalog(exp):
    return dict(weak=list(range(1, 40)), generation=sorted(dyn.GEN),
                load=sorted(b for b,s in exp.plant.base_load.items() if s.real > 0))


def trajectory(exp, events):
    plant = exp.plant
    x = plant.init_state()
    z0 = plant.zg(())
    configs = []
    for mode, bus, onset, a in events:
        z, acceleration = z0, np.zeros(10)
        if mode == "generation":
            j = dyn.GEN.index(bus)
            acceleration[j] = .1*a/(2*plant.H[j])
        else:
            demand = .01 if mode == "weak" else .1*plant.base_load[bus]
            y = plant.Y0 + plant.Yg
            y[bus-1,bus-1] += np.conj(demand*a)/plant.net.vbase[bus]**2
            z = np.linalg.inv(y)[:,plant.gi]
        configs.append((onset,z,acceleration))
    output = []
    for t in range(2*N):
        z, acceleration = z0, np.zeros(10)
        for u, active_z, active_acceleration in configs:
            if u <= t < u+30:
                z, acceleration = active_z, active_acceleration
        def derivative(state):
            dx, _ = plant._f(state,z)
            dx[10:20] += acceleration
            return dx
        dt = dyn.DT
        for _ in range(dyn.REPORT_EVERY):
            k1 = derivative(x)
            k2 = derivative(x+dt*k1/2)
            k3 = derivative(x+dt*k2/2)
            k4 = derivative(x+dt*k3)
            x += dt*(k1+2*k2+2*k3+k4)/6
        output.append(exp.measure(z @ (plant.yg*plant.mag*np.exp(1j*x[:10]))))
    return np.array(output)


def continuous_noise(model, rng):
    # Same state update and 199-report burn-in as the preceding branch experiment.
    states = rng.multivariate_normal(np.zeros(len(model.q)),model.q,size=199+2*N)
    for t in range(1,len(states)):
        states[t] += model.transition @ states[t-1]
    return np.clip(states[199:] @ model.loading,-8,8)*model.scale


def generate(seed=476209, folder=HERE, scratch=SCRATCH):
    exp = Experiment()
    sites = catalog(exp)
    rng = np.random.default_rng(seed)
    schedules = list(itertools.product(MODES, repeat=2))*8
    rng.shuffle(schedules)
    truth, records = [], []
    for rid, modes in enumerate(schedules):
        exp.plant.H = dyn.H*rng.uniform(.8,1.2)
        exp.plant.D = dyn.D*rng.uniform(.8,1.2)
        events = []
        for w,mode in enumerate(modes):
            bus = 0
            if mode != "quiet":
                bus = int(rng.choice(sites[mode]))
                events.append((mode,bus,int(w*N+rng.choice(STARTS)),rng.uniform(.7,1.3)))
            truth.append(dict(record=rid,window=w,mode=mode,bus=bus))
        y = trajectory(exp,events)
        y[:,:16] += rng.normal(0,SIGMA,y[:,:16].shape)
        base = abs(exp.i0)+exp.mag.center
        y[:,16:24] = np.maximum(0,base+y[:,16:24]+continuous_noise(exp.mag,rng))-base
        y[:,24:] = (y[:,24:]+continuous_noise(exp.ang,rng)+180)%360-180
        records.append(y)
    scratch.mkdir(parents=True,exist_ok=True)
    np.save(scratch/"observations.npy",records)
    pd.DataFrame(truth).to_csv(folder/"truth.csv",index=False)


def log_interval(lo, hi):
    # In the positive tail subtract survival probabilities.
    right = lo > 0
    upper = log_ndtr(np.where(right,-lo,hi))
    lower = log_ndtr(np.where(right,-hi,lo))
    return upper + np.log(-np.expm1(lower-upper))


class Filter:
    def __init__(self, exp):
        front, tail, self.keys, self.priors = [], [], [], []
        for mode,sites in catalog(exp).items():
            for bus in sites:
                signature = trajectory(exp,[(mode,bus,0,1.)])
                for u in STARTS:
                    shifted = np.pad(signature,((u,0),(0,0)))[:2*N]
                    front.append(exp.whiten(shifted[:N]).ravel())
                    tail.append(exp.whiten(shifted[N:]).ravel())
                    self.keys.append((mode,bus))
                    self.priors.append(-np.log(4*len(sites)*len(STARTS)))
        self.front = np.asarray(front)
        self.tail = np.asarray(tail)
        self.energy = np.sum(self.front**2,axis=1)
        self.root = np.sqrt(self.energy)
        self.priors = np.asarray(self.priors)

    def likelihood(self, y, profile=False):
        cross = self.front @ y
        mean = cross/self.energy
        if profile:
            a = np.clip(mean,.7,1.3)
            evidence = a*cross-.5*a*a*self.energy
        else:
            lo = (.7-mean)*self.root
            hi = (1.3-mean)*self.root
            evidence = (.5*cross*mean + .5*np.log(2*np.pi) - np.log(.6*self.root)
                        + log_interval(lo,hi))
        return np.r_[-np.log(4), evidence+self.priors], mean

    def decide(self, logp):
        prob = np.exp(logp-logsumexp(logp))
        if prob[0]>=.5:
            return "quiet",0
        # Repeated entries correspond to onset candidates, then assets.
        by_site = {}
        for key,p in zip(self.keys,prob[1:]):
            by_site[key] = by_site.get(key,0.)+p
        masses = {mode:sum(v for (m,_),v in by_site.items() if m==mode) for mode in MODES[1:]}
        family = max(masses,key=masses.get)
        return max((k for k in by_site if k[0]==family),key=by_site.get)

    def profile(self, y):
        # Maximize over onset for each asset, then combine competing sites/families.
        logp,_ = self.likelihood(y,profile=True)
        groups = logp[1:].reshape(-1,len(STARTS))
        best = np.argmax(groups,axis=1)
        score = groups[np.arange(len(groups)),best]+np.log(len(STARTS))
        groups[:] = -np.inf
        groups[np.arange(len(groups)),best] = score
        return self.decide(logp)

    def carry(self, y, old, means, rng):
        p = np.exp(old-logsumexp(old))
        cdf = p.cumsum()
        cdf[-1] = 1.
        indices = np.searchsorted(cdf,(np.arange(PARTICLES)+rng.random(PARTICLES))/PARTICLES)
        scores = []
        for j in indices:
            residual = y
            if j:
                k = j-1
                sd = 1/self.root[k]
                a = truncnorm.ppf(rng.random(),(.7-means[k])/sd,(1.3-means[k])/sd,
                                  loc=means[k],scale=sd)
                residual = y-a*self.tail[k]
            evidence,_ = self.likelihood(residual)
            scores.append(evidence-.5*(residual@residual))
        return self.decide(logsumexp(scores,axis=0))


def predict():
    exp = Experiment()
    bank = Filter(exp)
    rng = np.random.default_rng(91283)
    rows = []
    for rid,record in enumerate(np.load(SCRATCH/"observations.npy")):
        for w,obs in enumerate(np.split(record,2)):
            y = exp.whiten(obs).ravel()
            evidence, means = bank.likelihood(y)
            bayes = bank.decide(evidence)
            history = bank.carry(y,old,old_means,rng) if w else bayes
            for name,(mode,bus) in zip(("profile","bayes","history"),(bank.profile(y),bayes,history)):
                rows.append(dict(record=rid,window=w,method=name,pred=mode,asset=bus))
            old,old_means = evidence,means
    path = HERE/"predictions.csv"
    pd.DataFrame(rows).to_csv(path,index=False)
    (HERE/"seal.sha256").write_text(hashlib.sha256(path.read_bytes()).hexdigest())


def score(folder=HERE):
    path = folder/"predictions.csv"
    assert hashlib.sha256(path.read_bytes()).hexdigest()==(folder/"seal.sha256").read_text()
    truth = pd.read_csv(folder/"truth.csv")
    truth["previous"] = truth.groupby("record")["mode"].shift().fillna("quiet")
    joined = pd.read_csv(path).merge(truth,validate="many_to_one")
    report = []
    for method,g in joined.groupby("method"):
        for context,group in (("all",g),("after_event",g[g.previous!="quiet"]),
                              ("from_rest",g[g.previous=="quiet"])):
            event = group["mode"]!="quiet"
            alarm = group.pred!="quiet"
            family = group.pred==group["mode"]
            exact = family & (group.bus==group.asset)
            report.append(dict(method=method,context=context,events=int(event.sum()),
                quiet=int((~event).sum()), detected=int((event&alarm).sum()),
                family_correct_events=int((event&family).sum()),joint=int((event&exact).sum()),
                false_alarms=int((~event&alarm).sum()),
                macro_f1=f1_score(group["mode"],group.pred,labels=MODES,average="macro"),
                confusion=confusion_matrix(group["mode"],group.pred,labels=MODES).tolist()))
    (folder/"scores.json").write_text(json.dumps(report,indent=2))
    for row in report:
        if row["context"]=="all": print(row)


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("stage",choices=("generate","predict","score"))
    args=p.parse_args()
    {"generate":generate,"predict":predict,"score":score}[args.stage]()

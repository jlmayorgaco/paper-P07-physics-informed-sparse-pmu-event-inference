"""Causal marginal evidence for newly started interventions on the measured electrical graph."""
from collections import deque

import numpy as np
from numba import njit
from scipy.special import logsumexp

from common import DATA, MODEL, load
from discrepancy import FILE
from operators import TAIL, WINDOW, coordinates


class Bank:
    def __init__(self):
        folder = DATA/"bank"
        for k in load(folder/"inputs.json")["arrays"]:
            setattr(self,k,np.load(folder/(k+".npy"),mmap_mode="r",allow_pickle=False))
        # Ages are contiguous in time for the posterior recursion. A row covers all marks at one age.
        self.templates = np.ascontiguousarray(self.waves[self.young,:WINDOW].transpose(1,0,2),dtype=float)
        self.matrix = self.templates.reshape(-1,31)
        self.energy = np.einsum("amc,amc->am",self.templates,self.templates)
        self.young_group = self.group[self.young]
        self.group_logprior = self.logprior[None,:]
        with np.load(FILE) as arc:
            self.discrepancy = dict(arc)
        self.matrices,self.energies = [self.matrix],[self.energy]
        for a1,a2,w in zip(self.discrepancy["ar1"],self.discrepancy["ar2"],self.discrepancy["white"]):
            increments = self.templates.copy()
            increments[1:] -= self.templates[:-1]@a1.T
            increments[2:] -= self.templates[:-2]@a2.T
            increments = np.ascontiguousarray(increments@w.T)
            self.matrices.append(increments.reshape(-1,31))
            self.energies.append(np.einsum("amc,amc->am",increments,increments))


@njit(cache=True)
def update_scores(previous, projection, energy, concentration, multiplier, valid):
    m = energy.shape[1]
    for age in range(valid-1,-1,-1):
        for j in range(m):
            den = max(1e-12,concentration+energy[age,j]-2*projection[age,j])
            ratio = multiplier*np.log(concentration/den)
            previous[age,j] = (previous[age-1,j] if age else 0.)+ratio


class Observer:
    """One observer per independent stream. All timestamps are actual publication times."""
    def __init__(self, bank, model, config):
        self.bank, self.model = bank, model
        self.threshold = config["log_gate"]
        self.identify = config["identify"]
        self.hazard = config["hazard"]
        self.nu = float(model["nu"])
        self.k = -1
        self.count = 0
        self.score = np.zeros_like(bank.energy)
        self.prefix = []
        self.center = None
        self.state = np.zeros(30)
        self.noise = np.zeros(31)
        self.variance = 1.
        self.previous = None
        self.context = 0
        self.lag1,self.lag2 = np.zeros(31),np.zeros(31)
        self.carry = np.zeros((TAIL,31))
        self.carry_start = 0
        self.history = deque(maxlen=WINDOW)

    def _carry(self):
        age = self.k-self.carry_start
        return self.carry[age] if 0<=age<TAIL else np.zeros(31)

    def _log_measure(self, error_sq, variance):
        return -.5*(self.nu+31)*np.log1p(error_sq/(self.nu*variance))

    def _continuation(self, z, v):
        residual = z-self._carry()
        if self.previous is None:
            return residual,v
        start,ids,logw = self.previous
        age = self.k-start
        if age>=TAIL:
            self.previous = None
            return residual,v
        means = np.asarray(self.bank.waves[ids,age],dtype=float)
        weights = np.exp(logw)
        forecast = weights@means
        # A common scaled covariance represents the still uncertain previous return time.
        spread = weights@np.sum((means-forecast)**2,axis=1)/31
        posterior = logw+self._log_measure(np.sum((residual-means)**2,axis=1),v)
        self.previous = (start,ids,posterior-logsumexp(posterior))
        return residual-forecast, v+spread

    def _commit(self, start, group):
        # Compress the older episode only after publishing the next one. Its expected remaining
        # tail stays in the null and alternative predictions, including after restoration.
        old_age = self.k-self.carry_start
        carry = np.zeros_like(self.carry)
        remaining = max(0,TAIL-old_age)
        if remaining:
            carry[:remaining] = self.carry[old_age:]
        if self.previous is not None:
            old_start,ids,logw = self.previous
            age = self.k-old_start
            if age<TAIL:
                carry[:TAIL-age] += np.einsum("i,itc->tc",np.exp(logw),self.bank.waves[ids,age:])
        self.carry, self.carry_start = carry,self.k
        ids = np.flatnonzero(self.bank.group==group)
        logw = np.log(self.bank.weight[ids])
        for tick,residual,v in self.history:
            if tick>=start:
                means = self.bank.waves[ids,tick-start]
                logw += self._log_measure(np.sum((residual-means)**2,axis=1),v)
        self.previous = (start,ids,logw-logsumexp(logw))
        self.context = int(self.bank.code[group])
        age = self.k-start
        lag = list(self.history)
        weights = np.exp(self.previous[2])
        self.lag1 = lag[-1][1]-weights@self.bank.waves[ids,age]
        self.lag2 = (lag[-2][1]-weights@self.bank.waves[ids,age-1]
                     if age>0 and len(lag)>1 else np.zeros(31))
        self.count = 0
        self.history.clear()

    def step(self, report):
        raw = coordinates(report,self.model["floor"])
        self.k += 1
        if self.center is None:
            self.prefix.append(raw)
            if len(self.prefix)==30:
                self.center = np.mean(self.prefix,axis=0)
                for row in self.prefix:
                    self._innovation(row)
                self.prefix.clear()
            return []
        z,v = self._innovation(raw)
        return self._scan(z,v)

    def _innovation(self, raw):
        m = self.model
        y = (raw-self.center)/m["scale"]
        forecast = m["normal_a"]@self.state
        z = m["white"]@(y-m["normal_h"]@forecast-m["ar"]@self.noise)
        self.state = forecast+m["gain"]@z
        self.noise = y-m["normal_h"]@self.state
        v = self.variance
        self.variance = 1.+float(m["gamma"])*np.sum((raw[:16]-self.center[:16])**2)/8
        return z,v

    def _scan(self,z,v):
        r, variance = self._continuation(z,v)
        self.history.append((self.k,r,variance))
        self.count = min(WINDOW,self.count+1)
        context = self.context
        if context:
            d = self.bank.discrepancy
            j = context-1
            w = d["white"][j]
            corrected = w@(r-d["ar1"][j]@self.lag1-d["ar2"][j]@self.lag2)
            lag = w@self.lag1
            variance = max(variance,1.+d["gamma"][j]*(lag@lag)/31)
            self.lag2,self.lag1 = self.lag1,r
            r = corrected
        # Conditional innovations contain both sensor noise and uncertainty about rotor states.
        # Student predictive ratios integrate an unknown scale; their Gaussian limit is u-j/2.
        energy = self.bank.energies[context]
        proj = (self.bank.matrices[context]@r).reshape(energy.shape)
        concentration = self.nu*variance+r@r
        update_scores(self.score,proj,energy,concentration,.5*(self.nu+31),self.count)
        if self.k%3:
            return []
        logmass = self.score[:self.count]+self.bank.group_logprior
        peak = logmass.max()
        logprior = np.log(np.expm1(-self.count*np.log1p(-self.hazard))/self.count)
        # log(sum(exp)) <= max + log(number of terms).
        if peak+np.log(logmass.size)+logprior<self.threshold:
            return []
        mass = np.exp(logmass-peak)
        total = mass.sum()
        if peak+np.log(total)+logprior<self.threshold:
            return []
        by_group = np.bincount(self.bank.young_group,weights=mass.sum(axis=0),minlength=len(self.bank.code))
        g = int(by_group.argmax())
        if by_group[g]<self.identify*total:
            return []
        age = int(mass[:,self.bank.young_group==g].sum(axis=1).argmax())
        start = self.k-age
        self._commit(start,g)
        return [dict(detected=self.k,published=self.k,code=int(self.bank.code[g]),
                     source=str(self.bank.site[g]),onset_est=start)]


def run(record,bank,model,config):
    observer = Observer(bank,model,config)
    return [a for report in record for a in observer.step(report)]

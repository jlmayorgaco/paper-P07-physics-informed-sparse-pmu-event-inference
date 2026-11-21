"""Recovery-conditioned likelihood of a second switch from relative phasor components."""
from dataclasses import dataclass
from phase_data import angular
from model import SwitchModel, contrasts
import numpy as np
from scipy.special import softmax
from sklearn.covariance import LedoitWolf


def observations(y):
    return np.column_stack((y[:,:16],angular(y)))


def prefix(z):
    return np.diff(z[:30].reshape(6,5,z.shape[1]).mean(axis=1),axis=0).ravel()


@dataclass
class PhaseRecovery:
    curves: np.ndarray
    loads: np.ndarray
    scale: np.ndarray
    filters: np.ndarray
    norm: np.ndarray
    logprior: np.ndarray

    def residual(self,y,clear):
        z = observations(y)
        dot = self.filters@(prefix(z[clear:])/self.scale)
        amplitude = dot/(1+self.norm)
        evidence = np.where(self.loads,.5*(dot*amplitude-np.log1p(self.norm)),dot-.5*self.norm)
        p = softmax(np.r_[self.logprior+evidence,np.log(1/3)])[:-1]
        weights = p*np.where(self.loads,amplitude,1.)
        curve = (weights.astype(self.curves.dtype)@self.curves).reshape(-1,z.shape[1])
        r = z[clear:]-z[:30].mean(axis=0)
        overlap = min(len(curve),len(r))
        r[:overlap] -= curve[:overlap]
        r[overlap:] -= curve[-1]
        return r


def train_recovery(library,train):
    curves,ids = library["curves"],library["ids"]
    quiet = np.stack([prefix(observations(y[:30])) for y,_ in train])
    scale = quiet.std(axis=0)
    standardized = np.stack([prefix(z) for z in curves])/scale
    covariance = LedoitWolf().fit(quiet/scale).covariance_
    filters = np.linalg.solve(covariance,standardized.T).T
    norm = np.einsum("ij,ij->i",standardized,filters)
    prior = np.array([np.log(1/(3*9*np.count_nonzero(ids==a))) for a in ids])
    return PhaseRecovery(curves.reshape(len(ids),-1),np.char.startswith(ids,"BUS"),scale,filters,norm,prior)


def train_switch(residuals, library, length, width, ages):
    blocks = np.concatenate([contrasts(r,length,width,True) for r in residuals])
    center,scale = blocks.mean(axis=0),blocks.std(axis=0)
    assert np.all(scale>0)
    blocks -= center
    blocks /= scale
    covariance = LedoitWolf(assume_centered=True).fit(blocks).covariance_
    curves = library["curves"]
    times = np.arange(length)[None,:]-length+np.asarray(ages)[:,None]
    signals = curves[:,np.clip(times,0,curves.shape[1]-1)]*(times>=0)[None,:,:,None]
    means = signals.reshape(len(curves),len(ages),length//width,width,curves.shape[-1]).mean(axis=3)
    differences = np.diff(means,axis=2).reshape(len(curves),len(ages),-1)
    shifts = np.concatenate((means.mean(axis=2),differences),axis=2).reshape(-1,len(scale))/scale
    filters = np.linalg.solve(covariance,shifts.T).T
    prior = np.repeat(library["probabilities"]/len(ages),len(ages))
    offset = np.log(prior)-.5*np.einsum("ij,ij->i",shifts,filters)
    ids = np.repeat(library["ids"],len(ages))
    names = np.unique(ids)
    families = np.where(np.char.startswith(names,"BUS"),"load","line")
    return SwitchModel(length,width,center,scale,filters,offset,names,families,
                       tuple(np.flatnonzero(ids==a) for a in names),True)

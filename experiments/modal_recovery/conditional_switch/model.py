"""Likelihood ratios of onset-aligned PMU changes against continuing recovery."""
from dataclasses import dataclass
import numpy as np
from scipy.special import logsumexp
from sklearn.covariance import LedoitWolf


def contrasts(y, length, width, level=False):
    """Adjacent bin-mean differences, each row ending at the publication report."""
    if length % width or len(y) < length:
        raise ValueError("Insufficient PMU history or incompatible bin width")
    cumulative = np.concatenate([np.zeros((1, y.shape[1])), np.cumsum(y, axis=0)])
    ends = np.arange(length, len(y) + 1)[:, None] + np.arange(-length,1,width)
    averages = np.diff(cumulative[ends], axis=1) / width
    differences=np.diff(averages, axis=1).reshape(len(ends), -1)
    return np.column_stack((averages.mean(axis=1),differences)) if level else differences


def switch_vectors(signatures, length, width, ages, level=False):
    """The given age is the number of observed samples since a candidate switch."""
    time = np.arange(length)[None, :] - length + np.asarray(ages)[:, None]
    signals = signatures[:, np.clip(time, 0, signatures.shape[1]-1)] * (time >= 0)[None,:,:,None]
    bins = signals.reshape(*signals.shape[:2], length // width, width, 16).mean(axis=3)
    differences=np.diff(bins, axis=2).reshape(len(signatures),len(ages),-1)
    return np.concatenate((bins.mean(axis=2),differences),axis=2) if level else differences


@dataclass
class SwitchModel:
    length: int
    width: int
    center: np.ndarray
    scale: np.ndarray
    filters: np.ndarray
    offset: np.ndarray
    names: np.ndarray
    families: np.ndarray
    groups: tuple
    level: bool = False

    def matched(self, z):
        return ((z-self.center)/self.scale) @ self.filters.T + self.offset

    def scores(self, y):
        return logsumexp(self.matched(contrasts(y,self.length,self.width,self.level)), axis=1)

    def classify(self, y):
        if len(y) != self.length:
            raise ValueError("Diagnosis needs exactly one ending window")
        ratios = self.matched(contrasts(y,self.length,self.width,self.level))[0]
        masses = np.array([logsumexp(ratios[ix]) for ix in self.groups])
        families = np.unique(self.families)
        family = families[np.argmax([logsumexp(masses[self.families==f]) for f in families])]
        site = self.names[np.argmax(np.where(self.families==family, masses, -np.inf))]
        return [str(family), str(site)]


def fit(recoveries, templates, length, width, ages, level=False):
    # The templates have zero mean shift before their candidate onset. The joint
    # Gaussian ratio is therefore also the post-onset ratio conditional on that prefix.
    z = np.concatenate([contrasts(y[clear:],length,width,level) for y,clear in recoveries])
    center, scale = np.mean(z,axis=0), np.std(z,axis=0)
    cov = LedoitWolf(assume_centered=True).fit((z-center)/scale).covariance_
    d = switch_vectors(templates["signals"], length, width, ages,level).reshape(-1,z.shape[1]) / scale
    matched = np.linalg.solve(cov,d.T).T
    prior = np.repeat(templates["probabilities"] / len(ages), len(ages))
    offset = np.log(prior) - 0.5*np.einsum("ij,ij->i",d,matched)
    ids = np.repeat(templates["ids"],len(ages))
    names = np.unique(ids)
    families = np.array(["load" if x.startswith("BUS") else "line" for x in names])
    groups = tuple(np.flatnonzero(ids==a) for a in names)
    return SwitchModel(length,width,center,scale,matched,offset,names,families,groups,level)

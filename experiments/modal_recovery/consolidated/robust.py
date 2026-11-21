"""Profile the eight unknown PMU clock phases before applying physical switch likelihoods."""
from dataclasses import dataclass
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"clock_stress"))
from stress_plan import Errors,Setting,phase_data,study
from phase_model import observations,prefix,train_switch
from benchmark import call
from scipy.special import softmax
from sklearn.covariance import LedoitWolf
import numpy as np
import joblib

TMP = study.ROOT/"tmp/consolidated"
RESULT = HERE/"results"
CONDITIONS = {
    "native":Setting("nominal"),
    "joint":Setting("joint",angle=.005,jitter=.25),
    "severe":Setting("joint",angle=.008,jitter=.5),
    "holdover":Setting("joint",angle=.005,jitter=.1,drift=.07,step=1.),
}


@dataclass
class Recovery:
    columns: np.ndarray
    curves: np.ndarray
    loads: np.ndarray
    scale: np.ndarray
    filters: np.ndarray
    norm: np.ndarray
    logprior: np.ndarray

    def residual(self,y,clear):
        z = observations(y)[:,self.columns]
        dot = self.filters @ (prefix(z[clear:])/self.scale)
        amplitude = dot/(1+self.norm)
        evidence = np.where(self.loads,.5*(dot*amplitude-np.log1p(self.norm)),dot-.5*self.norm)
        mass = softmax(np.r_[self.logprior+evidence,np.log(1/3)])[:-1]
        predicted = (mass*np.where(self.loads,amplitude,1.)).astype(self.curves.dtype) @ self.curves
        curve = predicted.reshape(-1,len(self.columns))
        r = z[clear:]-z[:30].mean(axis=0)
        common = min(len(r),len(curve))
        r[:common] -= curve[:common]
        r[common:] -= curve[-1]
        return r


def fit_recovery(lib,train,columns):
    curves = np.ascontiguousarray(lib["curves"][:,:,columns])
    ids = lib["ids"]
    quiet = np.stack([prefix(observations(y[:30])[:,columns]) for y,_ in train])
    scale = quiet.std(axis=0)
    shapes = np.stack([prefix(z) for z in curves])/scale
    cov = LedoitWolf().fit(quiet/scale).covariance_
    filters = np.linalg.solve(cov,shapes.T).T
    norm = np.einsum("ij,ij->i",shapes,filters)
    prior = np.array([np.log(1/(3*9*np.count_nonzero(ids==a))) for a in ids])
    return Recovery(columns,curves.reshape(len(ids),-1),np.char.startswith(ids,"BUS"),scale,filters,norm,prior)


def records(split):
    manifest = study.read(phase_data.TMP/split/"manifest.json")
    for i,(k,digest) in enumerate(sorted(manifest["hashes"].items())):
        path = phase_data.folder(split)/(k+".npz")
        assert study.digest(path)==digest
        y,c = study.unpack(path)
        yield i,k,y,c


def fit(name):
    columns = np.r_[0:16,23:31] if name=="local" else np.arange(31)
    train = []
    for i,k,y,c in records("fit"):
        setting = list(CONDITIONS.values())[i%len(CONDITIONS)]
        train.append((Errors(470000+i,len(y),c).apply(y,setting),c))
    with np.load(phase_data.TMP/"recovery.npz") as z:
        background = fit_recovery(z,train,columns)
    residuals = [background.residual(y,c) for y,c in train]
    with np.load(phase_data.TMP/"switch.npz") as z:
        lib = dict(curves=z["curves"][:,:,columns],ids=z["ids"],probabilities=z["probabilities"])
        detector = train_switch(residuals,lib,60,4,(5,12,20,32,42))
        source = train_switch(residuals,lib,84,4,np.arange(29,72))
    TMP.mkdir(exist_ok=True,parents=True)
    joblib.dump((background,detector,source),TMP/(name+".joblib"),compress=3)


def decision(weights,y,c,tau):
    bg,gate,source = weights
    return call(bg.residual(y,c),c,gate,source,tau)


if __name__=="__main__":
    from robust import fit
    fit(sys.argv[1])

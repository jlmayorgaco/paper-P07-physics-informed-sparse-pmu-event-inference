"""Estimate the first physical intervention from the PMU history preceding clearance."""
from dataclasses import dataclass
from robust import TMP,CONDITIONS,Errors,records,phase_data,study,observations,train_switch,joblib
import numpy as np
from sklearn.covariance import LedoitWolf
import sys


@dataclass
class HistoryRecovery:
    columns: np.ndarray
    filters: np.ndarray
    energy: np.ndarray
    curves: np.ndarray
    offsets: np.ndarray
    loads: np.ndarray

    def residual(self,y,clear):
        z=observations(y)
        z-=z[:30].mean(axis=0)
        # Magnitudes and same-instrument current/voltage phase are clock invariant.
        observed=np.ascontiguousarray(z[:,np.r_[0:16,23:31]])
        earliest=max(30,clear-120)
        stop=min(clear,earliest+90)
        best=0.
        source=None
        for t in range(earliest,min(clear-59,stop)):
            n=stop-t
            dot=np.einsum("atc,tc->a",self.filters[:,:n],observed[t:stop],optimize=False)
            norm=self.energy[:,n-1]
            amp=dot/(1+norm)
            likelihood=np.where(self.loads,.5*(dot*amp-np.log1p(norm)),dot-.5*norm)
            i=int(likelihood.argmax())
            if likelihood[i]>best:
                best=float(likelihood[i])
                source=(i,clear-t,float(amp[i]) if self.loads[i] else 1.)
        r=z[clear:,self.columns].copy()
        if source is None:
            return r
        i,d,a=source
        stride=3 if self.loads[i] else 1
        ix=int(self.offsets[i]+(d-60)//stride)
        frac=((d-60)%stride)/stride
        curve=self.curves[ix]
        if frac:
            curve=(1-frac)*curve+frac*self.curves[ix+1]
        overlap=min(len(r),len(curve))
        r[:overlap]-=a*curve[:overlap]
        r[overlap:]-=a*curve[-1]
        return r


def background(train,columns):
    with np.load(phase_data.TMP/"switch.npz") as s:
        names=np.unique(s["ids"])
        nodes,_=np.polynomial.legendre.leggauss(5)
        amplitudes=.085+.055*nodes
        first=[]
        for name in names:
            signals=s["curves"][s["ids"]==name]
            if name.startswith("BUS"):
                upper=int(np.searchsorted(amplitudes,.10))
                weight=(.10-amplitudes[upper-1])/(amplitudes[upper]-amplitudes[upper-1])
                signals=(1-weight)*signals[5+upper-1]+weight*signals[5+upper]
            else:
                signals=signals[0]
            first.append(signals[:,np.r_[0:16,23:31]])
    quiet=[observations(y[:30])[:,np.r_[0:16,23:31]] for y,_ in train]
    noise=np.concatenate([q-q.mean(axis=0) for q in quiet])
    scale=noise.std(axis=0)
    precision=LedoitWolf().fit(noise/scale).precision_/scale[:,None]/scale[None,:]
    d=np.stack(first).astype(float)
    filters=d@precision
    energy=np.cumsum(np.einsum("atc,atc->at",d,filters),axis=1)
    with np.load(phase_data.TMP/"recovery.npz") as r:
        offsets=np.array([np.flatnonzero(r["ids"]==name)[0] for name in names])
        curves=np.ascontiguousarray(r["curves"][:,:,columns])
    return HistoryRecovery(columns,np.ascontiguousarray(filters),energy,curves,offsets,np.char.startswith(names,"BUS"))


def fit(name):
    columns=np.r_[0:16,23:31] if name=="history_local" else np.arange(31)
    train=[]
    for i,k,y,c in records("fit"):
        setting=list(CONDITIONS.values())[i%len(CONDITIONS)]
        train.append((Errors(470000+i,len(y),c).apply(y,setting),c))
    bg=background(train,columns)
    r=[bg.residual(y,c) for y,c in train]
    with np.load(phase_data.TMP/"switch.npz") as s:
        lib=dict(curves=s["curves"][:,:,columns],ids=s["ids"],probabilities=s["probabilities"])
        gate=train_switch(r,lib,60,4,(5,12,20,32,42))
        source=train_switch(r,lib,84,4,np.arange(29,72))
    joblib.dump((bg,gate,source),TMP/(name+".joblib"),compress=3)


if __name__=="__main__":
    from first_history import fit
    fit(sys.argv[1])

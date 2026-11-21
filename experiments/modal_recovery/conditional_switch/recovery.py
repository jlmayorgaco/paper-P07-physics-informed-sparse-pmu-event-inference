"""Estimate the uninterrupted physical recovery from its first second of PMUs."""
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import data
from cohort import TMP
import numpy as np
from scipy.special import softmax
from sklearn.covariance import LedoitWolf


def clean(task):
    asset, dwell = task
    event=data.sim.event(np.random.default_rng(0),asset,60,2*dwell)
    event["amplitude"]=.10 if asset["family"]=="load" else None
    clear=30+dwell
    sim=data.sim
    t,v,i,status=sim.plant.simulate(dict(duration_s=clear/30+9,events=[event]),sim.sim.MAP)
    assert status["valid"] and len(t)==clear+271
    meters=sim.sim.MAP
    base=100e6/(np.sqrt(3)*1000*sim.sim.KV[meters.terminal.to_numpy()-1])
    y=np.column_stack((abs(v[:,np.array(sim.sim.REPORT["pmus"])-1]),abs(i)*base*meters.gain.to_numpy()))
    output=y[clear:]-y[0]
    if dwell==60:
        # Nontrivial check against the full phasor reporting operator.
        _, raw=sim.physical(dict(duration_s=clear/30+9,events=[event]))
        expected=data.channels(raw)
        np.testing.assert_allclose(output,expected[clear:]-expected[0],rtol=1e-8,atol=1e-8)
    return output


def build():
    data.sim.initialize()
    tasks=[(a,d) for a in data.sim.assets for d in range(60,121,1 if a["family"]=="line" else 3)]
    with ProcessPoolExecutor(10,initializer=data.sim.initialize) as pool:
        traces=list(pool.map(clean,tasks,chunksize=3))
    with (TMP/"recoveries.npz").open("xb") as stream:
        np.savez_compressed(stream,curves=np.asarray(traces,dtype=np.float32),
                            ids=[a["id"] for a,_ in tasks], dwell=[d for _,d in tasks])


def prefix_shape(y):
    # Offsets cancel without a known pre-event operating phasor.
    bins=y[:30].reshape(6,5,16).mean(axis=1)
    return np.diff(bins,axis=0).ravel()


@dataclass
class Recovery:
    curves: np.ndarray
    ids: np.ndarray
    scale: np.ndarray
    weights: np.ndarray
    norm: np.ndarray
    logprior: np.ndarray
    use_quiet_reference: bool = False

    def residual(self,y,clear):
        is_load=np.char.startswith(self.ids,"BUS")
        dot=self.weights @ (prefix_shape(y[clear:])/self.scale)
        # For a prior load, its unknown signed size has N(0,1) prior in units of 10%.
        amp=dot/(1+self.norm)
        ll=np.where(is_load,.5*dot*amp-.5*np.log1p(self.norm), dot-.5*self.norm)
        p=softmax(np.r_[self.logprior+ll,np.log(1/3)])[:-1]
        curve=(p*np.where(is_load,amp,1.)).astype(self.curves.dtype) @ self.curves
        curve=curve.reshape(-1,16)
        n=len(y)-clear
        r=y[clear:].astype(float,copy=True)
        used=min(len(curve),n)
        r[:used]-=curve[:used]
        if used<n:
            r[used:]-=curve[-1]
        reference = y[:30] if self.use_quiet_reference else r[:30]
        return r-reference.mean(axis=0)


def fit(curves, quiet):
    records=curves["curves"].astype(np.float64)
    ids=curves["ids"]
    q=np.stack([prefix_shape(x) for x in quiet])
    scale=q.std(axis=0)
    cov=LedoitWolf().fit(q/scale).covariance_
    x=np.stack([prefix_shape(y) for y in records])/scale
    weights=np.linalg.solve(cov,x.T).T
    norm=np.einsum("ij,ij->i",x,weights)
    logprior=np.array([np.log(1/(3*9*np.count_nonzero(ids==a))) for a in ids])
    return Recovery(curves["curves"].reshape(len(ids),-1),ids,scale,weights,norm,logprior)


if __name__=="__main__":
    build()

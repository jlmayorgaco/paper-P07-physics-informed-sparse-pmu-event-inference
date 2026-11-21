"""Prospective measurement-error grid for the frozen relative-phase estimator."""
from dataclasses import dataclass
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent/"relative_phase"))
import phase_data
from phase_data import study
import campaign as frozen
import numpy as np
from scipy.signal import lfilter
from scipy.special import ndtr

TMP = study.ROOT/"tmp/clock_stress"
RESULT = HERE/"results"
SIZES = {"catalog":480,"bus31":120}
SEEDS = {"catalog":73948211,"bus31":16480373}
ERROR_SEED = 19662273
DEG_PER_US = 360*60e-6


@dataclass(frozen=True)
class Setting:
    name: str
    angle: float = 0
    jitter: float = 0
    offset: float = 0
    drift: float = 0
    step: float = 0

    @property
    def key(self):
        return self.name+"_"+str(max(self.angle,self.jitter,self.offset,self.drift,self.step))


GRID = [Setting("nominal")]
for family, levels in {
    "angle":(.0001,.00025,.0005,.001,.002,.003,.004,.005,.008,.01,.02),
    "jitter":(.005,.01,.025,.05,.075,.1,.15,.25,.5,1,2.5),
    "offset":(1,26.5),
    "drift":(.005,.01,.025,.05,.07,.1,.25,.5,1,10),
    "step":(.025,.05,.1,.25,.5,1,2.5,5,10,26.5),
}.items():
    GRID.extend(Setting(family,**{family:x}) for x in levels)
GRID.extend(Setting("joint",angle=a,jitter=j) for a,j in
            ((.0001,.005),(.00025,.01),(.0005,.025),(.001,.05),(.0015,.075),
             (.002,.1),(.003,.15),(.005,.25),(.008,.5),(.01,1)))
assert len({x.key for x in GRID})==len(GRID)


def stationary(rng,n,dim,tau):
    rho = np.exp(-1/(30*tau))
    e = rng.standard_normal((n,dim))*np.sqrt(1-rho**2)
    e[0] = rng.standard_normal(dim)
    return lfilter([1.],[1.,-rho],e,axis=0)


class Errors:
    def __init__(self,stream,n,clear):
        rng = np.random.default_rng([ERROR_SEED,int(stream)])
        # A bounded marginal with unit variance and serial dependence.
        self.instrument = np.sqrt(3)*(2*ndtr(stationary(rng,n,16,.1))-1)
        self.clock = stationary(rng,n,8,.5)
        self.fixed = rng.uniform(-1,1,size=8)
        self.device = int(rng.integers(8))
        sign = rng.choice([-1.,1.])
        k = np.arange(n)
        self.ramp = sign*np.clip((k-clear)/30,0.,8.)
        self.change = sign*(k>=clear+int(rng.integers(15,181)))

    def apply(self,y,s):
        if s.name=="nominal":
            return y
        delta = s.jitter*self.clock+s.offset*self.fixed
        delta[:,self.device] += s.drift*self.ramp+s.step*self.change
        shift = DEG_PER_US*delta
        out = y.copy()
        out[:,16:24] += shift+s.angle*self.instrument[:,:8]
        out[:,24:] += shift+s.angle*self.instrument[:,8:]
        out[:,16:] = (out[:,16:]+180)%360-180
        return out


def verify():
    frozen.verify_freeze()
    seal = study.read(RESULT/"protocol_seal.json")
    assert seal["weights"]==study.digest(phase_data.RESULT/"freeze.json")
    for name, checksum in seal["files"].items():
        assert study.digest(HERE/name)==checksum,name
    return seal

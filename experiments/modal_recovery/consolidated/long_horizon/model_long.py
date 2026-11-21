"""Use the full conditional recovery trajectory, preserving every frozen decision parameter."""
from copy import copy
from pathlib import Path
import sys
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from graph_estimator import GraphEstimator
from robust import TMP, RESULT, phase_data, study, Errors, CONDITIONS
from extend_curves import load_tail

OUT=HERE/"results"
WORK=TMP/"horizon"


def extend_component(weights,tail,columns):
    bg,gate,source=weights
    new=copy(bg)
    n,w=len(tail),len(columns)
    old=bg.curves.reshape(n,-1,w)
    assert old.shape[1]==271
    curves=np.concatenate((old,tail[:,:,columns]),axis=1)
    new.curves=curves.reshape(n,-1) if bg.curves.ndim==2 else curves
    return new,gate,source


def load():
    base=GraphEstimator.load()
    out=copy(base)
    tail=load_tail()
    out.nominal=extend_component(base.nominal,tail,np.arange(31))
    out.invariant=extend_component(base.invariant,tail,base.invariant[0].columns)
    out.conditional=extend_component(base.conditional,tail,base.conditional[0].columns)
    return base,out


def inputs(path,meta):
    assert study.digest(path)==meta["sha"]
    with np.load(path,allow_pickle=False) as z:
        c=int(z["clearance"])
        raw={k:z[k] for k in z.files if k!="clearance"}
    y=phase_data.channels(raw)
    seed_offset=530000 if path.parent==TMP/"pmu" else 631337
    errors=Errors(seed_offset+meta["stream"],len(y),c)
    for name in ("native","joint"):
        z=errors.apply(y,CONDITIONS[name])[:c+900]
        assert len(z)==c+900
        yield name,{k:(z[:,16:24] if k=="voltage_angle" else z[:,24:32] if k=="current_angle" else v[:len(z)]) for k,v in raw.items()},c

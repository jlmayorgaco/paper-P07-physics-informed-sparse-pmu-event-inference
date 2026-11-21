"""Retrospective long-quiet audit of the frozen physical detectors on disclosed P2 streams."""
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from robust import RESULT, CONDITIONS, Errors, phase_data, study
from graph_estimator import GraphEstimator
from adaptive import is_quiet
from odds import features
from stress_plan import frozen


def initialize():
    global current, earlier
    current=GraphEstimator.load()
    earlier=frozen.arms()


def above(y,c,weights,threshold):
    bg,gate,_=weights
    residual=bg.residual(y,c)
    n=len(residual)-gate.length+1
    return np.concatenate([gate.scores(residual[i:i+512+gate.length-1])>threshold for i in range(0,n,512)])


def counts(flags):
    return dict(episodes=int(np.count_nonzero(flags & ~np.r_[False,flags[:-1]])),reports=len(flags))


def evaluate(task):
    index,row=task
    key=row["id"]
    path=study.RUN/"observations/P2/TEST"/(key+"_nominal.npz")
    assert study.digest(path)==row["files"]["nominal"]
    with np.load(path,allow_pickle=False) as raw:
        y=phase_data.channels(raw)
    c=360
    errors=Errors(841000+index,len(y),c)
    mag=counts(above(y[:,:16],c,*earlier["magnitudes"]))
    out={}
    for name,setting in CONDITIONS.items():
        z=errors.apply(y,setting)
        angular=above(z,c,*earlier["angles"])
        graph=angular
        if not is_quiet(z,current.quality):
            local=above(z,c,current.invariant,current.thresholds[1])
            weak=current.correction.decision_function(features(current.conditional,z,c))>current.thresholds[2]
            graph=local|weak
        out[name]=dict(graph=counts(graph),angular=counts(angular),magnitude=mag)
    return key,out


if __name__=="__main__":
    manifest=study.read(study.RUN/"OBSERVATIONS_P2_TEST.json")
    rows=sorted((r for r in manifest if r["reports"]==18001),key=lambda r:r["id"])
    assert len(rows)==36
    with ProcessPoolExecutor(2,initializer=initialize) as pool:
        result={}
        for k,v in pool.map(evaluate,enumerate(rows)):
            result[k]=v
            if len(result)%6==0:
                print(len(result),"long-quiet records",flush=True)
    study.save(RESULT/"quiet_audit.json",result)

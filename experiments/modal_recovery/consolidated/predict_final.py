"""Prospective detection and attribution from opaque measurement records."""
from concurrent.futures import ProcessPoolExecutor
from robust import TMP, RESULT, CONDITIONS, Errors, phase_data, study, joblib
from stress_plan import frozen
from benchmark import call
from adaptive import infer as adaptive_decision, is_quiet
from odds import weak_decision
import rocket_arm as rocket
import numpy as np
import sys


def init():
    global physics, config, weights, tree, rockets, rocket_tau, hydra
    from hydra_arm import load_head
    import torch
    torch.set_num_threads(1)
    rocket.numba.set_num_threads(1)
    physics=frozen.arms()
    seal=study.read(RESULT/"freeze.json")
    config=seal["winner"]
    weights={name:joblib.load(RESULT/(name+".joblib")) for name in seal["physical_components"]}
    tree=joblib.load(RESULT/"odds.joblib") if config["name"]=="odds" else None
    rockets=joblib.load(RESULT/"rocket.joblib")
    hydra=load_head()
    rocket_tau=seal["rocket_tau"]


def previous(arm,y,c):
    (bg,g,h),tau=physics[arm]
    return call(bg.residual(y,c),c,g,h,tau)


def graph(y,c):
    chosen=config["name"]
    if chosen not in ("adaptive","odds"):
        bg,g,h=weights[chosen]
        return call(bg.residual(y,c),c,g,h,config["tau"])
    if is_quiet(y,config["quality"]):
        return previous("angles",y,c)
    bg,g,h=weights["local"]
    base=call(bg.residual(y,c),c,g,h,config["strong_tau"])
    if chosen=="odds":
        return weak_decision(y,c,weights["history_joint"],tree,config["tau"],base)
    if config.get("weak_disabled"):
        return base
    pack=(weights["local"],weights["history_joint"],physics["angles"],config["quality"],config["strong_tau"],config["tau"])
    return adaptive_decision(y,c,pack)


def minirocket(y,c):
    z,ends,scores=rocket.scan(y,c,rockets[0])
    hits=np.flatnonzero(scores>rocket_tau)
    b=int(ends[hits[0]]) if len(hits) else None
    return dict(alarm=b,label=rocket.label(z,b,rockets[1]))


def window_decision(pred):
    label=pred["label"]
    if label is None:
        return dict(event=0 if pred["alarm"] is None else -1,site=None)
    return dict(event={"line":2,"load":4}[label[0]],site=label[1])


def compute(task):
    from literature import li_wang
    import hydra_arm
    key,meta=task
    p=TMP/"pmu"/(key+".npz")
    assert study.digest(p)==meta["sha"]
    with np.load(p,allow_pickle=False) as archive:
        raw={k:archive[k] for k in archive.files if k!="clearance"}
        c=int(archive["clearance"])
    y=phase_data.channels(raw)
    errors=Errors(530000+meta["stream"],len(y),c)
    calls,window={},{}
    short=c+271
    mag=previous("magnitudes",y[:short,:16],c)
    for name,s in CONDITIONS.items():
        full=errors.apply(y,s)
        z=full[:short]
        ang=previous("angles",z,c)
        g=graph(z,c)
        mr=minirocket(z,c)
        b=g["alarm"]
        inputs={k:a[:len(z)] for k,a in raw.items()}
        inputs.update(voltage_angle=z[:,16:24],current_angle=z[:,24:32])
        calls[name]=dict(graph=g,angular=ang,magnitude=mag,minirocket=mr,
                         li_wang=dict(alarm=b,label=li_wang(inputs,c,b)),
                         hydra=dict(alarm=b,label=hydra_arm.label(z,b,hydra)))
        if meta["long"] and name in ("native","joint"):
            x=full[:c+900]
            assert len(x)==c+900
            window[name]=dict(graph=window_decision(graph(x,c)),minirocket=window_decision(minirocket(x,c)))
    return key,calls,window


def run(workers):
    from freeze_final import verify
    verify()
    manifest=study.read(RESULT/"inputs.json")
    calls,windows={},{}
    with ProcessPoolExecutor(workers,initializer=init) as pool:
        for key,record,window in pool.map(compute,sorted(manifest["records"].items()),chunksize=3):
            calls[key]=record
            if window:
                windows[key]=window
            if len(calls)%100==0:
                print(len(calls),"opaque records",flush=True)
    assert len(calls)==600 and len(windows)==96
    study.save(RESULT/"predictions.json",calls)
    study.save(RESULT/"window_predictions.json",windows)


if __name__=="__main__":
    run(int(sys.argv[1]) if len(sys.argv)>1 else 6)

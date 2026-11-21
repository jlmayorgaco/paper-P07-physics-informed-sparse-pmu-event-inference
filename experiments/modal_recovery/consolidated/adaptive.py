"""Use the quiet pre-event reports to identify the angular measurement regime."""
from robust import TMP, RESULT, CONDITIONS, Errors, records, phase_data, study, joblib
from stress_plan import frozen
from model import contrasts
from metrics import outcomes
from scipy.special import logsumexp
import numpy as np
import sys


def noise_level(y):
    # Quiet inter-PMU voltage angle increments (degrees), immune to static offsets.
    relative = y[:30, 17:24] - y[:30, 16:17]
    increments = (np.diff(relative, axis=0) + 180) % 360 - 180
    return float(np.log(max(np.median(np.abs(increments)), 1e-12)))


def learn_quality():
    groups = [[], []]
    for i, _, y, c in records("fit"):
        errors = Errors(470000+i, len(y), c)
        for index, setting in enumerate(CONDITIONS.values()):
            groups[int(index != 0)].append(noise_level(errors.apply(y, setting)))
    return [(float(np.mean(g)), float(np.std(g))) for g in groups]


def is_quiet(y, quality):
    x = noise_level(y)
    scores = [-np.log(sd) - .5*((x-mu)/sd)**2 for mu, sd in quality]
    return scores[0] > scores[1]


def weak_scores(y, c, weights):
    bg, gate, _ = weights
    r = bg.residual(y,c)
    ix = gate.groups[list(gate.names).index("BUS31")]
    z = contrasts(r, gate.length, gate.width, gate.level)
    ratio = ((z-gate.center)/gate.scale) @ gate.filters[ix].T + gate.offset[ix]
    return logsumexp(ratio,axis=1), r


def infer(y,c,model):
    local, joint, angular, quality, strong_tau, weak_tau = model
    from benchmark import call
    if is_quiet(y,quality):
        (bg,gate,source),tau=angular
        return call(bg.residual(y,c),c,gate,source,tau)
    bg,gate,source=local
    ordinary=call(bg.residual(y,c),c,gate,source,strong_tau)
    scores,r=weak_scores(y,c,joint)
    hits=np.flatnonzero(scores>weak_tau)
    if not len(hits):
        return ordinary
    b=int(hits[0])+joint[1].length-1
    if ordinary["alarm"] is not None and ordinary["alarm"]<=c+b:
        return ordinary
    # A single-source physical alternative opens the alarm. Competing source
    # evidence at the ordinary publication deadline still determines the label.
    label=joint[2].classify(r[b+30-joint[2].length:b+30]) if b+29<len(r) else None
    return dict(alarm=c+b,label=label)


def evaluate():
    local=joblib.load(TMP/"local.joblib")
    joint=joblib.load(TMP/"history_joint.joblib")
    quality=learn_quality()
    peaks=[]
    for i,_,y,c in records("cal"):
        e=Errors(480000+i,len(y),c)
        peaks.append(max(float(weak_scores(e.apply(y,s),c,joint)[0].max()) for s in list(CONDITIONS.values())[1:]))
    thresholds=sorted(peaks)
    strong=study.read(TMP/"local_paired_selection.json")[-1]["tau"]
    angular=frozen.arms()["angles"]
    truth=study.read(phase_data.TMP/"dev/targets.json")
    options=[]
    for threshold in [thresholds[i] for i in (311,317,319)] + [max(peaks)+1e6]:
        model=(local,joint,angular,quality,strong,threshold)
        rows={s:dict(detection=0,family=0,exact=0,false=0,bus31=0) for s in CONDITIONS}
        for i,k,y,c in records("dev"):
            t=truth[k]
            e=Errors(490000+t["parent"],len(y),c)
            for name,s in CONDITIONS.items():
                call=infer(e.apply(y,s),c,model)
                v=outcomes(t,call)
                dst=rows[name]
                if t["on"] is None:
                    dst["false"]+=v["control_alarm"]
                else:
                    for m in ("detection","family","exact"):
                        dst[m]+=v[m]
                    dst["bus31"]+=v["detection"] and t["source"]=="BUS31"
        options.append(dict(name="adaptive",tau=threshold,strong_tau=strong,quality=quality,scenarios=rows))
        print(threshold,rows,flush=True)
    study.save(TMP/"adaptive_paired_selection.json",options)


if __name__=="__main__":
    evaluate()

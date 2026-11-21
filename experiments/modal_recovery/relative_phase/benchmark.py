"""Common publication deadline, matched controls, and paired endpoint counts."""
from collections import Counter
from phase_data import channels, study
from metrics import outcomes
import numpy as np
from scipy.stats import beta, binomtest


def call(residual,clear,gate,readout,threshold):
    scores = gate.scores(residual)
    hits = np.flatnonzero(scores>threshold)
    if not len(hits):
        return dict(alarm=None,label=None)
    b = gate.length-1+int(hits[0])
    end = b+29
    label = readout.classify(residual[end-readout.length+1:end+1]) if end<len(residual) else None
    return dict(alarm=clear+b,label=label)


def quiet(plant,split,background,gate,threshold=None):
    rows = study.read(study.RUN/f"OBSERVATIONS_{plant}_{split}.json")
    result = {}
    for row in rows:
        if row["reports"]!=18001:
            continue
        k = row["id"]
        path = study.RUN/"observations"/plant/split/(k+"_nominal.npz")
        assert study.digest(path)==row["files"]["nominal"]
        with np.load(path,allow_pickle=False) as z:
            r = background.residual(channels(z),360)
        lag = gate.length-1
        scores = np.concatenate([gate.scores(r[i:i+768+lag]) for i in range(0,len(r)-lag,768)])
        assert len(scores)==len(r)-lag and np.isfinite(scores).all()
        v = dict(peak=float(scores.max()),reports=len(scores))
        if threshold is not None:
            over = scores>threshold
            v["alarms"] = int(np.sum(over & ~np.r_[False,over[:-1]]))
        result[k]=v
    assert len(result)==36
    return result


def report(labels,calls):
    assert labels.keys()==calls.keys()
    groups = {}
    for k,t in labels.items():
        groups.setdefault(t["parent"],[]).append(k)
    assert len(groups)==240
    arms = ("magnitudes","angles")
    metrics = ("detection","family","exact","control_alarm","early")
    totals = {name:Counter() for name in metrics}
    discord = {name:Counter() for name in metrics}
    sources = {}
    strata = Counter()
    failures = []
    for parent,keys in groups.items():
        assert len(keys)==2
        p,n = sorted(keys,key=lambda k:labels[k]["on"] is None)
        t = labels[p]
        assert t["on"] is not None and labels[n]["on"] is None
        assert t["first"]==labels[n]["first"] and t["clearance"]==labels[n]["clearance"]
        strata[("load" if t["first"].startswith("BUS") else "line")+"/"+t["family"]]+=1
        per_source = sources.setdefault(t["source"],Counter())
        per_source["n"]+=1
        for name in metrics:
            k = n if name=="control_alarm" else p
            a,b = [outcomes(labels[k],calls[k][arm])[name] for arm in arms]
            for arm,ok in zip(arms,(a,b)):
                totals[name][arm] += ok
                if name in ("detection","family","exact"):
                    per_source[arm+"_"+name]+=ok
            discord[name]["added"]+=b and not a
            discord[name]["removed"]+=a and not b
        b = outcomes(t,calls[p]["angles"])
        if not b["exact"]:
            failures.append(dict(id=p,asset=t["source"],early=b["early"],detected=b["detection"],
                                 family=b["family"],alarm=calls[p]["angles"]["alarm"],label=calls[p]["angles"]["label"]))
    assert len(strata)==4 and set(strata.values())=={60}
    bounds = {}
    for name in metrics:
        v = discord[name]
        count = v["added"]+v["removed"]
        v["paired_p"] = float(binomtest(v["added"],count).pvalue) if count else 1.
        k = totals[name]["angles"]
        bounds[name]=[float(beta.ppf(.05,k,241-k)) if k else 0.,
                      float(beta.ppf(.95,k+1,240-k)) if k<240 else 1.]
    better_bus = sources["BUS31"]["angles_detection"]>sources["BUS31"]["magnitudes_detection"]
    efficacy = ("detection","family","exact")
    no_more = totals["control_alarm"]["angles"]<=totals["control_alarm"]["magnitudes"]
    added = discord["control_alarm"]["added"]
    return dict(parents=240,totals=totals,discordances=discord,
                one_sided_95_bounds=bounds,sources=sources,strata=strata,angle_failures=failures,
                upper95_extra_control_risk=float(beta.ppf(.95,added+1,240-added)) if added<240 else 1.,
                improved_in_development=better_bus and no_more and all(totals[m]["angles"]>=totals[m]["magnitudes"] for m in efficacy),
                meets_point_targets=all(totals[m]["angles"]>=228 for m in efficacy) and no_more and totals["control_alarm"]["angles"]<12)

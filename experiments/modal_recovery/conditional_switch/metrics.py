"""Score first alarms and delayed decisions on the original 60 Hz simulator ticks."""
from collections import Counter, defaultdict
from scipy.stats import beta, binomtest
import numpy as np


ARMS = ("current", "adjusted_gate", "adjusted")
METRICS = ("detection", "family", "exact", "control_alarm", "early")


def outcomes(target, call):
    b, label = call["alarm"], call["label"]
    if target["on"] is None:
        return {"control_alarm": b is not None}
    on, off = (round(60*target[k]) for k in ("on","off"))
    early = b is not None and 2*b < on
    detected = b is not None and on <= 2*b < off
    timely = bool(detected and label is not None and 2*(b+29) < off)
    return dict(detection=detected, family=bool(timely and label[0]==target["family"]),
                exact=bool(timely and label==[target["family"],target["source"]]), early=early)


def counts(truth, calls):
    assert calls.keys() == truth.keys()
    groups = defaultdict(list)
    for key, t in truth.items():
        groups[t["parent"]].append(key)
    assert len(groups)==240 and all(len(v)==2 for v in groups.values())
    matrices = {name: [] for name in METRICS}
    strata = Counter()
    failures = []
    by_family = defaultdict(Counter)
    for parent, keys in sorted(groups.items()):
        pos, neg = sorted(keys,key=lambda k: truth[k]["on"] is None)
        t = truth[pos]
        assert t["on"] is not None and truth[neg]["on"] is None
        assert t["clearance"]==truth[neg]["clearance"] and t["first"]==truth[neg]["first"]
        first = "load" if t["first"].startswith("BUS") else "line"
        strata[first+"-"+t["family"]] += 1
        pos_out = [outcomes(t, calls[pos][a]) for a in ARMS]
        neg_out = [outcomes(truth[neg], calls[neg][a]) for a in ARMS]
        for metric in METRICS:
            rows = neg_out if metric=="control_alarm" else pos_out
            matrices[metric].append([r[metric] for r in rows])
        by_family[t["family"]]["scheduled"] += 1
        for name in ("detection","family","exact","early"):
            by_family[t["family"]][name] += pos_out[-1][name]
        if not pos_out[-1]["exact"]:
            b = calls[pos]["adjusted"]["alarm"]
            reason = ("no alarm" if b is None else "early" if pos_out[-1]["early"]
                      else "late alarm" if not pos_out[-1]["detection"]
                      else "late diagnosis" if 2*(b+29)>=round(60*t["off"])
                      else "incorrect diagnosis")
            failures.append(dict(id=pos, parent=parent, source=t["source"], first=t["first"], reason=reason))
    assert len(strata)==4 and set(strata.values())=={60}
    report, comparisons, bounds = {}, {}, {}
    for metric, rows in matrices.items():
        table = np.asarray(rows,dtype=int)
        n = len(table)
        report[metric] = {a: int(table[:,i].sum()) for i,a in enumerate(ARMS)}
        delta = table[:,-1]-table[:,0]
        wins,losses = int(np.sum(delta>0)),int(np.sum(delta<0))
        if metric in ("control_alarm","early"):
            wins,losses = losses,wins
        comparisons[metric] = dict(adjusted_better=wins,current_better=losses,
                                   paired_p=float(binomtest(wins,wins+losses).pvalue) if wins+losses else 1.)
        k = report[metric]["adjusted"]
        bounds[metric]=dict(lower95=float(beta.ppf(.05,k,n-k+1)) if k else 0.,
                            upper95=float(beta.ppf(.95,k+1,n-k)) if k<n else 1.)
    efficacy = ("detection","family","exact")
    point = all(report[m]["adjusted"]>=228 for m in efficacy) and report["control_alarm"]["adjusted"]<12
    supported = all(bounds[m]["lower95"]>=.95 for m in efficacy) and bounds["control_alarm"]["upper95"]<.05
    return dict(parents=240, strata=dict(strata), counts=report, paired=comparisons,
                one_sided_exact95=bounds,passes_point_targets=point,passes_marginal_bounds=supported,
                adjusted_by_second_family=dict(by_family), adjusted_exact_failures=failures)

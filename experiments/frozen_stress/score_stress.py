"""Match alarms to distinct episodes, including intersecting windows and simultaneous sets."""
import numpy as np
from scipy.optimize import linear_sum_assignment


def matches(events,alarms,chronological=False):
    n,m=len(events),len(alarms)
    if not n or not m:
        return {}
    if chronological:
        chosen={}
        for i,e in enumerate(events):
            hit=next((j for j,a in enumerate(alarms) if j not in chosen.values() and
                      0<=a["detected"]-e["onset"]<=45),None)
            if hit is not None:
                chosen[i]=hit
        return chosen
    # Dummy columns represent a miss. Up to 3 events: coefficients strictly
    # prioritize cardinality, joint diagnosis, family, site and then delay.
    benefit=np.zeros((n,m+n))
    for i,e in enumerate(events):
        for j,a in enumerate(alarms):
            lag=a["detected"]-e["onset"]
            if 0<=lag<=45:
                timely=a["published"] is not None and a["published"]<=e["onset"]+45
                family=timely and a["code"]==e["code"]
                site=timely and a["source"]==e["source"]
                benefit[i,j]=1e7+1e5*(family and site)+1000*family+100*site-lag/46
    i,j=linear_sum_assignment(benefit,maximize=True)
    return {int(a):int(b) for a,b in zip(i,j,strict=True) if benefit[a,b]>0}


def contributions(events,alarms,chronological=False):
    pairs=matches(events,alarms,chronological)
    tab=np.zeros((5,6),int)
    sites=0
    for i,e in enumerate(events):
        c=e["code"]
        if i not in pairs:
            tab[c,0]+=1
            continue
        a=alarms[pairs[i]]
        timely=a["published"] is not None and a["published"]<=e["onset"]+45
        tab[c,min(a["code"],5) if timely else 0]+=1
        sites+=int(timely and a["source"]==e["source"])
    for j,a in enumerate(alarms):
        if j not in pairs.values():
            tab[0,min(a["code"] or 0,5)]+=1
    return np.r_[tab.ravel(),sites,0 if events else len(alarms),len(pairs)]


def measures(stats):
    stats=np.atleast_2d(stats)
    tab=stats[:,:30].reshape(-1,5,6)
    n=tab[:,1:,:].sum(axis=(1,2))
    diag=np.diagonal(tab[:,1:,1:5],axis1=1,axis2=2)
    den=tab[:,1:,:].sum(axis=2)+tab[:,:,1:5].sum(axis=1)
    f1=np.mean(2*diag/np.maximum(den,1),axis=1)
    return np.column_stack([f1,diag.sum(axis=1)/n,stats[:,30]/n,tab[:,0,:].sum(axis=1)])


def bootstrap(truth):
    rng=np.random.default_rng(838703)
    count=np.array([len(r) for r in truth])
    weights=np.zeros((4000,len(truth)),float)
    for k in np.unique(count):
        ix=np.flatnonzero(count==k)
        weights[:,ix]=rng.multinomial(len(ix),np.full(len(ix),1/len(ix)),size=4000)
    return weights


KEYS=("macro_f1","family_fraction","site_fraction","extras")


def intervals(values):
    return dict(zip(KEYS,np.quantile(values,[.025,.975],axis=0).T.tolist()))


def summary(truth,pred,weights):
    rows=np.array([contributions(e,a) for e,a in zip(truth,pred,strict=True)])
    total=rows.sum(axis=0)
    chronological=sum(contributions(e,a,True) for e,a in zip(truth,pred,strict=True))
    values=measures(total)[0]
    boot=measures(weights@rows)
    tab=total[:30].reshape(5,6)
    n=int(tab[1:].sum())
    hours=sum(not r for r in truth)*690/(30*3600)
    result=dict(events=n,records=len(truth),detected=int(total[32]),family=int(np.trace(tab[1:,1:5])),
                site=int(total[30]),macro_f1=float(values[0]),extras=int(values[3]),quiet_extras=int(total[31]),
                event_record_extras=int(values[3]-total[31]),quiet_hours=hours,
                quiet_fa_per_hour=float(total[31]/hours),confusion=tab.tolist(),ci95=intervals(boot),
                chronological=dict(zip(KEYS,measures(chronological)[0].tolist())))
    return result,boot

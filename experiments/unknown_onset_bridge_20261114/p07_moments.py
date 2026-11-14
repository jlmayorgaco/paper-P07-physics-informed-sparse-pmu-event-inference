"""P07-compatible analytic moment and marginal likelihood reference for a
single *common-coordinate* local Gaussian state conditioned on truncated load
severity. NumPy/SciPy reference; does NOT patch/execute the Julia P07 bank.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from scipy.special import ndtr,logsumexp
from scipy.stats import norm
from scipy.linalg import cho_factor,cho_solve
from unknown_onset import log_normal_interval

@dataclass
class Component:
    chart:str
    weight:float
    m:np.ndarray
    d:np.ndarray
    P:np.ndarray
    mu:float
    v:float
    l:float=-.2
    u:float=.2
    cause:str=''


def trunc_moments(mu,v,l,u):
    if not (l<u and v>0):raise ValueError('Expected l<u and v>0')
    sd=np.sqrt(v);a=(l-mu)/sd;b=(u-mu)/sd
    Z=ndtr(b)-ndtr(a)
    if Z<1e-15:raise ValueError('prior truncation too deep: use stable tail moment method')
    la=(norm.pdf(a)-norm.pdf(b))/Z
    mean=mu+sd*la
    var=v*(1+(a*norm.pdf(a)-b*norm.pdf(b))/Z-la**2)
    return float(mean), float(max(var,0))


def component_moments(c:Component):
    aa,va=trunc_moments(c.mu,c.v,c.l,c.u)
    m=c.m+c.d*aa
    P=c.P+va*np.outer(c.d,c.d)
    return m,P,aa,va,c.d*va


def compress(components):
    """Preserve within-component uncertainty, amplitude and between-history spread.
    Only legal for components in a common state chart / reference / modes.
    """
    if not components:raise ValueError('No histories')
    chart=components[0].chart
    if any(c.chart!=chart for c in components):
        raise ValueError('Cannot fuse histories in different equilibrium/gauge charts')
    w=np.array([c.weight for c in components],float)
    if not np.all(np.isfinite(w)) or np.any(w<0) or w.sum()<=0:raise ValueError('Invalid weights')
    w=w/w.sum()
    ms=[];covs=[];avars=[]
    for c in components:
        m,P,aa,va,ca=component_moments(c)
        ms.append(m);covs.append(P);avars.append(va*np.outer(c.d,c.d))
    ms=np.stack(ms);mean=w@ms
    within_base=sum(ww*c.P for ww,c in zip(w,components))
    within_amplitude=sum(ww*pp for ww,pp in zip(w,avars))
    between=sum(ww*np.outer(mm-mean,mm-mean) for ww,mm in zip(w,ms))
    cov=within_base+within_amplitude+between
    return {'mean':mean,'P':cov,'within_base':within_base,'within_amplitude':within_amplitude,
            'between_history':between,'weights':w}


def local_log_evidence(e,s,S,mu,v,l,u):
    """Integral: N(e; s a,S) * TN[a in l,u](mu,v) da.
    Exact for the conditional affine-Gaussian P07 submodel, not full DAE.
    """
    if v<=0 or l>=u:raise ValueError('Invalid truncated severity')
    e=np.asarray(e);s=np.asarray(s);S=np.asarray(S)
    c,low=cho_factor(S,lower=True,check_finite=True)
    eWe=float(e@cho_solve((c,low),e)); b=float(s@cho_solve((c,low),e));G=float(s@cho_solve((c,low),s))
    vpost=1/(1/v+G); mupost=vpost*(mu/v+b)
    logpdf=-.5*(eWe+np.linalg.slogdet(S)[1]+len(e)*np.log(2*np.pi))
    corr=.5*(np.log(vpost/v)+mupost*mupost/vpost-mu*mu/v)
    corr+=float(log_normal_interval(mupost,vpost,l,u)-log_normal_interval(mu,v,l,u))
    return logpdf+corr


def interval_partition_evidence(e,s,S,mu,v,edges):
    l,u=edges[0],edges[-1]
    logz0=float(log_normal_interval(mu,v,l,u))
    pieces=[]
    for a,b in zip(edges[:-1],edges[1:]):
        mass=float(log_normal_interval(mu,v,a,b)-logz0)
        pieces.append(mass+local_log_evidence(e,s,S,mu,v,a,b))
    return float(logsumexp(pieces))

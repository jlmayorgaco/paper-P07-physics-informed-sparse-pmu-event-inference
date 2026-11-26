"""Joint conditional Bayesian tensor; all evidence is added exactly once.

q|a,h,y ~ N(m_h + d_h*a,P), a|h,y ~ truncated N(mu_h,v_h).
The common P is valid for the DECLARED additive nominal-state tangent surrogate.
It is not an event-dependent nonlinear DAE covariance claim.
"""
from pathlib import Path
import json,time
import numpy as np
from scipy.linalg import cho_factor,cho_solve
from scipy.special import logsumexp,log_ndtr

def logdiff(a,b):return a+np.log(-np.expm1(np.minimum(b-a,-1e-15)))
def trunc(mu,var,lo,hi):
    sd=np.sqrt(np.maximum(var,1e-30));a=(lo-mu)/sd;b=(hi-mu)/sd
    left=b<=0;right=a>=0
    z=np.empty_like(a)
    z[left]=logdiff(log_ndtr(b[left]),log_ndtr(a[left]))
    z[right]=logdiff(log_ndtr(-a[right]),log_ndtr(-b[right]))
    middle=~(left|right);z[middle]=logdiff(log_ndtr(b[middle]),log_ndtr(a[middle]))
    ra=np.exp(np.minimum(-.5*a*a-.5*np.log(2*np.pi)-z,700))
    rb=np.exp(np.minimum(-.5*b*b-.5*np.log(2*np.pi)-z,700));shift=ra-rb
    mean=np.clip(mu+sd*shift,lo,hi)
    variance=np.clip(var*(1+a*ra-b*rb-shift*shift),0.,(hi-lo)**2/4)
    return z,mean,variance

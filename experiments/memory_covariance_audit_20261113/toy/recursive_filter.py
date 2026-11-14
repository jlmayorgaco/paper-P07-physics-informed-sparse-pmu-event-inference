"""Exact recursive Kalman bank over linear graph histories, with AR(1) noise.

Kalman state = [physical swing state x(6), new-event amplitude a(1),
                correlated instrument noise epsilon(3)].
History h is a mixture component, and c is new-event candidate.
This deliberately preserves state-amplitude cross-covariance.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import block_diag
from scipy.special import logsumexp
from experiment import setup,simulate,posterior


def infer_online(g, observations):
    """Return posterior p(new_source | y_0:k), p(old_history | y_0:k).

    Observations shape (frames, 3); ALL updates use each report once.
    """
    obs=np.asarray(observations,dtype=float)
    if obs.shape!=(g['T'],3): raise ValueError(f"expected ({g['T']},3), got {obs.shape}")
    rho=g['temporal_rho'];R0=g['R'][:3,:3]
    C=g['C'];Ad=g['Ad'];Bd=g['Bd'];nstate=10
    H=np.zeros((3,nstate));H[:,:6]=C;H[:,7:]=np.eye(3)
    trans_base=np.eye(nstate)
    trans_base[:6,:6]=Ad
    trans_base[7:,7:]=rho*np.eye(3)
    Q=np.zeros((nstate,nstate));Q[7:,7:]=(1-rho**2)*R0
    filters=[]
    for h in range(2):
        for c in range(3):
            m=np.zeros(nstate);m[:6]=g['m_h'][h]
            if c!=0: m[6]=g['mu_amp']
            P=np.zeros((nstate,nstate));P[:6,:6]=g['P'];P[7:,7:]=R0
            if c!=0:P[6,6]=g['sig_amp']**2
            filters.append(dict(h=h,c=c,m=m,P=P,logw=np.log(g['ph'][h])+np.log(g['pc'][c])))
    post_c=[];post_h=[];log_likelihood=[]
    for k,y in enumerate(obs):
        for f in filters:
            if k>0:
                T=trans_base.copy()
                # An onset on report 'onset' changes the transition onset -> onset+1.
                if f['c']!=0 and k-1>=g['onset']:
                    T[:6,6]=Bd[:,f['c']-1]
                f['m']=T@f['m']
                f['P']=T@f['P']@T.T+Q
            err=y-H@f['m']
            S=H@f['P']@H.T
            # Full rank due to AR innovation noise covariance and proper R0.
            sign,ldet=np.linalg.slogdet(S)
            if sign<=0: raise RuntimeError('innovation covariance must be SPD')
            Sinve=np.linalg.solve(S,err)
            f['logw']+=float(-.5*(err@Sinve+ldet+3*np.log(2*np.pi)))
            gain=np.linalg.solve(S,H@f['P']).T
            f['m']=f['m']+gain@err
            I_KH=np.eye(nstate)-gain@H
            f['P']=I_KH@f['P']@I_KH.T
            f['P']=(f['P']+f['P'].T)/2
        logvals=np.array([f['logw'] for f in filters]);norm=logsumexp(logvals)
        weights=np.exp(logvals-norm)
        cprob=np.array([sum(weights[i] for i,f in enumerate(filters) if f['c']==cc) for cc in range(3)])
        hprob=np.array([sum(weights[i] for i,f in enumerate(filters) if f['h']==hh) for hh in range(2)])
        post_c.append(cprob);post_h.append(hprob);log_likelihood.append(float(norm))
    return dict(p_new=np.array(post_c),p_old=np.array(post_h),log_likelihood=np.array(log_likelihood))


def demo():
    g=setup(horizon_s=.65,temporal_rho=.9)
    Y,c,h,a=simulate(g,1,42)
    stream=infer_online(g,Y[0].reshape(g['T'],3))
    exact_c,exact_h,exact_ll,_=posterior(g,Y,'labeled_histories')
    assert np.max(np.abs(stream['p_new'][-1]-exact_c[0]))<1e-10
    assert np.max(np.abs(stream['p_old'][-1]-exact_h[0]))<1e-10
    assert abs(stream['log_likelihood'][-1]-exact_ll[0])<1e-10
    return g,Y,stream,c,h

if __name__=='__main__':
    _,_,r,c,h=demo()
    print('CAUSAL KALMAN STREAM PASS: final new posterior',r['p_new'][-1],
          'old posterior',r['p_old'][-1], 'true new/old',c[0],h[0])

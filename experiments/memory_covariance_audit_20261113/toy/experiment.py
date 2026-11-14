"""Exact Gaussian-mixture vs moment compression, grounded in a linear swing network.
Known onset, single new input, no topology switching. No IEEE39 claim.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
from scipy.linalg import expm, cholesky, solve_triangular, toeplitz
from scipy.special import logsumexp

CLASSES = ('no_new_event','new_at_bus_1','new_at_bus_3')
HISTORY = ('old_history_component_1','old_history_component_2')
METHODS = ('mean_only','moment_gaussian','unlabeled_mixture','labeled_histories')


def physical_model():
    # Three swing nodes + ideal reference node (index 3), power-angle couplings.
    edges=[(0,1,5.),(1,2,3.5),(0,2,2.5),(0,3,2.0),(2,3,1.8)]
    L=np.zeros((3,3))
    for i,j,k in edges:
        if j==3: L[i,i]+=k
        else:
            L[i,i]+=k; L[j,j]+=k; L[i,j]-=k; L[j,i]-=k
    M=np.diag([2.7,2.2,2.9]); D=np.diag([.9,.6,.7])
    A=np.block([[np.zeros((3,3)),np.eye(3)],[-np.linalg.solve(M,L),-np.linalg.solve(M,D)]])
    # Inputs modify power injection at swing nodes 0 or 2.
    B=np.zeros((6,2));B[3:,0]=np.linalg.solve(M,np.array([1.,0.,0.]));B[3:,1]=np.linalg.solve(M,np.array([0.,0.,1.]))
    # Two observed bus angles and one oriented edge flow (DC surrogate).
    C=np.zeros((3,6));C[0,0]=1; C[1,2]=1; C[2,0]=5.;C[2,1]=-5.
    return A,B,C,L,edges,M,D


def discretize(A,B,dt):
    n=A.shape[0];u=B.shape[1]
    aug=np.zeros((n+u,n+u));aug[:n,:n]=A;aug[:n,n:]=B
    z=expm(aug*dt)
    return z[:n,:n],z[:n,n:]


def prior_means(Ad,Bd,amp_pre=.85,on_steps=27,off_steps=12,kind="two_sources"):
    means=[]
    for c in range(2):
        x=np.zeros(Ad.shape[0]);
        src=c if kind=="two_sources" else 0
        amp=amp_pre if (kind=="two_sources" or c==0) else -amp_pre
        for _ in range(on_steps): x=Ad@x+Bd[:,src]*amp
        for _ in range(off_steps): x=Ad@x
        means.append(x)
    return np.array(means)


def window_operators(Ad,Bd,C,T,onset):
    n=Ad.shape[0];p=C.shape[0]
    O=np.zeros((T*p,n));s=np.zeros((2,T*p))
    A_power=np.eye(n);signals=np.zeros((2,n))
    for k in range(T):
        sl=slice(k*p,(k+1)*p)
        O[sl,:]=C@A_power
        for j in range(2): s[j,sl]=C@signals[j]
        A_power=Ad@A_power
        signals=np.einsum('ij,kj->ki',Ad,signals)
        if k>=onset:
            signals+=Bd.T
    return O,s


def setup(horizon_s=.65,noise_scale=1.,spread=1.,dt=1/30,onset_s=.20,temporal_rho=0.0,history_kind="two_sources"):
    A,B,C,L,edges,M,D=physical_model()
    Ad,Bd=discretize(A,B,dt)
    onset=int(round(onset_s/dt)); T=onset+int(round(horizon_s/dt))+1
    O,S=window_operators(Ad,Bd,C,T,onset)
    m_h=prior_means(Ad,Bd,amp_pre=.85*spread,kind=history_kind)
    # Within-history state uncertainty, not engineered to depend on true class.
    P=np.diag([.025**2,.023**2,.025**2,.06**2,.06**2,.06**2])
    per_sensor=np.array([.024,.023,.115])*noise_scale
    corr=np.array([[1.,.15,.05],[.15,1.,-.10],[.05,-.10,1.]])
    R0=per_sensor[:,None]*corr*per_sensor[None,:]
    if not 0 <= temporal_rho < 1: raise ValueError("temporal_rho must be in [0,1)")
    R=np.kron(toeplitz(temporal_rho**np.arange(T)),R0)
    pc=np.array([.40,.30,.30]);ph=np.array([.5,.5]);mu_amp=.75;sig_amp=.19
    return dict(A=A,B=B,C=C,L=L,edges=edges,M=M,D=D,Ad=Ad,Bd=Bd,
                O=O,S=S,m_h=m_h,P=P,R=R,pc=pc,ph=ph,mu_amp=mu_amp,sig_amp=sig_amp,
                T=T,onset=onset,dt=dt,noise_scale=noise_scale,spread=spread,horizon_s=horizon_s,temporal_rho=temporal_rho,history_kind=history_kind)


def simulate(g,N,seed,force_class=None):
    rng=np.random.default_rng(seed)
    h=rng.choice(2,size=N,p=g['ph'])
    c=rng.choice(3,size=N,p=g['pc']) if force_class is None else np.full(N,int(force_class),dtype=int)
    x=g['m_h'][h]+rng.multivariate_normal(np.zeros(6),g['P'],size=N)
    a=rng.normal(g['mu_amp'],g['sig_amp'],size=N)
    xmean=x@g['O'].T
    amp_sig=np.zeros_like(xmean)
    for cc in (1,2):
        mask=c==cc
        amp_sig[mask]=a[mask,None]*g['S'][cc-1]
    L=cholesky(g['R'],lower=True,check_finite=False)
    noise=rng.standard_normal(xmean.shape)@L.T
    return xmean+amp_sig+noise,c,h,a


def logpdf_batch(Y,mu,cov):
    L=cholesky(cov,lower=True,check_finite=False)
    centered=(Y-mu).T
    r=solve_triangular(L,centered,lower=True,check_finite=False)
    return -.5*(np.einsum('ij,ij->j',r,r)+2*np.log(np.diag(L)).sum()+Y.shape[1]*np.log(2*np.pi))


def posterior(g,Y,mode):
    O=g['O']; S=g['S']; R=g['R'];P=g['P'];ph=g['ph'];pc=g['pc']
    m_h=g['m_h'];mbar=ph@m_h
    Pmix=P+sum(ph[k]*np.outer(m_h[k]-mbar,m_h[k]-mbar) for k in range(2))
    N=Y.shape[0]; C=3
    logjoint=np.zeros((N,2,C))
    for cc in range(C):
        sc=np.zeros(Y.shape[1]) if cc==0 else S[cc-1]
        amp_mu=0 if cc==0 else g['mu_amp']
        amp_var=0 if cc==0 else g['sig_amp']**2
        if mode=='mean_only':
            mu=O@mbar+sc*amp_mu
            cov=R+amp_var*np.outer(sc,sc)
            scores=logpdf_batch(Y,mu,cov)
            logjoint[:,:,cc]=scores[:,None]+np.log(pc[cc])+np.log(ph)[None,:]
        elif mode=='moment_gaussian':
            mu=O@mbar+sc*amp_mu
            cov=R+O@Pmix@O.T+amp_var*np.outer(sc,sc)
            scores=logpdf_batch(Y,mu,cov)
            logjoint[:,:,cc]=scores[:,None]+np.log(pc[cc])+np.log(ph)[None,:]
        else:
            cov=R+O@P@O.T+amp_var*np.outer(sc,sc)
            for hh in range(2):
                mu=O@m_h[hh]+sc*amp_mu
                logjoint[:,hh,cc]=logpdf_batch(Y,mu,cov)+np.log(pc[cc])+np.log(ph[hh])
    lognorm=logsumexp(logjoint,axis=(1,2),keepdims=True)
    logpost=logjoint-lognorm
    prob_c=np.exp(logsumexp(logpost,axis=1))
    prob_h=np.exp(logsumexp(logpost,axis=2))
    ll=logsumexp(logjoint,axis=(1,2))
    log_odds=logsumexp(logjoint[:,:,1:],axis=(1,2))-logsumexp(logjoint[:,:,0],axis=1)
    return prob_c,prob_h,ll,log_odds


def summary(Y,c,h,g,mode):
    post,ph,ll,log_odds=posterior(g,Y,mode)
    ptrue=post[np.arange(len(c)),c]
    accuracy=(post.argmax(axis=1)==c).mean()
    brier=np.mean(np.sum((post-np.eye(3)[c])**2,axis=1))
    logloss=-np.log(np.maximum(ptrue,1e-300)).mean()
    false_event=((1-post[c==0,0])>=.9).mean() if np.any(c==0) else np.nan
    false_class=((post[c==0,:].argmax(axis=1)!=0)).mean() if np.any(c==0) else np.nan
    event_correct=((post[c!=0].argmax(axis=1)==c[c!=0])).mean() if np.any(c!=0) else np.nan
    source_correct=((post[c!=0,1:].argmax(axis=1)==c[c!=0]-1)).mean() if np.any(c!=0) else np.nan
    ptrue_h=ph[np.arange(len(h)),h]
    old_acc=(ph.argmax(axis=1)==h).mean() if mode=='labeled_histories' else None
    return dict(accuracy=float(accuracy),event_accuracy=float(event_correct),source_accuracy_given_event=float(source_correct),
                brier=float(brier),log_loss=float(logloss),mean_NLL=float(-ll.mean()),
                false_event_p09=float(false_event),false_class_rate=float(false_class),
                old_source_accuracy=old_acc,old_source_logloss=float(-np.log(ptrue_h).mean()) if old_acc is not None else None)


def run_case(n=600,seed=20261113,noise_scale=1.,spread=1.,horizon_s=.65,temporal_rho=0.,history_kind="two_sources"):
    g=setup(horizon_s,noise_scale,spread,temporal_rho=temporal_rho,history_kind=history_kind)
    Y,c,h,a=simulate(g,n,seed)
    details={}
    posts={}
    for mode in METHODS:
        details[mode]=summary(Y,c,h,g,mode)
        posts[mode]=posterior(g,Y,mode)[0]
    maxdelta=float(np.abs(posts['unlabeled_mixture']-posts['labeled_histories']).max())
    assert maxdelta<1e-12,maxdelta
    return dict(assumptions=dict(noise_scale=noise_scale,prior_history_separation=spread,horizon_s=horizon_s,seed=seed,n=n,
                                 T=g['T'],dt=g['dt'],onset_frame=g['onset'],n_sensors=g['C'].shape[0],n_states=6,temporal_rho=temporal_rho,history_kind=history_kind,
                                 classes=CLASSES,histories=HISTORY),metrics=details,
                max_new_event_posterior_diff_C_D=maxdelta,
                raw=dict(Y=Y,c=c,h=h,a=a,post=posts),physical=dict(A=g['A'],B=g['B'],C=g['C'],L=g['L'],P=g['P'],R0=g['R'][:3,:3],m_h=g['m_h']))


if __name__=='__main__':
    for args in [(1,1,.65),(1,1,.35),(1.6,1,.65),(1,2,.65),(.8,1,.65)]:
        res=run_case(n=500,seed=20261113,noise_scale=args[0],spread=args[1],horizon_s=args[2])
        print('CASE',args,'m_h',res['physical']['m_h'].round(3))
        for mode,v in res['metrics'].items():
            print(mode,'accuracy',round(v['accuracy'],3),'source',round(v['source_accuracy_given_event'],3),
                  'logloss',round(v['log_loss'],3),'NLL',round(v['mean_NLL'],3), 'FP',round(v['false_class_rate'],3),'old',v['old_source_accuracy'])

"""Causal unknown-onset source attribution with truncated-Gaussian load severity.

This is a CONTROLLED SYNTHETIC graph-swing model, NOT the P07 IEEE-39 PowerDynamics
bank. It extends the previous known-onset memory ablation to multiple onset
candidates while preserving equal observation likelihoods/prior calibration.

The three memory models are: (A) mean-only, (B) moment-matched Gaussian,
(C) exact two-component recovery mixture. Historical labels D affect an
additional retrospective query but not the predictive distribution of C.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json
import numpy as np
from scipy.linalg import expm, cholesky, solve_triangular, toeplitz
from scipy.special import logsumexp, log_ndtr
from scipy.stats import truncnorm

DT=1/30
METHODS=('mean_only','shared_covariance','moment_gaussian','mixture')
SOURCES=('no_new_event','new_bus_1','new_bus_3')


def logsubexp(x,y):
    """Stable log(exp(x)-exp(y)) for x>=y; x,y broadcastable."""
    d=np.minimum(np.asarray(y)-np.asarray(x),0)
    return np.asarray(x)+np.log(-np.expm1(d))


def log_normal_interval(mu,var,l=-.2,u=.2):
    """Log P(l<=N(mu,var)<=u), stable for small Gaussian tails."""
    s=np.sqrt(var)
    a=(l-mu)/s; b=(u-mu)/s
    # If interval lies to the right of the mean, work in survival-function tails.
    with np.errstate(divide="ignore",invalid="ignore"):
        lleft=logsubexp(log_ndtr(b),log_ndtr(a))
        lright=logsubexp(log_ndtr(-a),log_ndtr(-b))
    return np.where(a>0,lright,lleft)


def matrices():
    # Three swing nodes with a grounded reference, graph Laplacian and damping.
    edges=[(0,1,5.0),(1,2,3.5),(0,2,2.5),(0,3,2.0),(2,3,1.8)]
    lap=np.zeros((3,3))
    for i,j,w in edges:
        lap[i,i]+=w
        if j!=3:
            lap[j,j]+=w;lap[i,j]-=w;lap[j,i]-=w
    M=np.diag([2.7,2.2,2.9]);D=np.diag([.9,.6,.7])
    A=np.block([[np.zeros((3,3)),np.eye(3)],[-np.linalg.solve(M,lap),-np.linalg.solve(M,D)]])
    B=np.zeros((6,2));B[3:,0]=np.linalg.solve(M,np.array([1,0,0]));B[3:,1]=np.linalg.solve(M,np.array([0,0,1]))
    C=np.zeros((3,6));C[0,0]=1;C[1,2]=1;C[2,0]=5;C[2,1]=-5
    return A,B,C,lap,M,D


def exact_discretization(A,B,dt=DT):
    n=A.shape[0];m=B.shape[1]
    E=np.zeros((n+m,n+m));E[:n,:n]=A;E[:n,n:]=B
    D=expm(E*dt)
    return D[:n,:n],D[:n,n:]


def history_means(Ad,Bd,sign_history=False,on=27,off=12):
    result=[]
    for h in range(2):
        x=np.zeros(Ad.shape[0]);c=0 if sign_history else h
        amp=.85*(1 if h==0 or not sign_history else -1)
        for _ in range(on):x=Ad@x+Bd[:,c]*amp
        for _ in range(off):x=Ad@x
        result.append(x)
    return np.array(result)


def source_signatures(Ad,Bd,C,T,onsets,gain=5.5):
    """Rows: source 1/2, onset candidate. Source enters after candidate frame."""
    p=C.shape[0]; out=[]
    for j in range(2):
        per_source=[]
        for onset in onsets:
            x=np.zeros(Ad.shape[0]); seq=[]
            for k in range(T):
                seq.extend(C@x)
                x=Ad@x+(gain*Bd[:,j] if k>=onset else 0)
            per_source.append(np.array(seq))
        out.append(np.array(per_source))
    return np.array(out)


def build(*,T=34,onsets=(5,10,15,20),rho=.42,noise=1.,history_sign=False,amp_gain=5.5):
    A,B,C,L,M,D=matrices();Ad,Bd=exact_discretization(A,B)
    m_h=history_means(Ad,Bd,sign_history=history_sign)
    n=A.shape[0]; p=C.shape[0]
    O=np.vstack([C@np.linalg.matrix_power(Ad,k) for k in range(T)])
    S=source_signatures(Ad,Bd,C,T,onsets,gain=amp_gain)
    P=np.diag([.025**2,.023**2,.025**2,.06**2,.06**2,.06**2])
    per=np.array([.024,.023,.115])*noise
    corr=np.array([[1,.15,.05],[.15,1,-.10],[.05,-.10,1]])
    R0=per[:,None]*corr*per[None,:]
    R=np.kron(toeplitz(rho**np.arange(T)),R0)
    ph=np.array([.5,.5]);pc=np.array([.4,.3,.3]);
    return dict(A=A,B=B,C=C,L=L,M=M,D=D,Ad=Ad,Bd=Bd,O=O,S=S,P=P,R=R,R0=R0,m_h=m_h,
                ph=ph,pc=pc,T=T,onsets=np.asarray(onsets,dtype=int),dt=DT,amp_mu=0.,amp_sd=.15,
                amp_l=-.2,amp_u=.2,rho=rho,noise=noise,history_sign=history_sign,amp_gain=amp_gain)


def sample(model,n,seed,force_class=None):
    rng=np.random.default_rng(seed)
    h=rng.choice(2,n,p=model['ph']); c=rng.choice(3,n,p=model['pc']) if force_class is None else np.full(n,force_class,dtype=int)
    onset=rng.integers(0,len(model['onsets']),size=n)
    x=model['m_h'][h]+rng.multivariate_normal(np.zeros(6),model['P'],size=n)
    a=truncnorm.rvs((model['amp_l']-model['amp_mu'])/model['amp_sd'],
                    (model['amp_u']-model['amp_mu'])/model['amp_sd'],
                    loc=model['amp_mu'],scale=model['amp_sd'],size=n,random_state=rng)
    y=x@model['O'].T
    for src in (1,2):
        ind=np.flatnonzero(c==src)
        if len(ind):y[ind]+=a[ind,None]*model['S'][src-1,onset[ind]]
    y+=rng.standard_normal(y.shape)@cholesky(model['R'],lower=True).T
    return y,c,h,onset,a


@dataclass
class Prepared:
    chol: np.ndarray
    logdet: float
    mu_hist: np.ndarray     # (num_histories, obs_dim)
    sign_chol: np.ndarray   # (num_source_times, obs_dim)
    G: np.ndarray           # (num_source_times,)
    pc:np.ndarray
    ph:np.ndarray
    n_onsets:int
    amp_prior_logz:float
    amp_var:float


def prepare(model,method):
    O=model['O'];P=model['P'];R=model['R'];hmean=model['m_h'];ph=model['ph']
    mbar=ph@hmean
    if method=='mean_only':
        cov=R; mus=(O@mbar)[None,:];w=np.array([1.])
    elif method=='shared_covariance':
        # P07-like closure: retain its shared nominal/regime Riccati P,
        # but omit amplitude and BETWEEN-history spread at compression.
        cov=R+O@P@O.T;mus=(O@mbar)[None,:];w=np.array([1.])
    elif method=='moment_gaussian':
        dm=hmean-mbar
        Pmix=P+np.einsum('h,hi,hj->ij',ph,dm,dm)
        cov=R+O@Pmix@O.T;mus=(O@mbar)[None,:];w=np.array([1.])
    elif method=='mixture':
        cov=R+O@P@O.T;mus=(O@hmean.T).T;w=ph
    else:raise ValueError(method)
    L=cholesky(cov,lower=True,check_finite=False)
    S=model['S'].reshape(-1,model['S'].shape[-1]);sign_white=solve_triangular(L,S.T,lower=True,check_finite=False).T
    return Prepared(chol=L,logdet=float(2*np.log(np.diag(L)).sum()),mu_hist=mus,
                    sign_chol=sign_white,G=(sign_white*sign_white).sum(axis=1),pc=model['pc'],ph=w,
                    n_onsets=len(model['onsets']),
                    amp_prior_logz=float(log_normal_interval(0,model['amp_sd']**2,model['amp_l'],model['amp_u'])),
                    amp_var=model['amp_sd']**2)


def infer(model,Y,method,prepared=None):
    """Returns class posterior, onset marginal, log model evidence, plus history posterior.

    Marginalizes four ONSET hypotheses and the bounded severity integral exactly
    for the conditional linear Gaussian physical model. No posterior selection leaks
    labels from the true event. Missing prefixes can be evaluated by new model build.
    """
    pr=prepared if prepared is not None else prepare(model,method)
    T=len(Y);nH=len(pr.ph);K=pr.n_onsets
    logjoint=np.empty((nH,3,K,T))
    prior_l= model['amp_l']; prior_u=model['amp_u'];v=pr.amp_var
    logbase=-.5*(pr.logdet+Y.shape[1]*np.log(2*np.pi))
    for hh in range(nH):
        Z=solve_triangular(pr.chol,(Y-pr.mu_hist[hh]).T,lower=True,check_finite=False)
        norm2=np.sum(Z*Z,axis=0)
        null=logbase-.5*norm2
        logjoint[hh,0,:,:]=null[None,:]+np.log(pr.ph[hh])+np.log(pr.pc[0])-np.log(K)
        bs=pr.sign_chol@Z
        vv=1/(1/v+pr.G)
        mm=vv[:,None]*bs
        # analytic integral of bounded severity, not a profile approximation
        gain=.5*(np.log(vv[:,None]/v)+(mm*mm)/vv[:,None])
        gain+=log_normal_interval(mm,vv[:,None],prior_l,prior_u)-pr.amp_prior_logz
        for src in (1,2):
            i0=(src-1)*K
            logjoint[hh,src,:,:]=null[None,:]+gain[i0:i0+K,:]+np.log(pr.ph[hh])+np.log(pr.pc[src])-np.log(K)
    ls=logsumexp(logjoint,axis=(0,1,2))
    post=np.exp(logsumexp(logjoint,axis=(0,2))-ls[None,:]).T
    # conditional onset among event sources, posterior sums to one over onset (for event positive)
    log_src_onset=logsumexp(logjoint[:,1:,:,:],axis=(0,1))
    onset_probs=np.exp(log_src_onset-logsumexp(log_src_onset,axis=0)[None,:]).T
    history_post=np.exp(logsumexp(logjoint,axis=(1,2))-ls[None,:]).T
    odds=logsumexp(logjoint[:,1:,:,:],axis=(0,1,2))-logsumexp(logjoint[:,0,:,:],axis=(0,1))
    return post,onset_probs,ls,history_post,odds


def metrics(Y,c,h,onset,model,pr,tau):
    post,pon,ll,ph,odds=infer(model,Y,'mixture',prepared=pr)
    return None


def evaluate(model,*,ncal=650,ntest=1100,seed=20261114):
    Yn,_,_,_,_=sample(model,ncal,seed+1,force_class=0)
    Y,c,h,j,a=sample(model,ntest,seed+2)
    output={}; posts={};odds={}; ll={}; p_onsets={}; decisions={}
    for name in METHODS:
        pre=prepare(model,name)
        _,_,_,_,cn=infer(model,Yn,name,pre)
        # Empirical finite-sample null calibration: conservative tail rank.
        target=.05
        sorted_cal=np.sort(cn)
        idx=int(np.ceil((ncal+1)*(1-target)))-1
        idx=np.clip(idx,0,ncal-1)
        threshold=float(sorted_cal[idx])
        pc,p_on,l,h_post,ld=infer(model,Y,name,pre)
        event=(ld>threshold)
        src=np.argmax(pc[:,1:],axis=1)+1
        correct=(event&(src==c)&(c>0))
        fpr=float(np.mean(event[c==0])); eventcov=float(np.sum(correct)/max(np.sum(c>0),1))
        clas=float(np.mean(src[c>0]==c[c>0]))
        onset_mae=float(np.mean(np.abs(model['onsets'][np.argmax(p_on[correct],axis=1)]-model['onsets'][j[correct]])*model['dt'])) if correct.sum()>0 else None
        lloss=float(-np.log(np.clip(pc[np.arange(ntest),c],1e-300,1)).mean())
        brier=float(np.mean(((pc-np.eye(3)[c])**2).sum(axis=1)))
        output[name]=dict(threshold_log_event_odds=threshold,ncal=ncal,ntest=ntest,
            normal_fpr_test=fpr,coverage_new_event_correct_source=eventcov,
            source_acc_conditional_on_event=clas,
            onset_mae_sec_on_correct=onset_mae,logloss=lloss,brier=brier,
            number_true_events=int(np.sum(c>0)),number_true_normal=int(np.sum(c==0)),
            number_correct_event_source=int(correct.sum()),n_onset_candidates=len(model['onsets']))
        posts[name]=pc;odds[name]=ld;ll[name]=l;p_onsets[name]=p_on;decisions[name]=correct
    assert np.allclose(posts['mixture'].sum(axis=1),1,atol=1e-10)
    positives=np.flatnonzero(c>0)
    rng=np.random.default_rng(seed+5)
    idx=rng.integers(0,len(positives),size=(1200,len(positives)))
    d={}
    for left,right in (('shared_covariance','mean_only'),('moment_gaussian','shared_covariance'),('mixture','moment_gaussian')):
        delta=decisions[left][positives].astype(float)-decisions[right][positives].astype(float)
        draws=delta[idx].mean(axis=1)
        d[left+'_minus_'+right]={'delta_percentage_points':round(100*float(delta.mean()),3),
                                  'bootstrap_95_pp':[round(100*float(v),3) for v in np.quantile(draws,[.025,.975])]}
    output['paired_bootstrap']=d
    return output,dict(Y=Y,c=c,h=h,onset=j,a=a,post=posts,odds=odds,onset_probs=p_onsets,correct=decisions)


def write_results(root:Path, ncal=1000,ntest=1700,seed=20261114):
    root.mkdir(parents=True,exist_ok=True)
    configs={
     'base_unknown_onset':dict(T=34,onsets=(5,10,15,20),rho=.42,noise=1.,history_sign=False),
     'stronger_independent_noise':dict(T=34,onsets=(5,10,15,20),rho=.0,noise=1.75,history_sign=False),
     'signed_recovery':dict(T=34,onsets=(5,10,15,20),rho=.42,noise=1.,history_sign=True),
     'short_window':dict(T=22,onsets=(4,7,10,13),rho=.42,noise=1.,history_sign=False),
    }
    summary={'model':'synthetic linear swing graph, NOT PowerDynamics P07',
             'mechanism':'unknown event onset; exact truncated Gaussian amplitude; same observations and independent null calibration',
             'prior':'TN[-0.2,0.2](mean=0, var=0.15^2), input direction times 5.5',
             'seed':seed,'per_scenario':{},'limitations':[
                 'known previous mixture prior, not learned from PMU prefix',
                 'no real P07 47-channel exporter or Sauer-Pai dynamics',
                 'no line opening, no simultaneous events',
                 'simulation/noise matches inference assumptions',
                 'calibration controls per-window false alarms, not per-hour sequential alarms',
                 'exploratory scenario selection; no confirmatory IEEE-39 claim'
             ]}
    for i,(name,cfg) in enumerate(configs.items()):
        model=build(**cfg)
        out,sample_data=evaluate(model,ncal=ncal,ntest=ntest,seed=seed+1000*i)
        summary['per_scenario'][name]={'configuration':cfg,'metrics':out}
        print(name, ' | '.join(f"{m}: {out[m]['coverage_new_event_correct_source']:.1%} FPR={out[m]['normal_fpr_test']:.1%} logloss={out[m]['logloss']:.3f}" for m in METHODS),flush=True)
        if i==0:
            np.savez_compressed(root/'sample_200.npz',Y=sample_data['Y'][:200],truth_c=sample_data['c'][:200],
                truth_h=sample_data['h'][:200],truth_onset=sample_data['onset'][:200],
                post_A=sample_data['post']['mean_only'][:200],post_shared=sample_data['post']['shared_covariance'][:200],
                post_B=sample_data['post']['moment_gaussian'][:200],
                post_C=sample_data['post']['mixture'][:200])
    (root/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,default=lambda x:float(x) if isinstance(x,np.floating) else int(x)))
    return summary

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--ncal',type=int,default=1000);p.add_argument('--ntest',type=int,default=1700)
    p.add_argument('--seed',type=int,default=20261114);p.add_argument('--out',default=str(Path(__file__).parent/'results'))
    args=p.parse_args();write_results(Path(args.out),args.ncal,args.ntest,args.seed)

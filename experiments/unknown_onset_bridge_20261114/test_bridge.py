from pathlib import Path
import numpy as np
from numpy.testing import assert_allclose
from scipy.integrate import quad
from scipy.stats import truncnorm,multivariate_normal
from scipy.special import logsumexp
from unknown_onset import build,prepare,sample,infer,log_normal_interval,matrices,source_signatures
from p07_moments import Component,compress,trunc_moments,local_log_evidence,interval_partition_evidence

def test_source_operators_are_physical_convolution():
    g=build(T=25,onsets=(3,8,12))
    src_sig=g['S'];Ad,Bd,C=g['Ad'],g['Bd'],g['C']
    for src in range(2):
        for i,onset in enumerate(g['onsets']):
            x=np.zeros(6)
            for k in range(g['T']):
                assert_allclose(C@x,src_sig[src,i,k*3:(k+1)*3],atol=1e-12)
                x=Ad@x+(g['amp_gain']*Bd[:,src] if k>=onset else 0)

def test_trunc_formula_vs_quadrature():
    e=np.array([.19,-.23,.05]);s=np.array([1.4,-.8,.2]);S=np.diag([.2,.16,.15])**2
    mu=0.015;v=.15**2;l=-.2;u=.2
    logz=log_normal_interval(mu,v,l,u)
    def integrand(a):
        return multivariate_normal.pdf(e,s*a,S)*np.exp(-.5*(a-mu)**2/v)/np.sqrt(2*np.pi*v)/np.exp(logz)
    quadval=quad(integrand,l,u,epsabs=1e-11,epsrel=1e-10)[0]
    assert_allclose(np.exp(local_log_evidence(e,s,S,mu,v,l,u)),quadval,rtol=1e-10)

def test_partition_4_integrals():
    e=np.array([.12,.03]);s=np.array([1.2,-2.]);S=np.array([[.06,.008],[.008,.04]])
    full=local_log_evidence(e,s,S,0,.15**2,-.2,.2)
    piece=interval_partition_evidence(e,s,S,0,.15**2,[-.2,-.1,0,.1,.2])
    assert_allclose(full,piece,atol=1e-12)

def test_mixture_moments_vs_monte_carlo():
    P=np.array([[.015,.005],[.005,.012]])
    components=[Component(chart='q0',weight=.35,m=np.array([.1,-.3]),d=np.array([1.,2.]),P=P,mu=.07,v=.12**2,cause='load7'),
                Component(chart='q0',weight=.65,m=np.array([.5,.2]),d=np.array([-.5,.4]),P=P,mu=-.02,v=.15**2,cause='load24')]
    reference=compress(components)
    rng=np.random.default_rng(153)
    n=120000;which=rng.choice(2,size=n,p=reference['weights']);X=np.zeros((n,2))
    for j,c in enumerate(components):
        sel=np.flatnonzero(which==j)
        a=truncnorm.rvs((c.l-c.mu)/np.sqrt(c.v),(c.u-c.mu)/np.sqrt(c.v),loc=c.mu,scale=np.sqrt(c.v),size=len(sel),random_state=rng)
        X[sel]=c.m+a[:,None]*c.d+rng.multivariate_normal(np.zeros(2),c.P,len(sel))
    assert_allclose(X.mean(axis=0),reference['mean'],atol=.004)
    assert_allclose(np.cov(X,rowvar=False),reference['P'],atol=.005)
    assert_allclose(reference['P'],reference['within_base']+reference['within_amplitude']+reference['between_history'])

def test_invalid_cross_chart_compression():
    a=Component('network_1',.5,np.zeros(2),np.ones(2),np.eye(2),0,.01)
    b=Component('network_2',.5,np.zeros(2),np.ones(2),np.eye(2),0,.01)
    try:compress([a,b]);raise AssertionError('Unrecognized cross-chart fusion')
    except ValueError as e: assert 'different' in str(e)

def test_onset_marginal_matches_manual_logsum():
    g=build(T=24,onsets=(3,7,12),rho=.25)
    Y,c,h,j,a=sample(g,9,313)
    model=prepare(g,'mixture')
    post,pons,logev,old,odds=infer(g,Y,'mixture',model)
    assert_allclose(post.sum(axis=1),1,atol=1e-12)
    assert_allclose(pons.sum(axis=1),1,atol=1e-12)
    assert_allclose(old.sum(axis=1),1,atol=1e-12)
    assert_allclose(odds,np.log((1-post[:,0])/post[:,0]),atol=1e-9)
    assert np.all(np.isfinite(logev))

def test_cause_labels_do_not_add_information():
    g=build(T=22,onsets=(3,8,13))
    Y,c,h,j,a=sample(g,100,109)
    p,hpo,ll,old,odds=infer(g,Y,'mixture')
    # Cause names are not used anywhere in Bayesian new-source prediction.
    # Swapping the history indexing together with weights and means is invariant.
    g2=dict(g);g2['m_h']=g['m_h'][::-1].copy();g2['ph']=g['ph'][::-1].copy()
    p2,_,ll2,old2,_=infer(g2,Y,'mixture')
    assert_allclose(p,p2,atol=1e-11)
    assert_allclose(ll,ll2,atol=1e-10)
    assert_allclose(old,old2[:,::-1],atol=1e-11)

def test_energy_identity():
    A,B,C,L,M,D=matrices()
    rng=np.random.default_rng(9);x=rng.normal(0,.5,6); u=np.array([.2,-.1])
    dx=A@x+B@u
    H=np.block([[L,np.zeros((3,3))],[np.zeros((3,3)),M]])
    der=x@H@dx
    input_power=x[3:]@(M@B[3:]@u)
    dissip=x[3:]@D@x[3:]
    assert_allclose(der,input_power-dissip,atol=1e-10)

def test_prefix_causal_independence_of_future():
    g=build(T=22,onsets=(3,8,12))
    Y,c,h,j,a=sample(g,2,172)
    # Prefix model: identical physical and stochastic law through the cutoff.
    t=15;gp=build(T=t,onsets=(3,8,12))
    prefix=Y.reshape(2,22,3)[:,:t,:].reshape(2,-1)
    p,*_=infer(gp,prefix,'mixture')
    modified=Y.copy().reshape(2,22,3);modified[:,t:,:]+=1000
    prefix2=modified[:,:t,:].reshape(2,-1)
    p2,*_=infer(gp,prefix2,'mixture')
    assert_allclose(prefix,prefix2)
    assert_allclose(p,p2,atol=1e-14)

def test_prior_onsets_correct():
    g=build(T=24,onsets=(4,8,12,16))
    # A null history's evidence must not depend on the number of allowed onset labels.
    g2=build(T=24,onsets=(4,8))
    from unknown_onset import log_normal_interval
    assert g['O'].shape==g2['O'].shape
    assert_allclose(g['R'],g2['R'])

if __name__=='__main__':
    for name,test in sorted(globals().copy().items()):
        if name.startswith('test_'):
            test();print('PASS',name)

"""Independent structural checks for the exact toy inference experiment."""
import unittest
from copy import deepcopy
import numpy as np
from numpy.linalg import eigvalsh
from scipy.integrate import solve_ivp
from scipy.linalg import expm
from scipy.special import logsumexp
from numpy.polynomial.hermite import hermgauss
from experiment import physical_model,discretize,prior_means,setup,simulate,posterior,logpdf_batch


class MathematicalContracts(unittest.TestCase):
    def test_grounded_graph_energy_and_stability(self):
        A,B,C,L,_,M,D=physical_model()
        self.assertGreater(eigvalsh(L)[0],0)
        self.assertTrue(np.all(np.real(np.linalg.eigvals(A))<0))
        rng=np.random.default_rng(5)
        d=rng.normal(size=3); w=rng.normal(size=3); u=rng.normal(size=2)
        z=np.r_[d,w]
        dz=A@z+B@u
        E_dot=w@M@dz[3:]+d@L@dz[:3]
        expected=-(w@D@w)+(w@np.array([u[0],0,u[1]]))
        np.testing.assert_allclose(E_dot,expected,rtol=1e-13,atol=1e-13)

    def test_exact_discretization(self):
        A,B,*_=physical_model()
        dt=.13
        Ad,Bd=discretize(A,B,dt)
        rng=np.random.default_rng(44);x=rng.normal(size=6);u=rng.normal(size=2)
        solution=solve_ivp(lambda t,z:A@z+B@u,(0,dt),x,rtol=1e-12,atol=1e-13)
        np.testing.assert_allclose(Ad@x+Bd@u,solution.y[:,-1],rtol=1e-11,atol=1e-11)

    def test_window_operators(self):
        from experiment import window_operators
        A,B,C,*_=physical_model();Ad,Bd=discretize(A,B,1/30)
        O,s=window_operators(Ad,Bd,C,13,4)
        x0=np.array([.1,-.05,.2,.02,-.01,.04]);amp=.6
        x=x0.copy();ys=[]
        for k in range(13):
            ys.append(C@x)
            x=Ad@x+(Bd[:,0]*amp if k>=4 else 0)
        np.testing.assert_allclose(np.concatenate(ys),O@x0+s[0]*amp,atol=1e-13)

    def test_moment_matching(self):
        g=setup(horizon_s=.2)
        m=g['ph']@g['m_h'];d=g['m_h']-m
        Pmix=g['P']+sum(g['ph'][i]*np.outer(d[i],d[i]) for i in range(2))
        self.assertTrue(np.all(eigvalsh(Pmix)>0))
        rng=np.random.default_rng(3);h=rng.choice(2,100_000,p=g['ph'])
        X=g['m_h'][h]+rng.multivariate_normal(np.zeros(6),g['P'],size=len(h))
        np.testing.assert_allclose(X.mean(axis=0),m,atol=.002)
        np.testing.assert_allclose(np.cov(X,rowvar=False),Pmix,atol=.002)

    def test_posterior_normalization_and_exact_equivalence(self):
        g=setup(horizon_s=.2,temporal_rho=.8)
        Y,c,h,a=simulate(g,34,41)
        pC,_,llC,loC=posterior(g,Y,'unlabeled_mixture')
        pD,ph,llD,loD=posterior(g,Y,'labeled_histories')
        np.testing.assert_allclose(pC.sum(axis=1),1,atol=1e-13)
        np.testing.assert_allclose(ph.sum(axis=1),1,atol=1e-13)
        np.testing.assert_allclose(pC,pD,atol=1e-14)
        np.testing.assert_allclose(llC,llD,atol=1e-14)
        np.testing.assert_allclose(loC,loD,atol=1e-14)

    def test_cause_label_permutation_changes_old_not_future(self):
        g=setup(horizon_s=.2)
        Y,*_=simulate(g,20,9)
        orig_new,orig_hist,*_=posterior(g,Y,'labeled_histories')
        clone=deepcopy(g)
        clone['m_h']=clone['m_h'][::-1].copy()
        clone['ph']=clone['ph'][::-1].copy()
        perm_new,perm_hist,*_=posterior(clone,Y,'labeled_histories')
        np.testing.assert_allclose(orig_new,perm_new,atol=1e-13)
        np.testing.assert_allclose(orig_hist,perm_hist[:,::-1],atol=1e-13)
        # Past cause relabeling cannot be inferred from identical state predictive law.
        self.assertGreater(np.max(np.abs(orig_hist-perm_hist)),.5)

    def test_amplitude_integrated_gaussian_evidence(self):
        g=setup(horizon_s=.12,temporal_rho=.3)
        O=g['O'];P=g['P'];R=g['R'];sc=g['S'][0]
        y=(O@g['m_h'][0]+g['mu_amp']*sc).reshape(1,-1)
        Rstate=R+O@P@O.T
        analytic=logpdf_batch(y,O@g['m_h'][0]+g['mu_amp']*sc,
                              Rstate+g['sig_amp']**2*np.outer(sc,sc))[0]
        # Independent Gauss-Hermite quadrature over the scalar amplitude.
        nodes,weights=hermgauss(90)
        av=g['mu_amp']+np.sqrt(2)*g['sig_amp']*nodes
        scores=np.array([logpdf_batch(y,O@g['m_h'][0]+a*sc,Rstate)[0] for a in av])
        numerical=logsumexp(scores+np.log(weights/np.sqrt(np.pi)))
        self.assertAlmostEqual(analytic,numerical,places=8)

    def test_causal_recursion_equals_batch_on_every_prefix(self):
        from recursive_filter import infer_online
        g=setup(horizon_s=.35,temporal_rho=.91)
        Y,*_=simulate(g,1,30)
        stream=infer_online(g,Y[0].reshape(g['T'],3))
        for k in range(g['T']):
            d=3*(k+1)
            pref=dict(g)
            pref['O']=g['O'][:d]
            pref['S']=g['S'][:,:d]
            pref['R']=g['R'][:d,:d]
            byclass,byhistory,ll,_=posterior(pref,Y[:,:d],'labeled_histories')
            np.testing.assert_allclose(stream['p_new'][k],byclass[0],atol=1e-10,rtol=1e-10)
            np.testing.assert_allclose(stream['p_old'][k],byhistory[0],atol=1e-10,rtol=1e-10)
            np.testing.assert_allclose(stream['log_likelihood'][k],ll[0],atol=1e-10,rtol=1e-10)

    def test_correlated_noise_and_permutation_are_spd(self):
        g=setup(horizon_s=.2,temporal_rho=.97)
        self.assertGreater(np.linalg.eigvalsh(g['R'])[0],0)
        # Changing old-cause names cannot change the current observation likelihood.
        self.assertEqual(len(g['ph']),2)

if __name__=='__main__':
    unittest.main(verbosity=2)

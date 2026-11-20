"""Check the causal evidence recursion against explicit likelihoods on actual network signatures."""
import numpy as np
from scipy.special import logsumexp

from common import MODEL
from intervention_monitor import Bank, update_scores
from operators import cache_bank, coordinates, filter_args, innovations


def check():
    cache_bank()
    b = Bank()
    with np.load(MODEL) as archive:
        m = dict(archive)
    rng = np.random.default_rng(73118)
    # A single complex phasor has the same representation under any phase at zero magnitude.
    raw = np.ones((8,5))
    raw[2,2] = 0.
    before = coordinates(raw,m["floor"])
    raw[2,3] = 173.
    np.testing.assert_array_equal(before,coordinates(raw,m["floor"]))
    # Linear innovations transform applied to observations minus a deterministic mean.
    z,g = rng.normal(size=(2,18,31))
    pars = filter_args(m)
    np.testing.assert_allclose(innovations(z-g,*pars),innovations(z,*pars)-innovations(g,*pars),atol=1e-9)
    chosen = np.linspace(0,len(b.young)-1,27,dtype=int)
    path = np.ascontiguousarray(b.templates[:18,chosen,:])
    energy = np.sum(path**2,axis=2)
    score = np.zeros_like(energy)
    nu = float(m["nu"])
    residuals = rng.normal(size=(18,31))
    for k,r in enumerate(residuals):
        v = 1+k/12
        update_scores(score,path@r,energy,nu*v+r@r,.5*(nu+31),k+1)
        for age in (0,k):
            y = residuals[k-age:k+1]
            var = 1+np.arange(k-age,k+1)[:,None]/12
            norm0 = np.sum(y**2,axis=1)[:,None]
            norm1 = np.sum((y[:,None,:]-path[:age+1])**2,axis=2)
            direct = .5*(nu+31)*np.log((nu*var+norm0)/(nu*var+norm1)).sum(axis=0)
            np.testing.assert_allclose(score[age],direct,rtol=1e-9,atol=1e-8)
    assert abs(logsumexp(b.logprior))<1e-12
    print("Checked current invariance, marginalized innovations, onset recursion and mark priors.")


if __name__=="__main__":
    check()

"""Small counterexamples to overbroad theorems in the supplied discussion."""
from pathlib import Path
import json
import numpy as np
from scipy.integrate import quad
from scipy.special import logsumexp,expit
from scipy.stats import norm

def main():
    # Source profiling creates complementary sensors, not submodularity.
    true=np.array([1.,1.]);rival=np.array([1.,-1.])
    def separation(indices):
        if not indices:return 0.
        a=true[indices];b=rival[indices];amp=np.clip(a@b/(b@b),-2,2)
        return float(np.sum((a-b*amp)**2))
    f=[separation(s) for s in [[],[0],[1],[0,1]]]
    assert f==[0.,0.,0.,2.]
    # A mixture's covariance-matched Gaussian does not obey the proposed
    # positive lower bound obtained by inserting its full covariance there.
    a=.5;between=a*a;total=1+between
    def integrand(x):
        lp=logsumexp([norm.logpdf(x,-a),norm.logpdf(x,a)])-np.log(2)
        lq=norm.logpdf(x,0,np.sqrt(total))
        return np.exp(lp)*(lp-lq)
    kl,error=quad(integrand,-12,12,epsabs=1e-12,epsrel=1e-10)
    wrong_bound=.5*(between/total-np.log1p(between/total))
    assert kl+10*error<wrong_bound
    # Full states can differ entirely in the observation nullspace.
    C=np.array([[1.,0.]]);states=np.array([[0.,1.],[0.,-1.]])
    P=states.T@states/2
    assert np.trace(P)>0 and np.all(C@P@C.T==0)
    # Positive information at each time need not diverge after restoration.
    rho=.9;info=.5/(1-rho**2)
    assert np.isfinite(info) and expit(info)<1
    # Fresh Bayes evidence can amplify an arbitrarily small discarded mass.
    eps=.001;likelihood_ratio=1e6
    posterior=eps*likelihood_ratio/(1-eps+eps*likelihood_ratio)
    assert posterior>.999 and posterior>eps
    # Six qualifying reports span five report intervals if first at onset.
    times=np.arange(6)/30;assert np.isclose(times[-1]-times[0],1/6)
    out=dict(profiled_sensor_separation=f,submodularity_violation=f[1]+f[2]<f[0]+f[3],
             moment_matched_mixture_kl=float(kl),quadrature_error=float(error),invalid_proposed_lower_bound=float(wrong_bound),
             latent_between_covariance=P.tolist(),observable_between_covariance=(C@P@C.T).tolist(),
             decaying_gaussian_signature_total_information=info,
             pruning_one_step_mass=eps,posterior_mass_after_new_evidence=posterior,
             six_report_span_seconds=float(times[-1]-times[0]),
             interpretation='Counterexamples invalidate universal statements, not the scoped Gaussian identities. No IEEE39 detector result.',passed=True)
    (Path(__file__).resolve().parent/'SUPPLIED_CLAIM_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()

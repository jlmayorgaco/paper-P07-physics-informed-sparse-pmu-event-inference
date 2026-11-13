"""Small-model verification only; no IEEE-39 detector or campaign imports."""
from pathlib import Path
import hashlib,json,platform
import numpy as np
import scipy
from scipy.integrate import quad
from scipy.optimize import lsq_linear
from scipy.stats import multivariate_normal,norm

ROOT=Path(__file__).resolve().parents[1]

def structured_fit(target,basis,floor,upper):
    """Frobenius projection onto fixed PSD factors with bounded weights."""
    A=np.column_stack([b.ravel() for b in basis])
    fit=lsq_linear(A,(target-floor).ravel(),bounds=(0,upper),tol=1e-13)
    if not fit.success:raise RuntimeError(fit.message)
    return floor+sum(c*b for c,b in zip(fit.x,basis)),fit.x

def causal_noise_replay(y):
    """Scalar toy, Q=0 and known zero mean; score first, update next R."""
    R=.7;out=[];versions=[]
    for z in y:
        versions.append(R)
        out.append(float(norm.logpdf(z,scale=np.sqrt(R))))
        R=float(np.clip(.95*R+.05*z*z,.1,3.0))
    return np.array(out),np.array(versions)

def main():
    dest=ROOT/'generated/adaptive_extension_checks.json'
    dest.unlink(missing_ok=True)
    rng=np.random.default_rng(61513)
    m=np.array([.2,-.1,.3]);d=np.array([.4,-.2,.1])
    P=np.array([[.7,.1,.05],[.1,.5,.02],[.05,.02,.4]])
    F=np.array([[.9,.1,0],[0,.8,.1],[.05,0,.95]])
    B=np.array([.1,.2,-.05]);Q=np.diag([.02,.03,.01])
    H=np.array([[1,.2,-.1],[.1,.4,1]])
    D=np.array([.1,-.2]);R=np.array([[.3,.08],[.08,.4]])
    mm=F@m;dd=F@d+B;PP=F@P@F.T+Q
    S=H@PP@H.T+R;s=H@dd+D;e=np.array([.5,-.2])-H@mm
    K=np.linalg.solve(S,H@PP).T
    mu=.04;v=.08;lo=-.2;hi=.2
    vv=1/(1/v+s@np.linalg.solve(S,s));uu=vv*(mu/v+s@np.linalg.solve(S,e))
    Z=lambda a,b:norm.cdf((hi-a)/np.sqrt(b))-norm.cdf((lo-a)/np.sqrt(b))
    closed_log=multivariate_normal.logpdf(e,mean=np.zeros(2),cov=S)+.5*np.log(vv/v)+.5*(uu*uu/vv-mu*mu/v)+np.log(Z(uu,vv)/Z(mu,v))
    f=lambda a:multivariate_normal.pdf(e,mean=s*a,cov=S)*norm.pdf(a,loc=mu,scale=np.sqrt(v))/Z(mu,v)
    evidence=quad(f,lo,hi,epsabs=1e-12)[0]
    mean_a=quad(lambda a:a*f(a),lo,hi,epsabs=1e-12)[0]/evidence
    var_a=quad(lambda a:(a-mean_a)**2*f(a),lo,hi,epsabs=1e-12)[0]/evidence
    mplus=mm+K@e;dplus=dd-K@s
    C=(np.eye(3)-K@H)@PP@(np.eye(3)-K@H).T+K@R@K.T
    expected_mean=mplus+dplus*mean_a;expected_cov=C+np.outer(dplus,dplus)*var_a
    direct_mean=np.array([quad(lambda a:(mm+dd*a+K@(e-s*a))[i]*f(a),lo,hi,epsabs=1e-12)[0]/evidence for i in range(3)])
    direct_cov=np.empty((3,3))
    for i in range(3):
        for j in range(3):
            direct_cov[i,j]=quad(lambda a:(C[i,j]+((mm+dd*a+K@(e-s*a))-direct_mean)[i]*((mm+dd*a+K@(e-s*a))-direct_mean)[j])*f(a),lo,hi,epsabs=1e-12)[0]/evidence
    checks={
      'truncated_log_evidence_error':abs(closed_log-np.log(evidence)),
      'state_mean_quadrature_error':float(np.max(abs(expected_mean-direct_mean))),
      'state_covariance_quadrature_error':float(np.max(abs(expected_cov-direct_cov))),
      'joseph_vs_schur_error':float(np.max(abs(C-(PP-K@S@K.T))))}
    # Missing coordinates require a Gaussian marginal, not conditioning them
    # to zero: the submatrix of an inverse is generally the wrong precision.
    mask=np.array([[1.,0.]])
    subS=mask@S@mask.T
    checks['masked_marginal_density_error']=abs(multivariate_normal.logpdf(mask@e,mean=[0.],cov=subS)-norm.logpdf(e[0],scale=np.sqrt(S[0,0])))
    wrong_precision_difference=abs(np.linalg.inv(S)[0,0]-1/S[0,0])
    assert wrong_precision_difference>1e-5
    # Exact common+local covariance target; fit only R, never joint free Q/R.
    U=np.ones(3)/np.sqrt(3);basis=[np.outer(U,U)]+[np.diag(np.eye(3)[i]) for i in range(3)]
    floor=.02*np.eye(3);truth=floor+.4*basis[0]+.1*basis[1]+.2*basis[2]+.3*basis[3]
    fitted,weights=structured_fit(truth,basis,floor,2.)
    checks['structured_covariance_projection_error']=float(np.max(abs(fitted-truth)))
    assert np.linalg.eigvalsh(fitted).min()>=.02-1e-12
    # Prequential accounting and replay determinism for the toy adaptive model.
    y=rng.normal(size=80);scores,versions=causal_noise_replay(y)
    early,early_versions=causal_noise_replay(y[:37])
    checks['prefix_score_error']=float(np.max(abs(early-scores[:37])))
    checks['prefix_covariance_version_error']=float(np.max(abs(early_versions-versions[:37])))
    cut=31;ledger=scores.copy()
    for _ in range(3):
        replacement=norm.logpdf(y[cut:],scale=np.sqrt(versions[cut:]))
        ledger[cut:]=replacement
    checks['replay_replacement_error']=abs(float(ledger.sum()-scores.sum()))
    assert all(x<1e-10 for x in checks.values()),checks
    # Two counterexamples, not evidence that an estimated gate succeeds.
    eta=.05;n=100;b=0.;a=1.
    for _ in range(n):b=(1-eta)*b+eta*a
    assert abs((a-b)-a*(1-eta)**n)<1e-12
    c=1.;conditional_variance=1-2*c*norm.pdf(c)/(2*norm.cdf(c)-1)
    numerical=quad(lambda z:z*z*norm.pdf(z),-c,c)[0]/(2*norm.cdf(c)-1)
    assert abs(conditional_variance-numerical)<1e-12 and conditional_variance<1
    result={'status':'PASS','scope':'small linear Gaussian / truncated-severity identities and counterexamples only; no detector performance',
      'checks':checks,'counterexamples':{'adaptive_center_remaining_step_fraction':(1-eta)**n,
      'eta':eta,'updates':n,'variance_after_selecting_abs_standard_normal_below_1':conditional_variance,
      'wrong_inverse_submatrix_difference':wrong_precision_difference},
      'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},
      'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()

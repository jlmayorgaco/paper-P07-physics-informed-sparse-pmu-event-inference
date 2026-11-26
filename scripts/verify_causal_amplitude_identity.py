"""Independent quadrature check of the displayed local amplitude integral.
Algebra validation only; neither IEEE-39 evidence nor an estimator change.
"""
from pathlib import Path
import json
import numpy as np
from scipy.integrate import quad
from scipy.stats import norm,multivariate_normal
ROOT=Path(__file__).resolve().parents[1]
def main():
    rows=[]
    S=np.array([[.3,.1],[.1,.2]]);s=np.array([1.2,-.4]);e=np.array([.3,-.2]);inv=np.linalg.inv(S)
    for mu,v,l,u in [(.02,.01,-.2,.3),(-.04,.04,-.3,0.)]:
        Z=lambda m,q:norm.cdf((u-m)/np.sqrt(q))-norm.cdf((l-m)/np.sqrt(q))
        g=float(s@inv@s);q=float(s@inv@e);vp=v/(1+v*g);mp=mu+vp*(q-mu*g)
        logp=multivariate_normal.logpdf(e,cov=S)+.5*(np.log(vp/v)+mp*mp/vp-mu*mu/v)+np.log(Z(mp,vp))-np.log(Z(mu,v))
        val,_=quad(lambda a:np.exp(multivariate_normal.logpdf(e-s*a,cov=S)+norm.logpdf(a,mu,np.sqrt(v)))/Z(mu,v),l,u,epsabs=1e-13)
        error=abs(np.exp(logp)-val);assert error<1e-10
        rows.append(dict(bounds=[l,u],absolute_error=error,passed=True))
    (ROOT/'generated/causal_amplitude_identity.json').write_text(json.dumps(dict(scope='Local Gaussian algebra; independent numerical quadrature; no new simulator evidence',checks=rows),indent=2)+'\n');print('CAUSAL_AMPLITUDE_QUADRATURE_PASS',max(r['absolute_error'] for r in rows))
if __name__=='__main__':main()

import json, math
import numpy as np
from pathlib import Path
out = {}
# T19: direct Woodbury identity, including perfect alignment loss fraction.
rng=np.random.default_rng(1919)
A=rng.normal(size=(5,5)); R=A@A.T+np.eye(5)
u=rng.normal(size=5); sig=.7; d=rng.normal(size=5)
W=np.linalg.inv(np.linalg.cholesky(R))
left=float(d @ np.linalg.solve(R+sig**2*np.outer(u,u), d))
wd=W@d; v=sig*W@u
right=float(wd@wd-(v@wd)**2/(1+v@v))
out['T19_woodbury_abs_error']=abs(left-right)
out['T19_alignment_loss_fraction']=float((4/(1+4))/1) # d aligned to v, ||v||^2=4
# T23: demonstrate error comparing arbitrary Sigma but eta defined versus R can be zero while inverse quadratic diverges.
R=np.eye(2); W=np.eye(2); Sigma=4*np.eye(2); Shat=R.copy(); eta=float(np.linalg.norm(W@Shat@W.T-np.eye(2),2)); d=np.array([1.,0.])
out['T23_counterexample']={'eta':eta,'dSigmaInvd':float(d@np.linalg.solve(Sigma,d)),'dShatInvd':float(d@np.linalg.solve(Shat,d)),'claimed_upper':float((d@np.linalg.solve(Sigma,d))/(1-eta)) if eta<1 else None}
# T23 logdet statement: with Sigma=I, Shat=(1-eta)I the exact shift is d*log(1-eta).
eta=.1; dim=3; exact=dim*math.log(1-eta); claimed_lower=-dim*math.log(1+eta)
out['T23_logdet_counterexample']={'eta':eta,'exact_logdet_difference':exact,'claimed_lower':claimed_lower,'violates_claimed_lower':exact<claimed_lower,'correct_interval':[dim*math.log(1-eta),dim*math.log(1+eta)]}
# T21 fixed shifted null: Gaussian p0=N(0,1), q=N(.5,1), true P'=N(0,1): KL(P'||p0)=0 yet likelihood ratio crosses? q/p0 is not martingale LR under p0? It is; empirical crossing rate estimate for alpha=.05 finite horizon.
# Also q=N(.5,1) has drift under P'=N(.35,1): E log(q/p0)=mu_q*m - mu_q^2/2 = .05, not KL(P'||p0)=.06125.
out['T21_drift_example']={'claimed_KL_Pprime_to_p0':0.35**2/2,'actual_E_log_q_over_p0_under_Pprime':0.5*0.35-0.5**2/2,'note':'drift is KL(Pprime||p0)-KL(Pprime||q), not KL(Pprime||p0), in general'}
# T10 count and log ratios
out['T10_counts']={'18_choose_2_plus_18':18+18*17//2,'catalog_log_ratio':math.log(171)/math.log(18),'linear_score_ratio_if_every_hypothesis_scored':171/18}
Path(__file__).with_name('numerical_checks.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2))

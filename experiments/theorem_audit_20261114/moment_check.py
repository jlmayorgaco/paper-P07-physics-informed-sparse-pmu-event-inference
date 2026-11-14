import numpy as np, json
w=np.array([.25,.75]); m=np.array([[0.,2.],[2.,0.]]); P=np.array([np.diag([.2,.1]),np.diag([.4,.3])]); mu=np.array([-1.,1.]); V=np.array([.1,.2]); C=np.array([[.02,-.01],[.04,.03]])
mb=(w[:,None]*m).sum(axis=0); mub=float(w@mu)
Ptot=sum(w[j]*P[j] for j in range(2))+sum(w[j]*np.outer(m[j]-mb,m[j]-mb) for j in range(2))
Ctot=sum(w[j]*C[j] for j in range(2))+sum(w[j]*(m[j]-mb)*(mu[j]-mub) for j in range(2))
Vtot=float(w@V+sum(w[j]*(mu[j]-mub)**2 for j in range(2)))
# Direct enumeration of within-history covariance blocks plus between-history block.
blocks=[]
for j in range(2):
 b=np.block([[P[j],C[j][:,None]],[C[j][None,:],np.array([[V[j]]])]])
 z=np.r_[m[j],mu[j]]; blocks.append(b+np.outer(z-np.r_[mb,mub],z-np.r_[mb,mub]))
direct=sum(w[j]*blocks[j] for j in range(2))
reassembled=np.block([[Ptot,Ctot[:,None]],[Ctot[None,:],np.array([[Vtot]])]])
out_path=__import__('pathlib').Path(__file__).with_name('moment_check.json')
from pathlib import Path
Path(out_path).write_text(json.dumps({'max_abs_mixture_identity_error':float(np.max(np.abs(direct-reassembled))),'mean':mb.tolist(),'severity_mean':mub,'covariance':Ptot.tolist(),'cross_covariance':Ctot.tolist(),'severity_variance':Vtot},indent=2))
print(Path(out_path).read_text())

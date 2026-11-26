"""Independent exact linear-Gaussian evidence checks for all 136 event supports."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
import json
import numpy as np
from kernels import reference_functions,synthetic_dictionary,SharedBank

ref=reference_functions();D,_,_=synthetic_dictionary(ref)
Q=np.zeros_like(D);cross={p:np.zeros(960) for p in ref['PAIRS']}
bank=SharedBank(D,Q,cross,ref);r=np.random.default_rng(390139).normal(size=960)
raw,_,_,_=bank.infer(r,batched=True,normalized=True);base=-.5*(960*np.log(2*np.pi)+r@r)
errors=[];variance=ref['SIGMA_A']**2
supports=[(b,) for b in ref['BUSES']]+ref['PAIRS']
for index,support in enumerate(supports,1):
    basis=D[:,[ref['BUSES'].index(b) for b in support]];g=basis.T@r
    K=np.eye(len(support))+variance*basis.T@basis
    expected=base+.5*(variance*g@np.linalg.solve(K,g)-np.linalg.slogdet(K)[1])
    errors.append(abs(float(raw[index]-expected)))
assert max(errors)<1e-9
result=dict(passed=True,supports=136,max_log_evidence_error=max(errors),reference='Exact Gaussian marginal likelihood, arbitrary nonzero linear signatures',physical_replay=False,C01_modified=False)
(Path(__file__).resolve().parent/'run/NORMALIZATION_ANALYTIC_CHECK.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))

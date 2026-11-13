"""Canonical rotor coordinates versus the actual nominal predictor operators.

This is an equivalence control, not a new detector or a performance campaign.
"""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import json,hashlib,re,datetime
import numpy as np
import pandas as pd
from scipy.special import logsumexp
from scipy.linalg import solve_triangular,cholesky
from scipy.sparse import csr_matrix
P=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    inputs=[P/'protocol.json',P/'dynamic_index.csv',P/'initial_parameters.csv',P/'source_predictor_protocol.json',P.parent/'channel_information_20261112/input_snapshot.npz',Path(__file__)]
    out=P/'run';out.mkdir(exist_ok=True)
    seal=P/'COORDINATE_EXTENDED_FREEZE.json'
    assert not seal.exists(),'Preserve previous execution'
    seal.write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':{str(x.relative_to(P.parent)):sha(x) for x in inputs}},indent=2)+'\n')
    pars=pd.read_csv(P/'initial_parameters.csv').set_index('symbol').value
    dynamic=pd.read_csv(P/'dynamic_index.csv').symbol.tolist()
    cfg=json.loads((P/'source_predictor_protocol.json').read_text())
    with np.load(inputs[-2]) as z:b={k:z[k] if k=='group' else z[k].astype(np.longdouble) for k in z.files}
    L=np.ones(b['T'].shape[1],dtype=np.longdouble);rotors=[]
    for i,s in enumerate(dynamic):
        if 'machine₊ω)' in s or 'machine₊δ)' in s:
            root=s.rsplit('₊',1)[0]
            if 'machine₊ω)' in s:
                H=float(pars[root+'₊H)']);Sn=float(pars[root+'₊Sn)'])
                bus=int(re.search(r'VIndex\((\d+)',s)[1])
                wb=float(pars[f'VIndex({bus}, :systembase₊ωbase)'])
                L[i]=2*H*Sn/wb*cfg['state_prior']['omega'];rotors.append(i)
            else:L[i]=cfg['state_prior']['delta']
    assert len(rotors)==10 and len(dynamic)==114
    # ON at report end has no physical-state forcing. OFF at report end
    # has exactly the same physical forcing as one full stay interval.
    for c in range(9):
        assert np.max(abs(b['u'][2+5*c,:114]))<1e-12
        assert np.allclose(b['u'][3+5*c,:114],b['u'][1+5*c,:114],rtol=1e-12,atol=1e-12)
    T=[csr_matrix(x) for x in b['T']]
    Tp=[csr_matrix(x*L[:,None]/L[None,:]) for x in b['T']]
    Jp=b['J']/L[None,None,:]
    gp=b['g']*L;up=b['u']*L;Kp=L[:,None]*b['K0']
    rng=np.random.default_rng(json.loads((P/'protocol.json').read_text())['seeds']['inference'])
    n=180;native=np.zeros((18,n,47),dtype=np.longdouble);canonical=native.copy();max_state=0.
    for c in range(18):
        x=np.zeros(len(L),dtype=np.longdouble);xp=x.copy();a=.002 if c<9 else 0.
        for k in range(n):
            op=0 if k<30 or k>90 else 2+5*c if k==30 else 3+5*c if k==90 else 1+5*c
            group=int(b['group'][op])
            native[c,k]=b['J'][group]@x+b['j'][op]+a*b['v'][op]
            canonical[c,k]=Jp[group]@xp+b['j'][op]+a*b['v'][op]
            x=T[group]@x+b['g'][op]+a*b['u'][op]
            xp=Tp[group]@xp+gp[op]+a*up[op]
            max_state=max(max_state,float(np.max(abs(x-xp/L))))
    rel=float(np.max(abs(native-canonical))/max(1.,np.max(abs(native))))
    # Null whitening and likelihood are evaluated separately in both coordinates.
    W=solve_triangular(cholesky(b['S'],lower=True),np.eye(47),lower=True)
    en=[];ec=[]
    for y,yy in zip(native,canonical):
        m=np.zeros(len(L),dtype=np.longdouble);mp=m.copy();a=[];aa=[]
        for v,vv in zip(y,yy):
            e=v-b['J'][0]@m;ee=vv-Jp[0]@mp
            a.append(W@e);aa.append(W@ee)
            m=T[0]@m+b['K0']@e;mp=Tp[0]@mp+Kp@ee
        en.append(a);ec.append(aa)
    en=np.array(en).reshape(18,-1);ec=np.array(ec).reshape(18,-1)
    # Controlled Gaussian source likelihood, known signatures. This does not
    # reproduce R11 births, pruning, marginal severity or publication clocks.
    maxll=maxpost=0.;different=0
    for i in range(180):
        y=en[i%18]+rng.normal(size=en.shape[1])
        ln=-.5*np.sum((en-y)**2,axis=1);lc=-.5*np.sum((ec-y)**2,axis=1)
        maxll=max(maxll,float(np.max(abs(ln-lc))))
        pn=np.exp(ln-logsumexp(ln));pc=np.exp(lc-logsumexp(lc))
        maxpost=max(maxpost,float(np.max(abs(pn-pc))));different+=int(np.argmax(ln)!=np.argmax(lc))
    result={'scope':'Extended-precision arithmetic follow-up of same operator equivalence, unchanged tolerance and draws; not a detector rerun',
      'sources':18,'reports_per_source':n,'noise_draws':180,'rotor_coordinates':10,
      'max_relative_prediction_difference':rel,'max_absolute_state_difference':max_state,
      'max_absolute_loglik_difference':maxll,'max_posterior_difference':maxpost,
      'different_source_decisions':different,'physical_on_off_index_check':True,
      'passed':bool(rel<1e-9 and maxll<1e-6 and maxpost<1e-8 and different==0)}
    (out/'COORDINATE_EXTENDED_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n')
    np.savez_compressed(out/'coordinate_extended_predictions.npz',native=native,canonical=canonical,scale=L)
    print(json.dumps(result,indent=2));assert result['passed']
if __name__=='__main__':main()

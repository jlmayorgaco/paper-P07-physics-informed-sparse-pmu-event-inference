"""Execute algebra/equivalence checks and a synthetic CPU microbenchmark.
Does not read C01 predictions or reserved truth, nor run/recalibrate a plant.
"""
import os
for name in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
    os.environ[name]='1'
from pathlib import Path
import csv,json,time,platform,hashlib
import numpy as np
import scipy
from scipy.stats import multivariate_normal,norm
from scipy.integrate import quad
from kernels import (reference_functions,SharedBank,synthetic_dictionary,
                     gaussian_low_rank,conditional_log_bf,whitened_statistics,source_hashes,ROOT)

OUT=Path(__file__).resolve().parent/'run';OUT.mkdir(exist_ok=True)

def main():
    started=time.time();hashes=source_hashes();ref=reference_functions()
    D,Q,cross=synthetic_dictionary(ref);B,G=ref['basis'](D,Q,cross);bank=SharedBank(D,Q,cross,ref)
    rng=np.random.default_rng(390138);residuals=[];checks=[]
    for n,(ai,aj) in enumerate([(0.,0.),(.0002,0.),(.006,0.),(.0002,-.0005),(.01,-.02),(-.03,.025)]):
        mean=ai*D[:,0]+ai*ai*Q[:,0]+aj*D[:,7]+aj*aj*Q[:,7]+ai*aj*cross[(3,18)]
        r=mean+rng.normal(size=960);residuals.append(r)
        a=ref['infer'](r,D,Q,cross,B,G);b=bank.infer(r)
        errors=[float(np.max(abs(x-y))) for x,y in zip(a,b)]
        same1=bool(np.argmax(a[1])==np.argmax(b[1]));same3=bool(np.array_equal(np.argsort(-a[1])[:3],np.argsort(-b[1])[:3]))
        assert errors[0]<1e-7 and errors[1]<1e-9 and same1 and same3,(n,errors)
        assert np.allclose(a[2],b[2],rtol=1e-8,atol=1e-9)
        assert np.allclose(a[3],b[3],rtol=1e-8,atol=1e-8)
        checks.append(dict(fixture=n,max_log_evidence_error=errors[0],max_posterior_error=errors[1],same_top1=same1,same_top3=same3))
        c=bank.infer(r,batched=True);error=float(np.max(abs(a[0]-c[0])))
        assert error<1e-7 and np.max(abs(a[1]-c[1]))<1e-9
        assert np.array_equal(np.argsort(-a[1])[:3],np.argsort(-c[1])[:3])
        assert all(np.allclose(x,y,rtol=1e-8,atol=1e-8) for x,y in zip(a[2:],c[2:]))
        checks[-1].update(batched_log_evidence_error=error,batched_posterior_error=float(np.max(abs(a[1]-c[1]))),batched_same_top3=True)
    numerical=[]
    zero=np.zeros_like(D);zero_cross={p:np.zeros(960) for p in ref['PAIRS']}
    zero_bank=SharedBank(zero,zero,zero_cross,ref)
    _,legacy,_,_=zero_bank.infer(np.zeros(960),batched=True)
    _,corrected,_,_=zero_bank.infer(np.zeros(960),batched=True,normalized=True)
    mass=lambda p:[float(p[0]),float(p[1:17].sum()),float(p[17:].sum())]
    assert np.allclose(mass(corrected),ref['CARD_PRIOR'],atol=1e-12)
    assert not np.allclose(mass(legacy),ref['CARD_PRIOR'],atol=1e-3)
    normalization=dict(legacy_null_masses=mass(legacy),corrected_null_masses=mass(corrected),declared_prior=ref['CARD_PRIOR'],correction_single_logZ=float(np.log(2*np.pi)),legacy_bug_preserved_in_replay=True,physical_data_replay_pending=True)
    A=rng.normal(size=(32,32));Sigma=.1*np.eye(32)+A@A.T/32;N=rng.normal(size=(32,3));E=rng.normal(size=(32,3));L=np.diag([.1,.2,.05]);r=rng.normal(size=32)
    for amplitude in [0.,.02,-.05]:
        design=N+amplitude*E;cov=Sigma+design@L@L.T@design.T
        error=abs(gaussian_low_rank(r,Sigma,design,L)-multivariate_normal.logpdf(r,cov=cov))
        assert error<1e-10;numerical.append(dict(check='hypothesis_covariance',amplitude=amplitude,error=error))
    error=abs(gaussian_low_rank(r,Sigma,N,np.zeros_like(L))-multivariate_normal.logpdf(r,cov=Sigma));assert error<1e-10
    numerical.append(dict(check='R0_zero_parameter_uncertainty',error=error))
    cov=np.array([[.5,.1],[.1,.4]]);res=np.array([.2,-.4]);signature=np.array([1.,-.7]);v=.03
    integral=quad(lambda x:np.exp(multivariate_normal.logpdf(res-signature*x,cov=cov)+norm.logpdf(x,scale=np.sqrt(v))),-2.,2.,epsabs=1e-12)[0]
    error=abs(conditional_log_bf(res,signature,cov,v)-(np.log(integral)-multivariate_normal.logpdf(res,cov=cov)));assert error<1e-10
    numerical.append(dict(check='conditional_Bayes_factor',error=error))
    blocks=rng.normal(size=(30,8,5));ys=rng.normal(size=(30,8));prefix=whitened_statistics(blocks,ys)
    future=ys.copy();future[15:]+=99.;alternative=whitened_statistics(blocks,future)
    for k,(h,g,q) in enumerate(prefix):
        flat=blocks[:k+1].reshape(-1,5);y=ys[:k+1].reshape(-1)
        assert np.allclose(h,flat.T@flat) and np.allclose(g,flat.T@y) and np.isclose(q,y@y)
        if k<15:assert all(np.array_equal(a,b) for a,b in zip(prefix[k],alternative[k]))
    numerical.append(dict(check='prefix_additivity_and_future_independence',prefixes=30,error=0.))
    # Same full frozen numerical functions; only repeated support projections differ.
    timing=[]
    for _ in range(3):ref['infer'](residuals[0],D,Q,cross,B,G);bank.infer(residuals[0]);bank.infer(residuals[0],batched=True)
    for n in range(30):
        r=residuals[n%len(residuals)]
        methods=[('existing_support_Gram',lambda:ref['infer'](r,D,Q,cross,B,G)),('shared_Gram_candidate',lambda:bank.infer(r)),('batched_GH31_candidate',lambda:bank.infer(r,batched=True))]
        if n%2:methods.reverse()
        for method,call in methods:
            t=time.perf_counter();call();timing.append(dict(repetition=n,method=method,milliseconds=(time.perf_counter()-t)*1000))
    with (OUT/'timings.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(timing[0]));w.writeheader();w.writerows(timing)
    summary=[]
    for method in ['existing_support_Gram','shared_Gram_candidate','batched_GH31_candidate']:
        x=np.array([z['milliseconds'] for z in timing if z['method']==method])
        summary.append(dict(method=method,p50_ms=float(np.percentile(x,50)),p95_ms=float(np.percentile(x,95)),p99_ms=float(np.percentile(x,99)),repetitions=len(x)))
    assert source_hashes()==hashes
    physical=ROOT/'research/pmu_hybrid_dae_bayes/powerdynamics_ieee39/output'
    missing=[str(p.relative_to(ROOT)) for p in [physical/'load_tangent_v2/results/load_fd_central_operator.npz',physical/'load_multi_bayes_v1/results/load_multi_qij.npz'] if not p.exists()]
    report=dict(status='ALGEBRA_AND_SYNTHETIC_EQUIVALENCE_PASS',IEEE39_physical_replay_executed=False,not_R11_speed_benchmark=True,legacy_Gram_already_implemented=True,hypotheses=137,GH_order=31,quadrature_nodes=1+16*31+120*31*31,dimensions=960,basis_columns=152,equivalence=checks,numerical=numerical,normalization=normalization,timings=summary,pair_cache_bytes=int(B.nbytes+G.nbytes),shared_cache_bytes=int(bank.F.nbytes+bank.H.nbytes+bank.G.nbytes+bank.index.nbytes),processor=platform.processor(),logical_CPUs=os.cpu_count(),numpy=np.__version__,scipy=scipy.__version__,blas_threads=1,source_hashes=hashes,missing_original_replay_inputs=missing,C01_modified=False,RAW0002_opened=False,wall_seconds=time.time()-started)
    (OUT/'RESULTS.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

if __name__=='__main__':main()

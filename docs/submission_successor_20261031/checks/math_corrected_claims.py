"""Independent numerical checks for corrected supplementary claims M1--M7.

All examples are dimensionless. No campaign module, simulator, observations,
truth, or historical outputs are imported/read. Only this script's own JSON
is written. These checks do not add physical-performance evidence.
"""
from pathlib import Path
import itertools
import hashlib
import json
import math
import numpy as np
from scipy.integrate import quad, dblquad
from scipy.optimize import minimize_scalar, nnls
from scipy.special import gamma, ndtr, logsumexp
from scipy.stats import norm

HERE = Path(__file__).resolve().parent
rng = np.random.default_rng(20261031)
results = {}


def direction(angle):
    return np.array([np.cos(angle), np.sin(angle)])


def directed_minimum_by_nnls(arc, competitor):
    """Minimize over one cone's unit arc, project independently onto the other."""
    columns = np.stack([direction(competitor[0]), direction(competitor[1])], axis=1)
    def value(angle):
        return nnls(columns, direction(angle))[1]**2
    grid = np.linspace(arc[0], arc[1], 51)
    values = np.array([value(a) for a in grid])
    candidates = [values[0], values[-1]]
    for index in np.argsort(values)[:3]:
        lo, hi = grid[max(0,index-1)], grid[min(len(grid)-1,index+1)]
        if hi > lo:
            opt = minimize_scalar(value, bounds=(lo,hi), method='bounded', options={'xatol':1e-13})
            candidates.append(opt.fun)
    return np.sqrt(max(0.,min(candidates)))


# M1: the two directions are solved independently, not by transposing a shared
# pairwise cosine matrix. Includes disjoint, overlapping and opposite cones.
cone_cases = [((0.,np.pi/6),(np.pi/3,np.pi/2)),
              ((0.,np.pi/3),(np.pi/6,np.pi/2)),
              ((-.1,.1),(np.pi-.1,np.pi+.1))]
for _ in range(12):
    a,b = rng.uniform(-np.pi,np.pi,2)
    widths = rng.uniform(.1,1.8,2)
    cone_cases.append(((a,a+widths[0]),(b,b+widths[1])))
cone_errors=[]
for s,c in cone_cases:
    forward=directed_minimum_by_nnls(s,c)
    reverse=directed_minimum_by_nnls(c,s)
    cone_errors.append(abs(forward-reverse))
assert max(cone_errors)<2e-7
assert abs(directed_minimum_by_nnls(*cone_cases[0])-.5)<2e-7
results['M1_cone_symmetry']={'cases':len(cone_cases),'max_independent_direction_error':max(cone_errors)}

# M2: regular positive-mass cone, half-line, proper half-normal prior.
# The unnormalized Gaussian observation kernel is kept identical in the exact
# and asymptotic expressions; data y=eps*z has a nonzero limiting score.
laplace=[]
tau=.7
prior_at_zero=2*norm.pdf(0,scale=tau)
for z in (-2.,0.,1.):
    errors=[]
    for eps in (.1,.05,.025,.0125):
        exact=eps*quad(lambda t: np.exp(-.5*(t-z)**2)*2*norm.pdf(eps*t,scale=tau),0,np.inf,epsabs=1e-13,epsrel=1e-12)[0]
        equivalent=prior_at_zero*eps*np.sqrt(2*np.pi)*ndtr(z)
        errors.append(abs(exact/equivalent-1))
    assert errors[-1]<errors[0]
    assert errors[-1]<.002
    laplace.append({'score':z,'relative_errors':errors})
results['M2_regular_cone_laplace']={'cases':laplace,'limiting_cone_mass_positive':True}

# The previous cusp counterexample is outside the repaired theorem: its tangent
# cone spans dimension one although the parameter chart has dimension two.
cusp_ratios=[]
for eps in (.05,.025,.0125):
    def integrand(t):
        inner=quad(lambda v: np.exp(-.5*eps**2*t**4*v*v),0,1,epsabs=1e-13)[0]
        return t*t*np.exp(-.5*t*t)*inner
    evidence=3*eps**3*quad(integrand,0,min(1/eps,12),epsabs=1e-12)[0]
    cusp_ratios.append(evidence/eps**3)
assert abs(cusp_ratios[-1]/(3*np.sqrt(np.pi/2))-1)<.001
results['M2_excluded_cusp']={'chart_dimension':2,'tangent_dimension':1,'nonempty_interior':False,'evidence_over_epsilon_cubed':cusp_ratios,'limit':3*np.sqrt(np.pi/2)}

# M3: a genuinely redundant likelihood coordinate with a correlated proper
# prior. Integrating it out numerically agrees with the induced-prior integral.
y=.4
prior_mean=.3
prior_sd=.5
noise_sd=.4
full=dblquad(lambda zeta,xi: norm.pdf(y,xi,noise_sd)*norm.pdf(xi,prior_mean,prior_sd)*norm.pdf(zeta,xi,.8),-5,5,lambda xi:-8,lambda xi:8,epsabs=1e-10,epsrel=1e-10)[0]
reduced=quad(lambda xi: norm.pdf(y,xi,noise_sd)*norm.pdf(xi,prior_mean,prior_sd),-5,5,epsabs=1e-12)[0]
assert abs(full-reduced)<1e-9
varying_variance=quad(lambda z: .5*norm.pdf(0,0,np.exp(z)),-1,1,epsabs=1e-13)[0]
representative=norm.pdf(0)
assert abs(varying_variance-representative)>.05
results['M3_full_law_fibers']={'full_vs_reduced_error':abs(full-reduced),'excluded_mean_only_counterexample_difference':abs(varying_variance-representative)}

# M4: proper uniform prior on [-1,1]^2, observable map (xi,a^k), centered data.
# The finite-domain integral factorizes, independently of the displayed gamma
# constant; compare the finite epsilon integral for k=1,2,3.
mixed=[]
for k in (1,2,3):
    constant=.25*np.sqrt(2*np.pi)*gamma(1/(2*k))/k*2**(1/(2*k))
    errors=[]
    for eps in (.1,.03,.01):
        regular=eps*quad(lambda u: np.exp(-.5*u*u),-min(1/eps,12),min(1/eps,12),epsabs=1e-13)[0]
        bound=min(eps**(-1/k),8)
        singular=eps**(1/k)*quad(lambda t: np.exp(-.5*t**(2*k)),-bound,bound,epsabs=1e-13)[0]
        actual=.25*regular*singular
        errors.append(abs(actual/(constant*eps**(1+1/k))-1))
    assert max(errors)<1e-9
    mixed.append({'k':k,'relative_errors':errors})
noiseless=quad(lambda t: np.exp(-.5*t**4),-8,8,epsabs=1e-13)[0]
shifted=quad(lambda t: np.exp(-.5*(t*t-1)**2),-8,8,epsabs=1e-13)[0]
one_sided=quad(lambda t: np.exp(-.5*t**4),0,8,epsabs=1e-13)[0]
assert abs(shifted/noiseless-1)>.1
assert abs(one_sided/noiseless-.5)<1e-12
results['M4_centered_bilateral_constant']={'cases':mixed,'noncentered_constant_ratio':shifted/noiseless,'one_sided_factor_at_equal_local_prior_density':one_sided/noiseless}

# M5: all 137 supports, comparing historical score factors with the mathematically
# equivalent effective prior. This validates interpretation, not physical scores.
cardinalities=np.array([0]+[1]*16+[2]*120)
declared_cardinality=np.array([.2,.5,.3])
support_prior=declared_cardinality[cardinalities]/np.array([1,16,120])[cardinalities]
offset=-np.log(2*np.pi)*(cardinalities==1)
effective_cardinality=declared_cardinality*np.array([1,1/(2*np.pi),1])
effective_cardinality/=effective_cardinality.sum()
effective_support_prior=effective_cardinality[cardinalities]/np.array([1,16,120])[cardinalities]
prior_errors=[]
for _ in range(20):
    logevidence=rng.normal(0,10,137)
    historical=logevidence+offset+np.log(support_prior)
    equivalent=logevidence+np.log(effective_support_prior)
    ph=np.exp(historical-logsumexp(historical))
    pe=np.exp(equivalent-logsumexp(equivalent))
    prior_errors.append(float(np.max(abs(ph-pe))))
assert max(prior_errors)<1e-13
null_posterior=np.exp(offset+np.log(support_prior)-logsumexp(offset+np.log(support_prior)))
null_cardinality=np.array([null_posterior[cardinalities==k].sum() for k in range(3)])
assert np.max(abs(null_cardinality-effective_cardinality))<1e-13
assert np.max(abs(null_cardinality-declared_cardinality))>.3
results['M5_historical_effective_prior']={'supports':137,'cases':20,'max_posterior_equivalence_error':max(prior_errors),'zero_response_cardinality':null_cardinality.tolist(),'corrected_physical_results_claimed':False}

# M6: explicit coefficient-domain margin counts null directions of wide maps.
wide=np.array([[1.,1.]])
wide_margin=np.sqrt(max(0.,np.linalg.eigvalsh(wide.T@wide)[0]))
assert wide_margin==0
H=rng.normal(size=(8,6))
K=2
restricted=min(np.sqrt(max(0.,np.linalg.eigvalsh(H[:,U].T@H[:,U])[0])) for n in range(1,2*K+1) for U in itertools.combinations(range(6),n))
assert restricted>0
bound_slack=[]
for _ in range(30):
    a,b=np.zeros(6),np.zeros(6)
    a[rng.choice(6,K,replace=False)]=rng.normal(size=K)
    b[rng.choice(6,K,replace=False)]=rng.normal(size=K)
    epsilon=np.linalg.norm(H@(a-b))/2
    bound=2*epsilon/restricted
    bound_slack.append(float(bound-np.linalg.norm(a-b)))
assert min(bound_slack)>=-1e-12
results['M6_restricted_margin']={'wide_map_margin':wide_margin,'full_column_restricted_margin':restricted,'minimum_bound_slack':min(bound_slack),'bound_cases':30}

# M7: positive-definite nuisance information admits inverse-order comparison;
# singular and zero-tangent examples are explicitly outside the scalar formulas.
information_gains=[]
for _ in range(30):
    X=rng.normal(size=(6,4))
    d,N=X[:,0],X[:,1:]
    block=N.T@N
    C=rng.normal(size=(3,3))
    precision=C@C.T
    cross=d@N
    before=d@d-cross@np.linalg.solve(block,cross)
    after=d@d-cross@np.linalg.solve(block+precision,cross)
    information_gains.append(float(after-before))
assert min(information_gains)>=-1e-12
singular=np.ones((2,2))
assert np.linalg.eigvalsh(singular)[0]==0
null_tangent=np.zeros(4)
nonzero=np.arange(1.,5.)
projector=np.eye(4)-null_tangent[:,None]@np.linalg.pinv(null_tangent[:,None])
assert np.allclose(projector@nonzero,nonzero)
results['M7_domains']={'positive_definite_cases':30,'minimum_preevent_information_gain':min(information_gains),'singular_precision_rejected':True,'null_competitor_tangent_scalar_division_rejected':True}

results['all_checks_passed']=True
results['scope']='Dimensionless independent algebra only; no simulator, RAW, C01 or physical-performance evaluation.'
paper_root=HERE.parents[2]
results['reviewed_source_sha256']={name:hashlib.sha256((paper_root/name).read_bytes()).hexdigest() for name in ['supplement/appendix_d_theory.tex','supplement/appendix_e_estimator.tex']}
results['check_script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
path=HERE/'math_corrected_claims.json'
path.write_text(json.dumps(results,indent=2),encoding='utf-8')
print(json.dumps(results,indent=2))

"""Independent algebraic checks; no manuscript/runtime imports or simulations.

Only the audit's own JSON result is written. No data arrays, event truth, or
campaign output is read. All experiments are dimensionless counterexamples.
"""
from pathlib import Path
import json
import math
import itertools
import numpy as np
from scipy.integrate import quad
from scipy.special import ndtr, gamma
from scipy.stats import norm

HERE = Path(__file__).resolve().parent
rng = np.random.default_rng(20261031)
out = {}

# The causal integral in appendix_causal_walkthrough.tex:121-154.
integral_errors = []
state_errors = []
for trial in range(12):
    n, m = 3, 2
    B = rng.normal(size=(n, n))
    P = B @ B.T + np.eye(n)
    J = rng.normal(size=(m, n))
    T = rng.normal(size=(n, n))
    R = np.eye(m) * 0.7
    Q = np.eye(n) * 0.2
    mh, dh, go, uo = rng.normal(size=(4, n))
    jo, vo, y = rng.normal(size=(3, m))
    mu, v, lo, hi = 0.1, 0.4, -0.2, 0.2
    e, s = y - J @ mh - jo, J @ dh + vo
    S = R + J @ P @ J.T
    Si = np.linalg.inv(S)
    K = T @ P @ J.T @ Si
    g, q = s @ Si @ s, s @ Si @ e
    vp = 1 / (1 / v + g)
    mup = vp * (mu / v + q)
    Z = ndtr((hi - mu) / np.sqrt(v)) - ndtr((lo - mu) / np.sqrt(v))
    Zp = ndtr((hi - mup) / np.sqrt(vp)) - ndtr((lo - mup) / np.sqrt(vp))
    logL = (-0.5 * (e @ Si @ e + np.linalg.slogdet(S)[1] + m*np.log(2*np.pi))
            + 0.5 * (np.log(vp/v) + mup*mup/vp - mu*mu/v) + np.log(Zp/Z))
    def integrand(a):
        residual = e - s*a
        ll = -0.5*(residual @ Si @ residual + np.linalg.slogdet(S)[1] + m*np.log(2*np.pi))
        return np.exp(ll) * norm.pdf(a, mu, np.sqrt(v)) / Z
    L = quad(integrand, lo, hi, epsabs=1e-13, epsrel=1e-12)[0]
    integral_errors.append(abs(np.exp(logL)/L-1))
    Ea = quad(lambda a: a*integrand(a), lo, hi, epsabs=1e-13)[0]/L
    Ea2 = quad(lambda a: a*a*integrand(a), lo, hi, epsabs=1e-13)[0]/L
    mp, dp = T@mh + go + K@e, T@dh + uo - K@s
    closed_mean = mp + dp*Ea
    direct_mean = np.array([quad(lambda a: (T@(mh+dh*a)+go+uo*a+K@(e-s*a))[i]*integrand(a), lo, hi, epsabs=1e-12)[0]/L for i in range(n)])
    state_errors.append(float(np.max(np.abs(closed_mean-direct_mean))))
out['causal_integral_and_conditional_state'] = dict(
    cases=12, max_relative_evidence_error=max(integral_errors),
    max_conditional_state_mean_error=max(state_errors),
    scope='exact conditional Gaussian algebra only; shared Riccati/pruning not validated')

# Rank-deficient nuisance profiling and exact prefix consistency.
profile_errors, increments = [], []
for trial in range(30):
    N0 = rng.normal(size=(6, 2))
    N = np.c_[N0, N0[:, 0]+N0[:, 1]]
    d = rng.normal(size=6)
    B = rng.normal(size=(6, 6))
    Sigma = B@B.T + np.eye(6)
    W = np.linalg.inv(np.linalg.cholesky(Sigma))
    A, f = W@N, W@d
    residual = f - A@np.linalg.lstsq(A, f, rcond=None)[0]
    I = d@np.linalg.solve(Sigma,d) - d@np.linalg.solve(Sigma,N)@np.linalg.pinv(N.T@np.linalg.solve(Sigma,N))@N.T@np.linalg.solve(Sigma,d)
    profile_errors.append(abs(I-residual@residual))
    values=[]
    for t in (3,4,5,6):
        Wt=np.linalg.inv(np.linalg.cholesky(Sigma[:t,:t]))
        At, ft=Wt@N[:t], Wt@d[:t]
        rt=ft-At@np.linalg.lstsq(At,ft,rcond=None)[0]
        values.append(float(rt@rt))
    increments.extend(np.diff(values))
out['fisher_and_prefix'] = dict(cases=30,max_identity_error=max(profile_errors), minimum_prefix_increment=float(min(increments)))

# The stated minimum gap of cones is symmetric, even for different apertures.
def ray(angle):
    return np.array([np.cos(angle),np.sin(angle)])
S=np.array([ray(a) for a in np.linspace(0,np.pi/6,151)])
C=np.array([ray(a) for a in np.linspace(np.pi/3,np.pi/2,151)])
cosines=S@C.T
forward=float(np.sqrt(1-max(0.,np.max(cosines))**2))
reverse=float(np.sqrt(1-max(0.,np.max(cosines.T))**2))
out['cone_minimum_gap'] = dict(forward=forward,reverse=reverse,analytical=0.5, conclusion='Definition in appendix D is symmetric; the asymmetry sentence is false.')

# Laplace cusp: proper uniform prior 3 on 0<=x<=1, 0<=y<=x^2.
# Positive definite H=I; isotropic tangent cone is the positive x ray.
# Gaussian normalizer-free evidence is positive and asymptotic to
# 3*sqrt(pi/2)*eps^3, not eps^2 times a nonzero Gaussian cone mass.
cusp=[]
for eps in (0.2,0.1,0.05,0.025,0.0125):
    def transformed(t):
        inner=quad(lambda v: np.exp(-0.5*eps*eps*t**4*v*v),0,1,epsabs=1e-13)[0]
        return t*t*np.exp(-0.5*t*t)*inner
    value=3*eps**3*quad(transformed,0,min(1/eps,12),epsabs=1e-12)[0]
    cusp.append(dict(epsilon=eps,evidence=value,over_epsilon_cubed=value/eps**3))
out['cone_laplace_cusp'] = dict(results=cusp,leading_constant=3*np.sqrt(np.pi/2),limiting_gaussian_cone_probability=0.,conclusion='Need positive Gaussian mass/full-dimensional cone for multiplicative equivalent; otherwise only a zero leading coefficient is proved.')

# Mixed regular/higher-order theorem: mu(xi,a)=(xi,a^2).
# Show the constant depends on observation z in y=(0,eps*z), and on domain.
mixed=[]
base_integral=quad(lambda t: np.exp(-0.5*t**4),-8,8,epsabs=1e-13)[0]
for z in (0.,1.,-1.):
    normal=quad(lambda t: np.exp(-0.5*(t*t-z)**2),-8,8,epsabs=1e-13)[0]
    mixed.append(dict(z=z,normal_integral=normal,relative_to_noiseless=normal/base_integral))
out['mixed_higher_order_constant'] = dict(
    signed_normal_integral=base_integral, formula=gamma(0.25)*2**0.25/2,
    shifted_observation=mixed,one_sided_factor_at_fixed_prior_density=0.5,
    conclusion='Displayed constant is correct for signed interior a and noiseless centered data; these conditions need stating.')

# NumPy's standard rectangular sigma_min omits the null singular directions.
H=np.array([[1.,1.]])
mins=[]
for count in (1,2):
    for columns in itertools.combinations(range(2),count):
        mins.append(float(np.linalg.svd(H[:,columns],compute_uv=False)[-1]))
av,bv=np.array([1.,0.]),np.array([0.,1.])
out['restricted_margin_convention'] = dict(
    standard_rectangular_svd_margin=min(mins),
    difference_norm=float(np.linalg.norm(av-bv)),
    observed_difference=float(np.linalg.norm(H@(av-bv))),
    rayleigh_minimum=0.,
    conclusion='Use sqrt(lambda_min(H_U.T@H_U)) or inf over unit coefficient vectors; otherwise the general stability statement fails for wide matrices.')

# Rank deficiency is permitted by the preceding nuisance theorem.
Nv=np.array([[1.,1.]])
out['preevent_inverse_domain'] = dict(nuisance_fisher=(Nv.T@Nv).tolist(),rank=int(np.linalg.matrix_rank(Nv.T@Nv)),allowed_pre_event_precision=np.zeros((2,2)).tolist(),conclusion='Ordinary inverse in pre-event corollary needs positive definiteness or identifiable quotient.')

# Equal observable means do not imply redundant likelihood coordinates when
# covariance depends on that coordinate. zeta~Uniform[-1,1], sigma=exp(zeta).
mixture_at_zero=quad(lambda z: 0.5*norm.pdf(0,0,np.exp(z)),-1,1,epsabs=1e-13)[0]
out['redundant_fiber_requires_full_law'] = dict(
    marginalized_density_y0=mixture_at_zero,
    density_at_arbitrary_representative_zeta0=float(norm.pdf(0)),
    analytical_ratio=float(np.sinh(1)),
    conclusion='Mean map is constant along zeta fibers but likelihood is not; require full conditional-law invariance, e.g. fixed covariance.')

legacy=np.array([0.20,0.50/(2*np.pi),0.30])
out['acknowledged_legacy_normalizer'] = dict(
    declared=[0.20,0.50,0.30],effective=(legacy/legacy.sum()).tolist(),
    single_log_evidence_offset=float(-np.log(2*np.pi)),
    conclusion='Zero-response posterior equals effective prior; historical defect already disclosed, distinct from R11.')

assert max(integral_errors) < 1e-11
assert max(state_errors) < 1e-11
assert max(profile_errors) < 1e-10
assert min(increments) >= -1e-10
assert abs(forward-reverse) < 1e-14
assert abs(cusp[-1]['over_epsilon_cubed']/(3*np.sqrt(np.pi/2))-1)<0.001
assert np.linalg.norm(H@(av-bv)) == 0
assert np.linalg.norm(av-bv)>1
out['all_checks_passed']=True

target=HERE/'math_independent_checks.json'
target.write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2))

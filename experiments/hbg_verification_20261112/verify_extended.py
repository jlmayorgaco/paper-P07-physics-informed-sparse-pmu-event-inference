#!/usr/bin/env python3
"""Independent low-cost checks for the supplied HBG derivation.

All checks concern Gaussian identities or a reduced lossless swing model.
They do not simulate the IEEE-39 DAE or PMU pipeline.
"""
import json
import os
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import numpy as np
from scipy.integrate import quad, solve_ivp
from scipy.linalg import cho_factor, cho_solve
from scipy.special import ndtr
from scipy.stats import multivariate_normal

TOL = 2e-8
gates = {}
metrics = {}


def gate(name, condition, metric=None):
    gates[name] = bool(condition)
    if metric is not None:
        metrics[name] = float(metric)


# Gaussian Bayes factor: compare the rank-one expression with normalized
# densities, and independently integrate the scalar Gaussian prior.
S = np.array([[1.4, .2, -.1], [.2, .9, .12], [-.1, .12, 1.1]])
s = np.array([.7, -.4, .2]); r = np.array([.3, -.8, .5]); v = .36
cf = cho_factor(S, lower=True)
Sinv_s = cho_solve(cf, s); Sinv_r = cho_solve(cf, r)
G, b = s @ Sinv_s, s @ Sinv_r
bf = v*b*b/(2*(1+v*G)) - .5*np.log1p(v*G)
bf_density = (multivariate_normal.logpdf(r, cov=S+v*np.outer(s, s))
              - multivariate_normal.logpdf(r, cov=S))
bf_integral = quad(lambda a: np.exp(multivariate_normal.logpdf(r-a*s, cov=S))
                   * np.exp(-a*a/(2*v))/np.sqrt(2*np.pi*v), -np.inf, np.inf,
                   epsabs=1e-12)[0]
bf_from_integral = np.log(bf_integral) - multivariate_normal.logpdf(r, cov=S)
gate("gaussian_bf_vs_direct_density", abs(bf-bf_density) < TOL, bf-bf_density)
gate("gaussian_bf_vs_integrated_prior", abs(bf-bf_from_integral) < TOL,
     bf-bf_from_integral)

# Truncated-normal normalizer and first moment checked by direct quadrature.
mu, sig, lo, hi = .35, .8, -.2, 1.1
Z = ndtr((hi-mu)/sig)-ndtr((lo-mu)/sig)
z_quad = quad(lambda x: np.exp(-.5*((x-mu)/sig)**2)/(sig*np.sqrt(2*np.pi)),
              lo, hi, epsabs=1e-13)[0]
mean_formula = mu + sig*(np.exp(-.5*((lo-mu)/sig)**2)-np.exp(-.5*((hi-mu)/sig)**2))/(np.sqrt(2*np.pi)*Z)
mean_quad = quad(lambda x: x*np.exp(-.5*((x-mu)/sig)**2)/(sig*np.sqrt(2*np.pi)),
                 lo, hi, epsabs=1e-13)[0]/z_quad
gate("truncated_gaussian_normalizer", abs(Z-z_quad) < TOL, Z-z_quad)
gate("truncated_gaussian_mean", abs(mean_formula-mean_quad) < TOL,
     mean_formula-mean_quad)

# Truncated-prior evidence: use posterior/prior truncation-normalizer ratio,
# then compare it with direct integration under the normalized truncated prior.
prior_mu, prior_sd, amin, amax = .12, .5, -.25, .7
logZprior = np.log(ndtr((amax-prior_mu)/prior_sd)-ndtr((amin-prior_mu)/prior_sd))
post_var = 1/(G+1/prior_sd**2)
post_mu = post_var*(b+prior_mu/prior_sd**2)
logZpost = np.log(ndtr((amax-post_mu)/np.sqrt(post_var))-
                   ndtr((amin-post_mu)/np.sqrt(post_var)))
bf_gaussian_shifted = (multivariate_normal.logpdf(r, mean=prior_mu*s,
                                                  cov=S+prior_sd**2*np.outer(s,s))
                       - multivariate_normal.logpdf(r, cov=S))
bf_trunc_formula = bf_gaussian_shifted + logZpost-logZprior
def trunc_integrand(a):
    return np.exp(multivariate_normal.logpdf(r-a*s, cov=S)
                  - multivariate_normal.logpdf(r, cov=S)
                  -.5*((a-prior_mu)/prior_sd)**2
                  -np.log(prior_sd*np.sqrt(2*np.pi))-logZprior)
bf_trunc_direct = np.log(quad(trunc_integrand, amin, amax, epsabs=1e-12)[0])
gate("truncated_prior_bf_normalization", abs(bf_trunc_formula-bf_trunc_direct) < TOL,
     bf_trunc_formula-bf_trunc_direct)

# Recovery uncertainty: marginal Woodbury/Schur solution vs full joint MAP.
rng = np.random.default_rng(261112)
n, m = 4, 7
A = rng.normal(size=(n, n)); P = A@A.T + .4*np.eye(n)
A = rng.normal(size=(m, m)); R = A@A.T + .7*np.eye(m)
O, s, r = rng.normal(size=(m, n)), rng.normal(size=m), rng.normal(size=m)
va = .55
Sigma = R + O@P@O.T
cf = cho_factor(Sigma, lower=True)
Sigr, Sigs = cho_solve(cf, r), cho_solve(cf, s)
ahat = (s@Sigr)/(s@Sigs+1/va)
Vhat = 1/(s@Sigs+1/va)
xhat = P@O.T@cho_solve(cf, r-s*ahat)
H = np.block([[O.T@np.linalg.solve(R, O)+np.linalg.inv(P), O.T@np.linalg.solve(R, s)[:, None]],
              [(s@np.linalg.solve(R, O))[None, :], np.array([[s@np.linalg.solve(R, s)+1/va]])]])
rhs = np.r_[O.T@np.linalg.solve(R, r), s@np.linalg.solve(R, r)]
joint = np.linalg.solve(H, rhs)
res = max(np.max(np.abs(joint[:n]-xhat)), abs(joint[-1]-ahat))
gate("woodbury_map_equals_joint_map", res < TOL, res)

# Profiling a free competing amplitude: adding a channel cannot reduce the
# minimum Mahalanobis distance. Correlated V/I channels make contributions
# non-additive, demonstrated against the incorrect sum of marginal distances.
Svi = np.array([[1.2, .25], [.25, .8]])
si = np.array([1., .2]); sj = np.array([.5, -.3]); atrue = .9
def profiled_d2(y, x, cov):
    ci_x = np.linalg.solve(cov, x); ci_y = np.linalg.solve(cov, y)
    return float(y@ci_y - (x@ci_y)**2/(x@ci_x))
d_joint = profiled_d2(atrue*si, sj, Svi)
d_v = profiled_d2(np.array([atrue*si[0]]), np.array([sj[0]]), Svi[:1,:1])
condvar = Svi[1,1]-Svi[1,0]**2/Svi[0,0]
cond_y = atrue*si[1] - Svi[1,0]/Svi[0,0]*(atrue*si[0])
cond_x = sj[1] - Svi[1,0]/Svi[0,0]*sj[0]
# Under the joint optimum, Mahalanobis distance decomposes into the V marginal
# residual plus the I|V conditional residual, sharing the same fitted amplitude.
Ci = np.linalg.inv(Svi)
b_joint = (sj@Ci@(atrue*si))/(sj@Ci@sj)
d_cond_at_joint = (cond_y-b_joint*cond_x)**2/condvar
d_decomposed = ((atrue*si[0]-b_joint*sj[0])**2/Svi[0,0])+d_cond_at_joint
# Separately minimizing V and I marginal distances uses two distinct amplitude
# fits; its sum need not equal the joint profile with one shared amplitude.
d_i = profiled_d2(np.array([atrue*si[1]]), np.array([sj[1]]), Svi[1:,1:])
gate("profile_distance_monotone_V_to_VI", d_joint + TOL >= d_v, d_joint-d_v)
gate("profile_distance_conditional_decomposition", abs(d_joint-d_decomposed) < TOL,
     d_joint-d_decomposed)
gate("profile_distance_not_sum_of_separate_marginal_profiles",
     abs(d_joint-(d_v+d_i)) > 1e-5, d_joint-(d_v+d_i))

# Hamiltonian balance for only a reduced lossless swing network; independently
# integrate power along dense solution output. This is explicitly not a DAE test.
B = np.array([[1., 0.], [-1., 1.], [0., -1.]])
K = np.array([1.7, .9]); M = np.diag([1.1, 1.3, .8]); D = np.diag([.12, .15, .1])
u = np.array([.04, -.02, .01]); theta0=np.array([.025,-.01,.015]); omega0=np.array([.01,-.006,.004])
def Hfun(th, om): return .5*om@M@om + np.sum(K*(1-np.cos(B.T@th)))
def f(t, state):
    th, om = state[:3], state[3:]
    return np.r_[om, np.linalg.solve(M, u-D@om-B@(K*np.sin(B.T@th)))]
sol=solve_ivp(f, (0, .7), np.r_[theta0,omega0], rtol=1e-11, atol=1e-13, dense_output=True)
gate("reduced_swing_solver_success", sol.success)
if not sol.success:
    raise RuntimeError(f"reduced swing integration failed: {sol.message}")
def power(t):
    om=sol.sol(t)[3:]
    return float(om@u-om@D@om)
balance=Hfun(sol.y[:3,-1],sol.y[3:,-1])-Hfun(theta0,omega0)-quad(power,0,.7,epsabs=1e-12)[0]
gate("reduced_swing_hamiltonian_balance", abs(balance) < 2e-9, balance)
switch_jump = -K[1]*(1-np.cos(B[:,1]@sol.y[:3,-1]))
switched_K=K.copy(); switched_K[1]=0.
actual_jump=(.5*sol.y[3:,-1]@M@sol.y[3:,-1]
             +np.sum(switched_K*(1-np.cos(B.T@sol.y[:3,-1])))) - Hfun(sol.y[:3,-1],sol.y[3:,-1])
gate("reduced_swing_switch_potential_jump", abs(actual_jump-switch_jump) < TOL,
     actual_jump-switch_jump)

# Nonzero-angle Hessian update for opening one edge (not merely the DC Laplacian).
theta_h = np.array([.21, -.08, .13])
angles = B.T@theta_h
Hess_closed = B@np.diag(K*np.cos(angles))@B.T
Hess_open = B@np.diag(np.array([K[0], 0.])*np.cos(angles))@B.T
rank_one = K[1]*np.cos(angles[1])*np.outer(B[:,1], B[:,1])
hess_res = np.linalg.norm(Hess_open-Hess_closed+rank_one)
gate("nonzero_angle_hessian_rank_one_update", hess_res < TOL, hess_res)

result = {"scope": "reduced Gaussian identities and lossless swing model only; no DAE/IEEE-39 claim",
          "tolerance": TOL, "gates": gates, "metrics": metrics,
          "passed": all(gates.values())}
print(json.dumps(result, indent=2, sort_keys=True))
if not result["passed"]:
    raise SystemExit(1)

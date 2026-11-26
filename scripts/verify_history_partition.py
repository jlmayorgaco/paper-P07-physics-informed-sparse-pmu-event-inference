"""Verify local filter identities without reading observations or running a bank.

Uses the byte-identical frozen C01 truncated-normal kernel shipped with this
paper. Its digest is verified against the original check report before source
execution; no project .pyc file is read or written. --research-root/--research
optionally verifies an explicitly supplied original research checkout.
The sequential sufficient-
statistic equations reproduce core_v6.process; the full history bank, pruning,
thresholds, and nonlinear plant are not executed. Independent quadrature, ODE
integration, and a joint Kalman recursion supply three numerical references.
All output is confined to generated/revision_math_20261103 in this repository.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import types
from pathlib import Path

import numpy as np
import scipy
from scipy.integrate import quad, solve_ivp
from scipy.linalg import expm
from scipy.special import logsumexp
from scipy.stats import norm

PAPER = Path(__file__).resolve().parents[1]
SNAPSHOT = PAPER / "generated/frozen/revision_math_kernel_20261103"
OUTPUT = PAPER / "generated/revision_math_20261103"
SEED = 20261103


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_kernel(research: Path | None):
    manifest_path = SNAPSHOT / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    baseline_path = SNAPSHOT / manifest["baseline"]["file"]
    if sha(baseline_path) != manifest["baseline"]["sha256"]:
        raise ValueError("Original check report hash mismatch")
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    recorded = {name.replace("\\", "/"):digest
                for name, digest in baseline["source_sha256"].items()}
    relative = manifest["kernel"]["source_relative_path"]
    expected = recorded[relative]
    if manifest["kernel"]["sha256"] != expected:
        raise ValueError("Kernel manifest disagrees with original checks.json")
    path = research / relative if research is not None else SNAPSHOT / manifest["kernel"]["file"]
    if not path.is_file():
        raise FileNotFoundError(f"Frozen amplitude kernel unavailable: {path}")
    content = path.read_bytes()
    if hashlib.sha256(content).hexdigest() != expected:
        raise ValueError("Kernel hash mismatch against original checks.json")
    sources = {"snapshot/MANIFEST.json":manifest_path,
               "snapshot/reference_checks.json":baseline_path,
               relative:path}
    if research is not None:
        for name,digest in recorded.items():
            original = research / name
            if not original.is_file() or sha(original) != digest:
                raise ValueError("Original source hash mismatch: " + name)
            sources[name] = original
    # Compile verified source bytes directly: SourceFileLoader could reuse a .pyc.
    module = types.ModuleType("p07_frozen_amplitude_kernel")
    module.__file__ = str(path)
    exec(compile(content, str(path), "exec"), module.__dict__)
    provenance = dict(mode="explicit_research_checkout" if research is not None else "bundled_snapshot",
                      kernel_sha256=expected,original_source_sha256=recorded,
                      original_checks_sha256=manifest["baseline"]["sha256"],
                      kernel_verified_before_execution=True,project_bytecode_used=False,
                      original_context_sources_reverified=research is not None)
    return module.trunc, sources, provenance


def update(trunc, mu, variance, lower, upper, observation, response, noise_var):
    old_z, _, _ = trunc(mu, variance, lower, upper)
    new_v = variance / (1 + variance * response**2 / noise_var)
    new_m = mu + new_v * (response * observation / noise_var - mu * response**2 / noise_var)
    new_z, mean, var = trunc(new_m, new_v, lower, upper)
    base = -.5 * (np.log(2 * np.pi * noise_var) + observation**2 / noise_var)
    log_predictive = base + .5 * (np.log(new_v / variance)
                                  + new_m**2 / new_v - mu**2 / variance) + new_z - old_z
    return new_m, new_v, log_predictive, mean, var


def direct_quadrature(y, response, noise_var):
    prior_v = .15**2
    precision = 1 / prior_v + np.sum(response**2 / noise_var)
    linear = np.sum(response * y / noise_var)
    mode = np.clip(linear / precision, -.2, .2)
    prior_z = norm.cdf(.2 / .15) - norm.cdf(-.2 / .15)

    def log_density(a):
        return float(np.sum(norm.logpdf(y, loc=response * a, scale=np.sqrt(noise_var)))
                     + norm.logpdf(a, scale=.15) - np.log(prior_z))

    shift = log_density(mode)
    moments = [quad(lambda a, k=k: a**k * np.exp(log_density(a) - shift),
                    -.2, .2, epsabs=1e-12, epsrel=1e-12)[0] for k in range(3)]
    mean = moments[1] / moments[0]
    return shift + np.log(moments[0]), mean, moments[2] / moments[0] - mean**2


def partition_checks(trunc, rng):
    knots = np.array([-.2, -.1, 0., .1, .2])
    scenarios = []
    for name, true_a in [("negative", -.16), ("negative_boundary", -.1),
                         ("zero_boundary", 0.), ("positive_boundary", .1),
                         ("upper_support", .19), ("zero_information", .08)]:
        response = rng.uniform(-1.4, 1.4, 12)
        noise_var = rng.uniform(.12, .22, 12)**2
        if name == "zero_information":
            response[:] = 0.
        observed = response * true_a + rng.normal(size=12) * np.sqrt(noise_var)
        mu1 = np.zeros(1); v1 = np.full(1, .15**2)
        mu4 = np.zeros(4); v4 = np.full(4, .15**2)
        lo1 = np.array([-.2]); hi1 = np.array([.2])
        lo4 = knots[:-1]; hi4 = knots[1:]
        initial_z, _, _ = trunc(mu4, v4, lo4, hi4)
        logweights = initial_z - logsumexp(initial_z)
        logz1 = 0.; logz4 = 0.; steps = []
        for k, (y, s, r) in enumerate(zip(observed, response, noise_var)):
            mu1, v1, l1, am1, av1 = update(trunc, mu1, v1, lo1, hi1, y, s, r)
            mu4, v4, l4, am4, av4 = update(trunc, mu4, v4, lo4, hi4, y, s, r)
            logz1 += float(l1[0])
            predictive = float(logsumexp(logweights + l4))
            logz4 += predictive
            logweights = logweights + l4 - predictive
            weights = np.exp(logweights)
            mixture_mean = float(weights @ am4)
            mixture_var = float(weights @ (av4 + am4**2) - mixture_mean**2)
            qlog, qmean, qvar = direct_quadrature(observed[:k+1], response[:k+1], noise_var[:k+1])
            row = dict(report=k+1, log_evidence_partition_error=abs(logz1-logz4),
                       amplitude_mean_partition_error=abs(float(am1[0])-mixture_mean),
                       amplitude_variance_partition_error=abs(float(av1[0])-mixture_var),
                       log_evidence_quadrature_error=abs(logz1-qlog),
                       amplitude_mean_quadrature_error=abs(float(am1[0])-qmean),
                       amplitude_variance_quadrature_error=abs(float(av1[0])-qvar),
                       interval_weight_sum_error=abs(float(weights.sum())-1.))
            if max(value for key, value in row.items() if key != "report") > 2e-10:
                raise AssertionError((name, row))
            steps.append(row)
        scenarios.append(dict(name=name, generating_amplitude=true_a, reports=12,
                              zero_information=name == "zero_information", steps=steps))
    return scenarios


def affine_flow(a, force, direction, duration):
    n = len(force)
    block = np.zeros((n+2, n+2))
    block[:n, :n] = a; block[:n, n] = force; block[:n, n+1] = direction
    flow = expm(duration * block)
    return flow[:n, :n], flow[:n, n], flow[:n, n+1]


def affine_checks(rng):
    a1 = np.array([[-.3, .8], [-.2, -.5]])
    a2 = np.array([[-.4, .3], [.4, -.7]])
    c1 = np.array([.15, -.2]); c2 = np.array([-.3, .1])
    u1 = np.array([.4, -.1]); u2 = np.array([0., 0.])
    rows = []
    for fraction in [0., .25, .5, .75, 1.]:
        h1 = fraction/30; h2 = (1-fraction)/30
        f1, b1, v1 = affine_flow(a1, c1, u1, h1)
        f2, b2, v2 = affine_flow(a2, c2, u2, h2)
        initial = rng.normal(size=2); amplitude = -.07
        composed = (f2 @ f1) @ initial + f2 @ b1 + b2 + (f2 @ v1 + v2)*amplitude
        current = initial.copy()
        for a, c, u, duration in [(a1,c1,u1,h1), (a2,c2,u2,h2)]:
            if duration:
                solved = solve_ivp(lambda _, x: a @ x+c+u*amplitude,
                                   (0.,duration), current, method="DOP853", rtol=1e-12, atol=1e-13)
                if not solved.success:
                    raise AssertionError(solved.message)
                current = solved.y[:, -1]
        error = float(np.max(np.abs(composed-current)))
        if error > 1e-10:
            raise AssertionError((fraction,error))
        rows.append(dict(switch_fraction=fraction, state_max_abs_error=error,
                         physical_state_reset=False))
    return rows


def joint_reference_checks(rng):
    # Gaussian amplitude (untruncated) makes the independent joint oracle exact.
    # Its purpose is to verify state-amplitude coupling, not TN approximation.
    m = np.array([.04, -.02]); d = np.array([.3, -.15])
    p = np.array([[.05,.012],[.012,.03]]); mu = .06; variance = .15**2
    mean = np.r_[m+d*mu, mu]
    cov = np.block([[p+np.outer(d,d)*variance, (d*variance)[:,None]],
                    [(d*variance)[None,:], np.array([[variance]])]])
    rows = []
    for k in range(12):
        mode = k % 3
        t = np.array([[.96, .03*(-1)**mode], [.02*mode, .93]])
        g = np.array([.015*mode, -.012]); u = np.array([.05, -.03*mode])
        j = np.array([[.8, -.3+.1*mode]])
        offset = .02*mode; direct = .1*(-1)**mode
        q = np.diag([.001,.002]); r = .04
        y = float(rng.normal(scale=.2))
        e = y-(j @ m).item()-offset
        s = (j @ d).item()+direct
        conditional_s = (j @ p @ j.T).item()+r
        gain = (t @ p @ j.T).ravel()/conditional_s
        new_v = 1/(1/variance+s*s/conditional_s)
        new_mu = new_v*(mu/variance+s*e/conditional_s)
        m = t @ m+g+gain*e
        d = t @ d+u-gain*s
        p = t @ p @ t.T+q-np.outer(gain,gain)*conditional_s
        mu, variance = new_mu, new_v
        predicted_mean = np.r_[m+d*mu,mu]
        predicted_cov = np.block([[p+np.outer(d,d)*variance,(d*variance)[:,None]],
                                  [(d*variance)[None,:],np.array([[variance]])]])

        h = np.r_[j.ravel(),direct][None,:]
        innovation = y-(h @ mean).item()-offset
        innovation_cov = (h @ cov @ h.T).item()+r
        joint_gain = cov @ h.T/innovation_cov
        mean = mean+joint_gain.ravel()*innovation
        # Joseph form gives an independent, numerically stable covariance update.
        eye = np.eye(3)-joint_gain @ h
        cov = eye @ cov @ eye.T+(joint_gain @ joint_gain.T)*r
        transition = np.block([[t,u[:,None]],[np.zeros((1,2)),np.ones((1,1))]])
        mean = transition @ mean+np.r_[g,0.]
        cov = transition @ cov @ transition.T+np.diag([.001,.002,0.])
        mean_error = float(np.max(np.abs(mean-predicted_mean)))
        covariance_error = float(np.max(np.abs(cov-predicted_cov)))
        if max(mean_error,covariance_error)>1e-10:
            raise AssertionError((k,mean_error,covariance_error))
        rows.append(dict(report=k+1, mean_max_abs_error=mean_error,
                         covariance_max_abs_error=covariance_error,
                         exact_conditional_covariance=True, bounded_amplitude=False))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--research-root", "--research", type=Path, default=None,
                        help="Explicit original research checkout; default uses the bundled verified kernel")
    args = parser.parse_args()
    research = args.research_root.resolve() if args.research_root is not None else None
    trunc, sources, provenance = load_kernel(research)
    before = {name:sha(path) for name,path in sources.items()}
    rng = np.random.default_rng(SEED)
    partition = partition_checks(trunc,rng)
    affine = affine_checks(rng)
    joint = joint_reference_checks(rng)
    after = {name:sha(path) for name,path in sources.items()}
    if before != after:
        raise AssertionError("Frozen source hash changed during verification")
    allsteps = [step for scenario in partition for step in scenario["steps"]]
    summary = [
        ("Log evidence: partition", max(r["log_evidence_partition_error"] for r in allsteps),2e-10),
        ("Amplitude mean/variance", max(max(r["amplitude_mean_partition_error"],r["amplitude_variance_partition_error"]) for r in allsteps),2e-10),
        ("Log evidence: quadrature", max(r["log_evidence_quadrature_error"] for r in allsteps),2e-10),
        ("Affine flow: ODE reference", max(r["state_max_abs_error"] for r in affine),1e-10),
        ("Joint mean/covariance", max(max(r["mean_max_abs_error"],r["covariance_max_abs_error"]) for r in joint),1e-10)]
    report = dict(status="PASS_LOCAL_IDENTITIES_ONLY",seed=SEED,
                  kernel="frozen C01 amplitude_parent.trunc",source_sha256=before,
                  source_provenance=provenance,
                  verification_script_sha256=sha(Path(__file__)),sources_unchanged=True,
                  python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,
                  scope=dict(full_bank_executed=False,nonlinear_plant_executed=False,
                             campaign_data_read=False,pruning_executed=False,
                             calibration_established=False,new_event_outcomes=0),
                  partition=partition,affine_flow=affine,joint_gaussian_reference=joint,
                  summary=[dict(check=name,max_abs_error=error,tolerance=tol) for name,error,tol in summary])
    OUTPUT.mkdir(parents=True,exist_ok=True)
    (OUTPUT/"checks.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    table = [r"\begin{table}[t]\centering\small",
             r"\caption{Deterministic local-model checks. Maximum absolute errors over 72 scalar updates, five switch positions, and 12 joint Gaussian updates; each row uses its stated reference.}",
             r"\label{tab:implemented-filter-checks}",
             r"\begin{tabular}{@{}lr@{}}\toprule",
             r"Check & Maximum error \\\midrule"]
    for name,error,_ in summary:
        mantissa, exponent = f"{error:.2e}".split("e")
        table.append(name+rf" & ${mantissa}\times10^{{{int(exponent)}}}$ \\")
    table += [r"\bottomrule\end{tabular}",r"\end{table}"]
    table_path = OUTPUT / "checks_table.tex"
    table_text = "\n".join(table)+"\n"
    if not table_path.exists() or table_path.read_text(encoding="utf-8") != table_text:
        table_path.write_text(table_text, encoding="utf-8")
    print(json.dumps(dict(status=report["status"],summary=report["summary"],
                          result=str(OUTPUT/"checks.json")),indent=2))


if __name__ == "__main__":
    main()

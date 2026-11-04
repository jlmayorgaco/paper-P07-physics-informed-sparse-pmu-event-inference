"""Small mathematical checks for the review; no paper experiment is rerun."""
import json
import math
from pathlib import Path

import numpy as np
from scipy.integrate import quad
from scipy.special import ndtr
from scipy.stats import multivariate_normal


def evidence(e, s, S, mu, v, lo, hi):
    inv = np.linalg.inv(S)
    vp = 1 / (1 / v + s @ inv @ s)
    mup = vp * (mu / v + s @ inv @ e)
    z = ndtr((hi - mu) / math.sqrt(v)) - ndtr((lo - mu) / math.sqrt(v))
    zp = ndtr((hi - mup) / math.sqrt(vp)) - ndtr((lo - mup) / math.sqrt(vp))
    log_l = (multivariate_normal.logpdf(e, mean=np.zeros(len(e)), cov=S)
             + .5 * math.log(vp / v) + .5 * (mup**2 / vp - mu**2 / v)
             + math.log(zp / z))
    return math.exp(log_l), z


def main():
    e = np.array([.09, -.03])
    s = np.array([.8, -.3])
    S = np.array([[.02, .003], [.003, .01]])
    mu, v = 0., .15**2
    lo, hi = -.2, .2
    analytic, z = evidence(e, s, S, mu, v, lo, hi)
    def integrand(a):
        prior = math.exp(-.5 * (a - mu)**2 / v) / math.sqrt(2 * math.pi * v) / z
        return multivariate_normal.pdf(e, mean=s * a, cov=S) * prior
    numeric, _ = quad(integrand, lo, hi, epsabs=1e-11, epsrel=1e-11)
    edges = [-.2, -.1, 0., .1, .2]
    partitioned = sum(evidence(e, s, S, mu, v, l, u)[0] *
                      evidence(e, s, S, mu, v, l, u)[1] / z
                      for l, u in zip(edges[:-1], edges[1:]))
    # Exact smooth polynomial. Mixed and diagonal curvature can cancel.
    a, b = .1, .1
    truth = a + b + a*a + b*b - 1.5*a*b
    linear = a + b
    diagonal = linear + a*a + b*b
    full = diagonal - 1.5*a*b
    checks = {
        "scope": "Mathematical identities only; not validation of R11, F01, or empirical calibration.",
        "truncated_gaussian": {
            "closed_form": analytic, "adaptive_quadrature": numeric,
            "weighted_four_intervals": partitioned,
            "relative_error_quadrature": abs(analytic-numeric)/numeric,
            "relative_error_partition": abs(analytic-partitioned)/analytic,
            "qualification": "Same affine likelihood on all intervals; piecewise operators/pruning can change equivalence."
        },
        "taylor_counterexample": {
            "function": "a+b+a^2+b^2-1.5*a*b", "a": a, "b": b,
            "absolute_error_linear": abs(truth-linear),
            "absolute_error_diagonal": abs(truth-diagonal),
            "absolute_error_full_quadratic": abs(truth-full),
            "qualification": "Refutes impossibility claim; does not certify repository derivative tensors."
        },
        "zero_alarm_poisson_95_upper_per_hour": {
            "B01_1_96h": -math.log(.05)/1.96,
            "C02_3_92h": -math.log(.05)/3.92,
            "qualification": "Conditional on Poisson/exposure assumptions; not a guarantee after threshold selection or across correlated replicas."
        }
    }
    assert checks["truncated_gaussian"]["relative_error_quadrature"] < 1e-10
    assert checks["truncated_gaussian"]["relative_error_partition"] < 1e-10
    assert abs(truth-diagonal) > 2 * abs(truth-linear)
    assert abs(truth-full) < 1e-14
    output = Path(__file__).with_name("MATHEMATICAL_CHECKS.json")
    output.write_text(json.dumps(checks, indent=2), encoding="utf-8")
    print(json.dumps(checks, indent=2))


if __name__ == "__main__":
    main()

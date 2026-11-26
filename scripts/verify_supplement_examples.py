"""Check the supplement's illustrative calculations, without changing evidence."""
import json
import math

from scipy.integrate import quad
from scipy.stats import norm


def main():
    # Scalar interval from the supplement, independently integrated.
    mu, v, lower, upper = 0.0, 1.0, 0.0, 1.0
    residual, sensitivity, variance = 1.0, 2.0, 1.0
    vp = 1 / (1 / v + sensitivity**2 / variance)
    mp = vp * (mu / v + sensitivity * residual / variance)
    z = norm.cdf(upper) - norm.cdf(lower)
    alpha, beta = (lower - mp) / math.sqrt(vp), (upper - mp) / math.sqrt(vp)
    zp = norm.cdf(beta) - norm.cdf(alpha)
    closed = math.exp(norm.logpdf(residual) + 0.5 * (math.log(vp / v) + mp**2 / vp - mu**2 / v)) * zp / z
    integrand = lambda a: norm.pdf(residual - sensitivity * a) * norm.pdf(a) / z
    numeric = quad(integrand, lower, upper, epsabs=1e-13)[0]
    mean = mp + math.sqrt(vp) * (norm.pdf(alpha) - norm.pdf(beta)) / zp
    numeric_mean = quad(lambda a: a * integrand(a), lower, upper, epsabs=1e-13)[0] / numeric
    assert abs(closed - numeric) < 1e-12
    assert abs(mean - numeric_mean) < 1e-12
    assert abs(closed - 0.342688) < 5e-7
    assert abs(mean - 0.464941) < 5e-7
    at_off = 1 - math.exp(-2)
    one_second_after = at_off * math.exp(-1)
    assert abs(at_off - 0.864665) < 5e-7
    assert abs(one_second_after - 0.318092) < 5e-7
    before = 0.5 * 0.8 + 0.5 * 0.2
    after = 0.75 * 0.8 + 0.25 * 0.2
    assert abs(after - before - 0.15) < 1e-12
    print(json.dumps({"scope": "Illustrative algebra only; no simulation evidence",
                      "likelihood": closed, "posterior_mean": mean,
                      "quadrature_error": abs(closed - numeric),
                      "recovery_at_off": at_off,
                      "recovery_one_second_after": one_second_after,
                      "model_reweighting_change": after - before}, indent=2))


if __name__ == '__main__':
    main()

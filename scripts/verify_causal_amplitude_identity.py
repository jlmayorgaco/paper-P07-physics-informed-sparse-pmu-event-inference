"""Check the two equivalent bounded-severity evidence formulas by quadrature."""
import json
from pathlib import Path

import numpy as np
from scipy.integrate import quad
from scipy.stats import multivariate_normal, norm

ROOT = Path(__file__).resolve().parents[1]


def main():
    covariance = np.array([[0.3, 0.1], [0.1, 0.2]])
    signature = np.array([1.2, -0.4])
    residual = np.array([0.3, -0.2])
    information = signature @ np.linalg.solve(covariance, signature)
    score = signature @ np.linalg.solve(covariance, residual)
    checks = []

    for center, variance, lower, upper in [(0.02, 0.01, -0.2, 0.3), (-0.04, 0.04, -0.3, 0.0)]:
        def interval_mass(mean, var):
            lo, hi = (np.array([lower, upper]) - mean) / np.sqrt(var)
            return norm.cdf(hi) - norm.cdf(lo)

        posterior_var = 1 / (1 / variance + information)
        posterior_center = posterior_var * (center / variance + score)
        prior_mass = interval_mass(center, variance)
        mass_ratio = interval_mass(posterior_center, posterior_var) / prior_mass

        def integrand(amplitude):
            prior = norm.pdf(amplitude, center, np.sqrt(variance)) / prior_mass
            return prior * multivariate_normal.pdf(residual, mean=signature * amplitude, cov=covariance)

        direct, _ = quad(integrand, lower, upper, epsabs=1e-13)
        gaussian_log = multivariate_normal.logpdf(residual, cov=covariance)
        completed_log = gaussian_log + 0.5 * (
            np.log(posterior_var / variance) + posterior_center**2 / posterior_var - center**2 / variance
        ) + np.log(mass_ratio)
        predictive_density = multivariate_normal.pdf(
            residual, mean=signature * center, cov=covariance + variance * np.outer(signature, signature)
        )
        completion_error = abs(np.exp(completed_log) - direct)
        predictive_error = abs(predictive_density * mass_ratio - direct)
        assert max(completion_error, predictive_error) < 1e-10
        checks.append(dict(bounds=[lower, upper], absolute_error=completion_error,
                           predictive_form_error=predictive_error, passed=True))

    report = dict(scope="Local bounded Gaussian evidence checked against scalar quadrature", checks=checks)
    (ROOT / "generated/causal_amplitude_identity.json").write_text(json.dumps(report, indent=2) + "\n")
    print("CAUSAL_AMPLITUDE_QUADRATURE_PASS", max(row["predictive_form_error"] for row in checks))


if __name__ == "__main__":
    main()

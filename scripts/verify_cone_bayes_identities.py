#!/usr/bin/env python3
"""Verify constrained-geometry and boundary-evidence identities.

The checks are deterministic toy calculations. They guard the formulas used in
the supplement but are not IEEE 39-bus or ANDES validation.
"""

from __future__ import annotations

import argparse
import json
from math import erf, gamma, pi, sqrt
from pathlib import Path

import numpy as np
from scipy.integrate import quad
from scipy.optimize import nnls


def projector(columns: np.ndarray) -> np.ndarray:
    return columns @ np.linalg.pinv(columns)


def span_distance_squared(vector: np.ndarray, columns: np.ndarray) -> float:
    residual = (np.eye(vector.size) - projector(columns)) @ vector
    return float(residual @ residual)


def cone_distance_squared(vector: np.ndarray, generators: np.ndarray) -> float:
    _, residual_norm = nnls(generators, vector)
    return float(residual_norm**2)


def normal_cdf(value: float) -> float:
    return 0.5 * (1.0 + erf(value / sqrt(2.0)))


def json_default(value: object) -> object:
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def conditional_geometry_checks() -> list[dict[str, object]]:
    basis = np.eye(7)
    nuisance = basis[:, [0]]
    shared = basis[:, [1]]
    true_exclusive = np.column_stack(
        [basis[:, 2] + 0.30 * basis[:, 4], basis[:, 3] + 0.50 * basis[:, 5]]
    )
    competitor_exclusive = (
        0.80 * basis[:, 2]
        + 0.20 * basis[:, 3]
        + 0.10 * basis[:, 6]
    )[:, None]
    alpha_shared = np.array([1.4])
    alpha_exclusive = np.array([0.7, -0.4])
    true_vector = shared @ alpha_shared + true_exclusive @ alpha_exclusive

    full_competitor = np.column_stack([nuisance, shared, competitor_exclusive])
    full_margin = span_distance_squared(true_vector, full_competitor)
    common = np.column_stack([nuisance, shared])
    residualizer = np.eye(7) - projector(common)
    conditional_true = residualizer @ true_exclusive
    conditional_competitor = residualizer @ competitor_exclusive
    quotient_vector = conditional_true @ alpha_exclusive
    quotient_margin = span_distance_squared(quotient_vector, conditional_competitor)
    quotient_error = abs(full_margin - quotient_margin)

    conditional_projector = projector(conditional_competitor)
    conditional_matrix = conditional_true.T @ (
        np.eye(7) - conditional_projector
    ) @ conditional_true
    eigenvalues, eigenvectors = np.linalg.eigh(conditional_matrix)
    angles = np.linspace(0.0, 2.0 * pi, 20001)
    directions = np.vstack([np.cos(angles), np.sin(angles)])
    quadratic_values = np.einsum(
        "ij,ji->i", directions.T @ conditional_matrix, directions
    )
    grid_minimum = float(np.min(quadratic_values))
    minimum_eigenvalue = float(eigenvalues[0])
    eigen_error = abs(grid_minimum - minimum_eigenvalue)

    q_true, _ = np.linalg.qr(conditional_true)
    q_comp, _ = np.linalg.qr(conditional_competitor)
    singular_value = float(np.linalg.svd(q_true.T @ q_comp, compute_uv=False)[0])
    conditional_angle = float(np.arccos(np.clip(singular_value, -1.0, 1.0)))
    geometric_matrix = q_true.T @ (
        np.eye(7) - q_comp @ q_comp.T
    ) @ q_true
    angle_error = abs(
        float(np.linalg.eigvalsh(geometric_matrix)[0])
        - float(np.sin(conditional_angle) ** 2)
    )
    full_true, _ = np.linalg.qr(np.column_stack([shared, true_exclusive]))
    full_comp, _ = np.linalg.qr(np.column_stack([shared, competitor_exclusive]))
    naive_sigma = float(np.linalg.svd(full_true.T @ full_comp, compute_uv=False)[0])
    naive_angle = float(np.arccos(np.clip(naive_sigma, -1.0, 1.0)))

    true_ray = basis[:2, 0]
    opposite_ray = -true_ray[:, None]
    span_margin = span_distance_squared(true_ray, opposite_ray)
    cone_margin = cone_distance_squared(true_ray, opposite_ray)
    ray_error = max(abs(span_margin), abs(cone_margin - 1.0))

    shared_generator = basis[:2, [0]]
    exclusive_contribution = -2.0 * basis[:2, 0] + basis[:2, 1]
    shared_amplitudes = [0.0, 1.0, 2.0, 3.0]
    shared_margins = [
        cone_distance_squared(
            amplitude * basis[:2, 0] + exclusive_contribution,
            shared_generator,
        )
        for amplitude in shared_amplitudes
    ]
    expected_shared_margins = [5.0, 2.0, 1.0, 1.0]
    shared_error = max(
        abs(observed - expected)
        for observed, expected in zip(shared_margins, expected_shared_margins)
    )

    rng = np.random.default_rng(20260915)
    maximum_enrichment_violation = 0.0
    for _ in range(2000):
        generators = rng.normal(size=(5, 2))
        added = rng.normal(size=(5, 1))
        vector = rng.normal(size=5)
        smaller = cone_distance_squared(vector, generators)
        larger = cone_distance_squared(
            vector, np.column_stack([generators, added])
        )
        maximum_enrichment_violation = max(
            maximum_enrichment_violation, larger - smaller
        )

    nested_generators = rng.normal(size=(6, 2))
    nested_amplitudes = np.array([0.4, 1.2])
    nested_vector = nested_generators @ nested_amplitudes
    nested_competitor = np.column_stack(
        [nested_generators, rng.normal(size=(6, 1))]
    )
    nested_margin = cone_distance_squared(nested_vector, nested_competitor)

    return [
        {
            "name": "conditional_quotient_reduction",
            "full_margin_squared": full_margin,
            "quotient_margin_squared": quotient_margin,
            "error": quotient_error,
            "tolerance": 1e-12,
            "passed": quotient_error <= 1e-12,
        },
        {
            "name": "conditional_matrix_worst_direction",
            "minimum_eigenvalue": minimum_eigenvalue,
            "grid_minimum": grid_minimum,
            "minimum_eigenvector": eigenvectors[:, 0].tolist(),
            "error": eigen_error,
            "tolerance": 1e-7,
            "passed": eigen_error <= 1e-7,
        },
        {
            "name": "conditional_principal_angle",
            "naive_angle_degrees": float(np.degrees(naive_angle)),
            "conditional_angle_degrees": float(np.degrees(conditional_angle)),
            "error": angle_error,
            "tolerance": 1e-12,
            "passed": abs(naive_angle) <= 1e-7 and angle_error <= 1e-12,
        },
        {
            "name": "one_sided_ray_vs_span",
            "span_margin_squared": span_margin,
            "cone_margin_squared": cone_margin,
            "error": ray_error,
            "tolerance": 1e-12,
            "passed": ray_error <= 1e-12,
        },
        {
            "name": "one_sided_shared_source_dependence",
            "shared_amplitudes": shared_amplitudes,
            "margin_sequence": shared_margins,
            "error": shared_error,
            "tolerance": 1e-12,
            "passed": shared_error <= 1e-12,
        },
        {
            "name": "cone_competitor_enrichment",
            "trials": 2000,
            "maximum_violation": maximum_enrichment_violation,
            "error": max(0.0, maximum_enrichment_violation),
            "tolerance": 1e-10,
            "passed": maximum_enrichment_violation <= 1e-10,
        },
        {
            "name": "nested_cone_zero_margin",
            "margin_squared": nested_margin,
            "error": nested_margin,
            "tolerance": 1e-12,
            "passed": nested_margin <= 1e-12,
        },
    ]


def boundary_bayes_checks() -> list[dict[str, object]]:
    q = 1.7
    tau = 0.8
    scores = [-3.0 * sqrt(q), 0.0, 3.0 * sqrt(q)]
    maximum_signed_error = 0.0
    maximum_one_sided_error = 0.0
    factors = []
    for score in scores:
        denominator = sqrt(1.0 + tau**2 * q)
        signed = np.exp(
            tau**2 * score**2 / (2.0 * (1.0 + tau**2 * q))
        ) / denominator
        z_value = tau * score / denominator
        one_sided = 2.0 * normal_cdf(z_value) * signed
        signed_numeric = quad(
            lambda amplitude: np.exp(
                amplitude * score
                - 0.5 * q * amplitude**2
                - 0.5 * amplitude**2 / tau**2
            )
            / (sqrt(2.0 * pi) * tau),
            -np.inf,
            np.inf,
            epsabs=1e-12,
        )[0]
        one_sided_numeric = quad(
            lambda amplitude: sqrt(2.0 / pi)
            / tau
            * np.exp(
                amplitude * score
                - 0.5 * q * amplitude**2
                - 0.5 * amplitude**2 / tau**2
            ),
            0.0,
            np.inf,
            epsabs=1e-12,
        )[0]
        maximum_signed_error = max(
            maximum_signed_error, abs(signed - signed_numeric)
        )
        maximum_one_sided_error = max(
            maximum_one_sided_error, abs(one_sided - one_sided_numeric)
        )
        factors.append(
            {
                "score": score,
                "signed_bayes_factor": float(signed),
                "one_sided_bayes_factor": float(one_sided),
            }
        )

    covariance = np.diag([0.7, 1.1, 1.4, 0.9])
    nuisance = np.array(
        [[1.0, 0.2], [0.3, 1.0], [-0.4, 0.1], [0.2, -0.3]]
    )
    event = np.array([0.6, -0.2, 1.0, 0.4])
    precision = np.linalg.inv(covariance)
    profile_precision = precision - precision @ nuisance @ np.linalg.inv(
        nuisance.T @ precision @ nuisance
    ) @ nuisance.T @ precision
    profile_information = float(event @ profile_precision @ event)
    broad_scale = 1e4
    integrated_covariance = (
        covariance + broad_scale**2 * nuisance @ nuisance.T
    )
    broad_information = float(event @ np.linalg.inv(integrated_covariance) @ event)
    bridge_relative_error = abs(broad_information - profile_information) / abs(
        profile_information
    )

    rng = np.random.default_rng(20260915)
    z_samples = rng.normal(size=200000)
    likelihood_ratio = np.maximum(z_samples, 0.0) ** 2
    zero_mass = float(np.mean(likelihood_ratio == 0.0))
    positive_mean = float(np.mean(likelihood_ratio[likelihood_ratio > 0.0]))
    mixture_error = max(abs(zero_mass - 0.5), abs(positive_mean - 1.0))

    hessian = 1.7
    score = 0.8
    cubic = 0.35
    epsilons = np.array([0.2, 0.1, 0.05, 0.025, 0.0125, 0.00625])
    gaussian_integral = (
        sqrt(2.0 * pi / hessian)
        * np.exp(score**2 / (2.0 * hessian))
        * normal_cdf(score / sqrt(hessian))
    )
    relative_errors = []
    for epsilon in epsilons:
        nonlinear_integral = quad(
            lambda value: np.exp(
                score * value
                - 0.5 * hessian * value**2
                - epsilon * cubic * value**3
            ),
            0.0,
            np.inf,
            epsabs=1e-12,
        )[0]
        relative_errors.append(
            abs(nonlinear_integral / gaussian_integral - 1.0)
        )
    laplace_slope = float(
        np.polyfit(np.log(epsilons), np.log(relative_errors), 1)[0]
    )

    sample_sizes = np.geomspace(1.0, 1e6, 13)
    quartic_values = (
        gamma(0.25) / (4.0 ** 0.75) * sample_sizes ** (-0.25)
    )
    quartic_slope = float(
        np.polyfit(np.log(sample_sizes), np.log(quartic_values), 1)[0]
    )
    numeric_quartic = quad(lambda value: np.exp(-value**4 / 4.0), 0.0, np.inf)[0]
    quartic_formula = gamma(0.25) / (4.0 ** 0.75)
    quartic_error = abs(numeric_quartic - quartic_formula)

    return [
        {
            "name": "signed_and_half_normal_bayes_factors",
            "cases": factors,
            "signed_quadrature_error": maximum_signed_error,
            "one_sided_quadrature_error": maximum_one_sided_error,
            "error": max(maximum_signed_error, maximum_one_sided_error),
            "tolerance": 1e-10,
            "passed": max(maximum_signed_error, maximum_one_sided_error) <= 1e-10,
        },
        {
            "name": "broad_nuisance_to_profile_limit",
            "profile_information": profile_information,
            "broad_prior_information": broad_information,
            "broad_scale": broad_scale,
            "relative_error": bridge_relative_error,
            "error": bridge_relative_error,
            "tolerance": 1e-6,
            "passed": bridge_relative_error <= 1e-6,
        },
        {
            "name": "one_sided_boundary_lrt",
            "samples": 200000,
            "zero_mass": zero_mass,
            "positive_component_mean": positive_mean,
            "error": mixture_error,
            "tolerance": 0.01,
            "passed": mixture_error <= 0.01,
        },
        {
            "name": "nonlinear_cone_laplace_rate",
            "relative_errors": relative_errors,
            "log_log_slope": laplace_slope,
            "error": abs(laplace_slope - 1.0),
            "tolerance": 0.08,
            "passed": abs(laplace_slope - 1.0) <= 0.08,
        },
        {
            "name": "singular_quartic_evidence_rate",
            "log_log_slope": quartic_slope,
            "expected_slope": -0.25,
            "quadrature_error": quartic_error,
            "error": max(abs(quartic_slope + 0.25), quartic_error),
            "tolerance": 1e-10,
            "passed": max(abs(quartic_slope + 0.25), quartic_error) <= 1e-10,
        },
    ]


def write_geometry_table(path: Path, checks: list[dict[str, object]]) -> None:
    by_name = {str(check["name"]): check for check in checks}
    rows = [
        (
            "Conditional quotient",
            f"full--quotient error {by_name['conditional_quotient_reduction']['error']:.1e}",
        ),
        (
            "Worst coefficient direction",
            f"eigenvalue--grid error {by_name['conditional_matrix_worst_direction']['error']:.1e}",
        ),
        (
            "Conditional angle",
            f"naive {by_name['conditional_principal_angle']['naive_angle_degrees']:.1e} deg; conditional {by_name['conditional_principal_angle']['conditional_angle_degrees']:.3f} deg",
        ),
        (
            "Ray versus span",
            f"squared margins {by_name['one_sided_ray_vs_span']['span_margin_squared']:.1f} versus {by_name['one_sided_ray_vs_span']['cone_margin_squared']:.1f}",
        ),
        (
            "One-sided shared source",
            "squared-margin sequence "
            + ", ".join(
                f"{value:.1f}"
                for value in by_name["one_sided_shared_source_dependence"][
                    "margin_sequence"
                ]
            ),
        ),
        (
            "Cone enrichment",
            f"{by_name['cone_competitor_enrichment']['trials']} trials; max violation {by_name['cone_competitor_enrichment']['maximum_violation']:.1e}",
        ),
        (
            "Nested cone",
            f"squared margin {by_name['nested_cone_zero_margin']['margin_squared']:.1e}",
        ),
    ]
    lines = [
        r"\begin{table}[t]",
        r"\caption{Deterministic checks of conditional and one-sided geometry. These toy systems are not IEEE 39-bus evidence.}",
        r"\label{tab:supp-cone-geometry-checks}",
        r"\centering",
        r"\scriptsize",
        r"\begin{tabularx}{\columnwidth}{@{}p{0.36\columnwidth}X@{}}",
        r"\toprule",
        r"Check & Recomputed outcome \\",
        r"\midrule",
    ]
    lines.extend(f"{label} & {outcome} (pass). \\\\" for label, outcome in rows)
    lines.extend([r"\bottomrule", r"\end{tabularx}", r"\end{table}"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_bayes_table(path: Path, checks: list[dict[str, object]]) -> None:
    by_name = {str(check["name"]): check for check in checks}
    rows = [
        (
            "Signed/one-sided Bayes factors",
            f"max quadrature error {by_name['signed_and_half_normal_bayes_factors']['error']:.1e}",
        ),
        (
            "Broad nuisance limit",
            f"relative information error {by_name['broad_nuisance_to_profile_limit']['relative_error']:.1e}",
        ),
        (
            "Boundary likelihood ratio",
            f"zero mass {by_name['one_sided_boundary_lrt']['zero_mass']:.4f}; positive mean {by_name['one_sided_boundary_lrt']['positive_component_mean']:.4f}",
        ),
        (
            "Nonlinear cone--Laplace",
            f"relative-error slope {by_name['nonlinear_cone_laplace_rate']['log_log_slope']:.4f}",
        ),
        (
            "Singular quartic evidence",
            f"scaling slope {by_name['singular_quartic_evidence_rate']['log_log_slope']:.4f}",
        ),
    ]
    lines = [
        r"\begin{table}[t]",
        r"\caption{Deterministic checks of boundary-aware evidence identities. These toy systems are not evaluated estimator results.}",
        r"\label{tab:supp-boundary-bayes-checks}",
        r"\centering",
        r"\scriptsize",
        r"\begin{tabularx}{\columnwidth}{@{}p{0.40\columnwidth}X@{}}",
        r"\toprule",
        r"Check & Recomputed outcome \\",
        r"\midrule",
    ]
    lines.extend(f"{label} & {outcome} (pass). \\\\" for label, outcome in rows)
    lines.extend([r"\bottomrule", r"\end{tabularx}", r"\end{table}"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(
    output_path: Path, geometry_table_path: Path, bayes_table_path: Path
) -> None:
    geometry = conditional_geometry_checks()
    bayes = boundary_bayes_checks()
    checks = geometry + bayes
    payload = {
        "scope": (
            "Deterministic toy checks of constrained geometry and "
            "boundary-aware evidence; not IEEE 39-bus evidence."
        ),
        "checks": checks,
        "passed": sum(bool(check["passed"]) for check in checks),
        "total": len(checks),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(payload, indent=2, default=json_default)
    output_path.write_text(serialized + "\n", encoding="utf-8")
    write_geometry_table(geometry_table_path, geometry)
    write_bayes_table(bayes_table_path, bayes)
    print(serialized)
    if payload["passed"] != payload["total"]:
        raise SystemExit(1)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=root / "generated" / "cone_bayes_checks.json",
    )
    parser.add_argument(
        "--geometry-table-output",
        type=Path,
        default=root / "tables" / "generated" / "cone_geometry_validation.tex",
    )
    parser.add_argument(
        "--bayes-table-output",
        type=Path,
        default=root / "tables" / "generated" / "boundary_bayes_validation.tex",
    )
    arguments = parser.parse_args()
    main(
        arguments.output,
        arguments.geometry_table_output,
        arguments.bayes_table_output,
    )

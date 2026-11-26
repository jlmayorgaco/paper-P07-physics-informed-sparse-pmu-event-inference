#!/usr/bin/env python3
"""Verify higher-order evidence, horizon, and information-limit identities.

Most checks use deterministic analytic or controlled numerical systems.  The
final check audits the frozen RAWSIM39 V1.2 gate ledger; it does not infer
higher-order derivatives that are absent from that checkpoint.
"""

from __future__ import annotations

import argparse
import csv
import json
from math import comb, erf, gamma, log, pi, sqrt
from pathlib import Path

import numpy as np
from scipy.integrate import quad
from scipy.optimize import minimize_scalar


def normal_cdf(value: float) -> float:
    return 0.5 * (1.0 + erf(value / sqrt(2.0)))


def normal_pdf(value: float, scale: float) -> float:
    return np.exp(-0.5 * (value / scale) ** 2) / (sqrt(2.0 * pi) * scale)


def log_slope(scales: np.ndarray, values: np.ndarray, tail: int = 4) -> float:
    return float(np.polyfit(np.log(scales[-tail:]), np.log(values[-tail:]), 1)[0])


def weighted_profile_distance(
    vector: np.ndarray, columns: np.ndarray, covariance: np.ndarray
) -> float:
    precision = np.linalg.inv(covariance)
    gram = columns.T @ precision @ columns
    coefficient = np.linalg.solve(gram, columns.T @ precision @ vector)
    residual = vector - columns @ coefficient
    return float(residual.T @ precision @ residual)


def evidence_scaling_checks() -> list[dict[str, object]]:
    epsilons = 0.2 / (2.0 ** np.arange(6))

    tau = 1.3
    redundant_exact = 1.0 / np.sqrt(1.0 + 2.0 * tau**2 / epsilons**2)
    redundant_asymptotic = epsilons / (sqrt(2.0) * tau)
    redundant_slope = log_slope(epsilons, redundant_exact)
    redundant_ratio = float(redundant_exact[-1] / redundant_asymptotic[-1])
    redundant_error = max(abs(redundant_slope - 1.0), abs(redundant_ratio - 1.0))

    higher_tau = 1.1
    higher_exact = []
    higher_asymptotic = []
    higher_constant = gamma(0.25) / (2.0 ** 0.75)
    for epsilon in epsilons:
        value = quad(
            lambda amplitude: np.exp(-amplitude**4 / (2.0 * epsilon**2))
            * normal_pdf(amplitude, higher_tau),
            -np.inf,
            np.inf,
            epsabs=1e-13,
            epsrel=1e-12,
            limit=300,
        )[0]
        higher_exact.append(value)
        higher_asymptotic.append(
            normal_pdf(0.0, higher_tau) * higher_constant * sqrt(epsilon)
        )
    higher_exact_array = np.asarray(higher_exact)
    higher_asymptotic_array = np.asarray(higher_asymptotic)
    higher_slope = log_slope(epsilons, higher_exact_array)
    higher_ratio = float(higher_exact_array[-1] / higher_asymptotic_array[-1])
    higher_error = max(abs(higher_slope - 0.5), abs(higher_ratio - 1.0))

    rho = 0.8
    curvature = 1.4
    tau_regular = 1.0
    tau_singular = 1.0
    mixed_exact = []
    mixed_asymptotic = []
    mixed_constant = (
        normal_pdf(0.0, tau_regular)
        * normal_pdf(0.0, tau_singular)
        * sqrt(2.0 * pi)
        * gamma(0.25)
        / 2.0
        * (2.0 / curvature**2) ** 0.25
    )
    for epsilon in epsilons:
        regular_factor = epsilon / sqrt(epsilon**2 + tau_regular**2)

        def reduced_integrand(amplitude: float) -> float:
            parallel = rho**2 * amplitude**4 / (
                2.0 * (epsilon**2 + tau_regular**2)
            )
            normal = curvature**2 * amplitude**4 / (2.0 * epsilon**2)
            return normal_pdf(amplitude, tau_singular) * np.exp(-parallel - normal)

        value = regular_factor * quad(
            reduced_integrand,
            -np.inf,
            np.inf,
            epsabs=1e-13,
            epsrel=1e-12,
            limit=300,
        )[0]
        mixed_exact.append(value)
        mixed_asymptotic.append(mixed_constant * epsilon**1.5)
    mixed_exact_array = np.asarray(mixed_exact)
    mixed_asymptotic_array = np.asarray(mixed_asymptotic)
    mixed_slope = log_slope(epsilons, mixed_exact_array)
    mixed_ratio = float(mixed_exact_array[-1] / mixed_asymptotic_array[-1])
    mixed_error = max(abs(mixed_slope - 1.5), abs(mixed_ratio - 1.0))

    base = epsilons / np.sqrt(epsilons**2 + 1.0)
    regular_bf = epsilons / np.sqrt(epsilons**2 + 1.0)
    singular_bf = []
    for epsilon in epsilons:
        singular_bf.append(
            quad(
                lambda amplitude: np.exp(-amplitude**4 / (2.0 * epsilon**2))
                * normal_pdf(amplitude, 1.0),
                -np.inf,
                np.inf,
                epsabs=1e-13,
                epsrel=1e-12,
                limit=300,
            )[0]
        )
    singular_bf_array = np.asarray(singular_bf)
    redundant_bf = (
        epsilons / np.sqrt(epsilons**2 + 2.0)
    ) / base
    slopes = {
        "regular": log_slope(epsilons, regular_bf),
        "order_2": log_slope(epsilons, singular_bf_array),
        "redundant": log_slope(epsilons, redundant_bf),
    }
    redundant_limit = float(redundant_bf[-1])
    nested_error = max(
        abs(slopes["regular"] - 1.0),
        abs(slopes["order_2"] - 0.5),
        abs(slopes["redundant"]),
        abs(redundant_limit - 1.0 / sqrt(2.0)),
    )

    return [
        {
            "name": "exact_redundancy_evidence_rate",
            "log_log_slope": redundant_slope,
            "smallest_scale_exact_to_asymptotic": redundant_ratio,
            "error": redundant_error,
            "tolerance": 0.02,
            "passed": redundant_error <= 0.02,
        },
        {
            "name": "higher_order_k2_evidence_rate",
            "log_log_slope": higher_slope,
            "smallest_scale_exact_to_asymptotic": higher_ratio,
            "error": higher_error,
            "tolerance": 0.02,
            "passed": higher_error <= 0.02,
        },
        {
            "name": "mixed_regular_plus_k2_evidence_rate",
            "log_log_slope": mixed_slope,
            "smallest_scale_exact_to_asymptotic": mixed_ratio,
            "error": mixed_error,
            "tolerance": 0.025,
            "passed": mixed_error <= 0.025,
        },
        {
            "name": "nested_support_occam_exponents",
            "slopes": slopes,
            "redundant_limit": redundant_limit,
            "error": nested_error,
            "tolerance": 0.02,
            "passed": nested_error <= 0.02,
        },
    ]


def horizon_checks() -> list[dict[str, object]]:
    rng = np.random.default_rng(20260916)
    maximum_violation = 0.0
    trials = 500
    for _ in range(trials):
        row_count = 7
        nuisance_count = 2
        factor = rng.normal(size=(row_count, row_count))
        covariance = factor @ factor.T + 0.5 * np.eye(row_count)
        vector = rng.normal(size=row_count)
        columns = rng.normal(size=(row_count, nuisance_count))
        old = weighted_profile_distance(vector[:-1], columns[:-1], covariance[:-1, :-1])
        extended = weighted_profile_distance(vector, columns, covariance)
        maximum_violation = max(maximum_violation, old - extended)

    decay = np.exp(-0.5)
    horizons = np.array([1, 2, 20, 80, 320, 1280])
    formula_values = []
    direct_values = []
    for horizon in horizons:
        index = np.arange(1, horizon + 1)
        nuisance = decay**index
        event = 2.0 * (1.0 - nuisance)
        direct = float(event @ event - (event @ nuisance) ** 2 / (nuisance @ nuisance))
        s1 = decay * (1.0 - decay**horizon) / (1.0 - decay)
        s2 = decay**2 * (1.0 - decay ** (2 * horizon)) / (1.0 - decay**2)
        formula = 4.0 * (horizon - s1**2 / s2)
        direct_values.append(direct)
        formula_values.append(formula)
    formula_error = float(
        np.max(np.abs(np.asarray(formula_values) - np.asarray(direct_values)))
    )
    rescue_error = max(
        abs(direct_values[0]),
        abs(direct_values[1] - 0.4527244641197043),
        abs(direct_values[-1] / horizons[-1] - 4.0),
    )

    amplitude = 0.005
    second_order_ratios = []
    for horizon in [2, 4, 8, 16]:
        signs = (-1.0) ** np.arange(horizon)

        def objective(eta: float) -> float:
            residual = amplitude - (eta + signs * eta**2)
            return float(residual @ residual)

        fit = minimize_scalar(
            objective,
            bracket=(0.5 * amplitude, 1.5 * amplitude),
            method="brent",
            options={"xtol": 1e-15},
        )
        second_order_ratios.append(float(fit.fun / amplitude**4))
    expected_ratios = np.array([2.0, 4.0, 8.0, 16.0])
    second_order_error = float(
        np.max(np.abs(np.asarray(second_order_ratios) - expected_ratios) / expected_ratios)
    )

    return [
        {
            "name": "profiled_horizon_monotonicity",
            "trials": trials,
            "maximum_violation": maximum_violation,
            "error": maximum_violation,
            "tolerance": 1e-10,
            "passed": maximum_violation <= 1e-10,
        },
        {
            "name": "first_order_temporal_rescue",
            "horizons": horizons.tolist(),
            "gamma_squared": direct_values,
            "formula_error": formula_error,
            "normalized_final": direct_values[-1] / horizons[-1],
            "error": rescue_error,
            "tolerance": 0.02,
            "passed": formula_error <= 1e-10 and rescue_error <= 0.02,
        },
        {
            "name": "second_order_temporal_rescue",
            "horizons": [2, 4, 8, 16],
            "distance_over_a4": second_order_ratios,
            "error": second_order_error,
            "tolerance": 2e-4,
            "passed": second_order_error <= 2e-4,
        },
    ]


def operational_limit_checks() -> list[dict[str, object]]:
    distances = np.array([0.5, 1.0, 2.0, 3.0, 4.0])
    exact_errors = np.array([normal_cdf(-distance / 2.0) for distance in distances])
    quadrature_errors = []
    for distance, exact in zip(distances, exact_errors):
        integrated = quad(
            lambda value: np.exp(-0.5 * value**2) / sqrt(2.0 * pi),
            distance / 2.0,
            np.inf,
            epsabs=1e-14,
            epsrel=1e-13,
        )[0]
        quadrature_errors.append(abs(integrated - exact))
    gaussian_error = max(quadrature_errors)

    rng = np.random.default_rng(20260917)
    nuisance = rng.normal(size=(8, 3))
    difference = rng.normal(size=8)
    projector = nuisance @ np.linalg.pinv(nuisance)
    residual = (np.eye(8) - projector) @ difference
    gamma_value = float(np.linalg.norm(residual))
    quotient_error_probability = normal_cdf(-gamma_value / 2.0)
    quotient_kl = 0.5 * gamma_value**2
    quotient_error = abs(quotient_kl - 0.5 * float(residual @ residual))

    beta_min_gamma = 1.6
    beta_min_amplitude = 0.005
    beta_min_error_probability = normal_cdf(
        -beta_min_gamma * beta_min_amplitude / 2.0
    )
    beta_min_error = abs(beta_min_error_probability - 0.5)

    phase_records: dict[str, list[float]] = {}
    horizon_grid = np.array([1e2, 1e4, 1e6])
    for order, betas in ((1, (0.6, 0.5, 0.4)), (2, (0.35, 0.25, 0.15))):
        for beta in betas:
            separation = np.sqrt(horizon_grid * horizon_grid ** (-2.0 * order * beta))
            phase_records[f"k{order}_beta{beta}"] = [
                normal_cdf(-value / 2.0) for value in separation
            ]
    phase_error = max(
        abs(phase_records["k1_beta0.5"][0] - phase_records["k1_beta0.5"][-1]),
        abs(phase_records["k2_beta0.25"][0] - phase_records["k2_beta0.25"][-1]),
    )

    fano_rng = np.random.default_rng(20260918)
    fano_rows = []
    maximum_fano_violation = 0.0
    hypothesis_count = 8
    sample_count = 300000
    labels = fano_rng.integers(0, hypothesis_count, size=sample_count)
    noise = fano_rng.normal(size=(sample_count, hypothesis_count))
    for delta in (0.4, 0.8):
        observations = noise.copy()
        observations[np.arange(sample_count), labels] += delta
        predictions = np.argmax(observations, axis=1)
        monte_carlo_error = float(np.mean(predictions != labels))
        average_pairwise_kl = (hypothesis_count - 1.0) / hypothesis_count * delta**2
        lower_bound = max(
            0.0,
            1.0
            - (average_pairwise_kl + log(2.0)) / log(float(hypothesis_count)),
        )
        maximum_fano_violation = max(
            maximum_fano_violation, lower_bound - monte_carlo_error
        )
        fano_rows.append(
            {
                "delta": delta,
                "fano_lower_bound": lower_bound,
                "map_monte_carlo_error": monte_carlo_error,
            }
        )

    combinatorial_rows = []
    target_error = 0.1
    for active_count in range(1, 5):
        support_count = comb(39, active_count)
        kl_required = (1.0 - target_error) * log(support_count) - log(2.0)
        combinatorial_rows.append(
            {
                "active_count": active_count,
                "support_count": support_count,
                "average_kl_required": kl_required,
                "equivalent_average_distance_squared": 2.0 * kl_required,
            }
        )

    return [
        {
            "name": "equal_covariance_gaussian_bayes_error",
            "distances": distances.tolist(),
            "error_probabilities": exact_errors.tolist(),
            "error": gaussian_error,
            "tolerance": 1e-12,
            "passed": gaussian_error <= 1e-12,
        },
        {
            "name": "gaussian_quotient_operational_map",
            "gamma": gamma_value,
            "bayes_error": quotient_error_probability,
            "kl_divergence": quotient_kl,
            "error": quotient_error,
            "tolerance": 1e-12,
            "passed": quotient_error <= 1e-12,
        },
        {
            "name": "beta_min_and_detection_boundary",
            "near_zero_error": beta_min_error_probability,
            "phase_records": phase_records,
            "error": phase_error,
            "tolerance": 1e-12,
            "passed": beta_min_error <= 0.002 and phase_error <= 1e-12,
        },
        {
            "name": "fano_multisupport_lower_bound",
            "rows": fano_rows,
            "maximum_violation": maximum_fano_violation,
            "ieee39_combinatorial_illustration": combinatorial_rows,
            "error": maximum_fano_violation,
            "tolerance": 0.0,
            "passed": maximum_fano_violation <= 0.0,
        },
    ]


def audit_rawsim39_checkpoint(frozen_root: Path) -> tuple[dict[str, object], list[dict[str, object]]]:
    decision_path = frozen_root / "rawsim39_v12_identifiability_decision.json"
    ledger_path = frozen_root / "rawsim39_v12_parameter_decision_ledger.csv"
    decision = json.loads(decision_path.read_text(encoding="utf-8-sig"))
    with ledger_path.open(encoding="utf-8-sig", newline="") as handle:
        ledger = list(csv.DictReader(handle))

    categories: dict[str, list[str]] = {
        "REGULAR_LOCAL_IDENTIFIABLE": [],
        "WEAK_FIRST_ORDER_INFORMATION": [],
        "NONLINEAR_CURVATURE_UNRESOLVED": [],
        "NEAR_REDUNDANT_FIRST_ORDER": [],
        "LOCAL_MODEL_DOMAIN_FAILURE": [],
    }
    for row in ledger:
        status = row["final_status"]
        reason = row["final_reason"]
        if status == "RELEASED_RESTRICTED_POSTERIOR":
            category = "REGULAR_LOCAL_IDENTIFIABLE"
        elif status == "REJECTED_PRIOR_DOMAIN":
            category = "LOCAL_MODEL_DOMAIN_FAILURE"
        elif status == "REJECTED_JOINT_IDENTIFIABILITY":
            category = "NEAR_REDUNDANT_FIRST_ORDER"
        elif status == "REJECTED_PRESELECTION" and "curvature_ratio" in reason:
            category = "NONLINEAR_CURVATURE_UNRESOLVED"
        elif status == "REJECTED_PRESELECTION":
            category = "WEAK_FIRST_ORDER_INFORMATION"
        else:
            raise ValueError(f"Unmapped RAWSIM39 status for {row['name']}: {status}")
        categories[category].append(row["name"])

    observed_counts = {category: len(names) for category, names in categories.items()}
    expected_counts = {
        "REGULAR_LOCAL_IDENTIFIABLE": 7,
        "WEAK_FIRST_ORDER_INFORMATION": 6,
        "NONLINEAR_CURVATURE_UNRESOLVED": 2,
        "NEAR_REDUNDANT_FIRST_ORDER": 2,
        "LOCAL_MODEL_DOMAIN_FAILURE": 1,
    }
    gate_values = {
        "candidate_count": int(decision["candidate_count"]),
        "eligible_candidate_count": int(decision["eligible_candidate_count"]),
        "eligible_full_condition_number": float(
            decision["eligible_full_condition_number"]
        ),
        "selected_parameter_count": int(decision["selected_parameter_count"]),
        "selected_condition_number": float(decision["selected_condition_number"]),
        "released_parameter_count": observed_counts["REGULAR_LOCAL_IDENTIFIABLE"],
    }
    count_error = max(
        abs(observed_counts[key] - expected_counts[key]) for key in expected_counts
    )
    gate_error = max(
        abs(gate_values["candidate_count"] - 18),
        abs(gate_values["eligible_candidate_count"] - 10),
        abs(gate_values["selected_parameter_count"] - 8),
        abs(gate_values["released_parameter_count"] - 7),
        abs(gate_values["eligible_full_condition_number"] - 722.9105686056365),
        abs(gate_values["selected_condition_number"] - 7.826727232395702),
    )
    check = {
        "name": "rawsim39_v12_gate_taxonomy",
        "gate_values": gate_values,
        "category_counts": observed_counts,
        "category_members": categories,
        "error": max(count_error, gate_error),
        "tolerance": 1e-10,
        "passed": count_error == 0 and gate_error <= 1e-10,
    }
    table_rows = [
        {
            "category": category,
            "count": observed_counts[category],
            "members": categories[category],
        }
        for category in expected_counts
    ]
    return check, table_rows


def write_validation_table(path: Path, checks: list[dict[str, object]]) -> None:
    by_name = {str(check["name"]): check for check in checks}
    slopes = by_name["nested_support_occam_exponents"]["slopes"]
    fano_rows = by_name["fano_multisupport_lower_bound"]["rows"]
    rows = [
        (
            "Evidence classes",
            f"slopes {slopes['regular']:.4f}, {slopes['order_2']:.4f}, and {slopes['redundant']:.4f} for regular, order-2, and redundant additions",
        ),
        (
            "Prefix monotonicity",
            f"{by_name['profiled_horizon_monotonicity']['trials']} correlated-noise trials; max violation {by_name['profiled_horizon_monotonicity']['maximum_violation']:.1e}",
        ),
        (
            "Temporal rescue",
            f"first-order $\\gamma_1^2(2)={by_name['first_order_temporal_rescue']['gamma_squared'][1]:.6f}$; second-order relative error {by_name['second_order_temporal_rescue']['error']:.1e}",
        ),
        (
            "Gaussian error map",
            f"quadrature error {by_name['equal_covariance_gaussian_bayes_error']['error']:.1e}",
        ),
        (
            "Fano lower bound",
            f"$M=8$ bounds {fano_rows[0]['fano_lower_bound']:.4f}/{fano_rows[1]['fano_lower_bound']:.4f}; no Monte Carlo violation",
        ),
    ]
    lines = [
        r"\begin{table}[!t]",
        r"\caption{Recomputed checks of higher-order evidence and information limits. Controlled systems are not IEEE 39-bus performance evidence.}",
        r"\label{tab:supp-information-limit-checks}",
        r"\centering",
        r"\scriptsize",
        r"\begin{tabularx}{\columnwidth}{@{}p{0.34\columnwidth}X@{}}",
        r"\toprule",
        r"Check & Recomputed outcome \\",
        r"\midrule",
    ]
    lines.extend(f"{label} & {outcome} (pass). \\\\" for label, outcome in rows)
    lines.extend([r"\bottomrule", r"\end{tabularx}", r"\end{table}"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def latex_escape(value: str) -> str:
    return value.replace("_", r"\_")


def write_rawsim_table(
    path: Path, checkpoint: dict[str, object], rows: list[dict[str, object]]
) -> None:
    labels = {
        "REGULAR_LOCAL_IDENTIFIABLE": "Regular local",
        "WEAK_FIRST_ORDER_INFORMATION": "Weak first-order",
        "NONLINEAR_CURVATURE_UNRESOLVED": "Curvature unresolved",
        "NEAR_REDUNDANT_FIRST_ORDER": "Near-redundant first-order",
        "LOCAL_MODEL_DOMAIN_FAILURE": "Local-domain failure",
    }
    boundaries = {
        "REGULAR_LOCAL_IDENTIFIABLE": "Released only under the local restricted posterior",
        "WEAK_FIRST_ORDER_INFORMATION": "Low information; order and temporal rescue unresolved",
        "NONLINEAR_CURVATURE_UNRESOLVED": "Linear surrogate failed; not evidence of order 2",
        "NEAR_REDUNDANT_FIRST_ORDER": "Small new orthogonal fraction; exact redundancy unproved",
        "LOCAL_MODEL_DOMAIN_FAILURE": "MAP left the declared local prior domain",
    }
    gate_values = checkpoint["gate_values"]
    lines = [
        r"\begin{table*}[!t]",
        r"\caption{Conservative taxonomy of the frozen RAWSIM39 V1.2 calibration checkpoint. The gate sequence was 18 candidates, 10 individually eligible ($\kappa=722.91$), eight rank-selected ($\kappa=7.83$), and seven released after one $6.15\sigma$ local-domain rejection.}",
        r"\label{tab:supp-rawsim39-v12-taxonomy}",
        r"\centering",
        r"\scriptsize",
        r"\begin{tabularx}{\textwidth}{@{}l c X X@{}}",
        r"\toprule",
        r"Category & Count & Directions & Evidence boundary \\",
        r"\midrule",
    ]
    for row in rows:
        category = str(row["category"])
        members = ", ".join(latex_escape(name) for name in row["members"])
        lines.append(
            f"{labels[category]} & {row['count']} & {members} & {boundaries[category]} \\\\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabularx}",
            r"\end{table*}",
        ]
    )
    if int(gate_values["candidate_count"]) != 18:
        raise ValueError("Unexpected RAWSIM39 candidate count while writing table")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def json_default(value: object) -> object:
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def main(
    output_path: Path,
    validation_table_path: Path,
    rawsim_table_path: Path,
    frozen_root: Path,
) -> None:
    checks = evidence_scaling_checks() + horizon_checks() + operational_limit_checks()
    checkpoint_check, checkpoint_rows = audit_rawsim39_checkpoint(frozen_root)
    checks.append(checkpoint_check)
    payload = {
        "scope": (
            "Analytic and controlled numerical checks of evidence scaling, temporal "
            "information, and fundamental limits, plus a gate-only audit of the "
            "frozen RAWSIM39 V1.2 checkpoint."
        ),
        "checks": checks,
        "passed": sum(bool(check["passed"]) for check in checks),
        "total": len(checks),
    }
    serialized = json.dumps(payload, indent=2, default=json_default)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(serialized + "\n", encoding="utf-8")
    write_validation_table(validation_table_path, checks)
    write_rawsim_table(rawsim_table_path, checkpoint_check, checkpoint_rows)
    print(serialized)
    if payload["passed"] != payload["total"]:
        raise SystemExit(1)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=root / "generated" / "information_limit_checks.json",
    )
    parser.add_argument(
        "--validation-table-output",
        type=Path,
        default=root / "tables" / "generated" / "information_limit_validation.tex",
    )
    parser.add_argument(
        "--rawsim-table-output",
        type=Path,
        default=root / "tables" / "generated" / "rawsim39_v12_taxonomy.tex",
    )
    parser.add_argument(
        "--frozen-root",
        type=Path,
        default=root / "generated" / "frozen",
    )
    arguments = parser.parse_args()
    main(
        arguments.output,
        arguments.validation_table_output,
        arguments.rawsim_table_output,
        arguments.frozen_root,
    )

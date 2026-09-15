#!/usr/bin/env python3
"""Reproduce deterministic checks used by the adopted local theory.

The suite guards the branch primitive, first- and second-order profiled
separation, rank-deficient nuisance profiling, and multi-event support geometry.
It intentionally uses explicit toy systems and does not simulate or validate the
IEEE 39-bus experiments.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def relative_error(actual: float, expected: float) -> float:
    return float(abs(actual - expected) / max(abs(expected), 1e-15))


def json_default(value: object) -> object:
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def branch_primitive_check() -> dict[str, float | bool | str]:
    tap = 1.08 * np.exp(1j * 0.17)
    admittance = 1 / (0.03 + 1j * 0.18)
    terminal_vector = np.array([1 / tap, -1])
    primitive = admittance * np.outer(terminal_vector.conj(), terminal_vector)
    primitive += np.diag([0.01 / abs(tap) ** 2 + 0.02j, 0.02 + 0.02j])
    voltage = np.array([1.01 * np.exp(1j * 0.04), 0.98 * np.exp(-1j * 0.03)])
    dissipated = float(np.vdot(voltage, primitive @ voltage).real)
    expected = float(
        admittance.real * abs(terminal_vector @ voltage) ** 2
        + 0.01 * abs(voltage[0] / tap) ** 2
        + 0.02 * abs(voltage[1]) ** 2
    )
    error = relative_error(dissipated, expected)
    return {
        "name": "branch_primitive_real_power",
        "error": error,
        "tolerance": 1e-12,
        "passed": error <= 1e-12,
    }


def regular_first_order_dae_check() -> dict[str, float | bool | str]:
    """Check the two-frame DAE example against its closed-form projection."""
    event_tangent = np.array(
        [2 * (1 - np.exp(-0.5)), 2 * (1 - np.exp(-1.0))]
    )
    nuisance_tangent = np.array([np.exp(-0.5), np.exp(-1.0)])
    projector = np.outer(nuisance_tangent, nuisance_tangent) / float(
        nuisance_tangent @ nuisance_tangent
    )
    residual = (np.eye(2) - projector) @ event_tangent
    gamma_squared = float(residual @ residual)
    expected_gamma_squared = 0.452724464118
    amplitudes = np.geomspace(1e-5, 1e-1, 17)
    squared_distances = amplitudes**2 * gamma_squared
    slope = float(np.polyfit(np.log(amplitudes), np.log(squared_distances), 1)[0])
    normal_error = float(abs(nuisance_tangent @ residual))
    error = max(
        relative_error(gamma_squared, expected_gamma_squared),
        abs(slope - 2.0),
        normal_error,
    )
    return {
        "name": "regular_first_order_dae",
        "gamma_squared": gamma_squared,
        "expected_gamma_squared": expected_gamma_squared,
        "squared_distance_log_slope": slope,
        "normal_equation_error": normal_error,
        "error": error,
        "tolerance": 1e-10,
        "passed": error <= 1e-10,
    }


def contact_order_check() -> dict[str, float | bool | str]:
    """Check the exact shared-tangent parabola with coefficient c=1.7."""
    curvature = 1.7
    amplitudes = np.geomspace(1e-5, 2e-2, 19)
    squared_distances = []
    for amplitude in amplitudes:
        roots = np.roots([2 * curvature**2, 0.0, 1.0, -amplitude])
        candidates = [root.real for root in roots if abs(root.imag) < 1e-10]

        def distance_squared(nuisance: float) -> float:
            return float((amplitude - nuisance) ** 2 + (curvature * nuisance**2) ** 2)

        best = min(candidates, key=distance_squared)
        squared_distances.append(distance_squared(best))

    slope = float(
        np.polyfit(np.log(amplitudes[:10]), np.log(squared_distances[:10]), 1)[0]
    )
    limiting_coefficient = float(squared_distances[0] / amplitudes[0] ** 4)
    expected_coefficient = curvature**2
    error = max(abs(slope - 4.0), relative_error(limiting_coefficient, expected_coefficient))
    return {
        "name": "relative_second_order_contact",
        "squared_distance_log_slope": slope,
        "expected_slope": 4.0,
        "limiting_coefficient": limiting_coefficient,
        "expected_coefficient": expected_coefficient,
        "error": error,
        "tolerance": 1e-3,
        "passed": error <= 1e-3,
    }


def rank_deficient_profile_check() -> dict[str, float | bool | str | int]:
    matrix = np.array(
        [
            [1.0, 0.0, 1.0],
            [0.0, 1.0, 1.0],
            [0.0, 0.0, 0.0],
        ]
    )
    tangent = np.array([0.5, -0.5, np.sqrt(0.5)])
    minimum_norm = np.linalg.pinv(matrix) @ tangent
    projector = matrix @ np.linalg.pinv(matrix)
    gamma_squared = float(np.linalg.norm((np.eye(3) - projector) @ tangent) ** 2)
    null_direction = np.array([-1.0, -1.0, 1.0]) / np.sqrt(3.0)
    fits = [matrix @ (minimum_norm + scale * null_direction) for scale in (-5, -1, 0, 1, 5)]
    fit_variation = max(float(np.linalg.norm(fit - fits[2])) for fit in fits)
    residual_variation = max(
        abs(float(np.linalg.norm(tangent - fit) ** 2) - gamma_squared) for fit in fits
    )
    error = max(abs(gamma_squared - 0.5), fit_variation, residual_variation)
    return {
        "name": "rank_deficient_profile",
        "rank": int(np.linalg.matrix_rank(matrix)),
        "parameter_count": int(matrix.shape[1]),
        "gamma_squared": gamma_squared,
        "max_projected_fit_variation": fit_variation,
        "max_residual_variation": residual_variation,
        "error": error,
        "tolerance": 1e-12,
        "passed": error <= 1e-12,
    }


def squared_distance_to_span(vector: np.ndarray, columns: np.ndarray) -> float:
    projector = columns @ np.linalg.pinv(columns)
    residual = (np.eye(vector.size) - projector) @ vector
    return float(residual @ residual)


def support_geometry_checks() -> list[dict[str, float | bool | str]]:
    basis = np.eye(5)
    nuisance = basis[:, [0]]
    source_i = basis[:, 1]
    source_j = basis[:, 2] + 0.2 * basis[:, 4]
    source_k = basis[:, 2]
    true_unique_amplitude = 0.7

    shared_competitor = np.column_stack([nuisance, source_i, source_k])
    shared_margins = []
    for shared_amplitude in (0.1, 1.0, 10.0, 100.0):
        true_direction = shared_amplitude * source_i + true_unique_amplitude * source_j
        shared_margins.append(squared_distance_to_span(true_direction, shared_competitor))
    expected_shared = (0.2 * true_unique_amplitude) ** 2
    shared_error = max(abs(value - expected_shared) for value in shared_margins)

    single_competitor = np.column_stack([nuisance, source_i])
    true_direction = source_i + true_unique_amplitude * source_j
    single_margin = squared_distance_to_span(true_direction, single_competitor)
    enriched_margin = squared_distance_to_span(true_direction, shared_competitor)
    enrichment_error = max(0.0, enriched_margin - single_margin)

    nested_competitor = np.column_stack([nuisance, source_i, source_j, source_k])
    nested_margin = squared_distance_to_span(true_direction, nested_competitor)

    angle = 0.37
    angle_true = basis[:, 1]
    angle_competitor = np.cos(angle) * basis[:, 1] + np.sin(angle) * basis[:, 2]
    angle_margin = squared_distance_to_span(angle_true, angle_competitor[:, None])
    angle_error = abs(np.sqrt(angle_margin) - np.sin(angle))

    event = basis[:, 1] + basis[:, 2] + basis[:, 3]
    nuisance_margins = [
        squared_distance_to_span(event, basis[:, [1]]),
        squared_distance_to_span(event, basis[:, [1, 2]]),
        squared_distance_to_span(event, basis[:, [1, 2, 3]]),
    ]
    monotonic_error = max(
        0.0,
        nuisance_margins[1] - nuisance_margins[0],
        nuisance_margins[2] - nuisance_margins[1],
    )

    return [
        {
            "name": "shared_source_cancellation",
            "expected_margin_squared": expected_shared,
            "margin_range": max(shared_margins) - min(shared_margins),
            "error": shared_error,
            "tolerance": 1e-12,
            "passed": shared_error <= 1e-12,
        },
        {
            "name": "competitor_enrichment_monotonicity",
            "single_margin_squared": single_margin,
            "enriched_margin_squared": enriched_margin,
            "error": enrichment_error,
            "tolerance": 1e-12,
            "passed": enrichment_error <= 1e-12,
        },
        {
            "name": "nested_support_zero_margin",
            "margin_squared": nested_margin,
            "error": nested_margin,
            "tolerance": 1e-12,
            "passed": nested_margin <= 1e-12,
        },
        {
            "name": "principal_angle_margin",
            "angle_radians": angle,
            "observed_margin": float(np.sqrt(angle_margin)),
            "expected_margin": float(np.sin(angle)),
            "error": angle_error,
            "tolerance": 1e-12,
            "passed": angle_error <= 1e-12,
        },
        {
            "name": "nuisance_absorption_monotonicity",
            "margin_sequence": nuisance_margins,
            "error": monotonic_error,
            "tolerance": 1e-12,
            "passed": monotonic_error <= 1e-12,
        },
    ]


def write_latex_table(path: Path, checks: list[dict[str, object]]) -> None:
    by_name = {str(check["name"]): check for check in checks}
    regular = by_name["regular_first_order_dae"]
    second = by_name["relative_second_order_contact"]
    rank_deficient = by_name["rank_deficient_profile"]
    shared = by_name["shared_source_cancellation"]
    enrichment = by_name["competitor_enrichment_monotonicity"]
    nested = by_name["nested_support_zero_margin"]
    angle = by_name["principal_angle_margin"]
    nuisance = by_name["nuisance_absorption_monotonicity"]
    rows = [
        (
            "Regular first-order DAE",
            r"slope $2$ and $\gamma_1^2=0.4527244641$",
            rf"{regular['squared_distance_log_slope']:.6f}; relative error {relative_error(float(regular['gamma_squared']), float(regular['expected_gamma_squared'])):.1e}",
        ),
        (
            "Shared-tangent second order",
            r"slope $4$ and $\gamma_2^2=2.89$",
            rf"{second['squared_distance_log_slope']:.6f}; coefficient {second['limiting_coefficient']:.6f}",
        ),
        (
            "Rank-deficient nuisance",
            r"unique projected fit and $\gamma_1^2=0.5$",
            rf"rank {rank_deficient['rank']}/{rank_deficient['parameter_count']}; max variation {rank_deficient['max_projected_fit_variation']:.1e}",
        ),
        (
            "Signed shared-source cancellation",
            r"margin independent of shared amplitude",
            rf"squared-margin range {shared['margin_range']:.1e}",
        ),
        (
            "Competitor enrichment",
            r"$\gamma(S\!\to\!C_2)\le\gamma(S\!\to\!C_1)$",
            rf"{enrichment['enriched_margin_squared']:.4f} versus {enrichment['single_margin_squared']:.4f}",
        ),
        (
            "Nested support",
            r"geometric margin $0$",
            rf"{nested['margin_squared']:.1e}",
        ),
        (
            "Principal angle",
            r"unit margin $\sin\theta$",
            rf"absolute error {angle['error']:.1e}",
        ),
        (
            "Nuisance enlargement",
            r"profiled margin cannot increase",
            "sequence " + ", ".join(f"{value:.1f}" for value in nuisance["margin_sequence"]),
        ),
    ]
    lines = [
        r"\begin{table}[t]",
        r"\caption{Deterministic checks of the local separation identities. These toy systems are not IEEE 39-bus evidence.}",
        r"\label{tab:supp-controlled-theory-checks}",
        r"\centering",
        r"\scriptsize",
        r"\begin{tabularx}{\columnwidth}{@{}p{0.30\columnwidth}X@{}}",
        r"\toprule",
        "Check & Prediction and recomputed outcome \\\\",
        r"\midrule",
    ]
    for label, prediction, observed in rows:
        lines.append(f"{label} & {prediction}; {observed} (pass). \\\\")
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabularx}",
            r"\end{table}",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(output_path: Path, table_path: Path) -> None:
    checks = [
        branch_primitive_check(),
        regular_first_order_dae_check(),
        contact_order_check(),
        rank_deficient_profile_check(),
        *support_geometry_checks(),
    ]
    payload = {
        "scope": "Deterministic toy checks of local theory; not IEEE 39-bus evidence.",
        "checks": checks,
        "passed": sum(bool(check["passed"]) for check in checks),
        "total": len(checks),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(payload, indent=2, default=json_default)
    output_path.write_text(serialized + "\n", encoding="utf-8")
    write_latex_table(table_path, checks)
    print(serialized)
    if payload["passed"] != payload["total"]:
        raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "generated" / "theory_checks.json",
    )
    parser.add_argument(
        "--table-output",
        type=Path,
        default=Path(__file__).resolve().parents[1]
        / "tables"
        / "generated"
        / "theory_validation.tex",
    )
    arguments = parser.parse_args()
    main(arguments.output, arguments.table_output)

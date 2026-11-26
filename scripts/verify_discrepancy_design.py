#!/usr/bin/env python3
"""Verify diagnosability-preserving discrepancy-covariance identities.

The checks are deterministic linear-algebra experiments.  They validate the
stated covariance, retention, and fixed-subspace likelihood formulas; they are
not IEEE 39-bus evidence and do not validate a learned discrepancy model.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.optimize import minimize_scalar


ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
TABLES = ROOT / "tables" / "generated"


def orthonormal_columns(matrix: np.ndarray) -> np.ndarray:
    q, _ = np.linalg.qr(matrix)
    return q[:, : matrix.shape[1]]


def record(name: str, error: float, tolerance: float, detail: str) -> dict[str, object]:
    return {
        "name": name,
        "error": float(error),
        "tolerance": float(tolerance),
        "passed": bool(error <= tolerance),
        "detail": detail,
    }


def main() -> None:
    rng = np.random.default_rng(20260915)
    m, r, q = 12, 3, 2
    q_u = orthonormal_columns(rng.normal(size=(m, r)))
    p_u = q_u @ q_u.T
    q_perp = orthonormal_columns((np.eye(m) - p_u) @ rng.normal(size=(m, q)))

    theta = np.deg2rad(30.0)
    q_d = np.column_stack(
        [np.cos(theta) * q_u[:, 0] + np.sin(theta) * q_perp[:, 0], q_perp[:, 1]]
    )
    p_d = q_d @ q_d.T
    cosine_squared = float(np.linalg.svd(q_u.T @ q_d, compute_uv=False)[0] ** 2)

    tau = 0.7
    variance = tau**2
    alpha = variance / (1.0 + variance)
    covariance = np.eye(m) + variance * p_d
    precision_formula = np.eye(m) - alpha * p_d
    inverse_error = float(
        np.linalg.norm(np.linalg.inv(covariance) - precision_formula, ord=2)
    )

    retention_matrix = q_u.T @ precision_formula @ q_u
    retention_numeric = float(np.linalg.eigvalsh(retention_matrix)[0])
    retention_formula = 1.0 - alpha * cosine_squared
    retention_error = abs(retention_numeric - retention_formula)

    rho_min = 0.8
    delta = 1.0 - rho_min
    variance_cap = delta / (cosine_squared - delta)
    alpha_cap = variance_cap / (1.0 + variance_cap)
    retention_at_cap = 1.0 - alpha_cap * cosine_squared
    cap_error = abs(retention_at_cap - rho_min)

    mismatch_factor = rng.normal(size=(m, 5))
    c_m = mismatch_factor @ mismatch_factor.T / mismatch_factor.shape[1]
    captured_energy = float(np.trace(q_d.T @ c_m @ q_d))

    def expected_relative_score(s: float) -> float:
        a = s / (1.0 + s)
        return q * np.log1p(s) - a * (q + captured_energy)

    unconstrained_variance = captured_energy / q
    optimal_variance = min(unconstrained_variance, variance_cap)
    numerical = minimize_scalar(
        expected_relative_score,
        bounds=(0.0, variance_cap),
        method="bounded",
        options={"xatol": 1e-13},
    )
    likelihood_error = abs(float(numerical.x) - optimal_variance)

    p_perp = np.eye(m) - p_u
    safe_covariance = p_perp @ c_m @ p_perp
    eigenvalues, eigenvectors = np.linalg.eigh(safe_covariance)
    q_safe = eigenvectors[:, -q:]
    safe_energy = float(np.trace(q_safe.T @ c_m @ q_safe))
    safe_bound = float(np.sum(eigenvalues[-q:]))
    random_best = -np.inf
    for _ in range(1000):
        candidate = orthonormal_columns(p_perp @ rng.normal(size=(m, q)))
        random_best = max(random_best, float(np.trace(candidate.T @ c_m @ candidate)))
    safe_error = max(
        abs(safe_energy - safe_bound),
        max(0.0, random_best - safe_energy),
        float(np.linalg.norm(q_u.T @ q_safe, ord=2)),
    )

    eigvals, eigvecs = np.linalg.eigh(retention_matrix)
    weakest = q_u @ eigvecs[:, 0]
    protected_ratio = float(weakest.T @ precision_formula @ weakest / (weakest.T @ weakest))
    distance_error = abs(protected_ratio - retention_formula)

    checks = [
        record(
            "low_rank_covariance_inverse",
            inverse_error,
            1e-12,
            "Woodbury/projector inverse for I + tau^2 P_D",
        ),
        record(
            "principal_angle_retention",
            retention_error,
            1e-12,
            "minimum protected information ratio",
        ),
        record(
            "retention_variance_cap",
            cap_error,
            1e-12,
            "closed-form variance cap reaches rho_min",
        ),
        record(
            "finite_full_likelihood_intensity",
            likelihood_error,
            1e-7,
            "analytic full-Gaussian optimum versus bounded scalar solve",
        ),
        record(
            "safe_projected_pca",
            safe_error,
            1e-10,
            "Ky Fan optimum inside the protected orthogonal complement",
        ),
        record(
            "protected_distance_floor",
            distance_error,
            1e-12,
            "least-retained protected direction attains the bound",
        ),
    ]

    payload = {
        "contract": {
            "seed": 20260915,
            "ambient_dimension": m,
            "protected_rank": r,
            "discrepancy_rank": q,
            "principal_angle_degrees": 30.0,
            "rho_min": rho_min,
        },
        "derived": {
            "cosine_squared": cosine_squared,
            "variance_cap": variance_cap,
            "captured_mismatch_energy": captured_energy,
            "unconstrained_likelihood_variance": unconstrained_variance,
            "selected_likelihood_variance": optimal_variance,
            "safe_projected_energy": safe_energy,
            "best_random_safe_energy": random_best,
        },
        "checks": checks,
        "all_passed": all(bool(check["passed"]) for check in checks),
        "evidence_boundary": (
            "Controlled algebraic checks only; no learned model or IEEE 39-bus "
            "discrepancy campaign is validated."
        ),
    }

    GENERATED.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    (GENERATED / "discrepancy_design_checks.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )

    labels = {
        "low_rank_covariance_inverse": "Low-rank covariance inverse",
        "principal_angle_retention": "Principal-angle retention",
        "retention_variance_cap": "Retention variance cap",
        "finite_full_likelihood_intensity": "Finite full-likelihood intensity",
        "safe_projected_pca": "Safe projected PCA",
        "protected_distance_floor": "Protected-distance floor",
    }
    rows = []
    for check in checks:
        rows.append(
            f"{labels[str(check['name'])]} & {float(check['error']):.2e} & "
            f"{float(check['tolerance']):.1e} & PASS \\\\"
        )
    table = """\\begin{table}[t]
\\caption{Deterministic checks for the discrepancy-retention identities. These are algebraic tests, not power-system experiments.}
\\label{tab:supp-discrepancy-design-checks}
\\centering
\\scriptsize
\\begin{tabular}{@{}lrrc@{}}
\\toprule
Check & Error & Tolerance & Status \\\\
\\midrule
""" + "\n".join(rows) + """
\\bottomrule
\\end{tabular}
\\end{table}
"""
    (TABLES / "discrepancy_design_validation.tex").write_text(table, encoding="ascii")

    if not payload["all_passed"]:
        failed = [str(check["name"]) for check in checks if not check["passed"]]
        raise SystemExit(f"Discrepancy-design checks failed: {failed}")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

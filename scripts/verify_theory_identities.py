#!/usr/bin/env python3
"""Reproduce the algebraic checks used by the adopted local theory.

These deterministic toy checks guard the branch primitive and the asymptotic
order in Proposition 3.  They do not simulate or validate the IEEE 39-bus
experiments.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def relative_error(actual: float, expected: float) -> float:
    return float(abs(actual - expected) / max(abs(expected), 1e-15))


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


def contact_order_check() -> dict[str, float | bool | str]:
    gamma, zeta = 0.5, 1.5
    amplitudes = np.geomspace(5e-4, 2e-2, 15)
    squared_distances = []
    for amplitude in amplitudes:
        roots = np.roots(
            [2 * gamma**2, 0.0, 1 - 2 * gamma * zeta * amplitude**2, -amplitude]
        )
        candidates = [root.real for root in roots if abs(root.imag) < 1e-10]

        def distance_squared(nuisance: float) -> float:
            return float(
                (amplitude - nuisance) ** 2
                + (zeta * amplitude**2 - gamma * nuisance**2) ** 2
            )

        best = min(candidates, key=distance_squared)
        squared_distances.append(distance_squared(best))

    slope = float(
        np.polyfit(np.log(amplitudes[:8]), np.log(squared_distances[:8]), 1)[0]
    )
    error = abs(slope - 4.0)
    return {
        "name": "relative_second_order_contact",
        "squared_distance_log_slope": slope,
        "expected_slope": 4.0,
        "error": error,
        "tolerance": 1e-3,
        "passed": error <= 1e-3,
    }


def main(output_path: Path) -> None:
    checks = [branch_primitive_check(), contact_order_check()]
    payload = {
        "scope": "Deterministic algebraic toy checks; not IEEE 39-bus evidence.",
        "checks": checks,
        "passed": sum(bool(check["passed"]) for check in checks),
        "total": len(checks),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if payload["passed"] != payload["total"]:
        raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "generated" / "theory_checks.json",
    )
    main(parser.parse_args().output)

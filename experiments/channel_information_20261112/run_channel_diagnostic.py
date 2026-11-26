from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.linalg import cholesky, solve_triangular
from scipy.sparse import csr_matrix


HERE = Path(__file__).resolve().parent
SNAPSHOT = HERE / "input_snapshot.npz"
ASSETS_PATH = HERE / "r11_assets.json"
READY_PATH = HERE / "source_CAL_READY.json"
F01_MAP = HERE / "F01_terminal_mapping.csv"
R11_MAP = HERE / "r11_terminal_mapping.csv"
HORIZONS = (3, 15, 30)
LOAD_AMPLITUDE = 0.10
CHANNELS = {
    "V": tuple(range(0, 16)),
    "VI": tuple(range(0, 31)),
    "all": tuple(range(0, 47)),
}
FIELDS = (
    ("voltage_magnitude", 0, 8),
    ("voltage_angle", 8, 16),
    ("current_magnitude", 16, 24),
    ("current_angle", 24, 31),
    ("frequency", 31, 39),
    ("rocof", 39, 47),
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def array_hash(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).view(np.uint8)).hexdigest()


def operator_index(cell: int, kind: str) -> int:
    # Frozen R11/C01 operator ordering: normal, then five rows per source.
    return 1 + 5 * cell + {"stay": 0, "on0": 1}[kind]


def read_assets() -> list[dict]:
    return json.loads(ASSETS_PATH.read_text(encoding="utf-8"))


def load_snapshot() -> dict[str, np.ndarray]:
    with np.load(SNAPSHOT, allow_pickle=False) as d:
        return {k: d[k] for k in d.files}


def event_mean(bank: dict[str, np.ndarray], assets: list[dict], horizon: int) -> np.ndarray:
    nsource = len(assets)
    out = np.empty((nsource, horizon, 47), dtype=np.float64)
    baseline = bank["j"][0]
    for cell, asset in enumerate(assets):
        family = asset["family"]
        amp = LOAD_AMPLITUDE if family == "load" else 0.0
        x = np.zeros(bank["T"].shape[1], dtype=np.float64)
        for t in range(horizon):
            op = operator_index(cell, "on0" if t == 0 else "stay")
            group = int(bank["group"][op])
            out[cell, t] = bank["J"][group] @ x + bank["j"][op] + bank["v"][op] * amp - baseline
            x = bank["T"][group] @ x + bank["g"][op] + bank["u"][op] * amp
    return out


def raw_covariance(bank: dict[str, np.ndarray], horizon: int) -> tuple[np.ndarray, np.ndarray]:
    """Common quiet-null raw covariance from the bank's full 47-D innovations.

    The null observer has m[k+1] = T m[k] + K e[k] and y[k] = J m[k] + e[k],
    with iid e[k] ~ N(0,S). This recursion forms Cov(y[0:h]) without treating
    filtered innovations as an invalid sensor ablation.
    """
    if int(bank["group"][0]) != 0:
        raise ValueError("Expected normal null operator to belong to group 0")
    tmat = csr_matrix(bank["T"][0])
    jmat = bank["J"][0]
    kmat = bank["K0"]
    sinv = bank["Sinv0"]
    s = (bank["S"] + bank["S"].T) * 0.5
    q = kmat @ s @ kmat.T
    pm = np.zeros((tmat.shape[0], tmat.shape[0]), dtype=np.float64)
    gamma = np.empty((horizon * 47, horizon * 47), dtype=np.float64)
    for k in range(horizon):
        rows_k = slice(k * 47, (k + 1) * 47)
        gamma[rows_k, rows_k] = s + jmat @ pm @ jmat.T
        c = pm @ jmat.T
        for ell in range(k + 1, horizon):
            if ell == k + 1:
                c = tmat @ c + kmat @ s
            else:
                c = tmat @ c
            rows_l = slice(ell * 47, (ell + 1) * 47)
            cross = jmat @ c
            gamma[rows_l, rows_k] = cross
            gamma[rows_k, rows_l] = cross.T
        tmp = tmat @ pm
        pm = np.asarray((tmat @ tmp.T).T) + q
        pm = (pm + pm.T) * 0.5
    return gamma, s


def channel_indices(h: int, channels: tuple[int, ...]) -> np.ndarray:
    return np.concatenate([np.arange(t * 47, t * 47 + 47)[list(channels)] for t in range(h)])


def stable_factor(gamma: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    scale = np.sqrt(np.diag(gamma))
    if not np.isfinite(scale).all() or (scale <= 0).any():
        raise ValueError("Raw covariance has a nonpositive or nonfinite diagonal")
    corr = gamma / scale[:, None] / scale[None, :]
    corr = (corr + corr.T) * 0.5
    return cholesky(corr, lower=True, check_finite=False), scale


def whitened_norm(l: np.ndarray, scale: np.ndarray, d: np.ndarray) -> float:
    z = solve_triangular(l, d / scale, lower=True, check_finite=False)
    return float(z @ z)


def schur_components(cov: np.ndarray, d: np.ndarray, na: int) -> tuple[float, float, float]:
    """Return total, A marginal, and B|A quadratic forms via stable SPD solves."""
    a = cov[:na, :na]
    ab = cov[:na, na:]
    bb = cov[na:, na:]
    da, db = d[:na], d[na:]
    la = cholesky(a, lower=True, check_finite=False)
    wa = solve_triangular(la, da, lower=True, check_finite=False)
    a_inv_ab = solve_triangular(la.T, solve_triangular(la, ab, lower=True, check_finite=False),
                                lower=False, check_finite=False)
    cond = db - ab.T @ solve_triangular(la.T, solve_triangular(la, da, lower=True, check_finite=False),
                                        lower=False, check_finite=False)
    schur = bb - ab.T @ a_inv_ab
    schur = (schur + schur.T) * 0.5
    ls = cholesky(schur, lower=True, check_finite=False)
    wb = solve_triangular(ls, cond, lower=True, check_finite=False)
    return float(wa @ wa + wb @ wb), float(wa @ wa), float(wb @ wb)


def main() -> None:
    assets = read_assets()
    bank = load_snapshot()
    ready = json.loads(READY_PATH.read_text(encoding="utf-8"))
    if not ready.get("nominal_only") or ready.get("truth_read"):
        raise ValueError("Source READY record is not nominal-only/truth-free")
    if F01_MAP.read_bytes() != R11_MAP.read_bytes():
        raise ValueError("R11 active terminal mapping differs from frozen F01 mapping")
    if len(assets) != 18 or len(bank["group"]) != 91 or bank["j"].shape[1] != 47:
        raise ValueError("Unexpected frozen R11 asset/operator/channel layout")
    if bank["T"].shape[0] != 46 or bank["J"].shape[1:] != (47, bank["T"].shape[1]):
        raise ValueError("Operator bank has an unexpected state or measurement shape")
    for arr in bank.values():
        if not np.isfinite(arr).all():
            raise ValueError("Nonfinite value in compact nominal snapshot")
    line_operator_residual_max = 0.0
    for cell, asset in enumerate(assets):
        if asset["family"] == "line":
            rows_for_line = slice(1 + 5 * cell, 1 + 5 * (cell + 1))
            line_operator_residual_max = max(
                line_operator_residual_max,
                float(np.max(np.abs(bank["u"][rows_for_line]))),
                float(np.max(np.abs(bank["v"][rows_for_line]))),
            )
    if line_operator_residual_max != 0.0:
        raise ValueError("A line candidate has a nonzero profiled-input operator; fixed switching contract violated")

    gamma, s = raw_covariance(bank, max(HORIZONS))
    means = event_mean(bank, assets, max(HORIZONS))
    contracts = {}
    factors = {}
    scales = {}
    for name, channels in CHANNELS.items():
        idx = channel_indices(max(HORIZONS), channels)
        cov = gamma[np.ix_(idx, idx)]
        l, scale = stable_factor(cov)
        factors[name], scales[name], contracts[name] = l, scale, cov

    # Independent raw-to-innovation likelihood identity, all sources/pairs/horizons.
    sinv = bank["Sinv0"]
    tmat = csr_matrix(bank["T"][0])
    jmat = bank["J"][0]
    kmat = bank["K0"]
    max_raw_innov_error = 0.0
    rows = []
    pair_means = []
    pair_meta = []
    for i in range(len(assets)):
        for j in range(len(assets)):
            if i == j:
                continue
            pair_means.append(means[i] - means[j])
            pair_meta.append((i, j))
    pair_means = np.asarray(pair_means)

    # Check the covariance recursion independently against the explicit finite
    # innovation-to-raw triangular transform at a short prefix.
    short = 3
    lmap = np.eye(short * 47)
    powers = [np.eye(tmat.shape[0])]
    for _ in range(short - 1):
        powers.append(np.asarray(tmat @ powers[-1]))
    for k in range(short):
        for r in range(k):
            block = jmat @ powers[k - r - 1] @ kmat
            lmap[k * 47:(k + 1) * 47, r * 47:(r + 1) * 47] = block
    explicit = lmap @ np.kron(np.eye(short), s) @ lmap.T
    gamma_short = gamma[:short * 47, :short * 47]
    covariance_recursion_error = float(np.max(np.abs(explicit - gamma_short)) /
                                        max(1.0, np.max(np.abs(explicit))))

    for horizon_index, h in enumerate(HORIZONS):
        d_h = pair_means[:, :h, :]
        # all-channel direct Gaussian quadratic must match the full-null
        # innovations quadratic over the same complete raw report vector.
        all_l = factors["all"][:h * 47, :h * 47]
        all_scale = scales["all"][:h * 47]
        for q, d3 in enumerate(d_h):
            m = np.zeros(bank["T"].shape[1], dtype=np.float64)
            innov = []
            for k in range(h):
                e = d3[k] - jmat @ m
                innov.append(e)
                m = tmat @ m + kmat @ e
            q_innov = sum(float(e @ sinv @ e) for e in innov)
            q_raw = whitened_norm(all_l, all_scale, d3.reshape(-1))
            max_raw_innov_error = max(max_raw_innov_error,
                                      abs(q_raw - q_innov) / max(1.0, abs(q_innov)))

        contract_q = {name: np.empty(len(pair_meta), dtype=np.float64) for name in CHANNELS}
        for name, channels in CHANNELS.items():
            m = len(channels)
            l = factors[name][:h * m, :h * m]
            scale = scales[name][:h * m]
            for q, d3 in enumerate(d_h):
                vec = d3[:, list(channels)].reshape(-1)
                contract_q[name][q] = whitened_norm(l, scale, vec)

        for q, (i, j) in enumerate(pair_meta):
            qv = contract_q["V"][q]
            qvi = contract_q["VI"][q]
            qall = contract_q["all"][q]
            rows.append({
                "source": assets[i]["id"], "competitor": assets[j]["id"],
                "reports": h, "seconds_at_30_fps": h / 30.0,
                "D2_V": qv, "D2_VI": qvi, "D2_all": qall,
                "increment_I_given_V": qvi - qv,
                "increment_f_rocof_given_VI": qall - qvi,
                "load_amplitude": LOAD_AMPLITUDE if assets[i]["family"] == "load" else "",
                "competitor_load_amplitude": LOAD_AMPLITUDE if assets[j]["family"] == "load" else "",
                "line_operator": "fixed_opening" if "line" in (assets[i]["family"], assets[j]["family"]) else "",
            })

    # Schur decomposition checks for every directed pair at each fixed horizon.
    max_schur_abs_error = 0.0
    max_schur_relative_error = 0.0
    min_increment = math.inf
    for horizon_index, h in enumerate(HORIZONS):
        for name, a_channels, b_channels in (
            ("VI", tuple(range(0, 16)), tuple(range(16, 31))),
            ("all", tuple(range(0, 31)), tuple(range(31, 47))),
        ):
            ia = channel_indices(h, a_channels)
            ib = channel_indices(h, b_channels)
            cov = gamma[np.ix_(np.concatenate((ia, ib)), np.concatenate((ia, ib)))]
            # Equilibrate by standard deviations before Schur solves.
            sd = np.sqrt(np.diag(cov))
            c = cov / sd[:, None] / sd[None, :]
            c = (c + c.T) * 0.5
            ia_dim = h * len(a_channels)
            da = np.stack([d3[:, list(a_channels)].reshape(-1) for d3 in pair_means[:, :h, :]])
            db = np.stack([d3[:, list(b_channels)].reshape(-1) for d3 in pair_means[:, :h, :]])
            dmat = np.concatenate((da, db), axis=1) / sd
            a = c[:ia_dim, :ia_dim]
            ab = c[:ia_dim, ia_dim:]
            bb = c[ia_dim:, ia_dim:]
            la = cholesky(a, lower=True, check_finite=False)
            z_a = solve_triangular(la, dmat[:, :ia_dim].T, lower=True, check_finite=False)
            solved_ab = solve_triangular(la.T, solve_triangular(la, ab, lower=True, check_finite=False),
                                         lower=False, check_finite=False)
            solved_da = solve_triangular(la.T, z_a, lower=False, check_finite=False)
            residual_b = dmat[:, ia_dim:].T - ab.T @ solved_da
            schur = bb - ab.T @ solved_ab
            schur = (schur + schur.T) * 0.5
            ls = cholesky(schur, lower=True, check_finite=False)
            z_b = solve_triangular(ls, residual_b, lower=True, check_finite=False)
            q_a = np.sum(z_a * z_a, axis=0)
            q_cond = np.sum(z_b * z_b, axis=0)
            q_tot = q_a + q_cond
            target_rows = rows[horizon_index * len(pair_meta):(horizon_index + 1) * len(pair_meta)]
            total_target = np.array([r["D2_VI"] if name == "VI" else r["D2_all"] for r in target_rows])
            base_target = np.array([r["D2_V"] if name == "VI" else r["D2_VI"] for r in target_rows])
            max_schur_abs_error = max(max_schur_abs_error,
                                      float(np.max(np.abs(q_tot - total_target))),
                                      float(np.max(np.abs(q_a - base_target))),
                                      float(np.max(np.abs(q_cond - (total_target - base_target)))))
            max_schur_relative_error = max(max_schur_relative_error,
                                           float(np.max(np.abs(q_tot - total_target) /
                                                        np.maximum(1.0, np.abs(total_target)))),
                                           float(np.max(np.abs(q_a - base_target) /
                                                        np.maximum(1.0, np.abs(base_target)))),
                                           float(np.max(np.abs(q_cond - (total_target - base_target)) /
                                                        np.maximum(1.0, np.abs(total_target - base_target)))))
            min_increment = min(min_increment, float(np.min(q_cond)))

    df_summary = []
    for h in HORIZONS:
        subset = [r for r in rows if r["reports"] == h]
        for name, value in (("V", "D2_V"), ("VI", "D2_VI"), ("all", "D2_all")):
            for source in range(len(assets)):
                own = [r for r in subset if r["source"] == assets[source]["id"]]
                nearest = min(own, key=lambda r: r[value])
                df_summary.append({
                    "source": assets[source]["id"], "reports": h,
                    "seconds_at_30_fps": h / 30.0, "channels": name,
                    "nearest_competitor": nearest["competitor"],
                    "nearest_D2": nearest[value], "nearest_distance": math.sqrt(nearest[value]),
                })

    monotone = all(
        r["D2_V"] <= r["D2_VI"] + 1e-10 * max(1.0, r["D2_all"]) and
        r["D2_VI"] <= r["D2_all"] + 1e-10 * max(1.0, r["D2_all"]) for r in rows)
    covariance_identity_error = float(np.max(np.abs(bank["S"] @ bank["Sinv0"] - np.eye(47))))
    s_cholesky = cholesky(bank["S"], lower=True, check_finite=False)
    s_positive_definite = bool(np.isfinite(s_cholesky).all())
    gates = {
        "covariance_recursion": covariance_recursion_error <= 1e-10,
        "raw_innovation_equivalence": max_raw_innov_error <= 1e-8,
        "schur_relative_identity": max_schur_relative_error <= 1e-8,
        "S_inverse_identity": covariance_identity_error <= 1e-9,
        "S_positive_definite": s_positive_definite,
        "line_operator_has_no_continuous_input": line_operator_residual_max == 0.0,
        "conditional_increment_nonnegative": min_increment >= -1e-7,
        "nested_channel_monotonicity": monotone,
    }
    if not all(gates.values()):
        raise ArithmeticError(f"Significant mathematical check failed; no result files written: {gates}")

    with (HERE / "pairwise_separation.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    with (HERE / "nearest_competitor.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(df_summary[0]))
        writer.writeheader(); writer.writerows(df_summary)

    metrics = {
        "design_frozen_before_calculation": {
            "horizons_reports": list(HORIZONS), "horizons_seconds_at_30_fps": [h / 30 for h in HORIZONS],
            "load_amplitude": LOAD_AMPLITUDE, "line_event": "fixed full opening operator",
            "severity_treatment": "fixed means conditional on these amplitudes/operators; no nuisance profiling",
            "sources": [a["id"] for a in assets], "directed_pair_count_per_horizon": len(pair_meta),
            "channel_contracts": {k: len(v) for k, v in CHANNELS.items()},
            "noise": "common quiet/null nominal Gaussian covariance; raw reports; full cross-channel and temporal covariance",
            "scope": "deterministic mean separation only; no detector score, calibration, or performance claim",
        },
        "source": {
            "candidate": "PAPER_RECOVERY_C03 CAL only; read-only bank copy; no C03 code executed",
            "observation_id": "C03_a1adb9f9adcf_nominal", "nominal_only": True,
            "prefix_reports": 300, "truth_read": False, "test_observations_read": False,
            "bank_sha256": ready["bank_sha256"],
            "snapshot_sha256": sha256(SNAPSHOT),
            "assets_sha256": sha256(ASSETS_PATH),
            "F01_terminal_mapping_sha256": sha256(F01_MAP),
            "R11_terminal_mapping_sha256": sha256(R11_MAP),
            "F01_R11_terminal_mapping_byte_identical": True,
            "source_ready_record_sha256": sha256(READY_PATH),
            "diagnostic_script_sha256": sha256(Path(__file__).resolve()),
            "measurement_layout_source_sha256": "87157dc0c6d0dd92b5486643a6211d3c0a9796e112948a26a93337d25d459dba",
            "snapshot_arrays_sha256": {k: array_hash(v) for k, v in sorted(bank.items())},
        },
        "layout": {
            "fields": [{"field": n, "start": a, "stop": b} for n, a, b in FIELDS],
            "terminal_map_bus5": "5-6, terminal 5; provisional historical alternative",
            "bus5_mapping_row": next(line.strip() for line in F01_MAP.read_text(encoding="utf-8").splitlines()
                                      if line.startswith("5,")),
        },
        "checks": {
            "S_positive_definite_cholesky": s_positive_definite,
            "line_operator_profiled_input_max_abs": line_operator_residual_max,
            "S_inverse_identity_max_absolute_error": covariance_identity_error,
            "raw_covariance_min_diagonal": float(np.diag(gamma).min()),
            "raw_covariance_recursion_vs_explicit_innovation_transform_relative_max_error": covariance_recursion_error,
            "raw_vs_full_null_innovation_quadratic_relative_max_error": max_raw_innov_error,
            "schur_decomposition_max_absolute_error": max_schur_abs_error,
            "schur_decomposition_max_relative_error": max_schur_relative_error,
            "minimum_conditional_increment": min_increment,
            "all_nested_channel_distances_monotone": monotone,
            "gates_passed_before_writing_results": gates,
        },
        "outputs": {
            "pairwise_separation.csv": sha256(HERE / "pairwise_separation.csv"),
            "nearest_competitor.csv": sha256(HERE / "nearest_competitor.csv"),
        },
    }
    (HERE / "diagnostic_summary.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False) + "\n",
                                                   encoding="utf-8")
    print(json.dumps(metrics["checks"], indent=2))


if __name__ == "__main__":
    main()

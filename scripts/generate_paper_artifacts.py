"""Generate every numerical table, macro, and empirical figure in the paper.

The script reads only the frozen, hashed artifacts imported by
``scripts/import_frozen_results.ps1``. It intentionally does not reach into the
research repository during a manuscript build.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import colors as mcolors, patches, ticker
import numpy as np
import pandas as pd
from scipy import stats


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "generated" / "frozen"
FIGURES = ROOT / "figures" / "generated"
TABLES = ROOT / "tables" / "generated"
GENERATED = ROOT / "generated"

BLUE = "#0072B2"
ORANGE = "#D55E00"
GREEN = "#009E73"
PURPLE = "#CC79A7"
SKY = "#56B4E9"
GRAY = "#6B7280"
LIGHT_GRAY = "#B7BDC5"

PMU_BUSES = {2, 5, 6, 10, 19, 22, 29, 39}
BUS_POSITIONS = {
    1: (0, 2.1), 2: (1.1, 2.15), 3: (2.1, 1.85), 4: (3, 1.55),
    5: (4, 1.55), 6: (5, 1.35), 7: (6, 1.45), 8: (6.8, 1.95),
    9: (7.3, 2.65), 10: (5.35, 0.25), 11: (4.55, 0.55),
    12: (3.7, 0.2), 13: (3.25, 0.8), 14: (3, 0.25),
    15: (2.3, -0.25), 16: (1.55, -0.55), 17: (0.85, -0.05),
    18: (1.25, 0.8), 19: (0.75, -1.05), 20: (0.2, -1.65),
    21: (2.15, -1.15), 22: (2.85, -1.55), 23: (3.65, -1.35),
    24: (2.65, -0.85), 25: (-0.15, 1.15), 26: (-0.95, 0.35),
    27: (0.15, 0), 28: (-1.55, 1), 29: (-2.35, 0.35),
    30: (1.35, 2.85), 31: (5.75, 2.05), 32: (6.1, 0),
    33: (0.2, -2.35), 34: (0.95, -2.15), 35: (3.05, -2.35),
    36: (4.35, -2), 37: (-0.85, 1.65), 38: (-2.95, 1.05),
    39: (0, 3.05),
}


def read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA / name)


def read_legacy_summary() -> pd.DataFrame:
    """Read the two-row header exported by the legacy event evaluation."""
    summary = pd.read_csv(DATA / "legacy_replayed_summary.csv", header=[0, 1], index_col=0)
    summary.index.name = "configuration"
    return summary


def setup_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 7.2,
            "axes.labelsize": 7.5,
            "axes.titlesize": 8.2,
            "legend.fontsize": 6.6,
            "xtick.labelsize": 6.8,
            "ytick.labelsize": 6.8,
            "axes.linewidth": 0.7,
            "lines.linewidth": 1.35,
            "lines.markersize": 4.2,
            "figure.dpi": 160,
            "savefig.dpi": 320,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def save_figure(fig: plt.Figure, stem: str) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    pdf_metadata = {"CreationDate": None, "ModDate": None}
    fig.savefig(
        FIGURES / f"{stem}.pdf",
        bbox_inches="tight",
        pad_inches=0.025,
        metadata=pdf_metadata,
    )
    fig.savefig(FIGURES / f"{stem}.png", bbox_inches="tight", pad_inches=0.025)
    plt.close(fig)


def fmt_percent(value: float, digits: int = 4) -> str:
    return f"{value:.{digits}f}\\%"


def write_macros(checks: dict[str, object]) -> None:
    nominal = read_csv("e04a_b0_b1_b2_summary.csv").set_index("method")
    e03 = read_csv("e04a1_e03_vs_e04.csv")
    mismatch = pd.read_parquet(DATA / "e06_standard_per_case.parquet")
    b2 = mismatch[mismatch["method"].eq("B2")].copy()
    nominal_ref = b2.loc[b2["m"].eq(0), "TVE_percent"].median()
    at_max = b2[b2["m"].eq(1.5)].groupby("family")["TVE_percent"].median()
    closure = read_csv("e06e_oracle_closure.csv")
    closure = closure[
        closure["family"].isin(["M1_NETWORK", "M6_OPERATING_POINT", "M7_COUPLED"])
        & closure["m"].gt(0)
        & closure["status"].eq("OK")
    ]
    calibration = read_csv("e04a3_test_calibration.csv").set_index("method")
    discrepancy = read_csv("e04a4_test_metrics.csv").set_index("model")
    adequacy = read_csv("e06_standard_adequacy.csv")
    e06e = read_csv("e06e_summary.csv")
    adaptation = e06e[
        e06e["split"].eq("TEST")
        & e06e["m"].eq(1.5)
        & e06e["family"].isin(["M1_NETWORK", "M6_OPERATING_POINT", "M7_COUPLED"])
    ].copy()
    adaptation["variant"] = np.where(
        adaptation["method"].eq("R0_FROZEN_B2"),
        "R0",
        np.where(
            adaptation["method"].eq("R1_ORACLE_RECENTERED"),
            "R1",
            np.where(adaptation["policy"].eq("ADAPTIVE_RECENTER"), "R2A", "OTHER"),
        ),
    )
    adaptation = adaptation[adaptation["variant"].ne("OTHER")]
    adaptation_medians = adaptation.groupby(["family", "variant"])["TVE_percent"].median().unstack()
    macro_adequacy = adequacy[adequacy["m"].isin([0.5, 1.0, 1.5])].groupby("m")[["AUROC", "AUPRC"]].mean()
    mismatch_coverage = mismatch[mismatch["method"].isin(["B2", "B2-U2"])].groupby("method")["coverage95"].mean()
    paired = read_csv("e04a_paired_comparisons.csv")
    paired_b2_b1 = paired[
        paired["comparison"].eq("B2_KALMAN - B1_SNAPSHOT_WLS")
        & paired["metric"].eq("TVE_fraction")
    ].iloc[0]
    nominal_cases = read_csv("e04a_per_case.csv")
    nominal_pivot = nominal_cases.pivot(index="traj", columns="method", values="TVE_percent")
    b2_win_rate = float(
        (nominal_pivot["B2_KALMAN"] < nominal_pivot["B1_SNAPSHOT_WLS"]).mean()
    )
    e06h_summary = read_csv("e06h_summary.csv").iloc[0]
    e06h_cases = read_csv("e06h_test_per_case.csv")
    e06h_medians = e06h_cases.groupby(["m", "method"])["hidden_V_TVE_percent"].median().unstack()
    e06h_closure = read_csv("e06h_closure.csv").set_index("m")
    e06h_ident = read_csv("e06h_identifiability.csv")
    e06h_uncertainty = read_csv("e06h_uncertainty.csv")
    e06h_nees = e06h_uncertainty.groupby("m")["NEES_like"].median()
    legacy = read_legacy_summary()
    legacy_selected = legacy.loc["hierarchical_448_availability"]
    legacy_gain = read_csv("legacy_paired_intervals_recomputed.csv")
    legacy_gain = legacy_gain[
        legacy_gain["method"].eq("hierarchical_448_availability")
        & legacy_gain["reference"].eq("hierarchical_136")
        & legacy_gain["metric"].eq("physical_row_top1")
    ].iloc[0]
    held_sources = read_csv("legacy_unseen_sources_recomputed.csv")
    raw_transfer = read_csv("legacy_raw0001_transfer_results.csv")
    raw_candidate = raw_transfer[raw_transfer["method"].eq("C_universal_z_candidate")]
    tangent_consistency = read_csv("load_tangent_fd_consistency.csv")
    tangent_stress = read_csv("load_tangent_finite_stress.csv")
    load_v1 = read_csv("load_bayes_v1_summary.csv").iloc[0]
    load_v1_models = read_csv("load_bayes_v1_model_comparison.csv").set_index("model")
    load_v2 = read_csv("load_bayes_v2_summary.csv").iloc[0]
    load_dictionary = read_csv("load_bayes_v2_dictionary_manifest.csv").iloc[0]
    load_whitening = read_csv("load_bayes_v2_whitening.csv").set_index("model")
    load_dev = read_csv("load_bayes_v2_dev_likelihood.csv").set_index("model")
    load_weak_detection = read_csv("load_bayes_v2_weak_detection.csv")
    load_weak_localization = read_csv("load_bayes_v2_weak_localization.csv")
    load_finite_calibration = read_csv("load_bayes_v2_finite_calibration.csv")
    structural_x = e03["functional_residual"].to_numpy()
    structural_y = e03["B2_TVE"].to_numpy()
    observed_rho = float(stats.spearmanr(structural_x, structural_y).statistic)
    rng = np.random.default_rng(20260912)
    bootstrap_rho = []
    for indices in rng.integers(0, len(structural_x), size=(10000, len(structural_x))):
        value = float(stats.spearmanr(structural_x[indices], structural_y[indices]).statistic)
        if np.isfinite(value):
            bootstrap_rho.append(value)
    permuted_rho = np.array(
        [stats.spearmanr(structural_x, rng.permutation(structural_y)).statistic for _ in range(10000)]
    )
    permutation_p = float((1 + np.sum(np.abs(permuted_rho) >= abs(observed_rho))) / (1 + len(permuted_rho)))
    kendall_tau = float(stats.kendalltau(structural_x, structural_y).statistic)

    macros = {
        "ObservedPMUCount": "8",
        "HiddenBusCount": "31",
        "NominalTestCount": str(int(nominal.loc["B2_KALMAN", "n_trajectories"])),
        "BZeroTVE": fmt_percent(nominal.loc["B0_NOMINAL", "TVE_percent"]),
        "BOneTVE": fmt_percent(nominal.loc["B1_SNAPSHOT_WLS", "TVE_percent"], 6),
        "BTwoTVE": fmt_percent(nominal.loc["B2_KALMAN", "TVE_percent"], 6),
        "BTwoRelativeImprovement": f"{100 * (1 - nominal.loc['B2_KALMAN', 'TVE_percent'] / nominal.loc['B1_SNAPSHOT_WLS', 'TVE_percent']):.1f}\\%",
        "BTwoMinusBOnePP": f"{100 * paired_b2_b1['mean_difference']:.6f}",
        "BTwoMinusBOneCILowPP": f"{100 * paired_b2_b1['paired_bootstrap_ci95_low']:.6f}",
        "BTwoMinusBOneCIHighPP": f"{100 * paired_b2_b1['paired_bootstrap_ci95_high']:.6f}",
        "BTwoWinRate": fmt_percent(100 * b2_win_rate, 1),
        "FunctionalSpearman": f"{e03['spearman_B2_TVE_vs_functional_residual'].dropna().iloc[0]:.4f}",
        "FunctionalSpearmanCILow": f"{np.quantile(bootstrap_rho, 0.025):.3f}",
        "FunctionalSpearmanCIHigh": f"{np.quantile(bootstrap_rho, 0.975):.3f}",
        "FunctionalPermutationP": f"{permutation_p:.4f}",
        "FunctionalKendall": f"{kendall_tau:.3f}",
        "MismatchMainCount": str(int((b2.shape[0]))),
        "MismatchRefinementCount": "175",
        "NetworkMismatchRatio": f"{at_max['M1_NETWORK'] / nominal_ref:.2f}",
        "OperatingMismatchRatio": f"{at_max['M6_OPERATING_POINT'] / nominal_ref:.2f}",
        "OnlineClosurePercent": fmt_percent(100 * closure["closure"].median(), 1),
        "UtwoNLL": f"{calibration.loc['U2_RE_IM_BLOCK_TEMPERATURE', 'nll']:.3f}",
        "UtwoCoverageRe": fmt_percent(100 * calibration.loc["U2_RE_IM_BLOCK_TEMPERATURE", "coverage95_re"], 1),
        "UtwoCoverageIm": fmt_percent(100 * calibration.loc["U2_RE_IM_BLOCK_TEMPERATURE", "coverage95_im"], 1),
        "OriginalInnovationACF": f"{discrepancy.loc['D0_B2_ORIGINAL', 'acf1']:.3f}",
        "MeasurementGMInnovationACF": f"{discrepancy.loc['D2_GM_DIAG_R4', 'acf1']:.3f}",
        "MismatchUzeroCoverage": fmt_percent(100 * mismatch_coverage["B2"], 1),
        "MismatchUtwoCoverage": fmt_percent(100 * mismatch_coverage["B2-U2"], 1),
        "AdequacyHalfAUROC": f"{macro_adequacy.loc[0.5, 'AUROC']:.3f}",
        "AdequacyHalfAUPRC": f"{macro_adequacy.loc[0.5, 'AUPRC']:.3f}",
        "AdequacyMaxAUROC": f"{macro_adequacy.loc[1.5, 'AUROC']:.3f}",
        "AdequacyMaxAUPRC": f"{macro_adequacy.loc[1.5, 'AUPRC']:.3f}",
        "NetworkFrozenTVE": fmt_percent(adaptation_medians.loc["M1_NETWORK", "R0"], 6),
        "NetworkOracleTVE": fmt_percent(adaptation_medians.loc["M1_NETWORK", "R1"], 6),
        "NetworkOnlineTVE": fmt_percent(adaptation_medians.loc["M1_NETWORK", "R2A"], 6),
        "OperatingFrozenTVE": fmt_percent(adaptation_medians.loc["M6_OPERATING_POINT", "R0"], 6),
        "OperatingOracleTVE": fmt_percent(adaptation_medians.loc["M6_OPERATING_POINT", "R1"], 6),
        "OperatingOnlineTVE": fmt_percent(adaptation_medians.loc["M6_OPERATING_POINT", "R2A"], 6),
        "CoupledFrozenTVE": fmt_percent(adaptation_medians.loc["M7_COUPLED", "R0"], 6),
        "CoupledOracleTVE": fmt_percent(adaptation_medians.loc["M7_COUPLED", "R1"], 6),
        "CoupledOnlineTVE": fmt_percent(adaptation_medians.loc["M7_COUPLED", "R2A"], 6),
        "EZeroHDevCount": str(int(e06h_summary["dev_cases"])),
        "EZeroHTestCount": str(int(e06h_summary["test_cases"])),
        "EZeroHValidRate": fmt_percent(100 * e06h_summary["test_valid_rate"], 1),
        "EZeroHClosureOverall": fmt_percent(100 * e06h_summary["closure_median"], 1),
        "EZeroHRuntimeMedian": f"{e06h_summary['runtime_median_ms']:.1f}",
        "EZeroHRuntimePNinetyFive": f"{e06h_summary['runtime_p95_ms']:.1f}",
        "EZeroHRank": str(int(e06h_summary["ident_rank_median"])),
        "EZeroHDimension": str(int(e06h_ident["parameter_dimension"].median())),
        "EZeroHNullity": str(int(e06h_summary["ident_nullspace_median"])),
        "EZeroHFunctionalResidual": f"{e06h_ident['functional_hidden_voltage_residual'].median():.4f}",
        "EZeroHFrozenHalf": fmt_percent(e06h_medians.loc[0.5, "S0-NOM"], 5),
        "EZeroHFrozenOne": fmt_percent(e06h_medians.loc[1.0, "S0-NOM"], 5),
        "EZeroHFrozenMax": fmt_percent(e06h_medians.loc[1.5, "S0-NOM"], 5),
        "EZeroHCorrectedHalf": fmt_percent(e06h_medians.loc[0.5, "S0-MAP-CORRECTED"], 5),
        "EZeroHCorrectedOne": fmt_percent(e06h_medians.loc[1.0, "S0-MAP-CORRECTED"], 5),
        "EZeroHCorrectedMax": fmt_percent(e06h_medians.loc[1.5, "S0-MAP-CORRECTED"], 5),
        "EZeroHClosureHalf": fmt_percent(100 * e06h_closure.loc[0.5, "closure_median"], 1),
        "EZeroHClosureOne": fmt_percent(100 * e06h_closure.loc[1.0, "closure_median"], 1),
        "EZeroHClosureMax": fmt_percent(100 * e06h_closure.loc[1.5, "closure_median"], 1),
        "EZeroHNEESHalf": f"{e06h_nees.loc[0.5]:.1f}",
        "EZeroHNEESOne": f"{e06h_nees.loc[1.0]:.1f}",
        "EZeroHNEESMax": f"{e06h_nees.loc[1.5]:.1f}",
        "LegacyEventTrajectories": "690",
        "LegacyEventDetectionFOne": f"{legacy_selected[('detection_f1', 'mean')]:.3f}",
        "LegacyEventMacroFOne": f"{legacy_selected[('event_macro_f1_all_labels', 'mean')]:.3f}",
        "LegacyPhysicalTopOne": f"{legacy_selected[('physical_top1', 'mean')]:.3f}",
        "LegacyPhysicalTopThree": f"{legacy_selected[('physical_top3', 'mean')]:.3f}",
        "LegacyIntegrityTopOne": f"{legacy_selected[('integrity_top1', 'mean')]:.3f}",
        "LegacyFalseAlarmsPerMinute": f"{legacy_selected[('false_alarm_episodes_per_min', 'mean')]:.2f}",
        "LegacyPhysicalGainPP": f"{100 * legacy_gain['estimate']:.1f}",
        "LegacyPhysicalGainCILowPP": f"{100 * legacy_gain['lower']:.1f}",
        "LegacyPhysicalGainCIHighPP": f"{100 * legacy_gain['upper']:.1f}",
        "HeldSourceCorrect": str(int(held_sources["correct"].sum())),
        "HeldSourceDecisions": str(int(len(held_sources))),
        "HeldSourceCases": str(int(held_sources["scenario_id"].nunique())),
        "HeldSourceRate": fmt_percent(100 * held_sources["correct"].mean(), 1),
        "RawCandidateEventEpisodes": f"{raw_candidate['event_episode_correct'].mean():.1f}",
        "RawCandidatePhysicalEpisodes": f"{raw_candidate['physical_episode_correct'].mean():.1f}",
        "LoadSourceCount": str(int(load_dictionary["n_sources"])),
        "LoadTangentMaxRelError": fmt_percent(100 * tangent_consistency[["central_vs_plus_relerr", "central_vs_minus_relerr"]].to_numpy().max(), 3),
        "LoadTangentMinCosine": f"{tangent_consistency['plus_minus_cosine'].min():.6f}",
        "LoadTangentMedianStressError": fmt_percent(100 * tangent_stress["relative_trajectory_error"].median(), 2),
        "LoadTangentMaxStressError": fmt_percent(100 * tangent_stress["relative_trajectory_error"].max(), 2),
        "LoadVOneEventCases": str(int(load_v1["event_cases"])),
        "LoadVOneNoEventCases": str(int(load_v1["no_event_test_cases"])),
        "LoadVOneFPR": fmt_percent(100 * load_v1_models.loc["W2_SEPARABLE_AR1", "event_FPR_at_.5"], 3),
        "LoadVOneTopOne": fmt_percent(100 * load_v1_models.loc["W2_SEPARABLE_AR1", "source_top1"], 1),
        "LoadWeakEventCases": str(int(load_v2["weak_test_events"])),
        "LoadWeakNoEventCases": str(int(load_v2["weak_test_no_event"])),
        "LoadFiniteEventCases": str(int(load_v2["finite_test_events"])),
        "LoadTruncationSlope": f"{load_v2['truncation_slope']:.2f}",
        "LoadTruncationCILow": f"{load_v2['truncation_ci95_low']:.2f}",
        "LoadTruncationCIHigh": f"{load_v2['truncation_ci95_high']:.2f}",
        "LoadWTwoNIS": f"{load_whitening.loc['W2_SEPARABLE_AR1', 'NIS_per_frame']:.3f}",
        "LoadWTwoACFOne": f"{load_whitening.loc['W2_SEPARABLE_AR1', 'ACF_lag_1']:.4f}",
        "LoadWTwoLjungP": f"{load_whitening.loc['W2_SEPARABLE_AR1', 'Ljung_Box_pvalue']:.3f}",
        "LoadLTwoDevCoverage": fmt_percent(100 * load_dev.loc["L2", "DEV_coverage95"], 1),
        "LoadEVIRho": f"{load_v2['evi_a90_spearman']:.3f}",
        "LoadProjectedFisherRho": f"{load_v2['J_confusion_spearman']:.3f}",
        "LoadWeakMinAUROC": f"{load_weak_detection['AUROC'].min():.3f}",
        "LoadWeakMinTopOne": fmt_percent(100 * load_weak_localization["top1"].min(), 1),
        "LoadFiniteCoverageMin": fmt_percent(100 * load_finite_calibration["coverage95"].min(), 1),
        "LoadFiniteCoverageMax": fmt_percent(100 * load_finite_calibration["coverage95"].max(), 1),
    }
    lines = [f"\\newcommand{{\\{name}}}{{{value}}}" for name, value in macros.items()]
    (GENERATED / "results_macros.tex").write_text("\n".join(lines) + "\n", encoding="ascii")

    checks.update(
        {
            "nominal_test_trajectories": int(nominal.loc["B2_KALMAN", "n_trajectories"]),
            "e06_main_b2_cases": int(b2.shape[0]),
            "e06_main_unique_physical_cases": int(b2["case_id"].nunique()),
            "e06_nominal_reference_tve_percent": float(nominal_ref),
            "e06e_median_oracle_closure": float(closure["closure"].median()),
            "e06h_test_cases": int(e06h_summary["test_cases"]),
            "e06h_test_valid_rate": float(e06h_summary["test_valid_rate"]),
            "e06h_median_closure": float(e06h_summary["closure_median"]),
            "e06h_nuisance_rank": int(e06h_summary["ident_rank_median"]),
            "e06h_nuisance_dimension": int(e06h_ident["parameter_dimension"].median()),
            "legacy_event_trajectories": 690,
            "legacy_held_source_decisions": int(len(held_sources)),
            "legacy_held_source_correct": int(held_sources["correct"].sum()),
            "load_tangent_sources": int(len(tangent_consistency)),
            "load_tangent_max_rel_error": float(tangent_consistency[["central_vs_plus_relerr", "central_vs_minus_relerr"]].to_numpy().max()),
            "load_v2_cal_normal": int(load_v2["cal_normal"]),
            "load_v2_dev_normal": int(load_v2["dev_normal"]),
            "load_v2_dev_event_cases": int(load_v2["dev_event_cases"]),
            "load_v2_weak_event_cases": int(load_v2["weak_test_events"]),
            "load_v2_weak_no_event_cases": int(load_v2["weak_test_no_event"]),
            "load_v2_finite_event_cases": int(load_v2["finite_test_events"]),
            "load_v2_dictionary_hash": str(load_v2["dictionary_hash"]),
            "load_v2_selected_whitening": str(load_v2["selected_whitening"]),
            "load_v2_selected_likelihood": str(load_v2["selected_likelihood"]),
            "load_v2_truncation_slope": float(load_v2["truncation_slope"]),
            "load_v2_evi_a90_spearman": float(load_v2["evi_a90_spearman"]),
            "load_v2_projected_fisher_confusion_spearman": float(load_v2["J_confusion_spearman"]),
            "load_v2_finite_coverage95_min": float(load_finite_calibration["coverage95"].min()),
            "load_v2_finite_coverage95_max": float(load_finite_calibration["coverage95"].max()),
        }
    )


def _draw_network(
    ax: plt.Axes,
    branches: pd.DataFrame,
    residuals: dict[int, float] | None = None,
    show_legend: bool = False,
) -> object | None:
    for edge in branches.itertuples():
        p = BUS_POSITIONS[int(edge.from_bus)]
        q = BUS_POSITIONS[int(edge.to_bus)]
        ax.plot([p[0], q[0]], [p[1], q[1]], color="#A5ABB3", linewidth=0.45, zorder=0)
    scalar_map = None
    if residuals:
        norm = mcolors.Normalize(vmin=min(residuals.values()), vmax=max(residuals.values()))
        scalar_map = plt.cm.ScalarMappable(norm=norm, cmap="cividis")
    for bus, (x, y) in BUS_POSITIONS.items():
        marker = "s" if bus >= 30 else "o"
        if bus in PMU_BUSES:
            face, edge, text_color = BLUE, "#003B5C", "white"
        elif residuals:
            face = scalar_map.to_rgba(residuals[bus])
            luminance = 0.2126 * face[0] + 0.7152 * face[1] + 0.0722 * face[2]
            edge, text_color = "#4B5563", "white" if luminance < 0.46 else "#111827"
        else:
            face, edge, text_color = "white", "#5E6670", "#25313C"
        ax.scatter(x, y, marker=marker, s=48, facecolor=face, edgecolor=edge, linewidth=0.65, zorder=2)
        ax.text(x, y, str(bus), ha="center", va="center", fontsize=4.8, color=text_color, zorder=3)
    if show_legend:
        ax.scatter([], [], s=28, facecolor=BLUE, edgecolor="#003B5C", label="PMU bus")
        ax.scatter([], [], s=28, facecolor="white", edgecolor="#5E6670", label="hidden bus")
        ax.scatter([], [], marker="s", s=28, facecolor="white", edgecolor="#5E6670", label="generator bus")
        ax.legend(frameon=False, fontsize=5.5, loc="lower right", handletextpad=0.3, labelspacing=0.25)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.margins(0.03)
    return scalar_map


def figure_system_architecture() -> None:
    branches = read_csv("branches_physical.csv")
    e03 = read_csv("e04a1_e03_vs_e04.csv")
    residuals = {int(row.hidden_bus): float(row.functional_residual) for row in e03.itertuples()}

    fig, axes = plt.subplots(
        1, 3, figsize=(7.16, 2.48), gridspec_kw={"width_ratios": [1.15, 0.92, 1.15]}
    )
    _draw_network(axes[0], branches, show_legend=True)
    axes[0].set_title("(a) IEEE 39-bus sensing geometry", loc="left")

    ax = axes[1]
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    def box(x: float, y: float, w: float, h: float, label: str, color: str) -> None:
        ax.add_patch(
            patches.FancyBboxPatch(
                (x, y), w, h, boxstyle="round,pad=0.02", facecolor=color,
                edgecolor="#34495E", linewidth=0.7
            )
        )
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=6.2)

    def arrow(start: tuple[float, float], end: tuple[float, float], color: str = "#34495E") -> None:
        ax.annotate("", xy=end, xytext=start, arrowprops={"arrowstyle": "->", "lw": 0.8, "color": color})

    box(0.08, 0.78, 0.84, 0.13, "8 PMUs: voltage +\nterminal-current phasors", "#E6F2FA")
    box(0.08, 0.54, 0.84, 0.13, "Audited local physics\n" + r"$A_d, C, L_{\mathcal{U}}$", "#E7F6F1")
    box(0.08, 0.30, 0.84, 0.13, "Functional reconstruction\n" + r"$\hat V_{\mathcal{U}}$ at 31 buses", "#E6F2FA")
    box(0.08, 0.06, 0.38, 0.12, "$r_F$: structural\nweakness", "#F1F3F5")
    box(0.54, 0.06, 0.38, 0.12, "$a_k$: model\nadequacy", "#FFF0E6")
    arrow((0.50, 0.78), (0.50, 0.67))
    arrow((0.50, 0.54), (0.50, 0.43))
    arrow((0.33, 0.30), (0.27, 0.18))
    arrow((0.67, 0.30), (0.73, 0.18), ORANGE)
    ax.set_title("(b) Target-specific reconstruction", loc="left")

    scalar_map = _draw_network(axes[2], branches, residuals=residuals)
    axes[2].set_title("(c) Preregistered functional residual", loc="left")
    colorbar = fig.colorbar(scalar_map, ax=axes[2], fraction=0.045, pad=0.01)
    colorbar.set_label("$r_{F,i}(180)$", fontsize=6.2)
    colorbar.ax.tick_params(labelsize=5.5, length=2)
    fig.tight_layout(w_pad=0.8)
    save_figure(fig, "system_architecture")


def figure_observability_horizon() -> None:
    audit = read_csv("pd_observability_horizons.csv")
    horizon = audit["horizon"].to_numpy()

    fig, axes = plt.subplots(1, 2, figsize=(3.50, 1.82), gridspec_kw={"width_ratios": [0.78, 1.22]})
    ax = axes[0]
    ax.plot(horizon, audit["rank"], marker="o", color=BLUE)
    ax.axhline(114, color=GRAY, linestyle="--", linewidth=0.8, label="state dimension")
    ax.set_xlabel("Horizon $N$")
    ax.set_ylabel("Gramian pseudo-rank")
    ax.set_title("(a) Threshold sensitivity", loc="left")
    ax.set_ylim(0, 122)
    ax.grid(alpha=0.2, linewidth=0.5)

    ax = axes[1]
    ax.semilogy(
        horizon,
        audit["functional_output_residual"],
        marker="o",
        color=ORANGE,
        label="functional residual",
    )
    ax.semilogy(
        horizon,
        audit["noise_information_bound_sigma1e3"],
        marker="s",
        color=GREEN,
        label="noise bound",
    )
    ax.set_xlabel("Horizon $N$")
    ax.set_ylabel("Frozen diagnostic value")
    ax.set_title("(b) Target residual and noise", loc="left")
    ax.grid(which="both", alpha=0.2, linewidth=0.5)
    ax.legend(frameon=False, fontsize=5.4, loc="best")
    fig.tight_layout(w_pad=0.7)
    save_figure(fig, "observability_horizon")


def figure_nominal() -> None:
    e03 = read_csv("e04a1_e03_vs_e04.csv")
    per_case = read_csv("e04a_per_case.csv")
    paired = read_csv("e04a_paired_comparisons.csv")
    methods = ["B0_NOMINAL", "B1_SNAPSHOT_WLS", "B2_KALMAN"]
    labels = ["B0\nEquilibrium", "B1\nLMMSE", "B2\nKalman"]
    colors = [LIGHT_GRAY, SKY, BLUE]

    fig, axes = plt.subplots(1, 3, figsize=(7.16, 2.45), gridspec_kw={"width_ratios": [0.88, 1.05, 0.92]})
    ax = axes[0]
    groups = [per_case.loc[per_case["method"].eq(method), "TVE_percent"].to_numpy() for method in methods]
    bp = ax.boxplot(groups, positions=np.arange(3), widths=0.52, patch_artist=True, showfliers=False)
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_edgecolor("#243244")
        patch.set_linewidth(0.6)
    for element in ("whiskers", "caps", "medians"):
        for artist in bp[element]:
            artist.set_color("#243244")
            artist.set_linewidth(0.65)
    rng = np.random.default_rng(20260912)
    for x0, values, color in zip(range(3), groups, colors):
        jitter = rng.normal(0, 0.045, size=len(values))
        ax.scatter(x0 + jitter, values, s=4.5, color=color, edgecolor="none", alpha=0.38, zorder=1)
    ax.set_xticks(range(3), labels)
    ax.set_yscale("log")
    ax.set_ylabel("Trajectory hidden-voltage HVRE (%)")
    ax.set_title("(a) Frozen nominal TEST distributions", loc="left")
    ax.grid(axis="y", which="both", alpha=0.2, linewidth=0.5)

    ax = axes[1]
    x = e03["functional_residual"].to_numpy()
    y = 100 * e03["B2_TVE"].to_numpy()
    ax.scatter(x, y, s=20, facecolors="white", edgecolors=BLUE, linewidths=0.9, zorder=3)
    weak = e03.nlargest(5, "B2_TVE")
    for _, row in weak.iterrows():
        ax.annotate(str(int(row["hidden_bus"])), (row["functional_residual"], 100 * row["B2_TVE"]), xytext=(2, 2), textcoords="offset points", fontsize=5.8)
    rho = e03["spearman_B2_TVE_vs_functional_residual"].dropna().iloc[0]
    ax.text(0.03, 0.94, rf"Spearman $\rho={rho:.4f}$", transform=ax.transAxes, va="top")
    ax.set_xlabel("Functional residual $r_{F,i}$")
    ax.set_ylabel("Per-bus Kalman HVRE (%)")
    ax.set_yscale("log")
    ax.set_title("(b) Structure predicts difficulty", loc="left")
    ax.grid(alpha=0.2, linewidth=0.5)

    ax = axes[2]
    pivot = per_case.pivot(index="traj", columns="method", values="TVE_percent")
    delta = np.sort((pivot["B2_KALMAN"] - pivot["B1_SNAPSHOT_WLS"]).to_numpy())
    comparison = paired[
        paired["comparison"].eq("B2_KALMAN - B1_SNAPSHOT_WLS")
        & paired["metric"].eq("TVE_fraction")
    ].iloc[0]
    ax.plot(np.arange(1, len(delta) + 1), delta, color=BLUE, linewidth=1.0)
    ax.axhline(0, color="#243244", linewidth=0.7, linestyle="--")
    ax.fill_between(np.arange(1, len(delta) + 1), delta, 0, where=delta <= 0, color=GREEN, alpha=0.18)
    mean_pp = 100 * comparison["mean_difference"]
    lo_pp = 100 * comparison["paired_bootstrap_ci95_low"]
    hi_pp = 100 * comparison["paired_bootstrap_ci95_high"]
    wins = 100 * np.mean(delta < 0)
    ax.text(0.03, 0.97, f"mean {mean_pp:.6f} pp\n95% CI [{lo_pp:.6f}, {hi_pp:.6f}]\nB2 wins {wins:.1f}%", transform=ax.transAxes, va="top", fontsize=5.7)
    ax.set_xlabel("Trajectory rank")
    ax.set_ylabel("B2 - B1 HVRE (percentage points)")
    ax.set_title("(c) Paired temporal contribution", loc="left")
    ax.grid(alpha=0.2, linewidth=0.5)
    fig.tight_layout(w_pad=0.9)
    save_figure(fig, "nominal_reconstruction")


def figure_temporal_uncertainty() -> None:
    lag = read_csv("e04a_b3_summary.csv")
    calibration = read_csv("e04a3_test_calibration.csv").set_index("method")
    d4 = read_csv("e04a4_test_metrics.csv").set_index("model")
    d5 = read_csv("e04a5_test_metrics.csv").set_index("model")

    fig, axes = plt.subplots(1, 3, figsize=(7.16, 2.35))
    ax = axes[0]
    ax.plot(lag["lag_seconds"], lag["TVE_percent"], marker="o", color=BLUE)
    ax.axhline(lag.iloc[0]["TVE_percent"], color=GRAY, linestyle="--", linewidth=0.9, label="lag 0")
    ax.set_xlabel("Fixed lag (s)")
    ax.set_ylabel("Hidden-voltage HVRE (%)")
    ax.set_title("(a) Smoothing adds no HVRE benefit")
    ax.ticklabel_format(axis="y", style="plain", useOffset=False)
    ax.grid(alpha=0.2, linewidth=0.5)

    ax = axes[1]
    nominal_levels = np.array([0.50, 0.90, 0.95])
    u0 = np.array(
        [
            calibration.loc["U0_ORIGINAL", "coverage50_re"],
            calibration.loc["U0_ORIGINAL", "coverage90_re"],
            calibration.loc["U0_ORIGINAL", "coverage95_re"],
        ]
    )
    u2_re = np.array(
        [
            calibration.loc["U2_RE_IM_BLOCK_TEMPERATURE", "coverage50_re"],
            calibration.loc["U2_RE_IM_BLOCK_TEMPERATURE", "coverage90_re"],
            calibration.loc["U2_RE_IM_BLOCK_TEMPERATURE", "coverage95_re"],
        ]
    )
    u2_im = np.array(
        [
            calibration.loc["U2_RE_IM_BLOCK_TEMPERATURE", "coverage50_im"],
            calibration.loc["U2_RE_IM_BLOCK_TEMPERATURE", "coverage90_im"],
            calibration.loc["U2_RE_IM_BLOCK_TEMPERATURE", "coverage95_im"],
        ]
    )
    ax.plot(nominal_levels, nominal_levels, color=GRAY, linestyle="--", label="ideal")
    ax.plot(nominal_levels, u0, marker="s", color=LIGHT_GRAY, markeredgecolor="#243244", label="U0")
    ax.plot(nominal_levels, u2_re, marker="o", color=BLUE, label="U2 Re")
    ax.plot(nominal_levels, u2_im, marker="^", color=ORANGE, label="U2 Im")
    ax.set_xlabel("Nominal coverage")
    ax.set_ylabel("Empirical coverage")
    ax.set_xlim(0.46, 0.98)
    ax.set_ylim(0.46, 1.02)
    ax.set_title("(b) Independent nominal calibration")
    ax.legend(frameon=False, ncol=2, loc="lower right")
    ax.grid(alpha=0.2, linewidth=0.5)

    ax = axes[2]
    lags = np.array([1, 2, 3, 5, 10])
    ax.plot(lags, [d5.loc["D0_B2_ORIGINAL", f"acf{i}"] for i in lags], marker="o", color=BLUE, label="B2")
    ax.plot(lags, [d4.loc["D2_GM_DIAG_R4", f"acf{i}"] for i in lags], marker="s", color=ORANGE, label="meas. GM r4")
    ax.plot(lags, [d5.loc["D2-P_GM_PROCESS_R1", f"acf{i}"] for i in lags], marker="^", color=GREEN, label="process GM r1")
    ax.axhline(0, color=GRAY, linewidth=0.7)
    ax.set_xlabel("Innovation lag (frames)")
    ax.set_ylabel("Autocorrelation")
    ax.set_xticks(lags)
    ax.set_title("(c) Residuals remain colored")
    ax.legend(frameon=False)
    ax.grid(alpha=0.2, linewidth=0.5)
    fig.tight_layout(w_pad=1.15)
    save_figure(fig, "temporal_uncertainty")


def figure_mismatch() -> None:
    per_case = pd.read_parquet(DATA / "e06_standard_per_case.parquet")
    b2 = per_case[per_case["method"].eq("B2")].copy()
    b2_u2 = per_case[per_case["method"].eq("B2-U2")].copy()
    adequacy = read_csv("e06_standard_adequacy.csv")
    ref = b2.loc[b2["m"].eq(0), "TVE_percent"].median()
    grouped = b2.groupby(["family", "m"])["TVE_percent"].median().unstack()
    coverage = b2_u2.groupby(["family", "m"])["coverage95"].mean().unstack()
    families = ["M1_NETWORK", "M2_MACHINE", "M3_GOVERNOR", "M4_AVR", "M5_LOAD_MODEL", "M6_OPERATING_POINT", "M7_COUPLED"]
    labels = ["M1 network", "M2 machine", "M3 governor", "M4 AVR", "M5 load", "M6 op. point", "M7 coupled"]
    scales = np.array([0.25, 0.5, 0.75, 1.0, 1.25, 1.5])
    ratio = grouped.loc[families, scales].to_numpy() / ref
    coverage_matrix = coverage.loc[families, scales].to_numpy()

    fig, axes = plt.subplots(1, 3, figsize=(7.16, 2.92), gridspec_kw={"width_ratios": [1.12, 1.05, 0.88]})
    ax = axes[0]
    log_ratio = np.log10(ratio)
    norm = mcolors.TwoSlopeNorm(vmin=min(-0.05, float(np.nanmin(log_ratio))), vcenter=0, vmax=float(np.nanmax(log_ratio)))
    im = ax.imshow(log_ratio, aspect="auto", cmap="PuOr", norm=norm)
    for i in range(len(families)):
        for j in range(len(scales)):
            color = "white" if abs(log_ratio[i, j]) > 0.58 else "#1F2937"
            ax.text(j, i, f"{ratio[i, j]:.2f}x", ha="center", va="center", fontsize=4.4, color=color)
    ax.set_xticks(range(len(scales)), [f"{m:g}" for m in scales])
    ax.set_yticks(range(len(families)), labels)
    ax.set_xlabel("Mismatch scale $m$")
    ax.set_title("(a) Median HVRE / nominal", loc="left")
    cbar = fig.colorbar(im, ax=ax, fraction=0.045, pad=0.02)
    cbar.set_label(r"$\log_{10}$ HVRE ratio", fontsize=5.8)
    cbar.ax.tick_params(labelsize=5.2, length=2)

    ax = axes[1]
    im = ax.imshow(coverage_matrix, aspect="auto", cmap="cividis", vmin=0, vmax=1)
    for i in range(len(families)):
        for j in range(len(scales)):
            color = "white" if coverage_matrix[i, j] < 0.45 else "#111827"
            ax.text(j, i, f"{100 * coverage_matrix[i, j]:.0f}", ha="center", va="center", fontsize=4.4, color=color)
    ax.set_xticks(range(len(scales)), [f"{m:g}" for m in scales])
    ax.set_yticks(range(len(families)), [])
    ax.set_xlabel("Mismatch scale $m$")
    ax.set_title("(b) Nominal U2 coverage (%)", loc="left")
    cbar = fig.colorbar(im, ax=ax, fraction=0.045, pad=0.02)
    cbar.set_label("95% marginal coverage", fontsize=5.8)
    cbar.ax.tick_params(labelsize=5.2, length=2)

    ax = axes[2]
    eval_scales = [0.5, 1.0, 1.5]
    auroc = [adequacy.loc[adequacy["m"].eq(scale), "AUROC"].mean(skipna=True) for scale in eval_scales]
    auprc = [adequacy.loc[adequacy["m"].eq(scale), "AUPRC"].mean(skipna=True) for scale in eval_scales]
    ax.plot(eval_scales, auroc, marker="o", color=BLUE, label="macro AUROC")
    ax.plot(eval_scales, auprc, marker="s", color=PURPLE, label="macro AUPRC")
    ax.set_ylim(0.70, 0.98)
    ax.set_xticks(eval_scales)
    ax.set_xlabel("Mismatch scale $m$")
    ax.set_ylabel("Adequacy discrimination")
    ax.set_title("(c) Observed-innovation gate", loc="left")
    ax.legend(frameon=False, loc="lower left", fontsize=5.7)
    ax.grid(alpha=0.2, linewidth=0.5)
    fig.tight_layout(w_pad=0.65)
    save_figure(fig, "physical_mismatch")


def figure_adequacy_adaptation() -> None:
    cases = read_csv("e06h_test_per_case.csv")
    closure = read_csv("e06h_closure.csv").set_index("m")
    uncertainty = read_csv("e06h_uncertainty.csv")
    scales = np.array([0.5, 1.0, 1.5])
    med = cases.groupby(["m", "method"])["hidden_V_TVE_percent"].median().unstack()
    nees = uncertainty.groupby("m")["NEES_like"].median()

    fig, axes = plt.subplots(1, 3, figsize=(7.16, 2.48), gridspec_kw={"width_ratios": [1.0, 0.92, 0.92]})
    ax = axes[0]
    ax.plot(scales, med.loc[scales, "S0-NOM"], marker="o", color=GRAY, label="frozen nominal center")
    ax.plot(scales, med.loc[scales, "S0-MAP-CORRECTED"], marker="s", color=GREEN, label="physical recentering")
    ax.set_yscale("log")
    ax.set_xticks(scales)
    ax.set_xlabel("Operating-point mismatch scale $m$")
    ax.set_ylabel("Median TEST HVRE (%)")
    ax.set_title("(a) Physical recentering", loc="left")
    ax.legend(frameon=False, fontsize=5.7)
    ax.grid(which="both", alpha=0.2, linewidth=0.5)

    ax = axes[1]
    center = closure.loc[scales, "closure_median"].to_numpy()
    low = center - closure.loc[scales, "closure_ci95_low"].to_numpy()
    high = closure.loc[scales, "closure_ci95_high"].to_numpy() - center
    ax.errorbar(scales, 100 * center, yerr=100 * np.vstack([low, high]), marker="o", color=BLUE, capsize=2.5)
    ax.axhline(100, color="#243244", linestyle="--", linewidth=0.7, label="oracle center")
    ax.set_ylim(90, 101)
    ax.set_xticks(scales)
    ax.set_xlabel("Operating-point mismatch scale $m$")
    ax.set_ylabel("Oracle-gap closure (%)")
    ax.set_title("(b) Paired bootstrap closure", loc="left")
    ax.legend(frameon=False, fontsize=5.7, loc="lower right")
    ax.grid(alpha=0.2, linewidth=0.5)

    ax = axes[2]
    points = ax.scatter(
        med.loc[scales, "S0-MAP-CORRECTED"], nees.loc[scales],
        c=scales, cmap="cividis", s=35, edgecolor="#243244", linewidth=0.5
    )
    annotation_style = {
        0.5: {"xytext": (3, 3), "ha": "left", "va": "bottom"},
        1.0: {"xytext": (-3, 4), "ha": "right", "va": "bottom"},
        1.5: {"xytext": (-3, -4), "ha": "right", "va": "top"},
    }
    for scale in scales:
        style = annotation_style[float(scale)]
        ax.annotate(
            f"$m={scale:g}$",
            (med.loc[scale, "S0-MAP-CORRECTED"], nees.loc[scale]),
            textcoords="offset points",
            fontsize=5.3,
            **style,
        )
    ax.axhline(1, color="#243244", linestyle="--", linewidth=0.7, label="NEES reference")
    ax.set_yscale("log")
    ax.set_xlabel("Corrected median HVRE (%)")
    ax.set_ylabel("Median NEES-like statistic")
    ax.set_title("(c) Accurate mean, partial uncertainty", loc="left")
    ax.legend(frameon=False, fontsize=5.5, loc="lower right")
    ax.grid(which="both", alpha=0.2, linewidth=0.5)
    fig.tight_layout(w_pad=0.8)
    save_figure(fig, "adequacy_adaptation")


def figure_event_inference_evidence() -> None:
    """Show the load-event evidence and retain the audited event-signature asset."""
    source_pdf = DATA / "legacy_event_traces.pdf"
    source_png = DATA / "legacy_event_traces.png"
    if not source_pdf.exists() or not source_png.exists():
        raise FileNotFoundError("Legacy event-trace artifacts were not imported")
    FIGURES.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_pdf, FIGURES / "event_signatures.pdf")
    shutil.copyfile(source_png, FIGURES / "event_signatures.png")

    truncation = read_csv("load_bayes_v2_truncation_dev.csv")
    truncation_order = read_csv("load_bayes_v2_truncation_order.csv").iloc[0]
    whitening = read_csv("load_bayes_v2_whitening.csv")
    detection = read_csv("load_bayes_v2_weak_detection.csv")
    localization = read_csv("load_bayes_v2_weak_localization.csv")
    detectability = read_csv("load_bayes_v2_detectability.csv")
    predictive = read_csv("load_bayes_v2_predictive_tests.csv").set_index("metric")["value"]
    finite = read_csv("load_bayes_v2_finite_calibration.csv")

    fig, axes = plt.subplots(2, 3, figsize=(7.16, 4.75))

    ax = axes[0, 0]
    truncation = truncation.assign(abs_amplitude=truncation["amplitude"].abs())
    curve = truncation.groupby("abs_amplitude")["error1_norm"].median().sort_index()
    ax.loglog(100 * curve.index, curve.values, marker="o", color=BLUE)
    ax.set_xticks([0.75, 1.5, 3.5, 6.0], ["0.75", "1.5", "3.5", "6"])
    ax.xaxis.set_minor_formatter(ticker.NullFormatter())
    ax.set_xlabel(r"Load-change magnitude $|a|$ (\%)")
    ax.set_ylabel(r"Median $\|r-aD\|_2$")
    ax.set_title("(a) Local truncation order", loc="left")
    ax.text(0.05, 0.92, rf"slope $p={truncation_order['slope_p']:.2f}$", transform=ax.transAxes, va="top")
    ax.grid(which="both", alpha=0.2, linewidth=0.5)

    ax = axes[0, 1]
    labels = ["W0\nidentity", "W1\nchannel", "W2\nchannel + AR(1)"]
    x = np.arange(3)
    ax.plot(x, whitening["NIS_per_frame"], marker="o", color=BLUE, label="NIS/frame")
    ax.plot(x, whitening["ACF_lag_1"].abs(), marker="s", color=ORANGE, label=r"$|$ACF(1)$|$")
    ax.set_yscale("log")
    ax.set_xticks(x, labels)
    ax.set_ylim(1e-8, 2)
    ax.set_title("(b) Normal-data whitening", loc="left")
    ax.legend(frameon=False, fontsize=5.8, loc="lower right")
    ax.grid(which="both", alpha=0.2, linewidth=0.5)

    def pool_signs(frame: pd.DataFrame) -> pd.DataFrame:
        pooled = frame.assign(abs_amplitude=frame["amplitude"].abs()).groupby("abs_amplitude").mean(numeric_only=True)
        return pooled.sort_index()

    det = pool_signs(detection)
    loc = pool_signs(localization)
    magnitude_percent = 100 * det.index.to_numpy()

    ax = axes[0, 2]
    ax.semilogx(magnitude_percent, det["AUROC"], marker="o", color=BLUE, label="AUROC")
    ax.semilogx(magnitude_percent, det["FNR"], marker="s", color=ORANGE, label="FNR at 0.5")
    ax.set_ylim(-0.03, 1.03)
    ax.set_xlabel(r"Load-change magnitude $|a|$ (\%)")
    ax.set_title("(c) Weak-event detection", loc="left")
    ax.legend(frameon=False, fontsize=5.8)
    ax.grid(which="both", alpha=0.2, linewidth=0.5)

    ax = axes[1, 0]
    ax.semilogx(magnitude_percent, loc["top1"], marker="o", color=GREEN, label="Top-1")
    ax.semilogx(magnitude_percent, loc["top3"], marker="s", color=PURPLE, label="Top-3")
    ax.axhline(1 / 16, color=GRAY, linestyle=":", linewidth=0.8, label="Top-1 chance")
    ax.set_ylim(0, 1.03)
    ax.set_xlabel(r"Load-change magnitude $|a|$ (\%)")
    ax.set_ylabel("Exact source success")
    ax.set_title("(d) Source-resolution boundary", loc="left")
    ax.legend(frameon=False, fontsize=5.7, loc="lower right")
    ax.grid(which="both", alpha=0.2, linewidth=0.5)

    ax = axes[1, 1]
    x_pred = 100 * detectability["a_min"]
    y_emp = 100 * detectability["a90"]
    ax.scatter(x_pred, y_emp, s=24, color=BLUE, edgecolor="#243244", linewidth=0.45)
    lim_low = 0.8 * min(x_pred.min(), y_emp.min())
    lim_high = 1.25 * max(x_pred.max(), y_emp.max())
    ax.plot([lim_low, lim_high], [lim_low, lim_high], color=GRAY, linestyle="--", linewidth=0.8)
    for row in detectability.itertuples():
        if row.source_bus in {8, 12, 20}:
            ax.annotate(str(row.source_bus), (100 * row.a_min, 100 * row.a90), xytext=(3, 2), textcoords="offset points", fontsize=5.5)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(lim_low, lim_high)
    ax.set_ylim(lim_low, lim_high)
    ax.set_xlabel("EVI-predicted threshold (%)")
    ax.set_ylabel("Empirical 90% threshold (%)")
    ax.set_title("(e) Detectability prediction", loc="left")
    ax.text(0.05, 0.92, rf"Spearman $\rho={predictive['EVI_vs_a90_spearman']:.2f}$", transform=ax.transAxes, va="top")
    ax.grid(which="both", alpha=0.2, linewidth=0.5)

    ax = axes[1, 2]
    ax.plot(100 * finite["amplitude"], 100 * finite["coverage95"], marker="o", color=PURPLE)
    ax.axhline(95, color=GRAY, linestyle="--", linewidth=0.8, label="nominal 95%")
    ax.set_ylim(88, 100)
    ax.set_xlabel("Signed load change $a$ (%)")
    ax.set_ylabel("Amplitude coverage (%)")
    ax.set_title("(f) Finite-amplitude calibration", loc="left")
    ax.legend(frameon=False, fontsize=5.8, loc="lower right")
    ax.grid(alpha=0.2, linewidth=0.5)

    fig.tight_layout(h_pad=1.0, w_pad=0.8)
    save_figure(fig, "load_event_inference")


def write_tables() -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    nominal = read_csv("e04a_b0_b1_b2_summary.csv").set_index("method")
    labels = {
        "B0_NOMINAL": "B0 equilibrium",
        "B1_SNAPSHOT_WLS": "B1 snapshot LMMSE",
        "B2_KALMAN": "B2 causal Kalman",
    }
    rows = []
    for key, label in labels.items():
        row = nominal.loc[key]
        rows.append(
            f"{label} & {row['complex_rmse']:.3e} & {row['vm_rmse']:.3e} & "
            f"{row['angle_rmse']:.5f} & {row['TVE_percent']:.6f} & "
            f"[{row['TVE_percent_ci95_low']:.6f}, {row['TVE_percent_ci95_high']:.6f}] \\\\"
        )
    nominal_tex = """\\begin{table*}[t]
\\caption{Nominal reconstruction on 100 frozen nonlinear TEST trajectories. HVRE is the trajectory-and-bus mean relative complex-voltage error over the 31 unobserved buses; intervals bootstrap independent trajectories.}
\\label{tab:nominal-results}
\\centering
\\footnotesize
\\begin{tabular}{lccccc}
\\toprule
Method & Complex RMSE & $|V|$ RMSE & Angle RMSE ($^\\circ$) & Mean HVRE (\\%) & 95\\% HVRE interval (\\%) \\\\
\\midrule
""" + "\n".join(rows) + """
\\bottomrule
\\end{tabular}
\\end{table*}
"""
    (TABLES / "nominal_results.tex").write_text(nominal_tex, encoding="ascii")

    cal = read_csv("e04a3_test_calibration.csv").set_index("method")
    d4 = read_csv("e04a4_test_metrics.csv").set_index("model")
    d5 = read_csv("e04a5_test_metrics.csv").set_index("model")
    uncertainty_rows = [
        ("U0 original", cal.loc["U0_ORIGINAL", "nll"], cal.loc["U0_ORIGINAL", "coverage95_re"], cal.loc["U0_ORIGINAL", "coverage95_im"], d4.loc["D0_B2_ORIGINAL", "acf1"], d4.loc["D0_B2_ORIGINAL", "TVE_percent"]),
        ("U2 Re/Im temperature", cal.loc["U2_RE_IM_BLOCK_TEMPERATURE", "nll"], cal.loc["U2_RE_IM_BLOCK_TEMPERATURE", "coverage95_re"], cal.loc["U2_RE_IM_BLOCK_TEMPERATURE", "coverage95_im"], d4.loc["D1_U2_TEMPERATURE", "acf1"], d4.loc["D1_U2_TEMPERATURE", "TVE_percent"]),
        ("D2-M measurement GM r4", d4.loc["D2_GM_DIAG_R4", "hidden_nll"], d4.loc["D2_GM_DIAG_R4", "coverage95_re"], d4.loc["D2_GM_DIAG_R4", "coverage95_im"], d4.loc["D2_GM_DIAG_R4", "acf1"], d4.loc["D2_GM_DIAG_R4", "TVE_percent"]),
        ("D2-P process GM r1", d5.loc["D2-P_GM_PROCESS_R1", "hidden_nll"], d5.loc["D2-P_GM_PROCESS_R1", "coverage95_re"], d5.loc["D2-P_GM_PROCESS_R1", "coverage95_im"], d5.loc["D2-P_GM_PROCESS_R1", "acf1"], d5.loc["D2-P_GM_PROCESS_R1", "TVE_percent"]),
    ]
    lines = [
        f"{label} & {nll:.3f} & {100*cre:.1f} & {100*cim:.1f} & {acf:.3f} & {tve:.6f} \\\\"
        for label, nll, cre, cim, acf, tve in uncertainty_rows
    ]
    uncertainty_tex = """\\begin{table*}[t]
\\caption{Frozen TEST uncertainty and colored-discrepancy ablations. U2 is fitted on a disjoint 30-trajectory calibration set; Gauss--Markov (GM) ranks are selected on that calibration set.}
\\label{tab:uncertainty-results}
\\centering
\\footnotesize
\\begin{tabular}{lccccc}
\\toprule
Variant & Hidden NLL & 95\\% cov. Re (\\%) & 95\\% cov. Im (\\%) & Innovation ACF(1) & HVRE (\\%) \\\\
\\midrule
""" + "\n".join(lines) + """
\\bottomrule
\\end{tabular}
\\end{table*}
"""
    (TABLES / "uncertainty_results.tex").write_text(uncertainty_tex, encoding="ascii")

    per_case = pd.read_parquet(DATA / "e06_standard_per_case.parquet")
    b2 = per_case[per_case["method"].eq("B2")]
    ref = b2.loc[b2["m"].eq(0), "TVE_percent"].median()
    max_scale = b2[b2["m"].eq(1.5)].groupby("family")["TVE_percent"].median()
    mismatch_labels = {
        "M1_NETWORK": "M1 network",
        "M2_MACHINE": "M2 machine",
        "M3_GOVERNOR": "M3 governor",
        "M4_AVR": "M4 AVR",
        "M5_LOAD_MODEL": "M5 load model",
        "M6_OPERATING_POINT": "M6 operating point",
        "M7_COUPLED": "M7 coupled",
    }
    mismatch_rows = [
        f"{label} & {max_scale[key]:.6f} & {max_scale[key]/ref:.3f}$\\times$ \\\\"
        for key, label in mismatch_labels.items()
    ]
    mismatch_tex = """\\begin{table}[t]
\\caption{Median B2 hidden-voltage HVRE at the largest mismatch scale, $m=1.5$. Ratios use the 140-case main-grid nominal median of 0.014744\\%.}
\\label{tab:mismatch-results}
\\centering
\\footnotesize
\\begin{tabular}{lcc}
\\toprule
Mismatch family & HVRE (\\%) & Ratio \\\\
\\midrule
""" + "\n".join(mismatch_rows) + """
\\bottomrule
\\end{tabular}
\\end{table}
"""
    (TABLES / "mismatch_results.tex").write_text(mismatch_tex, encoding="ascii")

    e06h_cases = read_csv("e06h_test_per_case.csv")
    e06h_closure = read_csv("e06h_closure.csv").set_index("m")
    e06h_ident = read_csv("e06h_identifiability.csv")
    e06h_uncertainty = read_csv("e06h_uncertainty.csv")
    e06h_runtime = read_csv("e06h_runtime.csv")
    e06h_medians = e06h_cases.groupby(["m", "method"])["hidden_V_TVE_percent"].median().unstack()
    ident_by_scale = e06h_ident.groupby("m")[["information_rank", "nullspace_dimension"]].median()
    nees_by_scale = e06h_uncertainty.groupby("m")["NEES_like"].median()
    runtime_by_scale = e06h_runtime.groupby("m")["runtime_ms"].median()
    adaptation_rows = []
    for scale in (0.5, 1.0, 1.5):
        c = e06h_closure.loc[scale]
        adaptation_rows.append(
            f"{scale:.1f} & {int(c['n'])} & {e06h_medians.loc[scale, 'S0-NOM']:.5f} & "
            f"{e06h_medians.loc[scale, 'S0-MAP-CORRECTED']:.5f} & "
            f"{100*c['closure_median']:.1f} [{100*c['closure_ci95_low']:.1f}, {100*c['closure_ci95_high']:.1f}] & "
            f"{int(ident_by_scale.loc[scale, 'information_rank'])}/43 & "
            f"{int(ident_by_scale.loc[scale, 'nullspace_dimension'])} & {nees_by_scale.loc[scale]:.1f} & "
            f"{runtime_by_scale.loc[scale]:.1f} \\\\"
        )
    adaptation_tex = r"""\begin{table*}[t]
\caption{Corrected physical static recentering on 60 held-out M6 operating-point cases. Gap-closure intervals bootstrap the 20 independent TEST cases at each scale. Rank and nullity refer to the 43-dimensional nuisance basis; runtime is per solve.}
\label{tab:e06h-results}
\centering
\footnotesize
\begin{tabular}{ccccccccc}
\toprule
$m$ & $n$ & Frozen HVRE (\%) & Corrected HVRE (\%) & Gap closure [95\% CI] (\%) & Rank & Nullity & Median NEES & Runtime (ms) \\
\midrule
""" + "\n".join(adaptation_rows) + r"""
\bottomrule
\end{tabular}
\end{table*}
"""
    (TABLES / "e06h_results.tex").write_text(adaptation_tex, encoding="ascii")

    summary = read_legacy_summary()
    event_rows = []
    for key, label in [
        ("hierarchical_136", "136-feature hierarchy"),
        ("hierarchical_448", "448-feature hierarchy"),
        ("hierarchical_448_availability", "448 features + availability"),
    ]:
        row = summary.loc[key]
        event_rows.append(
            f"{label} & {row[('detection_f1', 'mean')]:.3f} & "
            f"{row[('event_macro_f1_all_labels', 'mean')]:.3f} & "
            f"{row[('physical_top1', 'mean')]:.3f} & {row[('physical_top3', 'mean')]:.3f} & "
            f"{row[('integrity_top1', 'mean')]:.3f} & "
            f"{row[('false_alarm_episodes_per_min', 'mean')]:.2f} \\\\"
        )
    event_tex = r"""\begin{table*}[t]
\caption{Audited sequential event-diagnosis baseline on the known-source TEST split, mean over three fitted seeds. The independent split unit is the complete trajectory; timestamp-level scores retain the denominators of the frozen evaluator.}
\label{tab:legacy-event-results}
\centering
\footnotesize
\begin{tabular}{lcccccc}
\toprule
Configuration & Detection F1 & Event macro-F1 & Physical Top-1 & Physical Top-3 & Integrity Top-1 & False alarms/min \\
\midrule
""" + "\n".join(event_rows) + r"""
\bottomrule
\end{tabular}
\end{table*}
"""
    (TABLES / "legacy_event_results.tex").write_text(event_tex, encoding="ascii")

    weak_detection = read_csv("load_bayes_v2_weak_detection.csv")
    weak_localization = read_csv("load_bayes_v2_weak_localization.csv")
    weak = weak_detection.merge(weak_localization, on="amplitude", validate="one_to_one")
    weak["abs_amplitude"] = weak["amplitude"].abs()
    weak = weak.groupby("abs_amplitude").mean(numeric_only=True).sort_index()
    weak_rows = [
        f"{100*a:.3f} & {row['AUROC']:.3f} & {100*row['FPR']:.2f} & "
        f"{100*row['FNR']:.1f} & {100*row['top1']:.1f} & {100*row['top3']:.1f} \\\\"
        for a, row in weak.iterrows()
    ]
    weak_tex = r"""\begin{table}[t]
\caption{Sign-pooled weak load-event TEST results for the frozen W2/L2 model. Each row contains 1,600 event cases (16 source buses, two signs, 50 noise replicas); the false-positive rate uses 800 no-event records.}
\label{tab:load-weak-results}
\centering
\scriptsize
\setlength{\tabcolsep}{3.2pt}
\begin{tabular}{cccccc}
\toprule
$|a|$ (\%) & AUROC & FPR (\%) & FNR (\%) & Top-1 (\%) & Top-3 (\%) \\
\midrule
""" + "\n".join(weak_rows) + r"""
\bottomrule
\end{tabular}
\end{table}
"""
    (TABLES / "load_weak_results.tex").write_text(weak_tex, encoding="ascii")


def main() -> None:
    setup_style()
    checks: dict[str, object] = {}
    write_macros(checks)
    figure_system_architecture()
    figure_observability_horizon()
    figure_nominal()
    figure_temporal_uncertainty()
    figure_mismatch()
    figure_adequacy_adaptation()
    figure_event_inference_evidence()
    write_tables()

    assert checks["nominal_test_trajectories"] == 100
    assert checks["e06_main_b2_cases"] == 980
    assert checks["e06_main_unique_physical_cases"] == 980
    assert 0 <= checks["e06e_median_oracle_closure"] < 0.01
    assert checks["e06h_test_cases"] == 60
    assert checks["e06h_test_valid_rate"] == 1.0
    assert 0.95 < checks["e06h_median_closure"] < 1.0
    assert checks["e06h_nuisance_rank"] < checks["e06h_nuisance_dimension"]
    assert checks["legacy_event_trajectories"] == 690
    assert checks["legacy_held_source_decisions"] == 303
    assert checks["legacy_held_source_correct"] == 3
    assert checks["load_tangent_sources"] == 16
    assert checks["load_tangent_max_rel_error"] < 0.0025
    assert checks["load_v2_cal_normal"] == 1000
    assert checks["load_v2_dev_normal"] == 500
    assert checks["load_v2_dev_event_cases"] == 640
    assert checks["load_v2_weak_event_cases"] == 9600
    assert checks["load_v2_weak_no_event_cases"] == 800
    assert checks["load_v2_finite_event_cases"] == 8000
    assert checks["load_v2_selected_whitening"] == "W2_SEPARABLE_AR1"
    assert checks["load_v2_selected_likelihood"] == "L2"
    assert 1.9 < checks["load_v2_truncation_slope"] < 2.1
    assert checks["load_v2_evi_a90_spearman"] < -0.7
    assert abs(checks["load_v2_projected_fisher_confusion_spearman"]) < 0.5
    assert 0.9 < checks["load_v2_finite_coverage95_min"] <= 0.95
    assert 0.95 <= checks["load_v2_finite_coverage95_max"] < 0.98
    (GENERATED / "evidence_checks.json").write_text(
        json.dumps(checks, indent=2, sort_keys=True) + "\n", encoding="ascii"
    )
    print(json.dumps(checks, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

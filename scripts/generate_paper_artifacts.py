"""Generate every numerical table, macro, and empirical figure in the paper.

The script reads only the frozen, hashed artifacts imported by
``scripts/import_frozen_results.ps1``. It intentionally does not reach into the
research repository during a manuscript build.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


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


def read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA / name)


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
    fig.savefig(FIGURES / f"{stem}.pdf", bbox_inches="tight", pad_inches=0.025)
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

    macros = {
        "ObservedPMUCount": "8",
        "HiddenBusCount": "31",
        "NominalTestCount": str(int(nominal.loc["B2_KALMAN", "n_trajectories"])),
        "BZeroTVE": fmt_percent(nominal.loc["B0_NOMINAL", "TVE_percent"]),
        "BOneTVE": fmt_percent(nominal.loc["B1_SNAPSHOT_WLS", "TVE_percent"], 6),
        "BTwoTVE": fmt_percent(nominal.loc["B2_KALMAN", "TVE_percent"], 6),
        "BTwoRelativeImprovement": f"{100 * (1 - nominal.loc['B2_KALMAN', 'TVE_percent'] / nominal.loc['B1_SNAPSHOT_WLS', 'TVE_percent']):.1f}\\%",
        "FunctionalSpearman": f"{e03['spearman_B2_TVE_vs_functional_residual'].dropna().iloc[0]:.4f}",
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
        }
    )


def figure_nominal() -> None:
    nominal = read_csv("e04a_b0_b1_b2_summary.csv")
    e03 = read_csv("e04a1_e03_vs_e04.csv")
    names = ["Equilibrium", "Snapshot WLS", "Causal Kalman"]
    values = nominal["TVE_percent"].to_numpy()
    low = values - nominal["TVE_percent_ci95_low"].to_numpy()
    high = nominal["TVE_percent_ci95_high"].to_numpy() - values

    fig, axes = plt.subplots(1, 2, figsize=(7.16, 2.65), gridspec_kw={"width_ratios": [0.88, 1.12]})
    ax = axes[0]
    bars = ax.bar(
        names,
        values,
        yerr=np.vstack([low, high]),
        capsize=2.5,
        color=[LIGHT_GRAY, SKY, BLUE],
        edgecolor="#243244",
        linewidth=0.55,
    )
    ax.set_yscale("log")
    ax.set_ylabel("Mean hidden-bus TVE (%)")
    ax.set_title("(a) Nominal reconstruction, 100 TEST trajectories")
    ax.grid(axis="y", which="both", alpha=0.2, linewidth=0.5)
    ax.tick_params(axis="x", rotation=16)
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value * 1.16, f"{value:.4g}%", ha="center", va="bottom", fontsize=6.4)

    ax = axes[1]
    x = e03["functional_residual"].to_numpy()
    y = 100 * e03["B2_TVE"].to_numpy()
    ax.scatter(x, y, s=22, facecolors="white", edgecolors=BLUE, linewidths=1.0, zorder=3)
    weak = e03.nlargest(5, "B2_TVE")
    for _, row in weak.iterrows():
        ax.annotate(
            str(int(row["hidden_bus"])),
            (row["functional_residual"], 100 * row["B2_TVE"]),
            xytext=(3, 3),
            textcoords="offset points",
            fontsize=6.3,
            color="#243244",
        )
    rho = e03["spearman_B2_TVE_vs_functional_residual"].dropna().iloc[0]
    ax.text(0.03, 0.94, rf"Spearman $\rho={rho:.4f}$", transform=ax.transAxes, va="top")
    ax.set_xlabel("Preregistered functional residual")
    ax.set_ylabel("Per-bus Kalman TVE (%)")
    ax.set_yscale("log")
    ax.set_title("(b) Structural weakness predicts empirical difficulty")
    ax.grid(alpha=0.2, linewidth=0.5)
    fig.tight_layout(w_pad=1.5)
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
    ax.set_ylabel("Hidden-bus TVE (%)")
    ax.set_title("(a) Smoothing adds no TVE benefit")
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
    ref = b2.loc[b2["m"].eq(0), "TVE_percent"].median()
    grouped = b2.groupby(["family", "m"])["TVE_percent"].median().unstack()
    scales = grouped.columns.to_numpy(dtype=float)

    fig, axes = plt.subplots(1, 2, figsize=(7.16, 2.65), gridspec_kw={"width_ratios": [1.15, 0.85]})
    ax = axes[0]
    series = [
        ("M1 network", "M1_NETWORK", BLUE, "o"),
        ("M6 operating point", "M6_OPERATING_POINT", ORANGE, "s"),
        ("M7 coupled", "M7_COUPLED", PURPLE, "^"),
    ]
    for label, key, color, marker in series:
        ax.plot(scales, grouped.loc[key].to_numpy() / ref, marker=marker, color=color, label=label)
    minor = grouped.loc[["M2_MACHINE", "M3_GOVERNOR", "M4_AVR", "M5_LOAD_MODEL"]].to_numpy() / ref
    ax.fill_between(scales, minor.min(axis=0), minor.max(axis=0), color=LIGHT_GRAY, alpha=0.65, label="M2--M5 range")
    ax.axhline(2, color="#243244", linestyle="--", linewidth=0.8)
    ax.axhline(5, color="#243244", linestyle=":", linewidth=0.8)
    ax.set_xlabel("Mismatch scale $m$")
    ax.set_ylabel("Median TVE / nominal median")
    ax.set_title("(a) Frozen Kalman estimator under rebuilt plants")
    ax.legend(frameon=False, loc="upper left")
    ax.grid(alpha=0.2, linewidth=0.5)

    ax = axes[1]
    keys = ["M1_NETWORK", "M6_OPERATING_POINT", "M7_COUPLED"]
    labels = ["Network", "Operating\npoint", "Coupled"]
    values = grouped.loc[keys, 1.5].to_numpy()
    colors = [BLUE, ORANGE, PURPLE]
    bars = ax.bar(labels, values, color=colors, edgecolor="#243244", linewidth=0.5)
    ax.axhline(ref, color="#243244", linestyle="--", linewidth=0.9, label=f"nominal {ref:.4f}%")
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value * 1.03, f"{value:.3f}%", ha="center", va="bottom", fontsize=6.4)
    ax.set_ylabel("Median hidden-bus TVE (%)")
    ax.set_title("(b) Largest tested scale, $m=1.5$")
    ax.legend(frameon=False, loc="upper right")
    ax.grid(axis="y", alpha=0.2, linewidth=0.5)
    fig.tight_layout(w_pad=1.4)
    save_figure(fig, "physical_mismatch")


def figure_adequacy_adaptation() -> None:
    e06e = read_csv("e06e_summary.csv")
    adequacy = read_csv("e06_standard_adequacy.csv")
    families = ["M1_NETWORK", "M6_OPERATING_POINT", "M7_COUPLED"]
    selected = e06e[
        e06e["split"].eq("TEST") & e06e["m"].eq(1.5) & e06e["family"].isin(families)
    ].copy()
    selected["variant"] = np.where(
        selected["method"].eq("R0_FROZEN_B2"),
        "Frozen B2",
        np.where(
            selected["method"].eq("R1_ORACLE_RECENTERED"),
            "Oracle center",
            np.where(selected["policy"].eq("ADAPTIVE_RECENTER"), "Online offset", "exclude"),
        ),
    )
    selected = selected[selected["variant"].ne("exclude")]
    med = selected.groupby(["family", "variant"])["TVE_percent"].median().unstack()

    fig, axes = plt.subplots(1, 2, figsize=(7.16, 2.55), gridspec_kw={"width_ratios": [1.08, 0.92]})
    ax = axes[0]
    variants = ["Frozen B2", "Oracle center", "Online offset"]
    colors = [GRAY, GREEN, ORANGE]
    hatches = ["", "///", "xx"]
    x = np.arange(len(families))
    width = 0.24
    for i, (variant, color, hatch) in enumerate(zip(variants, colors, hatches)):
        ax.bar(
            x + (i - 1) * width,
            med.loc[families, variant],
            width,
            label=variant,
            color=color,
            hatch=hatch,
            edgecolor="#243244",
            linewidth=0.45,
        )
    ax.set_yscale("log")
    ax.set_xticks(x, ["Network", "Operating\npoint", "Coupled"])
    ax.set_ylabel("Median TEST TVE (%)")
    ax.set_title("(a) Causal offset proxy does not close oracle gap")
    ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.02))
    ax.grid(axis="y", which="both", alpha=0.2, linewidth=0.5)

    ax = axes[1]
    scales = [0.5, 1.0, 1.5]
    auroc = []
    auprc = []
    for scale in scales:
        rows = adequacy[adequacy["m"].eq(scale)]
        auroc.append(rows["AUROC"].mean(skipna=True))
        auprc.append(rows["AUPRC"].mean(skipna=True))
    ax.plot(scales, auroc, marker="o", color=BLUE, label="macro AUROC")
    ax.plot(scales, auprc, marker="s", color=PURPLE, label="macro AUPRC")
    ax.set_ylim(0.72, 0.98)
    ax.set_xticks(scales)
    ax.set_xlabel("Mismatch scale $m$")
    ax.set_ylabel("Macro score across families")
    ax.set_title("(b) Nominal-CAL model-adequacy statistic")
    ax.legend(frameon=False, loc="lower left")
    ax.grid(alpha=0.2, linewidth=0.5)
    fig.tight_layout(w_pad=1.2)
    save_figure(fig, "adequacy_adaptation")


def write_tables() -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    nominal = read_csv("e04a_b0_b1_b2_summary.csv").set_index("method")
    labels = {
        "B0_NOMINAL": "B0 equilibrium",
        "B1_SNAPSHOT_WLS": "B1 snapshot WLS",
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
\\caption{Nominal reconstruction on 100 frozen nonlinear TEST trajectories. Metrics use the 31 unobserved buses only; TVE is reported in percent and intervals bootstrap independent trajectories.}
\\label{tab:nominal-results}
\\centering
\\footnotesize
\\begin{tabular}{lccccc}
\\toprule
Method & Complex RMSE & $|V|$ RMSE & Angle RMSE ($^\\circ$) & Mean TVE (\\%) & 95\\% TVE interval (\\%) \\\\
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
Variant & Hidden NLL & 95\\% cov. Re (\\%) & 95\\% cov. Im (\\%) & Innovation ACF(1) & TVE (\\%) \\\\
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
\\caption{Median B2 hidden-bus TVE at the largest mismatch scale, $m=1.5$. Ratios use the 140-case main-grid nominal median of 0.014744\\%.}
\\label{tab:mismatch-results}
\\centering
\\footnotesize
\\begin{tabular}{lcc}
\\toprule
Mismatch family & TVE (\\%) & Ratio \\\\
\\midrule
""" + "\n".join(mismatch_rows) + """
\\bottomrule
\\end{tabular}
\\end{table}
"""
    (TABLES / "mismatch_results.tex").write_text(mismatch_tex, encoding="ascii")


def main() -> None:
    setup_style()
    checks: dict[str, object] = {}
    write_macros(checks)
    figure_nominal()
    figure_temporal_uncertainty()
    figure_mismatch()
    figure_adequacy_adaptation()
    write_tables()

    assert checks["nominal_test_trajectories"] == 100
    assert checks["e06_main_b2_cases"] == 980
    assert checks["e06_main_unique_physical_cases"] == 980
    assert 0 <= checks["e06e_median_oracle_closure"] < 0.01
    (GENERATED / "evidence_checks.json").write_text(
        json.dumps(checks, indent=2, sort_keys=True) + "\n", encoding="ascii"
    )
    print(json.dumps(checks, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

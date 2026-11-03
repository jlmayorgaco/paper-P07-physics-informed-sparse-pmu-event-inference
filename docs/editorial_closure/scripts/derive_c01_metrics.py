"""Create descriptive re-expressions of the tracked, frozen C01 exports.

This does not call C01's evaluator, read prediction artifacts, tune anything,
or change a scientific endpoint. It uses only generated/frozen/c01_20261029.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
FROZEN = ROOT / "generated" / "frozen" / "c01_20261029"
OUT = ROOT / "docs" / "editorial_closure" / "derived_c01"
METHODS = ["R11", "R11_NOMINAL", "ET_REFERENCE", "ET_CANDIDATE"]
METHOD_LABELS = {
    "R11": "Physical history",
    "R11_NOMINAL": "Nominal physical",
    "ET_REFERENCE": "ExtraTrees",
    "ET_CANDIDATE": "Short-window ExtraTrees",
}
CONDITIONS = ["MATCH", "RX_IN_SUPPORT", "RX_OUT_SUPPORT"]
FAMILIES = ["load", "line"]
NOISES = [1.0, 2.0]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    records = pd.read_csv(FROZEN / "RECORDS.csv")
    events = pd.read_csv(FROZEN / "EVENTS.csv")
    frozen_summary = pd.read_csv(FROZEN / "SUMMARY.csv")
    audit = pd.read_json(FROZEN / "EVALUATION_AUDIT.json", typ="series")

    # Scope to the four methods with continuous-event and report-level metrics.
    # Pair each event-lane row with normal-control rows for the same
    # method/condition/noise, matching the original evaluator's F1 aggregation.
    r = records[(records.method.isin(METHODS)) & records.lane.isin(["continuous", "normal"])].copy()
    e = events[(events.method.isin(METHODS)) & (events.lane == "continuous")].copy()
    require(set(r.method.unique()) == set(METHODS), "Expected all four frozen methods in RECORDS.csv")
    require(set(e.method.unique()) == set(METHODS), "Expected all four frozen methods in EVENTS.csv")
    require(set(r.condition.unique()) == set(CONDITIONS), "Unexpected report condition set")
    require(set(e.condition.unique()) == set(CONDITIONS), "Unexpected event condition set")
    require(set(e.family.unique()) == set(FAMILIES), "Unexpected event family set")
    require(set(r.noise.unique()) == set(NOISES), "Unexpected noise strata in records")
    require(set(e.noise.unique()) == set(NOISES), "Unexpected noise strata in events")

    report_rows: list[dict] = []
    for method in METHODS:
        for condition in CONDITIONS:
            subset = r[(r.method == method) & (r.condition == condition)]
            require(len(subset) == 60, f"Unexpected report-record denominator: {method}/{condition}: {len(subset)}")
            tp, fp, fn = (int(subset[k].sum()) for k in ("tp", "fp", "fn"))
            denom = 2 * tp + fp + fn
            f1 = 2 * tp / denom if denom else np.nan
            frozen_rows = frozen_summary[
                (frozen_summary.method == method)
                & (frozen_summary.lane == "continuous")
                & (frozen_summary.condition == condition)
            ]
            require(len(frozen_rows) == 2, f"Expected two frozen noise-stratum summary rows for {method}/{condition}")
            # The evaluator pools TP/FP/FN within each method/condition/noise.
            # Verify this derivation against every frozen per-noise F1 value.
            for noise in NOISES:
                cell = subset[subset.noise == noise]
                source = frozen_rows[frozen_rows.noise == noise]
                require(len(source) == 1, f"Missing frozen F1 row for {method}/{condition}/{noise}")
                ctp, cfp, cfn = (int(cell[k].sum()) for k in ("tp", "fp", "fn"))
                cd = 2 * ctp + cfp + cfn
                cell_f1 = 2 * ctp / cd if cd else np.nan
                require(
                    np.isclose(cell_f1, float(source.iloc[0].detection_f1), rtol=0, atol=1e-12, equal_nan=True),
                    f"Frozen SUMMARY F1 parity failed for {method}/{condition}/{noise}",
                )
            intended = len(subset)
            available = int(subset.available.astype(bool).sum())
            report_rows.append(
                dict(
                    method=method,
                    condition=condition,
                    noise_strata="1.0|2.0 (pooled; no retuning)",
                    intended_records=intended,
                    available_records=available,
                    unavailable_records=intended - available,
                    tp=tp,
                    fp=fp,
                    fn=fn,
                    report_f1=f1,
                    f1_denominator=denom,
                    abstentions=int(subset.abstentions.sum()),
                    monitored_reports=int(subset.monitored_reports.sum()),
                    open_eof=int(subset.open_eof.sum()),
                    report_f1_definition="2*TP/(2*TP+FP+FN), TP/FP/FN summed over event and normal records",
                )
            )
    report = pd.DataFrame(report_rows)

    event_rows: list[dict] = []
    for method in METHODS:
        for condition in CONDITIONS:
            for family in FAMILIES:
                cell = e[(e.method == method) & (e.condition == condition) & (e.family == family)]
                total = len(cell)
                require(total == 108, f"Unexpected event denominator: {method}/{condition}/{family}: {total}")
                available = int(cell.available.astype(bool).sum())
                counts = {metric: int(cell[metric].astype(bool).sum()) for metric in ("detected", "timely", "joint", "top3")}
                # The three published fractions use every truth event row as
                # denominator: misses remain failures in the numerator, not exclusions.
                event_rows.append(
                    dict(
                        method=method,
                        condition=condition,
                        family=family,
                        noise_strata="1.0|2.0 (pooled; no retuning)",
                        event_denominator=total,
                        available_event_rows=available,
                        unavailable_event_rows=total - available,
                        detected_n=counts["detected"],
                        timely_n=counts["timely"],
                        joint_n=counts["joint"],
                        top3_n=counts["top3"],
                        missed_n=total - counts["detected"],
                        timely_fraction=counts["timely"] / total,
                        joint_fraction=counts["joint"] / total,
                        top3_fraction=counts["top3"] / total,
                        fraction_denominator="all truth EVENTS rows in this method/condition/family, including missed alarms",
                    )
                )
    coverage = pd.DataFrame(event_rows)

    # Parity checks against the evaluator's frozen summary after pooling its
    # two noise strata. This is an audit of arithmetic only, not re-evaluation.
    for method in METHODS:
        for condition in CONDITIONS:
            source = frozen_summary[
                (frozen_summary.method == method)
                & (frozen_summary.lane == "continuous")
                & (frozen_summary.condition == condition)
            ]
            out = coverage[(coverage.method == method) & (coverage.condition == condition)]
            require(len(source) == 2 and int(source.events.sum()) == int(out.event_denominator.sum()), "Event denominator parity failed")
            for metric, source_col in (("timely_n", "timely"), ("joint_n", "joint"), ("top3_n", "top3")):
                require(int(source[source_col].sum()) == int(out[metric].sum()), f"{metric} parity failed for {method}/{condition}")

    report.to_csv(OUT / "report_f1_by_condition.csv", index=False)
    coverage.to_csv(OUT / "event_coverage_by_family_condition.csv", index=False)
    # Share aggregate summaries only; retain availability and censor counts in
    # report_f1_by_condition.csv without exporting record identifiers.
    old_record_export = OUT / "record_availability_and_censoring.csv"
    if old_record_export.exists():
        old_record_export.unlink()

    # Two-panel descriptive figure: report-level F1 by condition; and the
    # original event-level timely/joint/top-3 fractions by family-condition.
    colors = dict(zip(METHODS, ["#2166ac", "#67a9cf", "#b2182b", "#ef8a62"]))
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15.5, 6.8), gridspec_kw={"width_ratios": [0.8, 1.8]})
    x_cond = np.arange(len(CONDITIONS))
    for mi, method in enumerate(METHODS):
        vals = report[report.method == method].set_index("condition").loc[CONDITIONS]
        y = vals.report_f1.to_numpy(float)
        require(bool(np.isfinite(y).all()) and bool(((0 <= y) & (y <= 1.03)).all()), f"F1 plot values out of range for {method}")
        ax1.scatter(x_cond + (mi - 1.5) * 0.045, y, marker="o", s=38, color=colors[method], label=METHOD_LABELS[method], zorder=3)
    ax1.set_xticks(x_cond, ["Matched", "R/X in support", "R/X out of support"], rotation=18, ha="right")
    ax1.set_ylim(0, 1.03)
    ax1.set_ylabel("Report-level detection F1")
    ax1.set_title("A. Report-level F1")
    ax1.grid(axis="y", alpha=0.25)

    cats = [(condition, family) for condition in CONDITIONS for family in FAMILIES]
    cat_x = np.arange(len(cats))
    metrics = [("timely_fraction", "o", "Timely"), ("joint_fraction", "s", "Exact joint"), ("top3_fraction", "^", "Top-3")]
    method_offsets = np.linspace(-0.065, 0.065, len(METHODS))
    metric_offsets = [-0.18, 0.0, 0.18]
    plotted_event_values: list[float] = []
    for metric_i, (metric, marker, _) in enumerate(metrics):
        for method_i, method in enumerate(METHODS):
            vals = []
            for condition, family in cats:
                row = coverage[(coverage.method == method) & (coverage.condition == condition) & (coverage.family == family)]
                require(len(row) == 1, "Missing event fraction for plot")
                vals.append(float(row.iloc[0][metric]))
            y = np.asarray(vals, dtype=float)
            require(bool(np.isfinite(y).all()) and bool(((0 <= y) & (y <= 1.03)).all()), f"Event plot values out of range for {method}/{metric}")
            plotted_event_values.extend(y.tolist())
            ax2.scatter(
                cat_x + metric_offsets[metric_i] + method_offsets[method_i],
                y,
                s=31,
                marker=marker,
                color=colors[method],
                linewidths=0.35,
                edgecolors="white",
                zorder=3,
            )
    condition_label = {"MATCH": "Matched", "RX_IN_SUPPORT": "R/X in", "RX_OUT_SUPPORT": "R/X out"}
    ax2.set_xticks(cat_x, [f"{condition_label[condition]}\n{family}" for condition, family in cats], fontsize=8)
    ax2.set_xlim(-0.5, len(cats) - 0.5)
    ax2.set_ylim(0, 1.03)
    ax2.set_yticks(np.linspace(0, 1, 6))
    ax2.set_ylabel("Fraction of all truth event rows")
    ax2.set_title("B. Event-level outcomes by family and condition")
    ax2.grid(axis="y", alpha=0.25)
    method_handles = [plt.Line2D([0], [0], color=colors[m], marker="o", lw=0, label=METHOD_LABELS[m]) for m in METHODS]
    metric_handles = [plt.Line2D([0], [0], color="#555555", marker=marker, lw=0, label=label) for _, marker, label in metrics]
    fig.suptitle("Report detection and event attribution", fontsize=14, y=0.98)
    fig.text(
        0.5,
        0.105,
        "Panel A pools TP/FP/FN over event and normal records. Panel B fractions use all 108 truth events per family-condition; "
        "both noise strata are pooled, and missed alarms remain in the denominator. Descriptive restatement of frozen results, not a new test.",
        ha="center",
        va="center",
        fontsize=8,
        wrap=True,
    )
    fig.legend(
        handles=method_handles + metric_handles,
        labels=[METHOD_LABELS[m] for m in METHODS] + [label for _, _, label in metrics],
        frameon=False,
        fontsize=8,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.025),
        ncol=4,
    )
    fig.subplots_adjust(left=0.065, right=0.99, bottom=0.22, top=0.90, wspace=0.22)
    plotted_all = report.report_f1.to_numpy(float).tolist() + plotted_event_values
    require(bool(np.isfinite(plotted_all).all()), "Non-finite plotted metric")
    require(min(plotted_all) >= 0 and max(plotted_all) <= 1 and ax1.get_ylim() == (0.0, 1.03) and ax2.get_ylim() == (0.0, 1.03), "Plotted values fall outside displayed axis limits")
    fig.savefig(OUT / "c01_report_and_event_coverage.png", dpi=220, bbox_inches="tight")
    fig.savefig(OUT / "c01_report_and_event_coverage.pdf", bbox_inches="tight")
    plt.close(fig)

    # Record source audit counts and the checks this derivation passed.
    pd.DataFrame(
        [
            dict(
                check="C01 complete-intended-records",
                result=bool(audit["complete_intended_records"]),
                value=int(audit["intended_observed_records"]),
                note="Frozen evaluation audit; expected all 342 observed records.",
            ),
            dict(
                check="physical_rejections",
                result=len(audit["physical_rejections"]) == 0,
                value=len(audit["physical_rejections"]),
                note="Any rejection remains in source audit; none found in frozen C01.",
            ),
            dict(
                check="inference_failures",
                result=len(audit["inference_failures"]) == 0,
                value=len(audit["inference_failures"]),
                note="Any failure remains in source audit; none found in frozen C01.",
            ),
            dict(
                check="summary_arithmetic_parity",
                result=True,
                value=len(METHODS) * len(CONDITIONS) * (len(NOISES) + 1),
                note="Per-noise report F1 and pooled event counts checked against frozen SUMMARY.csv.",
            ),
        ]
    ).to_csv(OUT / "derivation_checks.csv", index=False)

    (OUT / "README.md").write_text(
        "# Frozen C01 metric restatement\n\n"
        "These outputs are a descriptive restatement of `generated/frozen/c01_20261029/`; "
        "they are not new observations, a new evaluator run, ROC/PR analysis, or a significance test.\n\n"
        "- `report_f1_by_condition.csv`: TP/FP/FN summed over continuous-event and normal-control records and both noise strata; "
        "F1 = 2TP/(2TP+FP+FN).\n"
        "- `event_coverage_by_family_condition.csv`: detected, timely, exact joint, and Top-3 counts/fractions by method, family, and condition. "
        "Each fraction denominator is all 108 truth event rows for that family-condition across the two noise strata; missed detections remain in it.\n"
        "- `c01_report_and_event_coverage.png` and `.pdf`: two-panel view of report-level F1 and the timely/joint/Top-3 event fractions.\n"
        "- `derivation_checks.csv`: complete-denominator, failure/rejection, and parity checks.\n\n"
        "Aggregated availability, abstention, and `open_eof` counts remain in the report F1 table. "
        "The figure uses a 0-to-1.03 vertical range in both panels and descriptive method labels; exact values are in the CSV. "
        "C01 has no physical rejections or inference failures in its frozen audit. "
        "No uncertainty interval is added here: the source analysis uses the physical parent cluster, and the plotted ratios are descriptive.\n",
        encoding="utf-8",
    )

    print(f"Wrote descriptive C01 outputs to {OUT}")
    print(f"Report F1 rows: {len(report)}; event coverage rows: {len(coverage)}")
    print(f"Checks: {OUT / 'derivation_checks.csv'}")


if __name__ == "__main__":
    main()

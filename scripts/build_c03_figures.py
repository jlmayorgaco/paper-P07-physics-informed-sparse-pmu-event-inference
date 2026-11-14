"""Build the C03 summary figure only from the immutable imported result bundle."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "generated/frozen/recovery_c03"
OUT = ROOT / "figures/generated/recovery_c03.pdf"
MACROS = ROOT / "generated/c03_extended_macros.tex"
SUPPLEMENT = ROOT / "supplement/c03_results.tex"
EXPECTED_RESULT = "00f36cf49996bbdf8865bbfdbf51052c5aecb604c5e066180078bd8a3342ddfc"
COLORS = {"history": "#087F78", "carry": "#C46B2C", "reset": "#596F9B"}
LABELS = {"history": "History bank", "carry": "Carry state", "reset": "Reset"}


def read_result() -> dict:
    manifest = json.loads((SNAPSHOT / "BUNDLE_MANIFEST.json").read_text())
    raw = (SNAPSHOT / "TEST_RESULTS.json").read_bytes()
    if (manifest.get("status") != "IMMUTABLE_COMPACT_IMPORT"
            or manifest["files"].get("TEST_RESULTS.json") != EXPECTED_RESULT
            or hashlib.sha256(raw).hexdigest() != EXPECTED_RESULT):
        raise ValueError("C03 result bundle hash/status mismatch")
    validation = json.loads((SNAPSHOT / "VALIDATION.json").read_text())
    report = json.loads(raw)
    if validation.get("decision") != report.get("decision"):
        raise ValueError("C03 decision differs from validated import")
    for plant in ("F01", "P2"):
        for arm in ("history", "carry", "reset"):
            s = report["results"][plant]["nominal"][arm]["summary"]
            if s["parents"] != 72 or s["short_events"] != 144 or s["short_timely"] > 144:
                raise ValueError(f"unexpected C03 denominator for {plant}/{arm}")
    report["_validation"] = validation
    return report


def build(report: dict):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8,
                         "pdf.fonttype": 42, "ps.fonttype": 42})
    fig, axes = plt.subplots(2, 3, figsize=(7.15, 4.25),
                             gridspec_kw={"width_ratios": [1.05, .9, 1.0]})
    fig.subplots_adjust(left=.12, right=.985, top=.87, bottom=.15, hspace=.56, wspace=.48)
    plants = ("F01", "P2")
    for row, plant in enumerate(plants):
        summary = report["results"][plant]["nominal"]
        ax_cov, ax_extra, ax_delta = axes[row]
        ys = [2, 1, 0]
        for arm, y in zip(("history", "carry", "reset"), ys):
            s = summary[arm]["summary"]
            cov = 100 * s["short_timely"] / s["short_events"]
            extra = s["extras"]
            ax_cov.barh(y, cov, color=COLORS[arm], height=.54)
            label_x = max(1, cov - 2) if cov >= 85 else cov + 1.4
            ax_cov.text(label_x, y, f"{cov:.1f}%  ({s['short_timely']}/{s['short_events']})", ha="right" if cov >= 85 else "left", va="center", fontsize=7)
            ax_extra.barh(y, extra, color=COLORS[arm], height=.54)
            ax_extra.text(extra + 12, y, str(extra), va="center", fontsize=7)
        for ax in (ax_cov, ax_extra):
            ax.set_yticks(ys, [LABELS[a] for a in ("history", "carry", "reset")])
            ax.spines[["top", "right", "left"]].set_visible(False)
            ax.spines["bottom"].set_color("#CBD3D7")
            ax.grid(axis="x", color="#DDE3E5", lw=.5)
            ax.set_axisbelow(True)
            ax.tick_params(length=0, labelsize=7)
        ax_extra.set_yticklabels([])
        ax_cov.set_xlim(0, 120)
        ax_cov.set_xlabel("Short-gap timely attribution (%)")
        ax_cov.set_title(f"({chr(97+3*row)}) {plant}: coverage", loc="left", fontweight="bold")
        ax_extra.set_xlim(0, max(1000, max(summary[a]["summary"]["extras"] for a in summary) * 1.2))
        ax_extra.set_xlabel("Unmatched event-record alarms (count)")
        ax_extra.set_title(f"({chr(98+3*row)}) {plant}: extra alarms", loc="left", fontweight="bold")
        pair = report["contrasts"][plant]["history_vs_carry"]["coverage"]
        diff, low, high = [100 * pair[k] for k in ("difference", "lower95", "upper95")]
        expected = 100 * (summary["history"]["summary"]["short_timely"]
                          - summary["carry"]["summary"]["short_timely"]) / 144
        if abs(diff - expected) > 1e-8 or not low <= diff <= high:
            raise ValueError(f"paired C03 contrast inconsistent for {plant}")
        ax_delta.axvline(0, color="#59666B", lw=.8, ls=(0, (3, 2)))
        ax_delta.errorbar(diff, 0, xerr=[[diff-low], [high-diff]], fmt="o",
                          color=COLORS["history"], capsize=3, lw=1.4)
        ax_delta.text(.5, .82, f"{diff:+.1f} pp\n[{low:+.1f}, {high:+.1f}]",
                      transform=ax_delta.transAxes, ha="center", va="center", fontsize=7)
        ax_delta.set_yticks([])
        ax_delta.set_xlim(-20, 55)
        ax_delta.set_ylim(-.5, .5)
        ax_delta.set_xlabel("History − carry (pp)")
        ax_delta.set_title(f"({chr(99+3*row)}) {plant}: coverage gain", loc="left", fontweight="bold")
        ax_delta.spines[["top", "right", "left"]].set_visible(False)
        ax_delta.spines["bottom"].set_color("#CBD3D7")
        ax_delta.grid(axis="x", color="#DDE3E5", lw=.5)
        ax_delta.set_axisbelow(True)
        ax_delta.tick_params(length=0, labelsize=7)
    fig.suptitle("Recovery histories: coverage gain on F01, inconclusive on P2", x=.02,
                 ha="left", fontsize=10, fontweight="bold")
    fig.text(.02, .035,
             "Primary denominator: 144 short-gap interventions per arm and plant. "
             "Extras are event-record alarms, distinct from normal false alarms.", fontsize=7, color="#4C5D67")
    return fig


def emit_macros(report: dict) -> None:
    """Emit all supplemental counts from the imported result, never by hand."""
    lines = ["% Generated from the immutable imported C03 TEST result. Do not edit."]
    def put(name: str, value) -> None:
        if isinstance(value, float):
            value = f"{value:.2f}"
        lines.append(r"\newcommand{\CThree" + name + "}{" + str(value) + "}")
    validation = report["_validation"]["validation"]
    for plant in ("F01", "P2"):
        short = plant.replace("0", "Zero").replace("1", "One").replace("2", "Two")
        put("Audit" + short + "EventParents", validation["plants"][plant]["event_parents"])
        put("Audit" + short + "NormalParents", validation["plants"][plant]["normal_parents"])
        for arm, label in (("history", "History"), ("carry", "Carry"), ("reset", "Reset")):
            s = report["results"][plant]["nominal"][arm]["summary"]
            pre = "Audit" + short + label
            for key, suffix in (("short_timely", "Short"), ("all_timely", "All"),
                                ("extras", "Extras"), ("early_restorations", "EarlyOFF"),
                                ("unmatched_restorations", "OrphanOFF"),
                                ("normal_alarms", "NormalAlarms"), ("parents", "Parents"),
                                ("events", "Events"), ("short_events", "ShortN"),
                                ("event_hours", "EventHours"), ("normal_hours", "NormalHours"),
                                ("normal_upper95_poisson", "NormalUpper")):
                put(pre + suffix, s[key])
            put(pre + "ExtrasPerHour", s["extras"] / s["event_hours"])
        for stress in ("dropout", "noise"):
            s = report["results"][plant][stress]["summary"]
            pre = "Audit" + short + stress.title()
            for key, suffix in (("events", "Events"), ("short_events", "ShortN"),
                                ("short_timely", "ShortTimely"), ("all_timely", "AllTimely"),
                                ("extras", "Extras"), ("normal_alarms", "NormalAlarms"),
                                ("normal_hours", "NormalHours"), ("normal_upper95_poisson", "NormalUpper"),
                                ("early_restorations", "EarlyOFF"),
                                ("unmatched_restorations", "OrphanOFF"),
                                ("unavailable", "Unavailable"), ("parents", "Parents"),
                                ("wall_seconds", "WallSeconds")):
                put(pre + suffix, "--" if s[key] is None else s[key])
            put(pre + "Available", s["parents"] - s["unavailable"])
            put(pre + "ExtrasPerHour", "--" if s["extras_per_hour"] is None else s["extras_per_hour"])
            comparison = report["results"][plant][stress]["versus_nominal"]
            for k, suffix in (("coverage", "Coverage"), ("extras_per_hour", "Extras")):
                q = comparison[k]
                for field, tail in (("difference", "Diff"), ("lower95", "Lower"), ("upper95", "Upper")):
                    scale = 100 if k == "coverage" else 1
                    put(pre + suffix + tail, "--" if q is None else q[field] * scale)
    MACROS.write_text("\n".join(lines) + "\n", encoding="utf-8")


def emit_supplement() -> None:
    # Values are macros generated above from the imported, validated JSON.
    body = r'''% Generated by scripts/build_c03_figures.py from sealed imported TEST_RESULTS.json.
\input{generated/c03_extended_macros}
\section{C03: Sealed History, Carry, and Reset Comparison}
\label{app:c03-results}
Each nominal plant-arm includes \CThreeAuditFZeroOneEventParents{} event and
\CThreeAuditFZeroOneNormalParents{} normal parents in F01, and \CThreeAuditPTwoEventParents{} event and \CThreeAuditPTwoNormalParents{} normal parents in P2; each arm scores \CThreeAuditFZeroOneHistoryEvents{} interventions and \CThreeAuditFZeroOneHistoryShortN{} primary short-gap interventions in F01 and \CThreeAuditPTwoHistoryEvents{}/\CThreeAuditPTwoHistoryShortN{} in P2. The design retained both event
and normal records;
No parent was unavailable in nominal
evaluation. Event extras, restoration errors, and normal alarms use distinct
definitions.

\begin{table*}[t]\centering\small
\caption{C03 nominal held-out results. Normal upper bounds are one-sided
95\% Poisson bounds; extras are unmatched alarms during event records.}
\label{tab:c03-nominal}
\begin{tabular}{llrrrrrrrr}
Plant & Arm & Short timely & All timely & Extras & Extras/h & Early OFF & Orphan OFF & Normal alarms & $U_{95}$/h\\\hline
F01 & History & \CThreeAuditFZeroOneHistoryShort/\CThreeAuditFZeroOneHistoryShortN & \CThreeAuditFZeroOneHistoryAll/\CThreeAuditFZeroOneHistoryEvents & \CThreeAuditFZeroOneHistoryExtras & \CThreeAuditFZeroOneHistoryExtrasPerHour & \CThreeAuditFZeroOneHistoryEarlyOFF & \CThreeAuditFZeroOneHistoryOrphanOFF & \CThreeAuditFZeroOneHistoryNormalAlarms & \CThreeAuditFZeroOneHistoryNormalUpper\\
F01 & Carry & \CThreeAuditFZeroOneCarryShort/\CThreeAuditFZeroOneHistoryShortN & \CThreeAuditFZeroOneCarryAll/\CThreeAuditFZeroOneHistoryEvents & \CThreeAuditFZeroOneCarryExtras & \CThreeAuditFZeroOneCarryExtrasPerHour & \CThreeAuditFZeroOneCarryEarlyOFF & \CThreeAuditFZeroOneCarryOrphanOFF & \CThreeAuditFZeroOneCarryNormalAlarms & \CThreeAuditFZeroOneCarryNormalUpper\\
F01 & Reset & \CThreeAuditFZeroOneResetShort/\CThreeAuditFZeroOneHistoryShortN & \CThreeAuditFZeroOneResetAll/\CThreeAuditFZeroOneHistoryEvents & \CThreeAuditFZeroOneResetExtras & \CThreeAuditFZeroOneResetExtrasPerHour & \CThreeAuditFZeroOneResetEarlyOFF & \CThreeAuditFZeroOneResetOrphanOFF & \CThreeAuditFZeroOneResetNormalAlarms & \CThreeAuditFZeroOneResetNormalUpper\\
P2 & History & \CThreeAuditPTwoHistoryShort/\CThreeAuditFZeroOneHistoryShortN & \CThreeAuditPTwoHistoryAll/\CThreeAuditFZeroOneHistoryEvents & \CThreeAuditPTwoHistoryExtras & \CThreeAuditPTwoHistoryExtrasPerHour & \CThreeAuditPTwoHistoryEarlyOFF & \CThreeAuditPTwoHistoryOrphanOFF & \CThreeAuditPTwoHistoryNormalAlarms & \CThreeAuditPTwoHistoryNormalUpper\\
P2 & Carry & \CThreeAuditPTwoCarryShort/\CThreeAuditFZeroOneHistoryShortN & \CThreeAuditPTwoCarryAll/\CThreeAuditFZeroOneHistoryEvents & \CThreeAuditPTwoCarryExtras & \CThreeAuditPTwoCarryExtrasPerHour & \CThreeAuditPTwoCarryEarlyOFF & \CThreeAuditPTwoCarryOrphanOFF & \CThreeAuditPTwoCarryNormalAlarms & \CThreeAuditPTwoCarryNormalUpper\\
P2 & Reset & \CThreeAuditPTwoResetShort/\CThreeAuditFZeroOneHistoryShortN & \CThreeAuditPTwoResetAll/\CThreeAuditFZeroOneHistoryEvents & \CThreeAuditPTwoResetExtras & \CThreeAuditPTwoResetExtrasPerHour & \CThreeAuditPTwoResetEarlyOFF & \CThreeAuditPTwoResetOrphanOFF & \CThreeAuditPTwoResetNormalAlarms & \CThreeAuditPTwoResetNormalUpper\\\hline
\end{tabular}\end{table*}

The paired primary coverage contrasts are history-minus-carry
\CThreeFOneHistoryCarryDifferencePP{} percentage points (95\% interval
\CThreeFOneHistoryCarryLowerPP{}--\CThreeFOneHistoryCarryUpperPP{}) in F01
and \CThreePTwoHistoryCarryDifferencePP{} points (95\% interval
\CThreePTwoHistoryCarryLowerPP{}--\CThreePTwoHistoryCarryUpperPP{}) in P2.
Carry-minus-reset is \CThreeFOneCarryResetDifferencePP{} points in F01 and
\CThreePTwoCarryResetDifferencePP{} in P2. The frozen decision is
\texttt{HISTORY\_ADVANTAGE\_F01\_ONLY}. Paired intervals resample parent
units as encoded in the sealed result; intervention rows within a parent
are not treated as independent. Early OFF counts premature closure of a
matched event; orphan OFF counts restorations without a matched event.

\begin{table*}[t]\centering\small
\caption{Stress cohorts under nominally selected thresholds. CAL was not
repeated for these cohorts.}
\label{tab:c03-stress}
\begin{tabular}{llrrrrrrrr}
Plant & Stress & Available & Timely / primary & Events & Extras & Normal alarms / h & $U_{95}$/h & Early OFF & Orphan OFF\\\hline
F01 & Dropout & \CThreeAuditFZeroOneDropoutAvailable/\CThreeAuditFZeroOneDropoutParents & \CThreeAuditFZeroOneDropoutShortTimely/\CThreeAuditFZeroOneDropoutShortN & \CThreeAuditFZeroOneDropoutEvents & \CThreeAuditFZeroOneDropoutExtras & \CThreeAuditFZeroOneDropoutNormalAlarms/\CThreeAuditFZeroOneDropoutNormalHours & \CThreeAuditFZeroOneDropoutNormalUpper & \CThreeAuditFZeroOneDropoutEarlyOFF & \CThreeAuditFZeroOneDropoutOrphanOFF\\
P2 & Dropout & \CThreeAuditPTwoDropoutAvailable/\CThreeAuditPTwoDropoutParents & \CThreeAuditPTwoDropoutShortTimely/\CThreeAuditPTwoDropoutShortN & \CThreeAuditPTwoDropoutEvents & \CThreeAuditPTwoDropoutExtras & \CThreeAuditPTwoDropoutNormalAlarms/\CThreeAuditPTwoDropoutNormalHours & \CThreeAuditPTwoDropoutNormalUpper & \CThreeAuditPTwoDropoutEarlyOFF & \CThreeAuditPTwoDropoutOrphanOFF\\
F01 & Independent noise & \CThreeAuditFZeroOneNoiseAvailable/\CThreeAuditFZeroOneNoiseParents & -- (planned N=\CThreeAuditFZeroOneNoiseShortN) & \CThreeAuditFZeroOneNoiseEvents & -- & -- & -- & -- & --\\
P2 & Independent noise & \CThreeAuditPTwoNoiseAvailable/\CThreeAuditPTwoNoiseParents & -- (planned N=\CThreeAuditPTwoNoiseShortN) & \CThreeAuditPTwoNoiseEvents & -- & -- & -- & -- & --\\\hline
\end{tabular}\end{table*}

The dropout cohort contains the stress-parent denominator encoded above. Stress-minus-nominal paired contrasts use the same parent subset. F01 short-gap coverage changed by \CThreeAuditFZeroOneDropoutCoverageDiff percentage points (95\% interval \CThreeAuditFZeroOneDropoutCoverageLower--\CThreeAuditFZeroOneDropoutCoverageUpper); P2 changed by \CThreeAuditPTwoDropoutCoverageDiff points (95\% interval \CThreeAuditPTwoDropoutCoverageLower--\CThreeAuditPTwoDropoutCoverageUpper). Event extras changed by \CThreeAuditFZeroOneDropoutExtrasDiff/h for F01 and \CThreeAuditPTwoDropoutExtrasDiff/h for P2. Interpret both outcomes jointly. The independent-noise cohort had no available parents; its realized hours and runtime are \CThreeAuditFZeroOneNoiseNormalHours{} and \CThreeAuditFZeroOneNoiseWallSeconds{} for F01, and \CThreeAuditPTwoNoiseNormalHours{} and \CThreeAuditPTwoNoiseWallSeconds{} for P2. Inspection of immutable rejection
metadata found every noise arm failed during prefix fitting because the
estimated voltage-angle noise scale exceeded the frozen support. This is a
model-support failure under
the configured 0.05\% TVE stress, not a measured coverage outcome.
No noise robustness estimate is supported. A repair would require a new
candidate with a calibrated support and independent CAL/TEST; old sealed
results remain unchanged.
'''
    SUPPLEMENT.write_text(body, encoding="utf-8")


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig = build(read_result())
    fig.savefig(OUT, bbox_inches="tight", pad_inches=.08)
    plt.close(fig)
    report = read_result()
    emit_macros(report)
    emit_supplement()
    print(f"Built {OUT.relative_to(ROOT)} from sealed C03 result {EXPECTED_RESULT}.")

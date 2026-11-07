"""Figure and macros for the measurement-integrity analysis (revision 2026-11-04).

Inputs (generated/revision_20261104/): integrity_raw0001*.json/series.csv,
integrity_coupling.json, integrity_information.csv/json and the copied
simulation stress summary integrity_stress.json.  Outputs:
figures/generated/integrity.pdf/png and generated/revision_integrity_macros.tex.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REV = ROOT / "generated/revision_20261104"
OUT = ROOT / "figures/generated"
BLUE, TEAL, ORANGE, DARK, GRAY, LIGHT = "#006a92", "#008f79", "#c46b22", "#263b49", "#777777", "#c9c9c9"
PMUS = [2, 5, 6, 10, 19, 22, 29, 39]
NEED = 15.0


def style() -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7.6, "axes.spines.top": False,
                         "axes.spines.right": False, "axes.edgecolor": "#8a8a8a", "axes.linewidth": .6,
                         "xtick.color": "#444444", "ytick.color": "#444444", "axes.labelcolor": DARK,
                         "xtick.major.width": .5, "ytick.major.width": .5, "legend.frameon": False})


def figure() -> None:
    ser = pd.read_csv(REV / "integrity_raw0001_series.csv")
    pre = json.loads((REV / "integrity_raw0001.json").read_text())
    inf = json.loads((REV / "integrity_raw0001_inflated.json").read_text())
    cp = json.loads((REV / "integrity_coupling.json").read_text())["per_pmu"]
    info = pd.read_csv(REV / "integrity_information.csv")
    fig, axes = plt.subplots(1, 3, figsize=(7.1, 2.35), gridspec_kw=dict(width_ratios=[1.15, 1, 1.05]))

    # (A) sequence parity at PMU 2: labeled corruption and two unlabeled spikes
    ax = axes[0]
    w = ser[(ser.time_s >= 2.5) & (ser.time_s < 13.0)]
    ax.axvspan(3.266, 3.966, color=LIGHT, alpha=.6, lw=0)
    ax.text(3.62, 3e5, "labeled\ncorruption", ha="center", va="top", fontsize=6, color=DARK)
    ax.plot(w.time_s, w.stat_2.clip(lower=1e-2), color=BLUE, lw=.7)
    ax.axhline(pre["threshold_gamma2"], color=DARK, lw=.8, ls="--")
    ax.axhline(inf["threshold_gamma2"], color=DARK, lw=.6, ls=":")
    ax.text(5.0, inf["threshold_gamma2"] * 1.5, "thresholds", ha="left", va="bottom", fontsize=6, color=DARK)
    for ts, yv in ((11.566, 1.5e5), (12.333, 1.2e4)):
        ax.annotate("", xy=(ts, yv), xytext=(9.7, 2.5e3), arrowprops=dict(arrowstyle="-", color=ORANGE, lw=.6))
    ax.text(9.6, 2.5e3, "unlabeled\nspikes", ha="right", va="center", fontsize=6, color=ORANGE)
    ax.set_yscale("log")
    ax.set_ylim(1e-2, 1e6)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Sequence-parity statistic, PMU 2")
    ax.set_title("(A) Per-phase corruption", fontsize=7.6, loc="left")

    # (B) network coupling: fault reports vs the balanced bus-29 excursion
    ax = axes[1]
    dv = ser[[f"dv_{b}" for b in PMUS]].to_numpy()
    dom = np.nanargmax(np.nan_to_num(dv, nan=-1), axis=1)
    x = dv[np.arange(len(dv)), dom]
    others = np.array([np.nanmax(np.delete(dv[k], dom[k])) for k in range(len(dv))])
    big = x > 0.10
    fault = big & (ser.time_s.between(1172.5, 1179.0)).to_numpy()
    b29 = big & (ser.time_s.between(2776.0, 2779.5)).to_numpy()
    ax.scatter(x[fault], others[fault], s=9, color=BLUE, label="three-phase fault, bus 39", zorder=3)
    ax.scatter(x[b29], np.maximum(others[b29], 1e-4), s=9, color=ORANGE, marker="s",
               label="unlabeled excursion, PMU 29", zorder=3)
    xx = np.logspace(-1, .3, 20)
    for b, ls in [(39, "-"), (29, "--")]:
        ax.plot(xx, cp[str(b)]["coupling"] * xx, color=DARK, lw=.7, ls=ls)
        ax.text(xx[-1], cp[str(b)]["coupling"] * xx[-1] * (1.15 if b == 39 else .55), f"$c_{{{b}}}$", fontsize=6.4,
                ha="right", va="bottom" if b == 39 else "top", color=DARK)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(.09, 2.2); ax.set_ylim(5e-5, 2)
    ax.set_xlabel("Balanced change at dominant PMU")
    ax.set_ylabel("Largest change at other PMUs")
    ax.legend(loc="lower right", fontsize=5.8, handletextpad=.2, borderaxespad=.1)
    ax.set_title("(B) Network-coupling test", fontsize=7.6, loc="left")

    # (C) information left with one PMU missing or corrupted
    ax = axes[2]
    for i, b in enumerate(PMUS):
        v = info[f"without_{b}"] / NEED
        jit = (np.arange(len(v)) % 6 - 2.5) * .07
        for fam, col in [("load", BLUE), ("line", ORANGE)]:
            m = (info.family == fam).to_numpy()
            ax.scatter(i + jit[m], v[m], s=6, color=col, lw=0, label=fam if i == 0 else None)
    ax.axhline(1, color=DARK, lw=.8, ls="--")
    ax.text(7.4, 1.4, "alarm evidence", ha="right", fontsize=6, color=DARK)
    ax.set_yscale("log")
    ax.set_xticks(range(8), [str(b) for b in PMUS], fontsize=6.4)
    ax.set_xlabel("Missing or corrupted PMU (bus)")
    ax.set_ylabel(r"$\Lambda^{(-p)}/\lambda^\star$ in 1 s")
    ax.legend(loc="lower left", bbox_to_anchor=(0, .09), fontsize=6, handletextpad=.1, borderaxespad=.1, ncol=2)
    ax.set_ylim(.3, 1e7)
    ax.set_title("(C) Information without one PMU", fontsize=7.6, loc="left")
    fig.tight_layout(w_pad=1.0)
    fig.savefig(OUT / "integrity.pdf", bbox_inches="tight", pad_inches=0.055)
    fig.savefig(OUT / "integrity.png", dpi=210, bbox_inches="tight", pad_inches=0.055)
    plt.close(fig)


def incidents(det: pd.DataFrame) -> int:
    """Unlabeled, non-transient detections merged into incidents (same PMU, gaps below 2 s)."""
    u = det[~det.labeled_corruption & det.after_physical_onset_s.isna()].sort_values(["pmu", "start_s"])
    n, last = 0, {}
    for _, r in u.iterrows():
        prev = last.get(r.pmu)
        if prev is None or r.reports == 1 or prev[1] == 1 or r.start_s - prev[0] > 2.0:
            n += 1
        last[r.pmu] = (r.end_s, r.reports)
    return n


def macros() -> None:
    pre = json.loads((REV / "integrity_raw0001.json").read_text())
    inf = json.loads((REV / "integrity_raw0001_inflated.json").read_text())
    cp = json.loads((REV / "integrity_coupling.json").read_text())
    ii = json.loads((REV / "integrity_information.json").read_text())
    st = json.loads((REV / "integrity_stress.json").read_text()) if (REV / "integrity_stress.json").exists() else {}
    det_pre = pd.DataFrame(pre["detections"]); det_inf = pd.DataFrame(inf["detections"])
    noise_pre = det_pre[~det_pre.labeled_corruption & det_pre.after_physical_onset_s.isna() & (det_pre.max_statistic < inf["threshold_gamma2"])
                        & (det_pre.mechanism == "sequence parity")]
    c = {b: v["coupling"] for b, v in cp["per_pmu"].items()}
    lab = pd.DataFrame(pre["labeled"])
    cor = lab[lab.kind == "corrupted"]
    m = {
        "IntCorrDet": f"{pre['n_labeled_corruption_detected']}", "IntCorrTot": f"{pre['n_labeled_corruption']}",
        "IntMissDet": f"{pre['n_labeled_missing_detected']}", "IntMissTot": f"{pre['n_labeled_missing']}",
        "IntMissReports": f"{pre['missing_reports']}",
        "IntPhaseOK": f"{int((cor.true_phase == cor.identified_phase).sum())}",
        "IntUnlabeled": f"{incidents(det_inf)}",
        "IntSwitching": f"{inf['n_switching_transients']}",
        "IntSwitchRate": f"{inf['switching_false_alarms_per_min']:.3f}",
        "IntNoiseExceed": f"{len(noise_pre)}",
        "IntNoiseRate": f"{len(noise_pre) / pre['monitored_minutes']:.2f}",
        "IntMinutes": f"{pre['monitored_minutes']:.1f}",
        "IntTau": f"{pre['threshold_gamma2']:.1f}", "IntTauInf": f"{inf['threshold_gamma2']:.1f}",
        "IntCouplingMin": f"{min(c.values()):.2f}", "IntCouplingMax": f"{max(c.values()):.2f}",
        "IntCouplingTwentyNine": f"{c['29']:.2f}", "IntCouplingThirtyNine": f"{c['39']:.2f}",
        "IntInfoMinFactor": f"{ii['min_worst_over_alarm']:.0f}",
        "IntInfoMedianFraction": f"{100 * ii['median_worst_fraction']:.0f}",
        "IntInfoMinFraction": f"{100 * ii['min_worst_fraction']:.0f}",
    }
    for k, v in st.items():
        m[k] = str(v)
    lines = ["% Generated by scripts/build_integrity_figure.py; do not edit."]
    lines += [f"\\newcommand{{\\{k}}}{{{v}}}" for k, v in m.items()]
    (ROOT / "generated/revision_integrity_macros.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


def table() -> None:
    pre = json.loads((REV / "integrity_raw0001.json").read_text())
    lab = pd.DataFrame(pre["labeled"]).sort_values("start_s")
    lines = [r"\begin{table}[t]\centering\small",
             r"\caption{Labeled integrity episodes of the competition record and their diagnosis. Delay is in reports "
             r"after the first labeled report; ``flagged'' counts diagnosed reports within the episode; phase is identified (labeled-data phase). Every episode was located at the correct PMU.}",
             r"\label{tab:integrity-raw}",
             r"\footnotesize\setlength{\tabcolsep}{3.5pt}\begin{tabular}{@{}llrrrrl@{}}\toprule",
             r"Type & PMU & Start (s) & Length (s) & Delay & Flagged & Phase\\\midrule"]
    for _, r in lab.iterrows():
        kind = "Missing" if r.kind == "missing" else "Corrupted"
        ph = "--" if r.kind == "missing" else f"{r.identified_phase} ({r.true_phase})"
        loc = "" if r.located == [r.pmu] else "*"
        lines.append(f"{kind} & {r.pmu}{loc} & {r.start_s:.1f} & {r.duration_s:.2f} & {r.delay_reports} & "
                     f"{r.reports_flagged}/{r.reports} & {ph}\\\\")
    lines += [r"\bottomrule\end{tabular}\end{table}"]
    (ROOT / "tables/generated/integrity_raw0001.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    style()
    figure()
    macros()
    table()

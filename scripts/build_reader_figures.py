"""Reader-facing figures from frozen development and C01 evidence.

This script only creates successor figures. It does not regenerate either
protected illustration or change predictions, scores, or campaign outputs.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from monitored_exposure import corrected_intervals


ROOT = Path(__file__).resolve().parents[1]
DEV = ROOT / "generated/frozen/narrative_case_20261030"
C01 = ROOT / "generated/frozen/c01_20261029"
OUT = ROOT / "figures/generated"
BLUE, TEAL, ORANGE, DARK, GRAY = "#006a92", "#008f79", "#c46b22", "#263b49", "#777777"
METHODS = ["R11", "R11_NOMINAL", "ET_REFERENCE", "ET_CANDIDATE"]
LABELS = ["Physical bank", "Nominal bank", "ExtraTrees", "ExtraTrees short"]
COLORS = [BLUE, TEAL, "#666666", "#aaaaaa"]


def verify_manifest(folder: Path) -> str:
    path = folder / "MANIFEST.json"
    data = path.read_bytes()
    manifest = json.loads(data)
    for item in manifest["files"]:
        content = (folder / item["path"]).read_bytes()
        actual = hashlib.sha256(content).hexdigest()
        if actual != item["sha256"]:
            # Git's Windows checkout has converted this one text inventory
            # from LF to CRLF. Verify its canonical bytes without rewriting it.
            canonical = hashlib.sha256(content.replace(b"\r\n", b"\n")).hexdigest()
            if not (folder == DEV and item["path"] == "branch.csv" and
                    canonical == item["sha256"]):
                raise RuntimeError(f"Frozen input changed: {item['path']}")
    return hashlib.sha256(data).hexdigest()


def save(fig, stem: str) -> None:
    fig.savefig(OUT / f"{stem}.pdf", bbox_inches="tight", pad_inches=0.055)
    fig.savefig(OUT / f"{stem}.png", dpi=210, bbox_inches="tight", pad_inches=0.055)
    plt.close(fig)


def load_development():
    records = {}
    for path in (DEV / "evaluation").glob("*.json"):
        item = json.loads(path.read_text(encoding="utf-8"))
        records[item["case"]["condition"]] = (item["record"]["id"], item["case"])
    assert set(records) == {"MATCH", "OUT_SUPPORT"}
    return records


def observed_signals(records) -> None:
    record_id, case = records["MATCH"]
    with np.load(DEV / "observed" / f"{record_id}.npz") as z:
        obs = {key: z[key].copy() for key in z.files}
    events = [next(e for e in case["events"] if e["family"] == family)
              for family in ("load", "line")]
    fig, axes = plt.subplots(2, 2, figsize=(7.1, 3.1), sharex="col",
                             layout="constrained")
    pmus = [(0, "PMU 2", BLUE), (7, "PMU 39", ORANGE)]
    time = obs["time_s"]
    for col, event in enumerate(events):
        onset, off = event["onset_s"], event["off_s"]
        shown = (time >= onset - .55) & (time <= off + 1.35)
        prefix = (time >= onset - .55) & (time < onset - .12)
        x = time[shown] - onset
        for row in range(2):
            ax = axes[row, col]
            for index, _, color in pmus:
                if row == 0:
                    signal = obs["current_magnitude"][:, index]
                    center = np.nanmedian(signal[prefix])
                    value = 100 * (signal[shown] / center - 1)
                else:
                    value = obs["rocof"][shown, index]
                ax.plot(x, value, color=color, lw=1.05)
            ax.axvspan(0, off - onset, color="#e9eceb", zorder=-1)
            ax.axvline(off - onset, color=DARK, ls="--", lw=.8)
            ax.axhline(0, color="#b6b6b6", lw=.55)
            ax.grid(axis="y", color="#e9e9e9", lw=.55)
        axes[0, col].set_title("Load at bus 24" if col == 0 else "Open line 9–39", pad=5)
        axes[1, col].set_xlabel("Time since ON (s)")
        axes[0, col].text(off - onset + .05, axes[0, col].get_ylim()[1] * .77,
                          "OFF", fontsize=7, color=DARK)
    axes[0, 0].set_ylabel("Terminal current change (%)")
    axes[1, 0].set_ylabel("ROCOF (Hz/s)")
    fig.legend([Line2D([], [], color=c, lw=1.5) for _, _, c in pmus],
               [name for _, name, _ in pmus], ncol=2, loc="outside upper center",
               frameon=False, bbox_to_anchor=(.5, 1.075))
    save(fig, "reader_observed_signals")


def episode_story(records) -> None:
    _, truth_case = records["MATCH"]
    truth = truth_case["events"]
    fig = plt.figure(figsize=(7.1, 3.6), layout="constrained")
    gs = fig.add_gridspec(2, 1, height_ratios=[1.55, 1], hspace=.20)
    ax = fig.add_subplot(gs[0])
    levels = {"truth": 2, "MATCH": 1, "OUT_SUPPORT": 0}
    for event in truth:
        color = BLUE if event["family"] == "load" else ORANGE
        ax.broken_barh([(event["onset_s"], event["off_s"] - event["onset_s"])],
                       (levels["truth"] - .11, .22), facecolors=color)
        name = event["source"].replace("LINE", "L").replace("BUS", "B")
        ax.text(event["onset_s"], 2.16, name, fontsize=6.5, color=DARK)
    for condition in ("MATCH", "OUT_SUPPORT"):
        record_id, _ = records[condition]
        messages = json.loads((DEV / "prediction" / f"{record_id}.json").read_text())["events"]
        level = levels[condition]
        for message in messages:
            if message["kind"] != "diagnosis":
                continue
            t = message["emitted_s"]
            on_time = any(e["source"] == message["source"] and
                          e["onset_s"] <= t <= e["off_s"] for e in truth)
            ax.scatter(t, level, color=TEAL if on_time else "#c1372c",
                       marker="o" if on_time else "X", s=31 if on_time else 45,
                       zorder=4, edgecolors="white", linewidths=.45)
            if condition == "OUT_SUPPORT" and not on_time:
                if message["source"] == "BUS20":
                    ax.annotate("extra: bus 20", (t, level), xytext=(t - 3.7, .42),
                                textcoords="data", fontsize=7, color="#a82c26",
                                arrowprops={"arrowstyle": "-", "color": "#a82c26", "lw": .6})
                elif message["source"] == "BUS31":
                    ax.annotate("bus 31 after OFF", (t, level), xytext=(t + .7, .42),
                                textcoords="data", fontsize=7, color="#a82c26",
                                arrowprops={"arrowstyle": "-", "color": "#a82c26", "lw": .6})
    ax.set_yticks([0, 1, 2], ["R/X outside bank", "Matched network", "True ON–OFF"])
    ax.set_xlim(14, 57)
    ax.set_ylim(-.53, 2.47)
    ax.set_xlabel("Time (s)")
    ax.grid(axis="x", alpha=.16)
    ax.set_title("Six interventions in one state-continuous record", loc="left", fontsize=9)
    ax2 = fig.add_subplot(gs[1])
    for condition, label, color, style in [
        ("MATCH", "Matched R/X", BLUE, "-"),
        ("OUT_SUPPORT", "R/X outside bank", ORANGE, "--"),
    ]:
        record_id, _ = records[condition]
        with np.load(DEV / "prediction" / f"{record_id}_compact.npz") as z:
            t = z["time_s"].copy()
            mass = z["M"].copy()
        assets = json.loads((DEV / "assets.json").read_text())
        index = next(i for i, item in enumerate(assets) if item["id"] == "BUS31")
        window = (t >= 37.2) & (t <= 42)
        ax2.plot(t[window], mass[window, index], color=color, ls=style, lw=1.5, label=label)
    bus31 = next(e for e in truth if e["source"] == "BUS31")
    ax2.axvspan(bus31["onset_s"], bus31["off_s"], color="#e9eceb", zorder=-1)
    ax2.axvline(bus31["off_s"], color=DARK, ls=":", lw=.85)
    ax2.text(bus31["off_s"] + .03, .12, "physical OFF", fontsize=6.7)
    ax2.set_xlim(37.2, 42)
    ax2.set_ylim(-.05, 1.09)
    ax2.set_ylabel("Active mass: bus 31")
    ax2.set_xlabel("Time (s)")
    ax2.legend(loc="upper left", ncol=2, frameon=False, fontsize=7)
    ax2.grid(axis="y", alpha=.15)
    save(fig, "reader_episode_story")


def c01_tradeoff(summary: pd.DataFrame, by_source: pd.DataFrame) -> None:
    continuous = summary[summary.lane == "continuous"]
    family = by_source[by_source.lane == "continuous"].groupby(["method", "family"])[["events", "timely"]].sum()
    assert sum(family.loc[("R11", family_name), "timely"] for family_name in ("load", "line")) == 644
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(7.1, 3.15),
                                 gridspec_kw={"width_ratios": [1.12, 1]}, layout="constrained")
    y = np.arange(4)
    for i, method in enumerate(METHODS):
        load = int(family.loc[(method, "load"), "timely"])
        line = int(family.loc[(method, "line"), "timely"])
        ax.barh(i - .16, load, height=.30, color=BLUE)
        ax.barh(i + .16, line, height=.30, color=ORANGE)
        ax.text(load + 4, i - .16, str(load), va="center", fontsize=7)
        ax.text(line + 4, i + .16, str(line), va="center", fontsize=7)
    ax.set_yticks(y, LABELS)
    ax.invert_yaxis()
    ax.set_xlim(0, 350)
    ax.set_xlabel("Correct family + source before OFF / 324")
    ax.set_title("A. Benefit is concentrated in loads", loc="left", fontsize=9)
    ax.legend([Line2D([], [], color=BLUE, lw=5), Line2D([], [], color=ORANGE, lw=5)],
              ["Load", "Line"], loc="lower center", bbox_to_anchor=(.52, -.34),
              ncol=2, frameon=False, fontsize=7)
    ax.grid(axis="x", alpha=.13)
    conditions = ["MATCH", "RX_IN_SUPPORT", "RX_OUT_SUPPORT"]
    x = np.arange(3)
    for method, label, color in zip(METHODS, LABELS, COLORS):
        value = [int(continuous[(continuous.method == method) &
                                 (continuous.condition == cond)].event_extras.sum())
                 for cond in conditions]
        bx.plot(x, value, color=color, marker="o", lw=1.3, ms=4, label=label)
        if method == "R11":
            bx.annotate("68", (2, value[2]), xytext=(-8, 7),
                        textcoords="offset points", color=color, fontsize=7)
    bx.set_xticks(x, ["Matched", "R/X in bank", "R/X outside"], fontsize=7)
    bx.set_xlim(-.18, 2.18)
    bx.set_ylim(-3, 96)
    bx.set_ylabel("Extra alarms / 216 event realizations")
    bx.set_title("B. Mismatch increases unmatched alarms", loc="left", fontsize=9)
    bx.legend(loc="upper left", frameon=False, fontsize=6.5, ncol=2)
    bx.grid(axis="y", alpha=.13)
    save(fig, "reader_c01_tradeoff")


def c01_intervals(intervals: pd.DataFrame) -> None:
    rows = intervals[(intervals.lane == "continuous") &
                     (intervals.method == "R11") &
                     (intervals.reference == "ET_REFERENCE")]
    order = [("MATCH", 1.0), ("MATCH", 2.0),
             ("RX_IN_SUPPORT", 1.0), ("RX_IN_SUPPORT", 2.0),
             ("RX_OUT_SUPPORT", 1.0), ("RX_OUT_SUPPORT", 2.0)]
    names = ["Matched · noise ×1", "Matched · noise ×2",
             "R/X in bank · ×1", "R/X in bank · ×2",
             "R/X outside · ×1", "R/X outside · ×2"]
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(7.1, 2.65), sharey=True,
                                 gridspec_kw={"width_ratios": [1, 1.1]}, layout="constrained")
    for axis, metric, factor in [(ax, "timely_fraction", 100),
                                 (bx, "extras_per_event_hour", 1)]:
        axis.axhspan(3.5, 5.5, color="#fff3e8", zorder=-2)
        axis.axvline(0, color=DARK, lw=.9)
        for i, (condition, noise) in enumerate(order):
            r = rows[(rows.condition == condition) & (rows.noise == noise) &
                     (rows.metric == metric)].iloc[0]
            color = ORANGE if condition == "RX_OUT_SUPPORT" else BLUE
            center = float(r.difference) * factor
            lo, hi = float(r.lower95) * factor, float(r.upper95) * factor
            axis.errorbar(center, i, xerr=[[center - lo], [hi - center]], fmt="o",
                          color=color, capsize=2, lw=1.1, ms=4.2)
        axis.set_ylim(5.6, -.6)
        axis.grid(axis="x", alpha=.12)
    ax.set_yticks(range(6), names, fontsize=7)
    ax.set_xlim(35, 60)
    alarm_rows=rows[rows.metric=='extras_per_event_hour']
    span=float(alarm_rows.upper95.max()-alarm_rows.lower95.min())
    bx.set_xlim(float(alarm_rows.lower95.min())-.1*span,float(alarm_rows.upper95.max())+.1*span)
    ax.set_xlabel("Timely gain (percentage points)")
    bx.set_xlabel("Extra alarms / monitored event-hour: difference")
    ax.set_title("A. More events attributed in time", loc="left", fontsize=9)
    bx.set_title("B. More unmatched alarms with R/X mismatch", loc="left", fontsize=9)
    fig.suptitle("Physical bank minus frozen ExtraTrees reference; 95% parent-cluster intervals",
                 fontsize=8.5)
    save(fig, "reader_c01_intervals")


def main() -> None:
    dev_hash = verify_manifest(DEV)
    c01_hash = verify_manifest(C01)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7.6,
                         "pdf.fonttype": 42, "axes.spines.top": False,
                         "axes.spines.right": False})
    records = load_development()
    observed_signals(records)
    episode_story(records)
    summary = pd.read_csv(C01 / "SUMMARY.csv")
    by_source = pd.read_csv(C01 / "BY_SOURCE.csv")
    intervals = corrected_intervals()
    c01_tradeoff(summary, by_source)
    c01_intervals(intervals)
    family = by_source[by_source.lane == "continuous"].groupby(["method", "family"])[["events", "timely"]].sum()
    extras = summary[summary.lane == "continuous"].groupby(["method", "condition"])["event_extras"].sum()
    macros = {
        "ReaderPhysicalLoad": int(family.loc[("R11", "load"), "timely"]),
        "ReaderPhysicalLine": int(family.loc[("R11", "line"), "timely"]),
        "ReaderNominalLoad": int(family.loc[("R11_NOMINAL", "load"), "timely"]),
        "ReaderNominalLine": int(family.loc[("R11_NOMINAL", "line"), "timely"]),
        "ReaderETLoad": int(family.loc[("ET_REFERENCE", "load"), "timely"]),
        "ReaderETLine": int(family.loc[("ET_REFERENCE", "line"), "timely"]),
        "ReaderETShortLoad": int(family.loc[("ET_CANDIDATE", "load"), "timely"]),
        "ReaderETShortLine": int(family.loc[("ET_CANDIDATE", "line"), "timely"]),
        "ReaderETShortTimely": int(summary[(summary.lane == "continuous") & (summary.method == "ET_CANDIDATE")]["timely"].sum()),
        "ReaderFamilyTotal": int(family.loc[("R11", "load"), "events"]),
        "ReaderETShortExtras": int(summary[(summary.lane == "continuous") & (summary.method == "ET_CANDIDATE")]["event_extras"].sum()),
        "ReaderPhysicalOutsideExtras": int(extras.loc[("R11", "RX_OUT_SUPPORT")]),
        "ReaderETOutsideExtras": int(extras.loc[("ET_REFERENCE", "RX_OUT_SUPPORT")]),
    }
    (ROOT / "generated/reader_macros.tex").write_text(
        "".join(f"\\newcommand{{\\{key}}}{{{value}}}\n" for key, value in macros.items()),
        encoding="utf-8")
    audit = {"development_manifest_sha256": dev_hash,
             "c01_manifest_sha256": c01_hash,
             "figures": ["reader_observed_signals", "reader_episode_story",
                         "reader_c01_tradeoff", "reader_c01_intervals"],
             "frozen_predictions_or_results_changed": False}
    (ROOT / "generated/reader_figure_audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    print("READER_FIGURES_BUILT", ", ".join(audit["figures"]))


if __name__ == "__main__":
    main()

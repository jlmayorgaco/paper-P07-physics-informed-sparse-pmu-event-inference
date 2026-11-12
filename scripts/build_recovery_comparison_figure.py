"""Plot the sealed C02 comparison without rerunning or reopening TEST."""
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "generated/frozen/recovery_c02_20261105"
OUT = ROOT / "figures/generated"
EXPECTED = "4f19cb72a2cf1929b5e68805c41fb00703fa88bdc365b726ed408fd57423349a"

C = {
    "ink": "#20282E",
    "muted": "#5C6971",
    "rule": "#CDD6DA",
    "teal": "#087F78",
    "orange": "#D55E00",
    "blue": "#0077A8",
    "green": "#4B7F52",
    "pale_teal": "#F0F7F6",
    "pale_blue": "#F2F7F9",
    "pale_orange": "#FBF5EF",
    "pale_gray": "#F6F8F8",
    "white": "#FFFFFF",
}

METHODS = [
    ("PHYSICAL_HISTORY", "History bank", C["teal"]),
    ("PHYSICAL_CONTINUOUS_GLR", "Continuous GLR", C["orange"]),
    ("EXTRATREES_ALL_SOURCES", "ExtraTrees", C["blue"]),
]

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 6.3,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})


def read_sealed_result():
    data = (SNAPSHOT / "TEST_EVALUATION.json").read_bytes()
    lock = json.loads((SNAPSHOT / "TEST_EVALUATION_LOCK.json").read_bytes())
    seal = json.loads((SNAPSHOT / "RESULTS_SEAL.json").read_bytes())
    digest = hashlib.sha256(data).hexdigest()
    if (digest != EXPECTED or lock.get("result_sha256") != EXPECTED
            or lock.get("status") != "COMPLETE_SINGLE_USE"
            or seal.get("files", {}).get("run/TEST_EVALUATION.json") != EXPECTED):
        raise ValueError("C02 result seal mismatch; refusing to draw the figure")
    report = json.loads(data)
    arms = report["arms"]
    bank = arms["PHYSICAL_HISTORY"]
    for key, _, _ in METHODS:
        arm = arms[key]
        if (arm["events"] != bank["events"]
                or arm["event_parents"] != bank["event_parents"]
                or arm["normal_monitored_s"] != bank["normal_monitored_s"]):
            raise ValueError("C02 arms do not share the sealed evaluation denominator")
    return report


def arrow(ax, start, end):
    ax.add_patch(FancyArrowPatch(
        start, end, arrowstyle="-|>", mutation_scale=7,
        linewidth=0.85, color=C["muted"], zorder=4,
    ))


def card(ax, x, y, w, h, title, body, color):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.035,rounding_size=0.08",
        linewidth=0.75, edgecolor=color, facecolor=C["white"], zorder=2,
    ))
    ax.text(x + 0.12, y + h - 0.12, title,
            fontsize=5.55, weight="bold", color=color, va="top", zorder=3)
    ax.text(x + 0.12, y + 0.10, body,
            fontsize=5.25, color=C["ink"], va="bottom", zorder=3)


def draw(report):
    fig, ax = plt.subplots(figsize=(7.15, 2.85))
    fig.subplots_adjust(0, 0, 1, 1)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.05)
    ax.axis("off")

    ax.text(0.18, 3.86, "HELD-OUT COMPARISON AT A FROZEN ALARM BUDGET",
            fontsize=8.5, weight="bold", color=C["ink"], va="center")

    # Calibration, freezing, and one-time evaluation are separated visually.
    card(ax, 0.25, 3.04, 2.53, 0.58,
         "CALIBRATE", "Select each threshold at 1 normal alarm/h", C["blue"])
    arrow(ax, (2.86, 3.33), (3.14, 3.33))
    card(ax, 3.22, 3.04, 2.42, 0.58,
         "FREEZE", "Lock predictors and publication rules", C["teal"])
    arrow(ax, (5.72, 3.33), (6.00, 3.33))
    test = report["arms"]["PHYSICAL_HISTORY"]
    normal_h = test["normal_monitored_s"] / 3600
    card(ax, 6.08, 3.04, 3.67, 0.58,
         "TEST ONCE", f"{test['event_parents']} event parents / {test['events']} events  ·  "
         f"{test['normal_parents']} normal parents / {normal_h:.2f} h", C["green"])

    # Two compact panels use exact values from the sealed evaluation file.
    panels = [(0.25, 0.70, 4.62, 2.10), (5.13, 0.70, 4.62, 2.10)]
    for x, y, w, h in panels:
        ax.add_patch(FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.035,rounding_size=0.08",
            linewidth=0.65, edgecolor=C["rule"], facecolor=C["white"],
            zorder=1,
        ))

    ax.text(0.45, 2.60, "TIMELY JOINT FAMILY + SOURCE BEFORE OFF",
            fontsize=6.25, weight="bold", color=C["ink"], va="center")
    ax.text(0.45, 2.38, "Correct interventions (%)",
            fontsize=5.4, color=C["muted"], va="center")
    left_x0, left_maxw = 1.73, 1.88
    for tick in (0, 50, 100):
        x = left_x0 + left_maxw * tick / 100
        ax.plot([x, x], [1.03, 2.24], color=C["rule"], lw=0.45, zorder=1.4)
        ax.text(x, 0.88, str(tick), ha="center", va="center",
                fontsize=5.0, color=C["muted"], zorder=3)
    y_rows = [2.05, 1.60, 1.15]
    for (key, label, color), y in zip(METHODS, y_rows):
        arm = report["arms"][key]
        pct = 100 * arm["timely_joint"] / arm["events"]
        ax.text(0.45, y + 0.095, label, fontsize=5.35,
                color=C["ink"], va="center", zorder=3)
        ax.add_patch(Rectangle((left_x0, y), left_maxw, 0.19,
                               facecolor=C["pale_gray"], edgecolor="none", zorder=1.5))
        ax.add_patch(Rectangle((left_x0, y), left_maxw * pct / 100, 0.19,
                               facecolor=color, edgecolor="none", zorder=2.2))
        ax.text(3.72, y + 0.095,
                f"{pct:.1f}%  ({arm['timely_joint']}/{arm['events']})",
                fontsize=5.25, color=C["ink"], va="center", zorder=3)

    ax.text(5.33, 2.60, "UNMATCHED ALARMS ON EVENT RECORDS",
            fontsize=6.25, weight="bold", color=C["ink"], va="center")
    ax.text(5.33, 2.38, "Count  ·  rate per monitored event-hour",
            fontsize=5.4, color=C["muted"], va="center")
    right_x0, right_maxw = 6.70, 1.76
    max_count = 90.0
    for tick in (0, 25, 50, 75, 90):
        x = right_x0 + right_maxw * tick / max_count
        ax.plot([x, x], [1.03, 2.24], color=C["rule"], lw=0.45, zorder=1.4)
        ax.text(x, 0.88, str(tick), ha="center", va="center",
                fontsize=5.0, color=C["muted"], zorder=3)
    for (key, label, color), y in zip(METHODS, y_rows):
        arm = report["arms"][key]
        count = arm["event_extras"]
        rate = arm["event_extras_per_h"]
        ax.text(5.33, y + 0.095, label, fontsize=5.35,
                color=C["ink"], va="center", zorder=3)
        ax.add_patch(Rectangle((right_x0, y), right_maxw, 0.19,
                               facecolor=C["pale_gray"], edgecolor="none", zorder=1.5))
        ax.add_patch(Rectangle((right_x0, y), right_maxw * count / max_count, 0.19,
                               facecolor=color, edgecolor="none", zorder=2.2))
        ax.text(8.60, y + 0.095, f"{count}  ({rate:.1f}/h)",
                fontsize=5.25, color=C["ink"], va="center", zorder=3)

    ax.text(0.30, 0.38,
            f"Normal records: 0 alarms in {normal_h:.2f} h per arm; one-sided 95% Poisson upper bound "
            f"{test['normal_Poisson_upper95_per_h']:.2f}/h. Uncertainty uses paired resampling by event parent.",
            fontsize=5.45, color=C["muted"], va="center")
    return fig


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    fig = draw(read_sealed_result())
    fig.savefig(OUT / "recovery_comparison_c02.pdf", bbox_inches="tight",
                pad_inches=0.03)
    fig.savefig(OUT / "recovery_comparison_c02.png", dpi=260,
                bbox_inches="tight", pad_inches=0.03, facecolor="white")
    plt.close(fig)
    print("Built C02 figure from the sealed TEST evaluation.")

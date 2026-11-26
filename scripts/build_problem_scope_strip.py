"""Build the scope strip that completes the three-part P07 overview figure."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures" / "generated"

C = {
    "ink": "#20282E",
    "muted": "#5C6971",
    "rule": "#CDD6DA",
    "blue": "#0077A8",
    "teal": "#087F78",
    "orange": "#D55E00",
    "green": "#4B7F52",
    "pale_blue": "#F2F7F9",
    "pale_teal": "#F0F7F6",
    "pale_orange": "#FBF5EF",
    "pale_gray": "#F6F8F8",
    "white": "#FFFFFF",
}

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 6.2,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})


def draw():
    fig, ax = plt.subplots(figsize=(7.15, 0.72))
    fig.subplots_adjust(0, 0, 1, 1)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 1.0)
    ax.axis("off")

    ax.add_patch(FancyBboxPatch(
        (0.10, 0.02), 9.80, 0.94,
        boxstyle="round,pad=0.02,rounding_size=0.10",
        linewidth=0.75, edgecolor=C["rule"], facecolor=C["pale_gray"],
        zorder=1,
    ))
    ax.text(0.30, 0.81, "SAME PMU REPORTS, DIFFERENT QUESTIONS",
            fontsize=7.2, weight="bold", color=C["ink"], va="center")
    ax.plot([0.30, 9.70], [0.67, 0.67], color=C["rule"], lw=0.6, zorder=2)

    cols = [
        (0.34, 2.94, C["blue"], "MEASUREMENT FRONT END",
         "PLL / SOGI  \u2192  reported phasors"),
        (3.53, 2.94, C["orange"], "STATE / STABILITY",
         "GNO  \u2192  rotor state   \u00b7   TSA  \u2192  stability"),
        (6.72, 2.94, C["teal"], "P07: EVENT ATTRIBUTION",
         "carry recovery  \u2192  test source  \u2192  onset / OFF"),
    ]
    for x, w, color, title, body in cols:
        ax.add_patch(FancyBboxPatch(
            (x, 0.30), w, 0.28,
            boxstyle="round,pad=0.025,rounding_size=0.055",
            linewidth=0.65, edgecolor=color,
            facecolor=C["white"], zorder=2,
        ))
        ax.text(x + 0.12, 0.44, title, fontsize=5.55, weight="bold",
                color=color, va="center", zorder=3)
        ax.text(x + 0.12, 0.14, body, fontsize=5.65,
                color=C["ink"], va="center", zorder=3)
    return fig


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    fig = draw()
    fig.savefig(OUT / "problem_scope_strip.pdf", bbox_inches="tight",
                pad_inches=0.025)
    fig.savefig(OUT / "problem_scope_strip.png", dpi=260,
                bbox_inches="tight", pad_inches=0.025, facecolor="white")
    plt.close(fig)
    print("Built scope strip for the P07 overview figure.")

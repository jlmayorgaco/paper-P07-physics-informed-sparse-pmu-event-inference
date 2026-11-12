"""Build a vector schematic of the physical and measurement contract."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

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
    "purple": "#72569A",
    "pale_blue": "#F2F7F9",
    "pale_teal": "#F0F7F6",
    "pale_orange": "#FBF5EF",
    "pale_green": "#F2F7F1",
    "pale_gray": "#F6F8F8",
    "white": "#FFFFFF",
}

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 6.5,
    "mathtext.fontset": "dejavusans",
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})


def card(ax, x, y, w, h, title, body, *, edge, face, body_size=5.8,
         title_size=6.5, title_color=None):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.04,rounding_size=0.10",
        linewidth=0.8, edgecolor=edge, facecolor=face, zorder=2,
    ))
    ax.add_patch(FancyBboxPatch(
        (x + 0.01, y + 0.09), 0.05, h - 0.18,
        boxstyle="round,pad=0.004,rounding_size=0.02",
        linewidth=0, edgecolor="none", facecolor=edge, zorder=3,
    ))
    ax.text(x + 0.16, y + h - 0.14, title, fontsize=title_size,
            weight="bold", color=title_color or edge, va="top", zorder=4)
    ax.text(x + 0.16, y + 0.18, body, fontsize=body_size,
            color=C["ink"], va="bottom", linespacing=1.17, zorder=4)


def arrow(ax, start, end, color=None, lw=0.95):
    ax.add_patch(FancyArrowPatch(
        start, end, arrowstyle="-|>", mutation_scale=7,
        linewidth=lw, color=color or C["muted"],
        connectionstyle="arc3,rad=0", shrinkA=0, shrinkB=1.5, zorder=5,
    ))


def draw():
    fig, ax = plt.subplots(figsize=(7.15, 2.55))
    fig.subplots_adjust(0, 0, 1, 1)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3.65)
    ax.axis("off")

    ax.text(0.16, 3.43, "FROM PHYSICAL INTERVENTION TO PMU REPORT",
            fontsize=8.8, weight="bold", color=C["ink"], va="center")
    ax.text(0.16, 3.17,
            "A switched network model and a causal measurement filter produce the vector seen by the history bank.",
            fontsize=6.5, color=C["muted"], va="center")
    ax.plot([0.16, 9.84], [2.98, 2.98], color=C["rule"], lw=0.65, zorder=1)

    # Physical intervention cards share one input to the switched DAE.
    card(ax, 0.25, 2.01, 1.46, 0.64, "LOAD", r"$P/Q$ step or restore",
         edge=C["orange"], face=C["pale_orange"], body_size=5.5,
         title_size=6.2)
    card(ax, 0.25, 1.17, 1.46, 0.64, "LINE", r"open / reclose $q$",
         edge=C["blue"], face=C["pale_blue"], body_size=5.5,
         title_size=6.2)

    card(ax, 1.99, 1.54, 1.92, 1.08, "SWITCHED NETWORK DAE",
         "$\\dot{x}=f_q(x,z,u)$\n$0=g_q(x,z,u)$\n$x$ continues; $z$ re-solves",
         edge=C["teal"], face=C["pale_teal"], body_size=5.45,
         title_size=6.0)
    card(ax, 4.18, 1.54, 1.62, 1.08, "ELECTRICAL MAP",
         "$h_q=H_q(x,z,u)$\n$V$ and oriented\nterminal $I$",
         edge=C["blue"], face=C["pale_blue"], body_size=5.5,
         title_size=6.2)
    card(ax, 6.08, 1.54, 1.62, 1.08, "PHASE MEMORY",
         "causal filter state $\\eta$\nphase $\\rightarrow f$, ROCOF",
         edge=C["purple"], face=C["white"], body_size=5.45,
         title_size=6.2)
    card(ax, 7.98, 1.54, 1.77, 1.08, "REPORTED VECTOR $y_k$",
         "8 PMUs; 47 coordinates\n8 |V| + 8 angle(V)\n8 |I| + 7 angle(I)\n8 f + 8 ROCOF",
         edge=C["green"], face=C["pale_green"], body_size=5.05,
         title_size=5.9)

    arrow(ax, (1.77, 2.33), (1.99, 2.15), C["orange"], lw=0.85)
    arrow(ax, (1.77, 1.49), (1.99, 1.90), C["blue"], lw=0.85)
    arrow(ax, (3.97, 2.08), (4.18, 2.08), C["teal"])
    arrow(ax, (5.86, 2.08), (6.08, 2.08), C["blue"])
    arrow(ax, (7.76, 2.08), (7.98, 2.08), C["purple"])

    ax.add_patch(FancyBboxPatch(
        (0.25, 0.31), 9.50, 0.52,
        boxstyle="round,pad=0.035,rounding_size=0.08",
        linewidth=0.65, edgecolor=C["rule"], facecolor=C["pale_gray"],
        zorder=1,
    ))
    ax.text(0.43, 0.57, "OFF / RESTORATION",
            fontsize=5.9, weight="bold", color=C["muted"], va="center")
    ax.text(1.97, 0.57,
            "input returns; $x$ and $\\eta$ persist; algebraic $z$ and terminal currents are recomputed.",
            fontsize=5.55, color=C["ink"], va="center")
    ax.text(0.43, 0.12,
            "P07 consumes phasors, not raw waveforms or harmonics; B/C values are reconstructed from phase A.",
            fontsize=5.25, color=C["muted"], va="center")
    return fig


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    fig = draw()
    fig.savefig(OUT / "physics_measurement_chain.pdf", bbox_inches="tight",
                pad_inches=0.03)
    fig.savefig(OUT / "physics_measurement_chain.png", dpi=260,
                bbox_inches="tight", pad_inches=0.03, facecolor="white")
    plt.close(fig)
    print("Built vector physics-to-PMU diagram.")

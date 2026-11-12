"""Build the compact P07 physical-to-report schematic."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures" / "generated"

C = {
    "ink": "#20303D",
    "muted": "#637481",
    "rule": "#D9E1E5",
    "blue": "#2D7EA4",
    "teal": "#13857D",
    "orange": "#C96F32",
    "purple": "#755F9D",
    "green": "#4D8058",
    "pale_blue": "#F1F7FA",
    "pale_teal": "#EFF7F5",
    "pale_orange": "#FBF5EF",
    "pale_purple": "#F5F2F8",
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


def box(ax, x, y, w, h, *, edge, face, lw=0.8, radius=1.25, z=1):
    p = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.012,rounding_size={radius}",
        edgecolor=edge, facecolor=face, linewidth=lw, zorder=z,
    )
    ax.add_patch(p)
    return p


def label(ax, x, y, s, *, size=6.3, color=None, weight=None,
          ha="left", va="center"):
    ax.text(x, y, s, fontsize=size, color=color or C["ink"], weight=weight,
            ha=ha, va=va, zorder=5)


def arrow(ax, a, b, color, lw=1.1):
    ax.add_patch(FancyArrowPatch(
        a, b, arrowstyle="-|>", mutation_scale=8, linewidth=lw,
        color=color, shrinkA=0, shrinkB=1.5, zorder=5,
    ))


def stage(ax, x, title, color, face, eq, detail, extra=None):
    y, w, h = 38.5, 29.2, 27.5
    box(ax, x, y, w, h, edge=C["rule"], face=C["white"], lw=0.75)
    label(ax, x + 1.3, y + h - 3.6, title, size=6.9,
          color=color, weight="bold")
    ax.plot([x + 1.3, x + w - 1.3], [y + h - 6.5, y + h - 6.5],
            color=C["rule"], lw=0.6, zorder=2)
    if extra:
        label(ax, x + w / 2, y + 17.3, eq, size=7.3,
              color=color, weight="medium", ha="center")
        label(ax, x + w / 2, y + 11.4, extra, size=7.0,
              color=C["ink"], weight="medium", ha="center")
        detail_y = y + 4.3
    elif isinstance(eq, (tuple, list)):
        label(ax, x + w / 2, y + 17.0, eq[0], size=7.6,
              color=color, weight="medium", ha="center")
        label(ax, x + w / 2, y + 13.4, eq[1], size=7.1,
              color=color, weight="medium", ha="center")
        detail_y = y + 6.2
    else:
        label(ax, x + w / 2, y + 15.2, eq, size=7.3,
              color=color, weight="medium", ha="center")
        detail_y = y + 7.2
    label(ax, x + w / 2, detail_y, detail, size=6.1,
          color=C["muted"], ha="center")


def draw():
    fig, ax = plt.subplots(figsize=(7.15, 2.82))
    fig.subplots_adjust(0, 0, 1, 1)
    ax.set_xlim(0, 100)
    ax.set_ylim(6, 100)
    ax.axis("off")

    label(ax, 2.4, 96.0, "FROM EVENT TO CAUSAL PMU REPORT",
          size=8.4, color=C["ink"], weight="bold")
    label(ax, 2.4, 91.8,
          "The intervention ends at OFF; its physical and measurement response continues.",
          size=6.4, color=C["muted"])
    ax.plot([2.4, 97.6], [88.6, 88.6], color=C["rule"], lw=0.7, zorder=1)

    # One shared event clock, with the load and line operators shown as
    # alternatives rather than simultaneous interventions.
    label(ax, 2.6, 84.8, "EVENT CLOCK · LOAD OR LINE",
          size=5.8, color=C["muted"], weight="bold")
    x0, xtau, xkappa, x1 = 22.0, 45.0, 74.0, 97.0
    label(ax, (x0 + xtau) / 2, 84.8, "BASE", size=5.5,
          color=C["muted"], weight="bold", ha="center")
    label(ax, (xtau + xkappa) / 2, 84.8, "INTERVENTION", size=5.5,
          color=C["orange"], weight="bold", ha="center")
    label(ax, (xkappa + x1) / 2, 84.8, "RESTORED", size=5.5,
          color=C["teal"], weight="bold", ha="center")
    box(ax, x0, 69.0, x1 - x0, 13.3,
        edge=C["rule"], face=C["white"], lw=0.65, radius=1.0)
    ax.add_patch(FancyBboxPatch(
        (xtau, 69.2), xkappa - xtau, 12.9,
        boxstyle="square,pad=0", linewidth=0,
        facecolor=C["pale_orange"], zorder=1,
    ))
    label(ax, 3.5, 77.0, "LOAD", size=5.8,
          color=C["orange"], weight="bold")
    label(ax, 3.5, 72.4, "LINE", size=5.8,
          color=C["blue"], weight="bold")
    for y, left, active, right, color in [
        (77.0, r"$u_0$", r"$u_0+\Delta u$", r"$u_0$", C["orange"]),
        (72.4, r"$q_0$", r"$q_{\mathrm{open}}$", r"$q_0$", C["blue"]),
    ]:
        label(ax, (x0 + xtau) / 2, y, left, size=6.0,
              color=C["muted"], ha="center")
        label(ax, (xtau + xkappa) / 2, y, active, size=6.0,
              color=color, weight="bold", ha="center")
        label(ax, (xkappa + x1) / 2, y, right, size=6.0,
              color=C["muted"], ha="center")
    for x in (xtau, xkappa):
        ax.plot([x, x], [69.6, 81.6], color=C["muted"], lw=0.7,
                ls=(0, (2.2, 2.2)), zorder=3)
    label(ax, xtau, 70.2, r"$\tau$", size=5.8,
          color=C["ink"], weight="bold", ha="center")
    label(ax, xkappa, 70.2, r"$\kappa$", size=5.8,
          color=C["ink"], weight="bold", ha="center")
    arrow(ax, (x0 + 1.0, 68.4), (x1 - 0.4, 68.4), C["muted"], lw=0.65)

    stage(ax, 2.6, "SWITCHED PLANT", C["teal"], C["pale_teal"],
          (r"$\dot{x}=f_q(x,z,u)$", r"$0=g_q(x,z,u)$"),
          "differential state and network equations")
    stage(ax, 35.4, "ELECTRICAL MAP", C["blue"], C["pale_blue"],
          r"$h_k=H_q(x,z,u)$",
          "bus-voltage phasors · oriented terminal currents")
    stage(ax, 68.2, "CAUSAL PMU REPORT", C["purple"], C["pale_purple"],
          r"$\eta_k=F_M(\eta_{k-1},h_k)$",
          "phasor, frequency and ROCOF channels",
          extra=r"$y_k\in\mathbb{R}^{47}$")
    for xa, xb, color in [
        (32.0, 35.2, C["teal"]),
        (64.8, 68.0, C["blue"]),
    ]:
        arrow(ax, (xa, 52.2), (xb, 52.2), color)

    # A single restoration statement replaces the previous row of explanatory
    # cards; detailed measurement assumptions remain in the adjacent text.
    box(ax, 2.6, 15.0, 94.8, 15.0,
        edge=C["rule"], face=C["pale_gray"], lw=0.65, radius=1.0)
    label(ax, 4.0, 25.8,
          "RESTORATION RETURNS THE OPERATOR, NOT THE RESPONSE",
          size=6.1, color=C["ink"], weight="bold")
    label(ax, 50.0, 20.0,
          r"$u,q$ return to base   ·   $x,\eta$ persist   ·   $z$ and terminal $I$ are recomputed",
          size=7.0, color=C["ink"], weight="medium", ha="center")
    label(ax, 2.8, 9.1,
          r"At report $k$, inference receives $y_{1:k}$; event truth and raw waveforms are not inputs.",
          size=5.8, color=C["muted"])
    return fig


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    fig = draw()
    fig.savefig(OUT / "physics_measurement_chain.pdf",
                bbox_inches="tight", pad_inches=0.035)
    fig.savefig(OUT / "physics_measurement_chain.png", dpi=300,
                bbox_inches="tight", pad_inches=0.035, facecolor="white")
    plt.close(fig)
    print("Built the compact physical-to-PMU schematic.")

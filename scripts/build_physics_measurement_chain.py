"""Build the physical-event to causal-PMU-report figure for P07."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures" / "generated"

C = {
    "ink": "#1F2D3A",
    "muted": "#526575",
    "rule": "#D4DEE4",
    "orange": "#C96A23",
    "blue": "#287BA5",
    "teal": "#087F78",
    "purple": "#71569C",
    "green": "#4B7F52",
    "pale_orange": "#FBF4ED",
    "pale_blue": "#F1F7FA",
    "pale_teal": "#EFF7F5",
    "pale_purple": "#F5F2F8",
    "pale_green": "#F1F6F0",
    "pale_gray": "#F5F7F8",
    "white": "#FFFFFF",
}

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 6.3,
    "mathtext.fontset": "dejavusans",
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})


def rounded(ax, xy, width, height, *, edge, face, lw=0.85, radius=1.6,
            zorder=1):
    patch = FancyBboxPatch(
        xy, width, height,
        boxstyle=f"round,pad=0.012,rounding_size={radius}",
        linewidth=lw, edgecolor=edge, facecolor=face, zorder=zorder,
    )
    ax.add_patch(patch)
    return patch


def arrow(ax, start, end, *, color=None, lw=1.15, scale=8):
    ax.add_patch(FancyArrowPatch(
        start, end, arrowstyle="-|>", mutation_scale=scale,
        linewidth=lw, color=color or C["muted"],
        shrinkA=0, shrinkB=1.5, zorder=6,
    ))


def text(ax, x, y, s, *, size=6.2, color=None, weight=None,
         ha="left", va="center", **kwargs):
    ax.text(x, y, s, fontsize=size, color=color or C["ink"], weight=weight,
            ha=ha, va=va, zorder=5, **kwargs)


def pipeline_card(ax, x, title, kicker, color, face, equation, lines,
                  *, eq_size=7.2):
    y, w, h = 39.5, 21.5, 27.5
    rounded(ax, (x, y), w, h, edge=C["rule"], face=C["white"], lw=0.8,
            radius=1.35)
    rounded(ax, (x + 1.0, y + h - 5.2), 3.2, 3.2, edge=color, face=face,
            lw=0, radius=0.9)
    text(ax, x + 2.6, y + h - 3.6, kicker, size=5.2, color=color,
         weight="bold", ha="center")
    text(ax, x + 5.2, y + h - 3.5, title, size=6.3, color=C["ink"],
         weight="bold")
    ax.plot([x + 1.0, x + w - 1.0], [y + h - 7.0, y + h - 7.0],
            color=C["rule"], lw=0.65, zorder=2)
    text(ax, x + w / 2, y + 15.2, equation, size=eq_size,
         color=color, weight="medium", ha="center")
    for j, line in enumerate(lines):
        text(ax, x + 1.25, y + 9.4 - j * 3.3, line, size=6.0,
             color=C["muted"])


def draw():
    fig, ax = plt.subplots(figsize=(7.15, 3.28))
    fig.subplots_adjust(0, 0, 1, 1)
    ax.set_xlim(0, 100)
    ax.set_ylim(8, 100)
    ax.axis("off")

    text(ax, 2.2, 96.1, "FROM SWITCHED PHYSICS TO CAUSAL PMU REPORT",
         size=8.5, color=C["ink"], weight="bold")
    text(ax, 2.2, 92.2,
         "A restored input changes the network mode; the physical and measurement states keep evolving.",
         size=6.2, color=C["muted"])
    ax.plot([2.2, 97.8], [89.1, 89.1], color=C["rule"], lw=0.7, zorder=1)

    # Event schedule. The load-step sign is intentionally unspecified.
    text(ax, 2.4, 85.8, "EVENT CLOCK · LOAD OR LINE", size=5.3,
         color=C["muted"],
         weight="bold")
    x0, xtau, xkappa, x1 = 23.0, 45.0, 74.0, 97.0
    text(ax, (x0 + xtau) / 2, 85.8, "PRE-EVENT", size=5.2,
         color=C["muted"], weight="bold", ha="center")
    text(ax, (xtau + xkappa) / 2, 85.8, "INTERVENTION ACTIVE",
         size=5.2, color=C["orange"], weight="bold", ha="center")
    text(ax, (xkappa + x1) / 2, 85.8, "OPERATOR RESTORED", size=5.2,
         color=C["teal"], weight="bold", ha="center")
    rounded(ax, (x0, 70.3), x1 - x0, 12.5, edge=C["rule"],
            face=C["white"], lw=0.65, radius=1.0)
    ax.add_patch(FancyBboxPatch(
        (xtau, 70.5), xkappa - xtau, 12.1,
        boxstyle="square,pad=0", linewidth=0, facecolor=C["pale_orange"],
        zorder=1,
    ))
    text(ax, 3.7, 78.9, "LOAD", size=5.5, color=C["orange"], weight="bold")
    text(ax, 3.7, 73.6, "LINE", size=5.5, color=C["blue"], weight="bold")
    for y, before, during, after, col in [
        (78.9, r"$u_0$", r"$u_0+\Delta u$", r"$u_0$", C["orange"]),
        (73.6, r"$q_0$", r"$q_{\mathrm{open}}$", r"$q_0$", C["blue"]),
    ]:
        text(ax, (x0 + xtau) / 2, y - 1.7, before, size=5.5,
             color=C["muted"], ha="center")
        text(ax, (xtau + xkappa) / 2, y - 1.7, during, size=5.5,
             color=col, weight="bold", ha="center")
        text(ax, (xkappa + x1) / 2, y - 1.7, after, size=5.5,
             color=C["muted"], ha="center")
    for x, label in [(xtau, r"$\tau$"), (xkappa, r"$\kappa$")]:
        ax.plot([x, x], [70.8, 83.4], color=C["muted"], lw=0.7,
                ls=(0, (2.2, 2.2)), zorder=3)
        text(ax, x, 82.0, label, size=6.0, color=C["ink"],
             weight="bold", ha="center")
    arrow(ax, (x0 + 1.0, 70.5), (x1 - 0.4, 70.5),
          color=C["muted"], lw=0.6, scale=6)

    pipeline_card(
        ax, 2.4, "SWITCHED PLANT", "01", C["teal"], C["pale_teal"],
        r"$\dot{x}=f_q(x,z,u)$",
        [r"$0=g_q(x,z,u)$", "load input or branch mode changes",
         "differential and algebraic states"],
    )
    pipeline_card(
        ax, 26.0, "ELECTRICAL MAP", "02", C["blue"], C["pale_blue"],
        r"$h_k=H_q(x,z,u)$",
        ["V phasors at PMU buses", "oriented I at declared ends",
         "terminal assignment is fixed"],
    )
    pipeline_card(
        ax, 49.6, "CAUSAL FILTER", "03", C["purple"], C["pale_purple"],
        r"$\eta_k=F_M(\eta_{k-1},h_k)$",
        ["phase history is carried forward", "phase evolution yields $f$",
         "filter history yields ROCOF"],
        eq_size=6.5,
    )
    pipeline_card(
        ax, 73.2, "REPORT TO INFERENCE", "04", C["green"], C["pale_green"],
        r"$y_k=G_M(\eta_k,h_k)+b+\varepsilon_k$",
        ["8 PMUs  ·  30 reports/s", "47 causal coordinates"],
        eq_size=6.0,
    )
    for xa, xb, col in [
        (23.9, 25.8, C["teal"]),
        (47.5, 49.4, C["blue"]),
        (71.1, 73.0, C["purple"]),
    ]:
        arrow(ax, (xa, 52.0), (xb, 52.0), color=col, lw=1.15, scale=8)

    # The groups contain 16 voltage, 15 current, and 16 frequency/ROCOF
    # coordinates. The bar represents report channels, not sensor counts.
    bx, by, bw, bh = 74.4, 40.0, 19.0, 3.5
    groups = [
        (16, "V · 16", C["blue"]),
        (15, "I · 15", C["orange"]),
        (16, "f/R · 16", C["purple"]),
    ]
    gap = 0.42
    usable = bw - 2 * gap
    widths = [usable * n / 47 for n, _, _ in groups]
    cursor = bx
    for i, ((_, label, color), width) in enumerate(zip(groups, widths)):
        rounded(ax, (cursor, by), width, bh, edge=color, face=color,
                lw=0, radius=0.8)
        text(ax, cursor + width / 2, by + bh / 2, label, size=4.6,
             color=C["white"], weight="bold", ha="center")
        cursor += width + (gap if i < 2 else 0)

    text(ax, 2.4, 36.0, "AT RESTORATION, THE OPERATOR RESETS; MEMORY DOES NOT",
         size=6.0, color=C["ink"], weight="bold")
    state_cards = [
        (2.4, 22.4, 32.0, 10.8, "DYNAMIC STATE  $x$", C["teal"], C["pale_teal"],
         r"$x(\kappa^+)=x(\kappa^-)$",
         "machine and control response continues"),
        (35.5, 22.4, 32.0, 10.8, "NETWORK STATE  $z$", C["blue"], C["pale_blue"],
         r"$g_{q_0}(x,z,u_0)=0$ is solved again",
         "voltages and terminal currents are recomputed"),
        (68.6, 22.4, 29.0, 10.8, r"FILTER STATE  $\eta$", C["purple"], C["pale_purple"],
         r"$\eta$ carries phase history forward",
         "post-restoration reports retain the transient"),
    ]
    for x, y, w, h, title, color, face, eq, desc in state_cards:
        rounded(ax, (x, y), w, h, edge=C["rule"], face=face,
                lw=0.65, radius=1.0)
        text(ax, x + 1.0, y + h - 2.5, title, size=6.0,
             color=color, weight="bold")
        text(ax, x + 1.0, y + 5.2, eq, size=6.3,
             color=C["ink"], weight="medium")
        text(ax, x + 1.0, y + 2.2, desc, size=5.6, color=C["muted"])

    ax.plot([2.4, 97.6], [20.8, 20.8], color=C["rule"], lw=0.65, zorder=1)
    text(ax, 2.4, 19.0, "INFERENCE INPUT", size=5.6, color=C["green"],
         weight="bold")
    text(ax, 16.0, 19.0,
         r"$y_{1:k}$ only  ·  no true source, switch time, solver state, or raw waveform",
         size=5.8, color=C["ink"])
    text(ax, 2.4, 14.2,
         "47 coordinates: 8 |V| + 8 angle(V) + 8 |I| + 7 angle(I) + 8 f + 8 ROCOF.",
         size=5.5, color=C["muted"])
    text(ax, 2.4, 10.5,
         "Phase-A phasors are exported; B/C phases are reconstructed. Raw waveforms and harmonics are not observed.",
         size=5.5, color=C["muted"])
    return fig


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    fig = draw()
    fig.savefig(OUT / "physics_measurement_chain.pdf", bbox_inches="tight",
                pad_inches=0.03)
    fig.savefig(OUT / "physics_measurement_chain.png", dpi=300,
                bbox_inches="tight", pad_inches=0.03, facecolor="white")
    plt.close(fig)
    print("Built the physical event to causal PMU report figure.")

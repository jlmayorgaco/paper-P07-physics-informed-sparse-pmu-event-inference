"""Build an illustrative physical-to-PMU report figure for the P07 paper."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Ellipse, FancyArrowPatch, Rectangle

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures" / "generated"

C = {
    "ink": "#20303D",
    "muted": "#657681",
    "rule": "#D7E0E4",
    "blue": "#287DA2",
    "teal": "#16877F",
    "orange": "#C96F32",
    "purple": "#755F9D",
    "pale_blue": "#EAF3F7",
    "pale_teal": "#EAF5F2",
    "pale_orange": "#FBF1E8",
    "pale_purple": "#F2EFF7",
    "white": "#FFFFFF",
}

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 6.5,
    "mathtext.fontset": "dejavuserif",
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})


def txt(ax, x, y, s, *, size=6.2, color=None, weight=None,
        ha="left", va="center", family=None, z=5):
    ax.text(x, y, s, fontsize=size, color=color or C["ink"], weight=weight,
            ha=ha, va=va, family=family, zorder=z)


def seg(ax, x0, y0, x1, y1, *, color=None, lw=0.8, ls="-", z=2):
    ax.plot([x0, x1], [y0, y1], color=color or C["ink"], linewidth=lw,
            linestyle=ls, solid_capstyle="round", zorder=z)


def arrow(ax, xy0, xy1, *, color=None, lw=1.0, scale=7, z=4):
    ax.add_patch(FancyArrowPatch(
        xy0, xy1, arrowstyle="-|>", mutation_scale=scale,
        linewidth=lw, color=color or C["ink"], shrinkA=0, shrinkB=0, zorder=z,
    ))


def panel_heading(ax, x, n, title, color):
    txt(ax, x, 81.0, n, size=6.1, color=color, weight="bold")
    txt(ax, x + 4.0, 81.0, title, size=6.4, color=C["ink"], weight="bold")
    seg(ax, x, 77.7, x + 21.5, 77.7, color=C["rule"], lw=0.75)


def draw_operator_panel(ax):
    panel_heading(ax, 3.0, "01", "PHYSICAL OPERATORS", C["orange"])

    # Load setpoint change: a bus with a controlled P/Q injection.
    txt(ax, 3.2, 73.0, "LOAD", size=5.9, color=C["orange"], weight="bold")
    txt(ax, 24.4, 73.0, r"$P,Q\;\mapsto\;(1+a)(P,Q)$", size=5.8,
        color=C["orange"], ha="right")
    seg(ax, 4.3, 63.6, 23.8, 63.6, color=C["ink"], lw=1.5)
    seg(ax, 6.5, 60.9, 6.5, 66.3, color=C["ink"], lw=1.0)
    seg(ax, 21.8, 60.9, 21.8, 66.3, color=C["ink"], lw=1.0)
    arrow(ax, (14.2, 62.7), (14.2, 55.4), color=C["orange"], lw=1.0, scale=7)
    ax.add_patch(Circle((14.2, 52.4), 2.35, edgecolor=C["orange"],
                        facecolor=C["white"], linewidth=1.0, zorder=3))
    txt(ax, 14.2, 52.4, "L", size=5.8, color=C["orange"], weight="bold", ha="center")
    txt(ax, 18.0, 52.4, r"$\Delta P,\;\Delta Q$", size=6.0,
        color=C["ink"])

    # Branch opening: the open contact is explicit, but is not a network map.
    txt(ax, 3.2, 42.7, "LINE", size=5.9, color=C["blue"], weight="bold")
    seg(ax, 4.3, 34.5, 11.9, 34.5, color=C["ink"], lw=1.45)
    seg(ax, 17.5, 34.5, 23.8, 34.5, color=C["ink"], lw=1.45)
    ax.add_patch(Circle((12.4, 34.5), 0.55, edgecolor=C["blue"],
                        facecolor=C["white"], linewidth=0.85, zorder=4))
    ax.add_patch(Circle((17.0, 34.5), 0.55, edgecolor=C["blue"],
                        facecolor=C["white"], linewidth=0.85, zorder=4))
    seg(ax, 12.6, 34.9, 16.5, 38.1, color=C["blue"], lw=1.2, z=4)
    seg(ax, 17.0, 31.8, 17.0, 37.2, color=C["ink"], lw=0.8)
    txt(ax, 14.3, 27.4, r"$q_0\;\rightarrow\;q_{\rm open}$", size=6.1,
        color=C["blue"], ha="center")
    txt(ax, 14.0, 19.1, "generic operator symbols; not bus locations",
        size=4.8, color=C["muted"], ha="center")


def draw_response_panel(ax):
    panel_heading(ax, 28.0, "02", "CAUSAL RESPONSE THROUGH RESTORATION", C["teal"])

    x0, xtau, xkap, x1 = 36.2, 44.2, 58.1, 66.0
    # ON interval is a shared visual clock for all four conceptual lanes.
    ax.add_patch(Rectangle((xtau, 26.0), xkap - xtau, 46.0,
                           facecolor=C["pale_orange"], edgecolor="none", zorder=0))
    for x, label in ((xtau, r"$\tau$"), (xkap, r"$\kappa$")):
        seg(ax, x, 25.7, x, 72.3, color=C["muted"], lw=0.65, ls=(0, (2.0, 2.1)), z=1)
        txt(ax, x, 74.0, label, size=6.3, color=C["ink"], weight="bold", ha="center")

    lanes = [
        ("u, q", 67.4, C["orange"]),
        ("x", 55.6, C["teal"]),
        ("z, I", 43.7, C["blue"]),
        (r"$\eta$", 31.8, C["purple"]),
    ]
    for name, y, color in lanes:
        txt(ax, 28.9, y, name, size=6.0, color=color, weight="bold")
        seg(ax, x0, y, x1, y, color=C["rule"], lw=0.55, z=1)

    # Operator pulse: returns to baseline at OFF.
    seg(ax, x0, 69.0, xtau, 69.0, color=C["orange"], lw=1.25)
    seg(ax, xtau, 69.0, xtau, 70.5, color=C["orange"], lw=1.25)
    seg(ax, xtau, 70.5, xkap, 70.5, color=C["orange"], lw=1.25)
    seg(ax, xkap, 70.5, xkap, 69.0, color=C["orange"], lw=1.25)
    seg(ax, xkap, 69.0, x1, 69.0, color=C["orange"], lw=1.25)
    txt(ax, (xtau + xkap) / 2, 71.7, "ON", size=4.9, color=C["orange"],
        weight="bold", ha="center")

    # Illustrative dynamic state: continuous at OFF and still evolving.
    t = np.linspace(x0, x1, 500)
    response = np.zeros_like(t)
    mask = t >= xtau
    s = (t[mask] - xtau) / (x1 - xtau)
    response[mask] = 2.65 * np.exp(-1.6 * s) * np.sin(5.2 * np.pi * s)
    ax.plot(t, 55.6 + response, color=C["teal"], linewidth=1.35,
            solid_capstyle="round", zorder=4)
    # OFF is a slope change, not a state reset.
    ix = int(np.argmin(np.abs(t - xkap)))
    ax.add_patch(Circle((xkap, 55.6 + response[ix]), 0.63,
                        facecolor=C["white"], edgecolor=C["teal"],
                        linewidth=0.9, zorder=5))

    # Algebraic voltages/currents are re-solved at both topology switches.
    zt = np.array([x0, xtau - 0.12, xtau, xtau + 0.10,
                   xkap - 0.10, xkap, xkap + 0.10, x1])
    zy = np.array([43.7, 43.7, 46.1, 46.1, 45.5, 44.1, 44.1, 44.6])
    ax.plot(zt, zy, color=C["blue"], linewidth=1.3,
            solid_capstyle="round", zorder=4)
    # Small damped settling after OFF, ending away from the pre-event value.
    t2 = np.linspace(xkap + 0.1, x1, 120)
    z2 = 44.6 - 0.5 * (1 - np.exp(-0.35 * (t2 - xkap - 0.1)))
    ax.plot(t2, z2, color=C["blue"], linewidth=1.3, zorder=4)

    # Instrumental phase-history state: filtered response also persists.
    t3 = np.linspace(x0, x1, 500)
    eta = np.zeros_like(t3)
    mask3 = t3 >= xtau + 1.5
    s3 = (t3[mask3] - xtau - 1.5) / (x1 - xtau)
    eta[mask3] = 1.75 * np.exp(-1.45 * s3) * np.sin(4.2 * np.pi * s3)
    ax.plot(t3, 31.8 + eta, color=C["purple"], linewidth=1.25,
            solid_capstyle="round", zorder=4)

    txt(ax, 67.0, 55.6, "continuous", size=4.7, color=C["teal"])
    txt(ax, 67.0, 43.7, "re-solved", size=4.7, color=C["blue"])
    txt(ax, 67.0, 31.8, "filtered", size=4.7, color=C["purple"])
    arrow(ax, (x0, 23.7), (x1, 23.7), color=C["muted"], lw=0.65, scale=6)
    txt(ax, (x0 + x1) / 2, 21.3, "report time", size=5.0,
        color=C["muted"], ha="center")
    txt(ax, 49.4, 16.9, "OFF restores the operator; it does not reset x or the filter state.",
        size=5.3, color=C["ink"], ha="center")
    txt(ax, 49.4, 11.7, "illustrative trajectories — not measured records",
        size=4.7, color=C["muted"], ha="center")


def draw_report_panel(ax):
    panel_heading(ax, 74.3, "03", "PMU REPORT", C["blue"])

    # Eight generic PMU glyphs communicate the sparse measurement layer without
    # implying a fictitious network layout or actual PMU placement.
    xs = np.linspace(77.2, 94.8, 4)
    for yy in (68.0, 59.8):
        for xx in xs:
            seg(ax, xx - 1.3, yy, xx + 1.3, yy, color=C["blue"], lw=0.9)
            # Compensate for the wide figure axes so the rendered glyph is round.
            ax.add_patch(Ellipse((xx, yy), width=1.55, height=3.3,
                                 facecolor=C["white"], edgecolor=C["blue"],
                                 linewidth=0.9, zorder=4))
            txt(ax, xx, yy, "P", size=4.6, color=C["blue"], weight="bold", ha="center")
    txt(ax, 86.0, 54.8, "8 PMUs · phase-A phasors", size=5.4,
        color=C["muted"], ha="center")
    arrow(ax, (86.0, 52.6), (86.0, 49.3), color=C["blue"], lw=0.9, scale=6)

    rows = [
        (r"$|V|,\angle V$", 16, C["blue"], 43.2),
        (r"$|I|,\angle I$", 15, C["orange"], 35.0),
        (r"$f,\dot f$", 16, C["purple"], 26.8),
    ]
    for label, count, color, yy in rows:
        txt(ax, 74.6, yy, label, size=5.8, color=C["ink"])
        xbar0, xbar1 = 84.2, 92.7
        ax.add_patch(Rectangle((xbar0, yy - 1.55), xbar1 - xbar0, 3.1,
                               facecolor=C["white"], edgecolor=C["rule"],
                               linewidth=0.55, zorder=1))
        # A compact bar with a central split recalls the paired channels.
        filled = (xbar1 - xbar0 - 0.5) * count / 16
        ax.add_patch(Rectangle((xbar0 + 0.25, yy - 1.0), filled,
                               2.0, facecolor=color, edgecolor="none", alpha=0.82, zorder=2))
        split = xbar0 + 0.25 + filled * (8 / count)
        seg(ax, split, yy - 1.25, split, yy + 1.25,
            color=C["white"], lw=0.65, z=3)
        txt(ax, 94.0, yy, str(count), size=5.6, color=color, weight="bold", ha="center")
    seg(ax, 74.6, 21.9, 97.0, 21.9, color=C["rule"], lw=0.65)
    txt(ax, 85.8, 17.3, r"$y_k\in\mathbb{R}^{47}$", size=9.0,
        color=C["ink"], weight="bold", ha="center")
    txt(ax, 85.8, 11.4, "30 reports/s · causal prefix only", size=5.0,
        color=C["muted"], ha="center")


def draw():
    fig, ax = plt.subplots(figsize=(7.15, 3.35))
    fig.subplots_adjust(0, 0, 1, 1)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    fig.patch.set_facecolor(C["white"])
    ax.set_facecolor(C["white"])

    txt(ax, 3.0, 95.2, "FROM PHYSICAL INTERVENTION TO CAUSAL PMU REPORT",
        size=8.0, color=C["ink"], weight="bold")
    txt(ax, 3.0, 90.8,
        "Restoration returns the network operator to base while dynamic and measurement histories continue.",
        size=5.8, color=C["muted"])
    seg(ax, 3.0, 87.5, 97.0, 87.5, color=C["rule"], lw=0.8)

    # Fine dividers create three editorial panels without enclosing cards.
    seg(ax, 26.5, 16.0, 26.5, 83.5, color=C["rule"], lw=0.7)
    seg(ax, 72.4, 16.0, 72.4, 83.5, color=C["rule"], lw=0.7)
    draw_operator_panel(ax)
    draw_response_panel(ax)
    draw_report_panel(ax)

    seg(ax, 3.0, 7.0, 97.0, 7.0, color=C["rule"], lw=0.7)
    txt(ax, 50.0, 3.4,
        r"$u,q$ return to base  ·  $x,\eta$ persist  ·  $z$ and terminal $I$ are re-solved",
        size=6.2, color=C["ink"], weight="medium", ha="center")
    return fig


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    fig = draw()
    fig.savefig(OUT / "physics_measurement_chain.pdf",
                bbox_inches="tight", pad_inches=0.035)
    fig.savefig(OUT / "physics_measurement_chain.png", dpi=300,
                bbox_inches="tight", pad_inches=0.035, facecolor="white")
    plt.close(fig)
    print("Built the illustrative causal physical-to-PMU schematic.")

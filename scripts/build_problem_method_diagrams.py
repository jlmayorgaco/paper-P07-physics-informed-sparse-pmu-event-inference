"""Build two polished vector diagrams for the P07 problem and method overview."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures" / "generated"

C = {
    "ink": "#20282E",
    "muted": "#5C6971",
    "rule": "#CDD6DA",
    "blue": "#0077A8",       # matches the protected IEEE-39 topology
    "orange": "#D55E00",
    "teal": "#087F78",
    "green": "#4B7F52",
    "pale_blue": "#F2F7F9",
    "pale_orange": "#FBF5EF",
    "pale_teal": "#F0F7F6",
    "pale_green": "#F2F7F1",
    "plot": "#FAFCFC",
    "white": "#FFFFFF",
}

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "mathtext.fontset": "dejavusans",
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})


def panel_frame(ax, letter, title, subtitle):
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7.5)
    ax.axis("off")
    ax.add_patch(FancyBboxPatch(
        (0.10, 0.10), 9.80, 7.28,
        boxstyle="round,pad=0.025,rounding_size=0.12",
        linewidth=0.85, edgecolor=C["rule"], facecolor=C["white"], zorder=0,
    ))
    ax.add_patch(Circle((0.61, 6.98), 0.20, facecolor=C["pale_blue"],
                        edgecolor="none", zorder=1))
    ax.text(0.61, 6.98, letter, ha="center", va="center",
            fontsize=8.2, weight="bold", color=C["blue"], zorder=2)
    ax.text(0.98, 7.00, title, fontsize=9.5, weight="bold",
            color=C["ink"], va="center", zorder=2)
    ax.text(0.52, 6.59, subtitle, fontsize=7.2,
            color=C["muted"], va="center", zorder=2)
    ax.plot([0.50, 9.50], [6.34, 6.34], color=C["rule"], lw=0.65, zorder=1)


def section_label(ax, x, y, text, color=None, size=6.8, weight="bold"):
    ax.text(x, y, text, fontsize=size, weight=weight,
            color=color or C["muted"], va="center", zorder=4)


def card(ax, x, y, w, h, title, body="", accent=None, face=None,
         title_size=7.2, body_size=6.6, title_color=None):
    accent = accent or C["rule"]
    face = face or C["white"]
    title_color = title_color or accent
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.045,rounding_size=0.12",
        linewidth=0.9, edgecolor=accent, facecolor=face, zorder=2,
    ))
    ax.add_patch(FancyBboxPatch(
        (x + 0.01, y + 0.10), 0.055, h - 0.20,
        boxstyle="round,pad=0.005,rounding_size=0.025",
        linewidth=0, edgecolor="none", facecolor=accent, zorder=3,
    ))
    ax.text(x + 0.20, y + h - 0.19, title, fontsize=title_size,
            weight="bold", color=title_color, va="top", zorder=4)
    if body:
        ax.text(x + 0.20, y + 0.24, body, fontsize=body_size,
                color=C["ink"], va="center", linespacing=1.15, zorder=4)


def chip(ax, x, y, w, h, text, edge, face, color, size=6.8):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.04,rounding_size=0.10",
        linewidth=0.85, edgecolor=edge, facecolor=face, zorder=2,
    ))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=size, weight="bold", color=color, zorder=3)


def arrow(ax, start, end, color=None, lw=1.0, scale=7.0):
    ax.add_patch(FancyArrowPatch(
        start, end, arrowstyle="-|>", mutation_scale=scale,
        linewidth=lw, color=color or C["ink"],
        connectionstyle="arc3,rad=0", shrinkA=0, shrinkB=1.8, zorder=5,
    ))


def save_figure(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{name}.pdf", bbox_inches="tight", pad_inches=0.035)
    fig.savefig(OUT / f"{name}.png", dpi=260,
                bbox_inches="tight", pad_inches=0.035, facecolor="white")
    plt.close(fig)


def draw_problem():
    fig, ax = plt.subplots(figsize=(3.55, 2.85))
    fig.subplots_adjust(0, 0, 1, 1)
    panel_frame(ax, "A", "WHY RECOVERY MATTERS",
                "A second event arrives before the first response fades.")

    section_label(ax, 0.55, 6.05, "EVENT SCHEDULE")
    ax.plot([1.15, 9.34], [5.56, 5.56], color=C["rule"], lw=1.05, zorder=1)
    # The two orange bars make ON intervals explicit and keep event labels
    # inside their intervals rather than over the line.
    for left, right, label in ((2.00, 4.22, "A  ACTIVE"),
                               (6.62, 8.76, "B  ACTIVE")):
        ax.add_patch(FancyBboxPatch(
            (left, 5.42), right - left, 0.28,
            boxstyle="round,pad=0.015,rounding_size=0.07",
            linewidth=0, edgecolor="none", facecolor=C["orange"], zorder=3,
        ))
        ax.text((left + right) / 2, 5.56, label, ha="center", va="center",
                fontsize=6.5, weight="bold", color=C["white"], zorder=4)
    for xmark in (2.00, 4.22, 6.62, 8.76):
        ax.plot([xmark, xmark], [5.34, 5.78], color=C["orange"],
                lw=1.0, zorder=3)
    ax.text(4.22, 5.18, "RESTORED", ha="center", va="top",
            fontsize=6.0, weight="bold", color=C["ink"])
    ax.text(6.62, 5.18, "B BEGINS", ha="center", va="top",
            fontsize=6.0, weight="bold", color=C["ink"])

    section_label(ax, 0.55, 4.46, "WHAT THE SPARSE PMUs OBSERVE")
    # Legend has a dedicated row above the plot, so it never covers the traces.
    ax.plot([1.20, 1.58], [4.18, 4.18], color=C["teal"], lw=1.35,
            ls=(0, (4, 2)), zorder=3)
    ax.text(1.68, 4.18, "A recovery", fontsize=6.4, color=C["ink"],
            va="center")
    ax.plot([5.15, 5.53], [4.18, 4.18], color=C["ink"], lw=1.45, zorder=3)
    ax.text(5.63, 4.18, "A recovery + B", fontsize=6.4, color=C["ink"],
            va="center")

    plot_x0, plot_x1 = 1.20, 9.35
    plot_y0, plot_y1 = 2.42, 3.91
    ax.add_patch(FancyBboxPatch(
        (plot_x0, plot_y0), plot_x1 - plot_x0, plot_y1 - plot_y0,
        boxstyle="round,pad=0.015,rounding_size=0.08",
        linewidth=0.45, edgecolor=C["rule"], facecolor=C["plot"], zorder=0.5,
    ))
    t = np.linspace(0, 10, 800)
    t_on, t_off, t_b = 1.05, 3.72, 6.66
    x_of_t = lambda v: plot_x0 + (plot_x1 - plot_x0) * v / 10
    x_off, x_b = x_of_t(t_off), x_of_t(t_b)
    ax.add_patch(Rectangle(
        (x_off, plot_y0 + 0.04), x_b - x_off, plot_y1 - plot_y0 - 0.08,
        linewidth=0, facecolor=C["pale_teal"], alpha=0.82, zorder=1,
    ))
    old = np.where(t >= t_on, 0.66 * np.exp(-0.245 * (t - t_on))
                   * np.sin(2.05 * (t - t_on) + 0.45), 0.0)
    dt = np.maximum(t - t_b, 0.0)
    new = np.where(t >= t_b, 0.45 * np.exp(-0.53 * dt)
                   * np.sin(3.0 * dt) + 0.15 * (1 - np.exp(-2.4 * dt))
                   * np.exp(-0.62 * dt), 0.0)
    center = 3.14
    ax.plot([plot_x0 + 0.08, plot_x1 - 0.08], [center, center],
            color=C["rule"], lw=0.65, zorder=1.4)
    ax.plot(x_of_t(t), center + old, color=C["teal"], lw=1.25,
            ls=(0, (4, 2)), zorder=2.2)
    ax.plot(x_of_t(t), center + old + new, color=C["ink"], lw=1.45,
            zorder=2.5)
    ax.plot([x_b, x_b], [plot_y0 + 0.08, plot_y1 - 0.08],
            color=C["orange"], lw=0.95, ls=(0, (2, 2)), zorder=1.8)
    ax.text(0.69, center, r"$r_k$", fontsize=7.7, weight="bold",
            color=C["blue"], va="center")
    axis_y = 2.32
    ax.plot([plot_x0 + 0.08, plot_x1 - 0.08], [axis_y, axis_y],
            color=C["muted"], lw=0.75, zorder=2)
    for tv, lab in ((t_on, r"$t_A$"), (t_off, "OFF"), (t_b, r"$t_B$")):
        xt = x_of_t(tv)
        ax.plot([xt, xt], [axis_y - 0.045, axis_y + 0.045],
                color=C["muted"], lw=0.75, zorder=2)
        ax.text(xt, 2.19, lab, ha="center", va="top",
                fontsize=6.2, color=C["muted"])

    card(ax, 0.55, 0.55, 4.30, 1.02, "RESET AT OFF",
         "Recovery tail can retrigger.",
         accent=C["orange"], face=C["pale_orange"],
         title_size=6.9, body_size=6.3)
    card(ax, 5.15, 0.55, 4.30, 1.02, "WAIT UNTIL SETTLED",
         "Waiting can miss event B.",
         accent=C["blue"], face=C["pale_blue"],
         title_size=6.9, body_size=6.3)
    return fig


def draw_method():
    fig, ax = plt.subplots(figsize=(3.55, 2.85))
    fig.subplots_adjust(0, 0, 1, 1)
    panel_frame(ax, "B", "HOW THE BANK REASONS",
                "Keep the old cause while testing for a new event.")

    ax.text(0.55, 6.16, "8 PMUs", fontsize=6.6, weight="bold",
            color=C["blue"], va="center")
    xs = np.linspace(1.70, 3.45, 8)
    for px in xs:
        ax.add_patch(Circle((px, 5.90), 0.095, facecolor=C["blue"],
                            edgecolor=C["white"], linewidth=0.55, zorder=3))
        ax.add_patch(Circle((px, 5.90), 0.026, facecolor=C["white"],
                            edgecolor="none", zorder=4))
    arrow(ax, (3.70, 5.90), (4.16, 5.90), C["blue"], lw=0.9)
    chip(ax, 4.20, 5.63, 1.63, 0.54, r"REPORT  $\mathbf{r}_k$",
         C["blue"], C["pale_blue"], C["blue"], size=6.5)
    arrow(ax, (5.86, 5.90), (6.34, 5.90), C["blue"], lw=0.9)
    chip(ax, 6.39, 5.63, 3.02, 0.54, "5 R/X MODELS",
         C["rule"], C["pale_blue"], C["blue"], size=6.7)

    # A straight branch sends the same report/model bank to both histories.
    ax.plot([7.90, 7.90], [5.63, 5.18], color=C["rule"], lw=0.95, zorder=2)
    ax.plot([2.67, 7.90], [5.18, 5.18], color=C["rule"], lw=0.95, zorder=2)
    ax.add_patch(Circle((7.90, 5.18), 0.055, facecolor=C["blue"],
                        edgecolor=C["white"], linewidth=0.45, zorder=3))
    section_label(ax, 0.55, 5.18, "HYPOTHESES", color=C["muted"], size=6.3)
    arrow(ax, (2.67, 5.18), (2.67, 4.94), C["teal"], lw=0.95)
    arrow(ax, (7.32, 5.18), (7.32, 4.94), C["orange"], lw=0.95)

    card(ax, 0.55, 4.02, 4.25, 0.86, "CONTINUE A",
         "Carry state through OFF.",
         accent=C["teal"], face=C["pale_teal"],
         title_size=7.0, body_size=6.35)
    card(ax, 5.20, 4.02, 4.25, 0.86, "TEST NEW B",
         "Test B during A's recovery.",
         accent=C["orange"], face=C["pale_orange"],
         title_size=7.0, body_size=6.35)

    # Both candidate histories reach a common scorer through separate vertical
    # arrows. No connector passes over a label or another connector.
    score_top, score_bottom = 3.68, 2.82
    arrow(ax, (2.67, 4.02), (2.67, score_top), C["teal"], lw=0.95)
    arrow(ax, (7.32, 4.02), (7.32, score_top), C["orange"], lw=0.95)
    card(ax, 0.80, score_bottom, 8.40, score_top - score_bottom,
         "SWITCHED-DAE PREDICTION + EVIDENCE",
         "Integrate load severity  ·  Switch the line model",
         accent=C["blue"], face=C["white"],
         title_size=7.2, body_size=6.55, title_color=C["ink"])

    # State/weight update and output flow are kept on one clean vertical/horizontal route.
    update_x, update_y, update_w, update_h = 0.55, 1.72, 5.00, 0.78
    update_cx = update_x + update_w / 2
    arrow(ax, (update_cx, score_bottom), (update_cx, update_y + update_h),
          C["ink"], lw=0.95)
    card(ax, update_x, update_y, update_w, update_h,
         "UPDATE STATE + WEIGHTS",
         "Replay once; keep state through OFF.",
         accent=C["teal"], face=C["pale_teal"],
         title_size=6.9, body_size=6.2, title_color=C["teal"])

    # Attribution panel: active intervention and originating cause stay distinct.
    metric_x, metric_y, metric_w, metric_h = 0.55, 0.50, 5.00, 0.88
    arrow(ax, (update_cx, update_y), (update_cx, metric_y + metric_h),
          C["ink"], lw=0.95)
    ax.add_patch(FancyBboxPatch(
        (metric_x, metric_y), metric_w, metric_h,
        boxstyle="round,pad=0.045,rounding_size=0.12",
        linewidth=0.9, edgecolor=C["rule"], facecolor=C["white"], zorder=2,
    ))
    ax.text(metric_x + metric_w / 2, 1.24, "ATTRIBUTION",
            ha="center", va="center", fontsize=6.1, weight="bold",
            color=C["muted"], zorder=3)
    ax.plot([metric_x + metric_w / 2, metric_x + metric_w / 2],
            [0.60, 1.10], color=C["rule"], lw=0.7, zorder=3)
    ax.text(metric_x + 1.25, 0.83, r"$M_c$  ACTIVE", ha="center", va="center",
            fontsize=6.6, weight="bold", color=C["blue"], zorder=3)
    ax.text(metric_x + 3.75, 0.83, r"$\Gamma_c$  CAUSE", ha="center",
            va="center", fontsize=6.6, weight="bold", color=C["teal"], zorder=3)

    pub_x, pub_y, pub_w, pub_h = 6.12, 0.50, 3.30, 0.88
    arrow(ax, (metric_x + metric_w, 0.94), (pub_x, 0.94), C["green"], lw=1.0)
    card(ax, pub_x, pub_y, pub_w, pub_h, "PUBLISH",
         "Source  ·  onset  ·  OFF",
         accent=C["green"], face=C["pale_green"],
         title_size=7.0, body_size=6.3, title_color=C["green"])
    return fig


if __name__ == "__main__":
    save_figure(draw_problem(), "problem_recovery_timeline")
    save_figure(draw_method(), "recovery_method_logic")
    print("Built two polished, editable vector problem/method diagrams.")

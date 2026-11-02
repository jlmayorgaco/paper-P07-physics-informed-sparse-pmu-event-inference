"""Draw the paper's problem-to-decision map without touching frozen figures."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures/generated"
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({"font.family": "DejaVu Sans", "pdf.fonttype": 42})
fig, ax = plt.subplots(figsize=(10.2, 3.15))
fig.patch.set_facecolor("white")
ax.set_xlim(0, 10.2)
ax.set_ylim(0, 3.15)
ax.axis("off")


def box(x, y, w, h, title, body, edge, fill):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle="round,pad=0.08,rounding_size=0.08",
                                linewidth=1.05, edgecolor=edge, facecolor=fill))
    ax.text(x + 0.13, y + h - 0.20, title, ha="left", va="top",
            fontsize=10.2, fontweight="bold", color=edge)
    ax.text(x + 0.13, y + h - 0.52, body, ha="left", va="top",
            fontsize=8.75, color="#202b35", linespacing=1.18)


def arrow(a, b, color="#54606a"):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=11,
                                 linewidth=1.15, color=color))


ax.text(0.10, 3.02, "THE PROBLEM", fontsize=10.4, fontweight="bold", color="#006f80")
ax.text(1.47, 3.02, "A PMU change after a switch has competing explanations", fontsize=10.3,
        color="#202b35")
box(0.12, 2.11, 2.90, 0.68, "Recovery", "Earlier event is OFF; machines still move", "#006f80", "#edf8f8")
box(3.65, 2.11, 2.90, 0.68, "New intervention", "Load or line changes during that recovery", "#b86220", "#fff5eb")
box(7.18, 2.11, 2.90, 0.68, "Model error", "True R/X can differ from the predictor", "#555b65", "#f4f5f6")

ax.text(0.10, 1.78, "AT EACH REPORT", fontsize=10.4, fontweight="bold", color="#006f80")
box(0.12, 0.76, 1.82, 0.78, "Observe", "8 PMUs: V, terminal I,\nf and ROCOF", "#15699b", "#edf6fb")
box(2.18, 0.76, 2.16, 0.78, "Propose histories", "No new event, load, line;\nretain past states", "#b86220", "#fff5eb")
box(4.59, 0.76, 2.16, 0.78, "Predict", "Switched DAE + PMU map\nunder fixed R/X models", "#006f80", "#edf8f8")
box(7.00, 0.76, 1.28, 0.78, "Compare", "Evidence and\nstate update", "#6d4d8a", "#f7f2fa")
box(8.53, 0.76, 1.55, 0.78, "Publish", "Alarm, source,\nOFF or wait", "#28744c", "#f0f8f2")
for x0, x1 in [(1.98, 2.14), (4.39, 4.55), (6.79, 6.96), (8.32, 8.49)]:
    arrow((x0, 1.15), (x1, 1.15))
ax.text(0.12, 0.40, "10 s of past states; onsets proposed over the latest 18 reports",
        fontsize=8.2, color="#525b64")
ax.text(5.19, 0.40, "State and cause retained after physical OFF",
        fontsize=8.2, color="#28744c")
ax.text(0.12, 0.12, "Reserved event truth enters only the later evaluation.",
        fontsize=8.2, color="#525b64")
fig.subplots_adjust(left=0.01, right=0.99, bottom=0.01, top=0.99)
fig.savefig(OUT / "reader_overview.pdf")
fig.savefig(OUT / "reader_overview.png", dpi=220)
plt.close(fig)

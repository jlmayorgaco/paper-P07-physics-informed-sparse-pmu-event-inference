"""Build the public condition table and figure from the sealed episode scores."""

import csv
from pathlib import Path
import sys
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from design_stress import c, RESULT, CONDITIONS


def table(scores):
    path = RESULT / "conditions.csv"
    fields = [
        "condition",
        "method",
        "records",
        "events",
        "macro_f1",
        "family",
        "family_fraction",
        "exact_site",
        "site_fraction",
        "extras",
        "quiet_extras",
        "event_record_extras",
        "quiet_hours",
        "quiet_fa_per_hour",
        "macro_f1_lo",
        "macro_f1_hi",
        "family_lo",
        "family_hi",
        "site_lo",
        "site_hi",
        "chronological_macro_f1",
        "chronological_family",
        "chronological_site",
        "chronological_extras",
    ]
    with path.open("w", encoding="utf8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        for s in CONDITIONS:
            for method, m in scores[s.name].items():
                seq = m["chronological"]
                ci = m["ci95"]
                writer.writerow(
                    [
                        s.name,
                        method,
                        m["records"],
                        m["events"],
                        m["macro_f1"],
                        m["family"],
                        m["family"] / m["events"],
                        m["site"],
                        m["site"] / m["events"],
                        m["extras"],
                        m["quiet_extras"],
                        m["event_record_extras"],
                        m["quiet_hours"],
                        m["quiet_fa_per_hour"],
                        *ci["macro_f1"],
                        *ci["family_fraction"],
                        *ci["site_fraction"],
                        seq["macro_f1"],
                        seq["family_fraction"],
                        seq["site_fraction"],
                        seq["extras"],
                    ]
                )


def figure(scores):
    loads = sorted(
        (s for s in CONDITIONS if s.name.startswith("load") or s.name == "reference"), key=lambda s: s.load
    )
    times = ["reference", "gap30", "gap15", "gap6", "gap0", "over10", "over25", "over50", "synchronous"]
    axes_spec = [
        (
            "Topología desconocida",
            ["reference", "topo1", "topo2"],
            [0, 1, 2],
            ["0", "1", "2"],
            "Líneas ya abiertas",
        ),
        (
            "Punto de operación",
            [s.name for s in loads],
            [(s.load - 1) * 100 for s in loads],
            None,
            "Cambio de demanda P y Q (%)",
        ),
        (
            "Separación de eventos",
            times,
            list(range(len(times))),
            ["ref.", "1 s", "0,5 s", "0,2 s", "0 s", "10 %", "25 %", "50 %", "simult."],
            "Intervalo tras despeje → superposición",
        ),
    ]
    fig, axes = plt.subplots(2, 3, figsize=(13, 6.5), width_ratios=[0.8, 1.25, 1.65])
    colors = ["#163d64", "#b04727", "#15775c"]
    labels = ["Macro-F1", "Familia", "Activo exacto"]
    methods = ["joint", "trees", "trees_refit"]
    mlabels = ["Grafo conjunto", "Árbol histórico", "Árbol reentrenado"]
    for j, (title, arms, x, ticks, xlabel) in enumerate(axes_spec):
        top, bottom = axes[:, j]
        top.set_title(title, weight="bold", fontsize=12)
        rows = [scores[k]["joint"] for k in arms]
        values = [[r["macro_f1"], r["family"] / r["events"], r["site"] / r["events"]] for r in rows]
        for a, (label, col, mk) in enumerate(zip(labels, colors, ["o", "s", "^"])):
            top.plot(x, [v[a] for v in values], color=col, marker=mk, ms=4, lw=1.4, label=label)
        top.axhline(0.96, color="#444444", ls="--", lw=1, label="Objetivo 0,96", zorder=0)
        top.set_ylim(-0.02, 1.035)
        for name, label, col, mk in zip(methods, mlabels, colors, ["o", "s", "^"]):
            bottom.plot(
                x,
                [scores[k][name]["extras"] for k in arms],
                marker=mk,
                ms=4,
                lw=1.4,
                color=col,
                label=label,
            )
        # Keep zero readable even when all comparators have very low counts.
        bottom.set_ylim(bottom=-max(1, bottom.get_ylim()[1] * 0.035))
        bottom.set_xlabel(xlabel, fontsize=10)
        for ax in (top, bottom):
            ax.grid(axis="y", alpha=0.22)
            ax.spines[["top", "right"]].set_visible(False)
            if ticks:
                ax.set_xticks(x, ticks)
            ax.tick_params(labelsize=9)
        top.tick_params(labelbottom=False)
        if j == 2:
            bottom.tick_params(axis="x", labelrotation=30)
    axes[0, 0].set_ylabel("Puntuación del grafo")
    axes[1, 0].set_ylabel("Alarmas extra / 132 registros")
    fig.legend(
        *axes[0, 0].get_legend_handles_labels(),
        loc="upper center",
        bbox_to_anchor=(0.5, 1.005),
        ncol=4,
        frameon=False,
    )
    fig.legend(
        *axes[1, 0].get_legend_handles_labels(),
        loc="lower center",
        bbox_to_anchor=(0.5, -0.005),
        ncol=3,
        frameon=False,
    )
    fig.tight_layout(rect=[0, 0.055, 1, 0.945], h_pad=1.3, w_pad=1.7)
    fig.savefig(RESULT / "stress.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    scores = c.load(RESULT / "scores.json")
    table(scores)
    figure(scores)

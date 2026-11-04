"""Figures and macros for the physics-derived detectability analysis (revision 2026-11-04).

Inputs: generated/revision_20261104/*.csv produced by theory_isolability.py,
theory_reset_cost.py and the N01 noise-stress evaluation (copied in by
import_noise_stress.py).  Outputs: figures/generated/theory_*.pdf/png and
generated/revision_20261104_macros.tex.  No campaign output is modified.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REV = ROOT / "generated/revision_20261104"
OUT = ROOT / "figures/generated"
BLUE, TEAL, ORANGE, DARK, GRAY, LIGHT = "#006a92", "#008f79", "#c46b22", "#263b49", "#777777", "#c9c9c9"
FAM = {"load": BLUE, "line": ORANGE}


def style() -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7.6, "axes.spines.top": False,
                         "axes.spines.right": False, "axes.edgecolor": "#8a8a8a", "axes.linewidth": .6,
                         "xtick.color": "#444444", "ytick.color": "#444444", "axes.labelcolor": DARK,
                         "xtick.major.width": .5, "ytick.major.width": .5, "legend.frameon": False})


def save(fig, stem: str) -> None:
    fig.savefig(OUT / f"{stem}.pdf", bbox_inches="tight", pad_inches=0.055)
    fig.savefig(OUT / f"{stem}.png", dpi=210, bbox_inches="tight", pad_inches=0.055)
    plt.close(fig)


def information_figure(summary: dict) -> dict:
    sig = pd.read_csv(REV / "isolability_signatures.csv")
    one = sig[sig.reports == 30].copy()
    one = one.sort_values(["family", "detection_info"], ascending=[False, True])
    need = summary["log_threshold"] - summary["log_prior_cell"]      # nats required at the true onset
    md = pd.read_csv(REV / "minimum_detectable_load.csv")
    fig, axes = plt.subplots(1, 2, figsize=(7.1, 2.55), gridspec_kw=dict(width_ratios=[1.05, 1]))
    ax = axes[0]
    y = np.arange(len(one))
    ax.barh(y, one.detection_info, color=[FAM[f] for f in one.family], height=.62)
    ax.scatter(one.isolation_info, y, marker="|", s=55, color=DARK, lw=1.3, zorder=3,
               label="isolation from nearest competitor")
    ax.axvline(need, color=DARK, lw=.9, ls="--")
    ax.text(need * 1.4, len(one) - .25, f"alarm needs {need:.0f} nats", fontsize=6.2, color=DARK, va="bottom")
    ax.set_xscale("log")
    ax.set_yticks(y, [s.replace("LINE", "L") for s in one.source], fontsize=6.4)
    ax.set_ylim(-.7, len(one) + .7)
    ax.set_xlabel("Expected log-likelihood ratio after 1 s (nats)")
    ax.set_title("(A) Detection information per source", fontsize=7.6, loc="left")
    ax.set_axisbelow(True)
    ax.grid(axis="x", color="#ececec", lw=.5)
    ax.text(.98, .02, "loads: 10% P/Q step\nlines: opening", transform=ax.transAxes, ha="right", va="bottom",
            fontsize=6.2, color="#444444")
    ax = axes[1]
    loads = md.copy()
    loads["pct"] = 100 * loads.min_fraction_1s
    for src, g in loads.groupby("source"):
        hot = src in ("BUS31", "BUS26")
        ax.plot(g.noise_multiplier, g.pct, color=BLUE if hot else LIGHT, lw=2 if hot else 1.1, marker="o",
                ms=3.2 if hot else 2.2, zorder=3 if hot else 2)
        last = g.iloc[-1]
        if hot or src in ("BUS20",):
            ax.text(last.noise_multiplier * 1.08, last.pct, f"{src} ({last.load_MW:.0f} MW)", fontsize=6.2,
                    va="center", color=DARK)
    ax.axhline(3, color=ORANGE, lw=.9, ls="--")
    ax.text(1.05, 3.4, "smallest tested change (3%)", fontsize=6.2, color=DARK)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xticks([1, 2, 5, 10, 20], ["1", "2", "5", "10", "20"])
    ax.set_xlim(.9, 60)
    ax.set_xlabel("Noise standard-deviation multiplier")
    ax.set_ylabel("Min. detectable change in 1 s (%)")
    ax.set_title("(B) Predicted detectability limit per load bus", fontsize=7.6, loc="left")
    ax.grid(color="#ececec", lw=.5)
    fig.tight_layout(w_pad=1.6)
    save(fig, "theory_information")
    b31 = loads[loads.source == "BUS31"].set_index("noise_multiplier")
    # multiplier at which BUS31 3% becomes undetectable within 1 s (interpolate: pct ~ multiplier)
    b31_cross = 3.0 / float(b31.pct.loc[1])
    others = loads[loads.source != "BUS31"]
    return dict(InfoNeed=f"{need:.0f}", InfoLoadMin=f"{one[one.family == 'load'].detection_info.min():.0f}",
                InfoLoadMax=f"{one[one.family == 'load'].detection_info.max():.1e}".replace("e+0", "\\times10^{").replace("e+", "\\times10^{") + "}",
                InfoLineMin=f"{one[one.family == 'line'].detection_info.min():.1e}".replace("e+0", "\\times10^{").replace("e+", "\\times10^{") + "}",
                BusThirtyOneCross=f"{b31_cross:.1f}",
                WorstOtherLoadPctTwenty=f"{others[others.noise_multiplier == 20].pct.max():.1f}",
                BusThirtyOneMW=f"{b31.load_MW.iloc[0]:.1f}")


def reset_figure() -> dict:
    r = pd.read_csv(REV / "reset_cost_prediction.csv")
    r["harm"] = (r.observed_extras_after > 0) | (r.next_event_timely_reset == False)  # noqa: E712
    s = json.loads((REV / "reset_cost_summary.json").read_text())
    need = s["log_threshold"] - s["log_prior_cell"]
    fig, ax = plt.subplots(figsize=(3.45, 2.15))
    rng = np.random.default_rng(7)
    for k, fam in enumerate(["load", "line"]):
        g = r[r.family == fam]
        x = k + rng.uniform(-.17, .17, len(g))
        ax.scatter(x[g.harm.to_numpy()], g.max_spurious_gain[g.harm], s=13, color=FAM[fam], lw=0, zorder=3)
        ax.scatter(x[~g.harm.to_numpy()], g.max_spurious_gain[~g.harm], s=13, facecolors="white",
                   edgecolors=FAM[fam], lw=.8, zorder=3)
        ax.text(k, g.max_spurious_gain.max() * 4, f"harm {g.harm.sum()}/{len(g)}", ha="center", fontsize=6.6,
                color=DARK)
    ax.axhline(need, color=DARK, lw=.9, ls="--")
    ax.text(1.45, need * 1.6, "alarm\nthreshold", fontsize=6.2, color=DARK, ha="right")
    ax.text(-.45, need * 1.6, "carry: gain = 0 (not on log axis)", fontsize=6.2, color=DARK)
    ax.set_yscale("log")
    ax.set_ylim(need / 3, r.max_spurious_gain.max() * 30)
    ax.set_xticks([0, 1], ["Load events", "Line events"])
    ax.set_xlim(-.5, 1.5)
    ax.set_ylabel("Spurious evidence after reset (nats)")
    ax.grid(axis="y", color="#ececec", lw=.5)
    ax.scatter([], [], s=13, color=GRAY, label="extra alarm or next event lost")
    ax.scatter([], [], s=13, facecolors="white", edgecolors=GRAY, label="no observed harm")
    ax.legend(loc="lower center", bbox_to_anchor=(.5, 1.0), ncol=2, fontsize=6.2, handletextpad=.2)
    fig.tight_layout()
    save(fig, "theory_reset_cost")
    return dict(ResetEvents=str(len(r)), ResetHarm=str(int(r.harm.sum())),
                ResetHarmLoad=f"{int(r[r.family == 'load'].harm.sum())}/{int((r.family == 'load').sum())}",
                ResetHarmLine=f"{int(r[r.family == 'line'].harm.sum())}/{int((r.family == 'line').sum())}",
                ResetGainMin=f"{r.max_spurious_gain.min():.1e}".replace("e+0", "\\times10^{").replace("e+", "\\times10^{") + "}",
                ResetFactorMin=f"{np.floor(np.log10(r.max_spurious_gain.min() / need)):.0f}")


def delay_macros() -> dict:
    d = pd.read_csv(REV / "predicted_vs_observed_delay.csv")
    g = d.groupby("family").observed_alarm_delay_s.median()
    return dict(PredAlarmDelay=f"{d.predicted_alarm_delay_s.median():.2f}", ObsLineDelay=f"{g['line']:.2f}",
                ObsLoadDelay=f"{g['load']:.2f}",
                LoadExcessReports=f"{round((g['load'] - d.predicted_alarm_delay_s.median()) * 30):.0f}")


def noise_figure() -> dict:
    path = REV / "noise_stress_events.csv"
    if not path.exists():
        return {}
    ev = pd.read_csv(path)
    nm = pd.read_csv(REV / "noise_stress_normals.csv")
    ex = pd.read_csv(REV / "noise_stress_extras.csv")
    md = pd.read_csv(REV / "minimum_detectable_load.csv")
    order = ["U1", "U5", "U10", "U20", "P05", "P10"]
    labels = ["×1", "×5", "×10", "×20", "+TVE\n0.05%", "+TVE\n0.1%"]
    fig, axes = plt.subplots(1, 2, figsize=(7.1, 2.45), gridspec_kw=dict(width_ratios=[1.3, 1]))
    ax = axes[0]
    x = np.arange(len(order))
    for k, fam in enumerate(["load", "line"]):
        rate = [ev[(ev.scenario == s) & (ev.family == fam)].timely.mean() * 100 for s in order]
        n = [len(ev[(ev.scenario == s) & (ev.family == fam)]) for s in order]
        ax.bar(x + (k - .5) * .38, rate, width=.36, color=FAM[fam], label=f"{fam} ({n[0]} interventions)",
               edgecolor="white", linewidth=1.0)
    ax.set_xticks(x, labels, fontsize=6.6)
    ax.set_ylim(0, 100)
    ax.set_ylabel("Timely correct source (%)")
    ax.set_title("(A) Unchanged nominal bank", fontsize=7.6, loc="left")
    ax.legend(loc="upper center", bbox_to_anchor=(.5, -.22), fontsize=6.4, ncol=2, handlelength=1.2)
    ax.set_axisbelow(True)
    ax.grid(axis="y", color="#ececec", lw=.5)
    ax.axvline(3.5, color=LIGHT, lw=.8, ls=":")
    ax = axes[1]
    oracle = pd.read_csv(REV / "independent_noise_oracle.csv")
    oracle = oracle[oracle.family == "load"]
    loads = ev[(ev.family == "load") & ev.scenario.isin(["P05", "P10"])].copy()
    loads["tve"] = loads.scenario.map({"P05": 0.0005, "P10": 0.001})
    m = loads.merge(oracle, on=["event", "tve"])
    rng = np.random.default_rng(3)
    for k, tve in enumerate([0.0005, 0.001]):
        g = m[m.tve == tve]
        xx = k + rng.uniform(-.16, .16, len(g))
        ok = g.timely.to_numpy()
        ax.scatter(xx[ok], g.oracle_info_angles[ok], s=16, color=TEAL, lw=0, zorder=3)
        ax.scatter(xx[~ok], g.oracle_info_angles[~ok], s=16, facecolors="white", edgecolors="#c1372c", lw=.9,
                   zorder=3)
    ax.axhline(15, color=DARK, lw=.9, ls="--")
    ax.text(1.45, 15 * 1.5, "alarm evidence", ha="right", fontsize=6.2, color=DARK)
    ax.set_yscale("log")
    ax.set_ylim(5, 1e6)
    ax.set_xlim(-.5, 1.5)
    ax.set_xticks([0, 1], ["+TVE 0.05%", "+TVE 0.1%"], fontsize=6.6)
    ax.set_ylabel("Angle information in 1 s (nats)")
    ax.set_title("(B) Load interventions: information vs outcome", fontsize=7.6, loc="left")
    ax.scatter([], [], s=16, color=TEAL, label="timely correct")
    ax.scatter([], [], s=16, facecolors="white", edgecolors="#c1372c", label="missed")
    ax.legend(loc="upper center", bbox_to_anchor=(.5, -.14), fontsize=6.4, ncol=2, handletextpad=.2)
    ax.set_axisbelow(True)
    ax.grid(axis="y", color="#ececec", lw=.5)
    fig.tight_layout(w_pad=1.6)
    save(fig, "noise_stress")
    loads_u = ev[(ev.family == "load") & ev.scenario.isin(["U1", "U5", "U10", "U20"])].copy()
    loads_u["alpha"] = loads_u.scenario.str[1:].astype(int)
    lim = md.set_index(["source", "noise_multiplier"]).min_fraction_1s
    predicted_ok = np.array([abs(a) >= lim.loc[(s, al)] for s, a, al in
                             zip(loads_u.source, loads_u.amplitude, loads_u.alpha)])
    agree = float((predicted_ok == loads_u.timely.to_numpy()).mean())
    out = dict(NoiseAgree=f"{100 * agree:.0f}", NoiseLoadEvents=str(len(ev[(ev.scenario == 'U1') & (ev.family == 'load')])),
               NoiseLineEvents=str(len(ev[(ev.scenario == 'U1') & (ev.family == 'line')])))
    for s in order:
        tag = {"U1": "One", "U5": "Five", "U10": "Ten", "U20": "Twenty", "P05": "TVEa", "P10": "TVEb"}[s]
        for fam in ["load", "line"]:
            g = ev[(ev.scenario == s) & (ev.family == fam)]
            out[f"Noise{tag}{fam.title()}"] = f"{int(g.timely.sum())}/{len(g)}"
        out[f"Noise{tag}Extras"] = str(int(ex[ex.scenario == s].extras.sum()))
        out[f"Noise{tag}NormalFA"] = str(int(nm[nm.scenario == s].alarms.sum()))
    out["NoiseNormalHours"] = f"{nm[nm.scenario == 'U1'].monitored_s.sum() / 3600:.2f}"
    return out


def main() -> None:
    style()
    OUT.mkdir(parents=True, exist_ok=True)
    summary = json.loads((REV / "isolability_summary.json").read_text())
    macros = {}
    macros.update(information_figure(summary))
    macros.update(reset_figure())
    macros.update(delay_macros())
    macros.update(noise_figure())
    lat = REV / "latency.json"
    if lat.exists():
        macros.update({k: v for k, v in json.loads(lat.read_text()).items() if isinstance(v, str)})
    prose = REV / "prose.json"   # hand-written sentences that quote N01 results (reviewed after the run)
    if prose.exists():
        macros.update(json.loads(prose.read_text(encoding="utf-8")))
    pending = ["AbstractNoise", "ConclusionNoise", "NomMsReport", "NomMsReportMax", "NomRecords", "NoiseDiscussion",
               "NoiseLoadEvents", "NoiseLineEvents", "NoiseNormalHours", "NoiseAgree"]
    for tag in ["One", "Five", "Ten", "Twenty", "TVEa", "TVEb"]:
        pending += [f"Noise{tag}{x}" for x in ["Load", "Line", "Extras", "NormalFA"]]
    for key in pending:
        macros.setdefault(key, r"\textbf{[PENDING]}")
    lines = ["% Generated by scripts/build_theory_figures.py -- do not edit"]
    for k, v in macros.items():
        lines.append(f"\\newcommand{{\\Rev{k}}}{{{v}}}")
    (ROOT / "generated/revision_20261104_macros.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()

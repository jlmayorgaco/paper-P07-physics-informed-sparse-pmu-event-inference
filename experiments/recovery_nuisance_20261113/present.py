"""Generate the manuscript values and the recovery-separation figure."""
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
seal = json.loads((HERE/"RESULTS_SEAL.json").read_text())
for name, expected in seal.items():
    if hashlib.sha256((HERE/name).read_bytes()).hexdigest() != expected:
        raise ValueError(f"Changed result input: {name}")
results = json.loads((HERE/"RESULTS.json").read_text())
geometry = results["geometry"]
timing = results["switching"]
matched, shifted = results["sequential"]
values = {
    "NuisanceContrasts": f'{geometry["rows"]:,}'.replace(",", r"\,"),
    "NuisanceWorstLoss": f'{100*(1-geometry["worst"]["retention"]):.1f}',
    "NuisanceRivalChanges": str(sum(g["changed"] for g in geometry["groups"])),
    "SwitchDerivativeError": f'{max(max(r["finite_difference_errors"]) for r in timing):.2e}'.replace("e-07", r"\times10^{-7}"),
    "SwitchMidpointError": f'{max(r["midpoint_max_ms"] for r in timing):.2f}',
    "NullMatchedCrossing": f'{100*matched["fraction"]:.2f}',
    "NullShiftedCrossing": f'{100*shifted["fraction"]:.2f}',
}
(ROOT/"generated/recovery_nuisance_macros.tex").write_text(
    "".join(f"\\newcommand{{\\{key}}}{{{value}}}\n" for key, value in values.items()))

plt.rcParams.update({"font.family":"serif","font.size":8,"pdf.fonttype":42,
                     "axes.spines.top":False,"axes.spines.right":False})
fig, ax = plt.subplots(figsize=(3.42, 2.12), layout="constrained")
for sd, color, marker, style, dx in ((.002,"#165268","o","-",-.05),
                                     (.01,"#a75228","s","--",.05)):
    groups = [g for g in geometry["groups"] if g["previous_sd"] == sd]
    x = [i+dx for i in range(len(groups))]
    median = [g["median"] for g in groups]
    p10 = [g["p10"] for g in groups]
    ax.errorbar(x, median, yerr=[[m-l for m,l in zip(median,p10)],[0]*len(x)],
                color=color, marker=marker, linestyle=style, linewidth=1,
                markersize=3.5, capsize=2, label=f"{100*sd:g}% prior SD")
ax.set_xticks(range(4), ["1/30","0.5","2","6"])
ax.set(xlabel="Gap after restoration (s)", ylabel="Separation retained",
       ylim=(.92,1.005), xlim=(-.27,3.27))
ax.set_yticks([.94,.96,.98,1.])
ax.yaxis.set_major_formatter(PercentFormatter(xmax=1,decimals=0))
ax.grid(axis="y",color="#dce4e7",linewidth=.6)
ax.legend(loc="lower left",frameon=False,fontsize=7,ncol=2)
path = ROOT/"figures/generated/recovery_nuisance.pdf"
fig.savefig(path)
fig.savefig(path.with_suffix(".png"), dpi=240)
plt.close(fig)

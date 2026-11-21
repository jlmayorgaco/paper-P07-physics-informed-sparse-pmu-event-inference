"""Plot blind exact-source success and control alarm rates by measurement condition."""
from pathlib import Path
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE=Path(__file__).resolve().parent
CONDITIONS=["native","joint","severe","holdover"]
LABELS=["Nominal","0.005°\n0.25 µs","0.008°\n0.50 µs","Drift +\nstep"]
NAMES={"graph":"Adaptive physics","angular":"Previous angles","magnitude":"Magnitudes","minirocket":"MiniRocket"}
COLORS=["#006557","#b54d17","#495c9b","#777777"]
MARKERS=["o","s","D","^"]


def plot():
    with (HERE/"results/summary.json").open() as f:
        primary=json.load(f)["primary"]
    fig,axes=plt.subplots(1,3,figsize=(10.9,3.6),sharey=True)
    panels=[("catalog","exact","Exact source · catalog"),("bus31","exact","Exact source · bus 31"),
            ("catalog","control_alarm","False alarms · catalog controls")]
    for ax,(panel,metric,title) in zip(axes,panels):
        for j,(arm,label) in enumerate(NAMES.items()):
            rows=[primary[panel][s] for s in CONDITIONS]
            n=rows[0]["controls" if metric=="control_alarm" else "positives"]
            y=np.array([r["arms"][arm][metric]/n for r in rows])*100
            ax.plot(np.arange(4)+(j-1.5)*.052,y,color=COLORS[j],marker=MARKERS[j],lw=1.25,
                    ms=5,label=label,zorder=5-j,alpha=.95)
        ax.set_title(title+f" (n={n})",fontsize=10)
        ax.set_xticks(range(4),LABELS,fontsize=8)
        ax.set_ylim(-4,104)
        ax.set_yticks([0,25,50,75,100])
        ax.grid(axis="y",alpha=.18)
        ax.spines[["top","right"]].set_visible(False)
    axes[0].set_ylabel("Records (%)")
    handles,labels=axes[0].get_legend_handles_labels()
    fig.legend(handles,labels,loc="lower center",ncol=4,frameon=False,fontsize=9)
    fig.subplots_adjust(left=.06,right=.985,top=.87,bottom=.25,wspace=.20)
    fig.savefig(HERE/"results/paired_performance.png",dpi=170,bbox_inches="tight")
    plt.close(fig)


if __name__=="__main__":
    plot()

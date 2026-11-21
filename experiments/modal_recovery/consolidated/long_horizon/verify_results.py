"""Verify supplemental counts and summarize detection and false alarms at the 30 s horizon."""
from pathlib import Path
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import f1_score
import numpy as np

HERE=Path(__file__).resolve().parent
OUT=HERE/"results"


def read(name):
    return json.loads((OUT/name).read_text(encoding="utf8"))


def audit():
    result,truth,calls,third=map(read,("summary.json","truth.json","predictions.json","zip_predictions.json"))
    code={"none":0,"line":2,"load":4}
    for cond in ("native","joint"):
        for arm in ("short_curve","graph","minirocket","hackathon"):
            mat=[]; found=family=exact=false=0
            for k,tests in third["cases"].items():
                t=truth[k]
                true=code[t["family"]]
                if arm=="hackathon":
                    pred=tests[cond]["zip"]; out=pred["event_code"]; site=pred["site"]
                elif arm=="minirocket":
                    pred=tests[cond]["minirocket"]; out=code.get(pred["class"],-1); site=pred["site"]
                else:
                    pred=calls[k][cond][arm]; site=pred["label"][1] if pred["label"] else None
                    out=code[pred["label"][0]] if pred["label"] else (-1 if pred["alarm"] is not None else 0)
                mat.append((true,out))
                if true==0:
                    false+=out!=0
                else:
                    found+=out!=0; family+=true==out; exact+=true==out and site==t["source"]
            check=result["window"][cond][arm]
            assert (found,family,exact,false)==tuple(check[m] for m in ("detection","family","exact","control_alarm"))
            assert abs(f1_score(*zip(*mat),labels=[0,2,4],average="macro",zero_division=0)-check["macro_f1"])<1e-12
    print("Recounted the eight native-window rows from individual source and event decisions.")


def plot():
    rows=read("summary.json")
    methods={"graph":"Adaptive physics · 30 s curves","short_curve":"Adaptive physics · 9 s curves",
             "minirocket":"MiniRocket","hackathon":"June ExtraTrees"}
    palette=["#00705e","#a66030","#4b6395","#666666"]
    fig,axes=plt.subplots(1,2,figsize=(8.8,3.8))
    for ax,key,title in zip(axes,("exact","control_alarm"),("Exact family and source","Alarms on recovery-only controls")):
        for j,(method,label) in enumerate(methods.items()):
            vals=[rows["window"][s][method][key] for s in ("native","joint")]
            x=np.arange(2)+(j-1.5)*.185
            ax.bar(x,vals,.165,color=palette[j],label=label)
            for xx,val in zip(x,vals):
                ax.text(xx,val+.8,str(val),ha="center",fontsize=8)
        ax.set_ylabel("Windows out of 48")
        ax.set_title(title,fontsize=10)
        ax.set_xticks([0,1],["Nominal","0.005° + 0.25 µs"])
        ax.set_ylim(0,54);ax.set_yticks([0,12,24,36,48])
        ax.spines[["top","right"]].set_visible(False)
    h,l=axes[0].get_legend_handles_labels()
    fig.legend(h,l,loc="lower center",ncol=2,fontsize=8,frameon=False)
    fig.subplots_adjust(bottom=.26,wspace=.32)
    fig.savefig(OUT/"full_window.png",dpi=180,bbox_inches="tight")
    plt.close(fig)


if __name__=="__main__":
    audit()
    plot()

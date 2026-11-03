"""Posthoc descriptive C01 restoration audit. Does not rematch events or change C01 metrics."""
from pathlib import Path
import csv, hashlib, json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
STAGE = HERE.parents[0]
PAPER = HERE.parents[3]
INPUT = PAPER / "generated" / "frozen" / "c01_20261029"
OUT = STAGE / "generated" / "closure_analysis"
TABLE = STAGE / "tables" / "generated" / "closure_restoration.tex"
FIG_DIR = STAGE / "figures" / "generated"
OUT.mkdir(parents=True, exist_ok=True); TABLE.parent.mkdir(parents=True, exist_ok=True); FIG_DIR.mkdir(parents=True, exist_ok=True)
MANIFEST = json.loads((INPUT / "MANIFEST.json").read_text(encoding="utf-8"))
expected = {x["path"]: x["sha256"] for x in MANIFEST["files"]}
for name in ("SUMMARY.csv", "EVENTS.csv", "PAIRED_INTERVALS.csv", "EVALUATION_AUDIT.json", "PREDICTIONS_SEAL.json"):
    actual = hashlib.sha256((INPUT / name).read_bytes()).hexdigest()
    if expected.get(name) != actual:
        raise SystemExit(f"C01 frozen copy hash mismatch: {name}: {actual}")

METHODS = {
    "R11": "Physical history bank",
    "R11_NOMINAL": "Nominal physical bank",
    "ET_REFERENCE": "Causal ExtraTrees",
    "ET_CANDIDATE": "Short-window ExtraTrees",
}
EXPECTED = {"R11": (644,72,0,4), "R11_NOMINAL": (643,92,0,5), "ET_REFERENCE": (330,29,52,318), "ET_CANDIDATE": (352,16,26,296)}
s = pd.read_csv(INPUT / "SUMMARY.csv")
e = pd.read_csv(INPUT / "EVENTS.csv")
s = s[(s.lane == "continuous") & s.method.isin(METHODS)]
e = e[(e.lane == "continuous") & e.method.isin(METHODS)]
rows=[]
for method in METHODS:
    sm=s[s.method==method]
    ev=e[e.method==method]
    event_total=int(sm.events.sum())
    timely=int(sm.timely.sum())
    extras=int(sm.event_extras.sum())
    off=ev.off_delay_s.dropna().astype(float).to_numpy()
    early=int(np.count_nonzero(off < -1/30))
    missing=int(ev.off_delay_s.isna().sum())
    if event_total != 648 or (timely,extras,early,missing) != EXPECTED[method]:
        raise SystemExit(f"Regression mismatch {method}: {(event_total,timely,extras,early,missing)}")
    rows.append({"method":method,"display_name":METHODS[method],"intended_event_realizations":event_total,
        "timely_attributions":timely,"event_extras":extras,"associated_restorations_available":len(off),
        "early_restorations_gt_one_report":early,"early_restorations_fraction_of_available":early/len(off) if len(off) else float("nan"),
        "events_without_associated_restoration_value":missing,"missing_fraction_of_648":missing/648,
        "minimum_signed_off_delay_s":float(off.min()) if len(off) else float("nan"),
        "median_signed_off_delay_s":float(np.median(off)) if len(off) else float("nan"),
        "maximum_signed_off_delay_s":float(off.max()) if len(off) else float("nan")})

# Machine-readable values with exact denominators and posthoc label.
with (OUT / "RESTORATION_AUDIT.csv").open("w", newline="", encoding="utf-8") as f:
    w=csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

tex=[r"\begin{table}[t]\centering\footnotesize\setlength{\tabcolsep}{2pt}",
 r"\caption{Posthoc description of episode restoration in the continuous evaluation. Early counts restorations with $d_{\mathrm{OFF}}<-1/30$ s (more than one report early); Early (\%) divides by Available. Missing counts absent restoration values out of 648 intended events, including omissions and not necessarily open episodes. Replays are dependent; no significance test is implied.}",
 r"\label{tab:closure-restoration}",
 r"\begin{tabular}{@{}lrrrr@{}}\toprule",
 r"Method & Available & Early & Missing & Early (\%) \\\midrule"]
table_names={"R11":"Physical bank","R11_NOMINAL":"Nominal bank","ET_REFERENCE":"ExtraTrees reference","ET_CANDIDATE":"ExtraTrees short"}
for r in rows:
    n=lambda x:f"{x:,}"
    tex.append(f"{table_names[r['method']]} & {n(r['associated_restorations_available'])} & {n(r['early_restorations_gt_one_report'])} & {n(r['events_without_associated_restoration_value'])} & {100*r['early_restorations_fraction_of_available']:.1f}" + r"\% " + r"\\")
tex += [r"\bottomrule\end{tabular}\end{table}"]
TABLE.write_text("\n".join(tex)+"\n", encoding="utf-8")

colors={"R11":"#006d77","R11_NOMINAL":"#83c5be","ET_REFERENCE":"#d1495b","ET_CANDIDATE":"#edae49"}
fig,ax=plt.subplots(1,2,figsize=(7.1,3.0),gridspec_kw={"width_ratios":[1.45,1]})
for m in METHODS:
    off=e.loc[e.method==m,"off_delay_s"].dropna().astype(float).to_numpy()
    x=np.sort(off); y=np.arange(1,len(x)+1)/len(x)
    ax[0].step(x,y,where="post",lw=1.6,color=colors[m],label=f"{METHODS[m]} (n={len(x)})")
ax[0].axvline(0,color="black",lw=.8)
ax[0].axvline(-1/30,color="#555555",lw=.8,ls="--")
ax[0].set(xlabel="Signed OFF delay (s)",ylabel="Empirical cumulative fraction",xlim=(float(e.off_delay_s.min())-.15,float(e.off_delay_s.max())+.15),ylim=(0,1))
ax[0].grid(axis="y",alpha=.22); ax[0].legend(frameon=False,fontsize=6.5,loc="lower right")
counts=[next(r["events_without_associated_restoration_value"] for r in rows if r["method"]==m) for m in METHODS]
labels=["Physical\nhistory","Nominal\nphysical","ExtraTrees\nreference","Short-window\nExtraTrees"]
bars=ax[1].bar(range(4),counts,color=[colors[m] for m in METHODS],width=.7)
ax[1].set_xticks(range(4),labels,fontsize=7); ax[1].set_ylabel("Events without restoration value / 648")
ax[1].set_ylim(0,350); ax[1].grid(axis="y",alpha=.22)
for bar,v in zip(bars,counts): ax[1].text(bar.get_x()+bar.get_width()/2,v+6,str(v),ha="center",va="bottom",fontsize=8)
fig.suptitle("Restoration timing and unavailable restoration values (posthoc)",fontsize=9)
fig.tight_layout()
fig.savefig(FIG_DIR / "closure_restoration.pdf",bbox_inches="tight")
fig.savefig(FIG_DIR / "closure_restoration.png",dpi=300,bbox_inches="tight")
plt.close(fig)

metadata={"status":"POSTHOC_DESCRIPTIVE_NO_REMATCHING","lane":"continuous","criterion":"off_delay_s < -1/30 s","criterion_interpretation":"more than one 30 Hz report early","early_denominator":"associated restoration values available for each method","missing_denominator":"648 intended event realizations per method; missing values include omissions and are not necessarily open episodes","replays":"dependent; no significance test","inputs":{n:hashlib.sha256((INPUT/n).read_bytes()).hexdigest() for n in ("SUMMARY.csv","EVENTS.csv","PAIRED_INTERVALS.csv","EVALUATION_AUDIT.json","PREDICTIONS_SEAL.json")},"results":rows}
(OUT/"RESTORATION_AUDIT.json").write_text(json.dumps(metadata,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"rows":rows,"outputs":[str(OUT/"RESTORATION_AUDIT.csv"),str(TABLE),str(FIG_DIR/"closure_restoration.pdf"),str(FIG_DIR/"closure_restoration.png"),str(OUT/"RESTORATION_AUDIT.json")]},indent=2))

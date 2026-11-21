"""Render all blind operating points and the contiguous tested limits from sealed scores."""
from stress_plan import RESULT,HERE,study
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


AXES = {"angle":("Instrument noise","angle","degrees RMS per channel"),
        "jitter":("Clock jitter","jitter","µs RMS per PMU"),
        "joint":("Combined noise and jitter","angle","degrees RMS per channel"),
        "drift":("Single-clock holdover","drift","µs/s for 8 s"),
        "step":("Single-clock step","step","µs"),
        "offset":("Persistent clock offset","offset","±µs per PMU")}


def label(row):
    s = row["setting"]
    if s["name"]=="nominal":
        return "native"
    if s["name"]=="joint":
        return f'{s["angle"]:g}° + {s["jitter"]:g} µs'
    value = s[AXES[s["name"]][1]]
    return f"{value:g}"


def span(rows,field):
    last = None
    fail = None
    later = []
    for row in rows:
        if row[field]:
            if fail is None:
                last = label(row)
            else:
                later.append(label(row))
        elif fail is None:
            fail = label(row)
    return last or "none",fail or "all passed",later


def figures(rows):
    fig,axes=plt.subplots(3,2,figsize=(11,10),layout="constrained")
    for ax,(family,(title,dim,unit)) in zip(axes.flat,AXES.items()):
        subset=[r for r in rows if r["setting"]["name"]==family]
        x=np.array([r["setting"][dim] for r in subset])
        a=np.array([min(r["catalog"]["angular"][k]/480 for k in ("detection","family","exact")) for r in subset])
        b=np.array([r["bus31"]["detected31"]/120 for r in subset])
        ax.plot(x,100*a,"o-",color="#245181",label="Lowest catalog efficacy")
        ax.plot(x,100*b,"^--",color="#217956",label="Bus-31 detection")
        ax.axhline(95,ls=":",lw=1,color="#444444")
        ax.set(xscale="log",ylim=(-3,105),title=title,xlabel=unit,ylabel="Correct (%)")
        ax.grid(alpha=.22)
        right=ax.twinx()
        alarms=[100*r["catalog"]["angular"]["control_alarm"]/480 for r in subset]
        right.plot(x,alarms,"s-",lw=1,ms=3,color="#ae5039",label="Alarmed catalog controls")
        right.set(ylim=(-3,105),ylabel="Alarmed controls (%)")
        passed=[j for j,r in enumerate(subset) if r["absolute_budget"]]
        ax.scatter(x[passed],np.full(len(passed),103),marker="|",s=50,color="black",label="Efficacy targets and <5% control alarms")
        if family=="angle":
            handles,labels=ax.get_legend_handles_labels()
            h,l=right.get_legend_handles_labels()
            fig.legend(handles+h,labels+l,loc="outside lower center",ncol=2,frameon=False)
    fig.savefig(RESULT/"operating_limits.png",dpi=165)
    plt.close(fig)


def main():
    rows=study.read(RESULT/"scores.json")["points"]
    for row in rows:
        target=row["bus31"]
        a=row["catalog"]["angular"]
        row["absolute_budget"]=(all(a[k]>456 for k in ("detection","family","exact"))
                                and target["detected31"]>114 and a["control_alarm"]<24)
        row["nominal_angular_budget"]=row["absolute_budget"] and a["control_alarm"]<=rows[0]["catalog"]["angular"]["control_alarm"]
        row["both_control_panels_and_quiet"]=(row["including_quiet_pass"] and
            target["angular"]["control_alarm"]<=target["magnitude"]["control_alarm"])
    native=rows[0]
    summary=["# Frozen PMU estimator under angular noise and clock error","",
             "The frozen angular estimator passed the full comparator-relative criterion in **0 of 55 conditions**. On the new native-noise cohort it correctly diagnosed all 480 catalog events and all 120 targeted loads at bus 31, but raised one alarm in 480 catalog controls. The magnitude estimator raised none. The angular arm also alarmed on two of the 120 targeted controls (zero for magnitudes). Independent static phase-reference offsets as large as ±26.5 µs produced exactly the same calls on all 1,200 records.","",
             "At 0.005° added angular noise per V and I channel, 335/480 first alarms preceded the actual second event. All 145 timely alarms gave the right family and asset. Only 38/120 targeted bus-31 loads were detected in time, and all 480 catalog controls alarmed. Premature triggering explains this loss at a scale near the low end of the [two-device laboratory measurements](https://arxiv.org/pdf/2103.09285). The experiment simulates instrument noise at these scales under the specified temporal model.","",
             "The estimator and protocol were frozen before new observations (commit `542d385`), the 1,200 anonymous records were archived at `079466c`, and every call was committed before unblinding at `86fea96`.","",
             "## Prospective operating limits","",
             "Each range extends from native noise to the last consecutively passing tested point. The left criterion uses the three catalog endpoints, recovery-control alarm budget and targeted bus-31 detection. The right criterion also requires no excess long-quiet episodes. A later passing point is listed separately after an earlier failure.","",
             "| Stress axis (units) | Last primary pass | First primary failure | Later primary passes | Last pass including long quiet | First failure including long quiet | Last pass also requiring no increase on targeted controls |",
             "|---|---:|---:|---|---:|---:|---:|"]
    for family,(title,dim,unit) in AXES.items():
        group=[native]+[r for r in rows if r["setting"]["name"]==family]
        last,fail,later=span(group,"primary_pass")
        long_last,long_fail,_=span(group,"including_quiet_pass")
        both_last,_,_=span(group,"both_control_panels_and_quiet")
        summary.append(f'| {title} ({unit}) | {last} | {fail} | {", ".join(later) or "—"} | {long_last} | {long_fail} | {both_last} |')
    if not any(row["primary_pass"] for row in rows):
        summary=summary[:summary.index("## Prospective operating limits")]
    summary.extend(["","## Descriptive limits under an absolute false-alarm budget","",
        "For interpretation, keep all four efficacy requirements but allow fewer than 5% of the 480 catalog recovery controls to alarm. This is a separate summary from the prespecified comparison against magnitudes. The last column instead allows at most the angular detector's own native count (one). Counts at each level, including high false-alarm rates on long quiet records, appear below.","",
        "| Axis | Last level below 5% catalog control alarms with all efficacy targets | First failing level | Last level with at most one alarm and all efficacy targets |",
        "|---|---:|---:|---:|"])
    for family,(title,_,unit) in AXES.items():
        group=[native]+[r for r in rows if r["setting"]["name"]==family]
        last,fail,_=span(group,"absolute_budget")
        own,_,_=span(group,"nominal_angular_budget")
        summary.append(f"| {title} ({unit}) | {last} | {fail} | {own} |")
    summary.extend(["","## Counts at every tested level","",
        "D, F and L count timely detection, correct family and exact location out of all 480 catalog second events. FA counts catalog recovery-only controls with alarms out of 480. The targeted panel has 120 independent bus-31 events and 120 controls. Long quiet counts upward-crossing episodes, with 5.861 eligible hours per setting. Repetitions across levels reuse the same inputs.","",
        f'The magnitude comparator reached {native["catalog"]["magnitude"]["detection"]}/480 detections, {native["catalog"]["magnitude"]["family"]}/480 correct families and {native["catalog"]["magnitude"]["exact"]}/480 locations, alarmed on {native["catalog"]["magnitude"]["control_alarm"]}/480 catalog controls, and detected {native["bus31"]["baseline31"]}/120 targeted bus-31 events. Its long-quiet count was {native["quiet"]["magnitude_episodes"]}.',"",
        "| Axis | Level | D | F | L | FA | Early | Bus 31 detected | Bus 31 exact | Targeted FA | Long quiet | Primary pass |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|:---:|"])
    for r in rows:
        a,b,q=r["catalog"]["angular"],r["bus31"]["angular"],r["quiet"]
        summary.append(f'| {r["setting"]["name"]} | {label(r)} | {a["detection"]} | {a["family"]} | {a["exact"]} | {a["control_alarm"]} | {a["early"]} | {b["detection"]} | {b["exact"]} | {b["control_alarm"]} | {q["angular_episodes"]} | {"yes" if r["primary_pass"] else "no"} |')
    summary.extend(["","The noise processes, input units, sampling approximation, denominators and inclusion rules are specified in the [prospective protocol](PROTOCOL.md). The [full scores](results/scores.json) include marginal uncertainty and discordant recovery-control calls. The [machine-readable grid](results/operating_points.csv) and [figure](results/operating_limits.png) use the same observations. Models and threshold stayed frozen throughout.",
        "","Recount from the committed outputs with `python score.py score`. To rerun both estimators on the archived anonymous PMUs at every level, run `python predict.py replay`. The quiet comparison uses the upstream P2 archive."])
    (HERE/"RESULTS.md").write_text("\n".join(summary)+"\n",encoding="utf8")
    figures(rows)


if __name__=="__main__":
    main()

"""Common-trigger CNN-F and HYDRA source decisions in the fresh late-event trial."""
from model_long import OUT,WORK,inputs,study
from literature import li_wang
import hydra_arm
from phase_data import channels
from adjudicate import committed
from metrics import outcomes
import sys


def predict():
    model=hydra_arm.load_head()
    import torch
    torch.set_num_threads(1)
    manifest=study.read(OUT/"inputs.json")["records"]
    graph=study.read(OUT/"predictions.json")
    calls={}
    for key,meta in sorted(manifest.items()):
        calls[key]={}
        for cond,raw,c in inputs(WORK/"pmu"/(key+".npz"),meta):
            alarm=graph[key][cond]["graph"]["alarm"]
            calls[key][cond]=dict(li_wang=dict(alarm=alarm,label=li_wang(raw,c,alarm)),
                                  hydra=dict(alarm=alarm,label=hydra_arm.label(channels(raw),alarm,model)))
    study.save(OUT/"literature_calls.json",calls)


def score():
    committed(OUT/"literature_calls.json")
    truth=study.read(OUT/"truth.json")
    calls=study.read(OUT/"literature_calls.json")
    graph=study.read(OUT/"predictions.json")
    summary={}
    for cond in ("native","joint"):
        counts=dict(eligible=0,graph_family=0,graph_exact=0,li_wang_family=0,hydra_family=0,hydra_exact=0)
        for key,t in truth.items():
            p=graph[key][cond]["graph"]
            b=p["alarm"]
            if t["on"] is None or b is None or 2*b<round(60*t["on"]) or 2*(b+29)>=round(60*t["off"]):
                continue
            counts["eligible"]+=1
            for arm,pred in dict(graph=p,**calls[key][cond]).items():
                assert pred["alarm"]==b
                v=outcomes(t,pred)
                counts[arm+"_family"]+=v["family"]
                if arm!="li_wang":
                    counts[arm+"_exact"]+=v["exact"]
        summary[cond]=counts
    if (OUT/"comparison_literature.json").exists():
        assert summary==study.read(OUT/"comparison_literature.json")
    else:
        study.save(OUT/"comparison_literature.json",summary)
    print(summary)


if __name__=="__main__":
    {"predict":predict,"score":score}[sys.argv[1]]()

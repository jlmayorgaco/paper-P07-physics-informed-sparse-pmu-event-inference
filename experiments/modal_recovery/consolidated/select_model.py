"""Choose a covariance model and alarm threshold on previously disclosed data only."""
from robust import TMP,RESULT,CONDITIONS,records,Errors,study,joblib
from metrics import outcomes
import numpy as np
import sys


def collect(name):
    bg,gate,source = joblib.load(TMP/(name+".joblib"))
    peaks=[]
    for i,k,y,c in records("cal"):
        noise=Errors(480000+i,len(y),c)
        peaks.append(max(float(gate.scores(bg.residual(noise.apply(y,s),c)).max()) for s in CONDITIONS.values()))
    thresholds=np.array(sorted(peaks))[[311,317,319]]
    truth=study.read(study.ROOT/"tmp/relative_phase/dev/targets.json")
    rows=[{name:dict(detection=0,family=0,exact=0,false=0,bus31=0) for name in CONDITIONS} for _ in thresholds]
    for i,k,y,c in records("dev"):
        t=truth[k]
        noise=Errors(490000+t["parent"],len(y),c)
        for setting,s in CONDITIONS.items():
            r=bg.residual(noise.apply(y,s),c)
            scores=gate.scores(r)
            for j,tau in enumerate(thresholds):
                hits=np.flatnonzero(scores>tau)
                b=gate.length-1+int(hits[0]) if len(hits) else None
                label=None
                if b is not None and b+29<len(r):
                    label=source.classify(r[b+30-source.length:b+30])
                v=outcomes(t,dict(alarm=c+b if b is not None else None,label=label))
                out=rows[j][setting]
                if t["on"] is None:
                    out["false"]+=v["control_alarm"]
                else:
                    for m in ("detection","family","exact"):
                        out[m]+=v[m]
                    out["bus31"]+=v["detection"] and t["source"]=="BUS31"
    data=[dict(name=name,tau=float(t),scenarios=r) for t,r in zip(thresholds,rows)]
    study.save(TMP/(name+"_paired_selection.json"),data)
    print(data,flush=True)


if __name__=="__main__":
    collect(sys.argv[1])

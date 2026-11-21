"""Select an onset model on two previously disclosed cohorts; never read the new test."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import study
from cohort import TMP, HERE
import model
import joblib
import numpy as np


def inputs(split):
    manifest=study.read(TMP/(split+"_manifest.json"))
    paths=sorted((TMP/split).glob("*.npz"))
    assert len(paths)==manifest["parents"] and all(study.digest(p)==manifest["hashes"][p.stem] for p in paths)
    return [study.unpack(p) for p in paths]


def development_set():
    rows=[]
    for raw, result in [("modal_recovery",study.RESULT),("modal_recovery_lag",study.HERE/"fixed_lag/results")]:
        truth=study.read(result/"truth.json")
        for k,t in sorted(truth.items()):
            y,clear=study.unpack(study.ROOT/"tmp"/raw/"test"/(k+".npz"))
            rows.append((k,y,clear,t))
    return rows


def first_alarm(gate, y, clear, threshold):
    scores=gate.scores(y[clear:])
    crossings=np.flatnonzero(scores>threshold)
    return clear+gate.length-1+int(crossings[0]) if len(crossings) else None


def evaluate(records, gate, threshold, readout):
    counts=dict(detect=0,family=0,site=0,false=0,early=0,miss=0)
    for _,y,clear,t in records:
        b=first_alarm(gate,y,clear,threshold)
        if t["on"] is None:
            counts["false"]+=b is not None
        elif b is None:
            counts["miss"]+=1
        elif 2*b<round(60*t["on"]):
            counts["early"]+=1
        elif 2*b<round(60*t["off"]):
            counts["detect"]+=1
            end=b+29
            if end<len(y) and 2*end<round(60*t["off"]):
                family,site=readout.classify(y[end-readout.length+1:end+1])
                counts["family"]+=family==t["family"]
                counts["site"]+=site==t["source"]
    return counts


def main():
    train,cal=inputs("fit"),inputs("cal")
    records=development_set()
    with np.load(TMP/"templates.npz") as z:
        templates=dict(z)
    readout=model.fit(train,templates,84,4,np.arange(29,64))
    joblib.dump(readout,TMP/"readout.joblib",compress=3)
    results=[]
    for width in (3,5):
        gate=model.fit(train,templates,60,width,(4,10,20,26))
        values=sorted(float(gate.scores(y[c:]).max()) for y,c in cal)
        joblib.dump(gate,TMP/f"gate{width}.joblib",compress=3)
        for level in (.99,.995):
            threshold=values[int(np.ceil(level*(len(cal)+1)))-1]
            counts=evaluate(records,gate,threshold,readout)
            row=dict(width=width,level=level,threshold=threshold,**counts)
            print(row,flush=True)
            results.append(row)
    study.save(TMP/"development.json",results)


if __name__=="__main__":
    main()

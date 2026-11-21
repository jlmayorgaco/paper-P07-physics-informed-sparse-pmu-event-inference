"""Develop a physical recovery predictor without access to the prospective test."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import study
import develop
import recovery
import model
from cohort import TMP
import joblib
import numpy as np


def main():
    train,cal=develop.inputs("fit"),develop.inputs("cal")
    records=develop.development_set()
    with np.load(TMP/"recoveries.npz") as z:
        background=recovery.fit(dict(z),[y[:30] for y,_ in train])
    joblib.dump(background,TMP/"background.joblib",compress=3)
    with np.load(TMP/"templates.npz") as z:
        templates=dict(z)
    residuals=[(background.residual(y,c),0) for y,c in train]
    controls=[background.residual(y,c) for y,c in cal]
    examples=[]
    for key,y,c,t in records:
        target=dict(t)
        if t["on"] is not None:
            target.update(on=t["on"]-c/30, off=t["off"]-c/30)
        examples.append((key,background.residual(y,c),0,target))
    readout=model.fit(residuals,templates,84,4,np.arange(29,72),level=True)
    joblib.dump(readout,TMP/"conditional_readout.joblib",compress=3)
    results=[]
    for widths,ages,name in [(4,(5,12,20,32,42),"short"), (5,(8,18,30,42,54),"long")]:
        gate=model.fit(residuals,templates,60,widths,ages,level=True)
        joblib.dump(gate,TMP/(name+".joblib"),compress=3)
        values=sorted(float(gate.scores(r).max()) for r in controls)
        for level in (.975,.99,.995):
            threshold=values[int(np.ceil(level*(len(cal)+1)))-1]
            counts=develop.evaluate(examples,gate,threshold,readout)
            item=dict(name=name,level=level,threshold=threshold,**counts)
            print(item,flush=True)
            results.append(item)
    study.save(TMP/"conditional_development_ticks.json",results)


if __name__=="__main__":
    main()

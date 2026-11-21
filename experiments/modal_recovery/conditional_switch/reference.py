"""Compare the original quiet PMU reference with a post-restoration reference."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import study
import develop
import model
from cohort import TMP
import joblib
import numpy as np


def score_short_finalist():
    background = joblib.load(TMP/"background.joblib")
    gate = joblib.load(TMP/"short.joblib")
    source = joblib.load(TMP/"conditional_readout.joblib")
    records = []
    for k,y,c,t in develop.development_set():
        target = dict(t)
        if t["on"] is not None:
            target.update(on=t["on"]-c/30,off=t["off"]-c/30)
        records.append((k,background.residual(y,c),0,target))
    floor = max(r["max"] for r in study.read(TMP/"quiet_cal_short.json").values())
    rows = []
    for row in study.read(TMP/"conditional_development_ticks.json"):
        if row["name"]=="short":
            bound = row["threshold"]
            threshold = max(bound,floor)
            rows.append(dict(name="short",level=row["level"],threshold=threshold,recovery_bound=bound,
                             quiet_bound=floor,**develop.evaluate(records,gate,threshold,source)))
    study.save(TMP/"short_development_final.json",rows)


def develop_reference():
    background = joblib.load(TMP/"background.joblib")
    background.use_quiet_reference = True
    joblib.dump(background, TMP/"quiet_reference.joblib", compress=3)
    train = [(background.residual(y,c), 0) for y,c in develop.inputs("fit")]
    cal = [background.residual(y,c) for y,c in develop.inputs("cal")]
    records = []
    for k,y,c,t in develop.development_set():
        target = dict(t)
        if t["on"] is not None:
            target.update(on=t["on"]-c/30, off=t["off"]-c/30)
        records.append((k,background.residual(y,c),0,target))
    with np.load(TMP/"templates.npz") as z:
        templates = dict(z)
    readout = model.fit(train, templates, 84, 4, np.arange(29,72), level=True)
    joblib.dump(readout,TMP/"reference_readout.joblib",compress=3)
    gate = model.fit(train, templates, 60, 4, (5,12,20,32,42), level=True)
    joblib.dump(gate,TMP/"reference.joblib",compress=3)
    values = sorted(float(gate.scores(r).max()) for r in cal)
    from quiet import scan
    quiet = scan("F01","CAL",background,gate)
    study.save(TMP/"quiet_cal_reference.json",quiet)
    floor = max(v["max"] for v in quiet.values())
    rows = []
    for level in (.975,.99,.995):
        bound = values[int(np.ceil(level*(len(cal)+1)))-1]
        threshold = max(bound, floor)
        rows.append(dict(name="reference",level=level,threshold=threshold,recovery_bound=bound,
                         quiet_bound=floor,**develop.evaluate(records,gate,threshold,readout)))
    study.save(TMP/"reference_development.json",rows)
    print(rows)


if __name__ == "__main__":
    score_short_finalist()
    develop_reference()

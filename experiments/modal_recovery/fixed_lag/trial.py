"""Fresh common-trigger confirmation of delayed physical family and source readouts."""
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import data
import study
import estimator
import argparse
import json
import joblib
import numpy as np
from scipy.stats import binomtest

RESULT = HERE / "results"
TMP = study.ROOT / "tmp/modal_recovery_lag"
TAGS = ["immediate"] + [f"{arm}_{delay}" for arm in study.ARMS for delay in ("fixed", "mixed")]


def extended_template(args):
    asset, size = args
    e = data.sim.event(np.random.default_rng(0), asset, 120, 150)
    e["amplitude"] = size
    _, raw = data.sim.physical(dict(duration_s=4.75, events=[e]))
    y = data.channels(raw)
    response = y[60:120] - y[5:60].mean(axis=0)
    return response


def fit(workers):
    old = study.verify()
    target = RESULT / "freeze.json"
    assert not target.exists()
    RESULT.mkdir(parents=True, exist_ok=True)
    data.sim.initialize()
    tasks = [(a, amp) for a in data.sim.assets for amp in
             ((-.14,-.09,-.04,.04,.09,.14) if a["family"] == "load" else (None,))]
    with ProcessPoolExecutor(workers, initializer=data.sim.initialize) as pool:
        full = np.stack(list(pool.map(extended_template,tasks)))
    with np.load(study.TMP / "templates.npz") as z:
        templates = dict(z)
    assert study.digest(study.TMP / "templates.npz") == old["template_sha"]
    np.testing.assert_allclose(full[:,:30], templates["signatures"], rtol=1e-10, atol=1e-8)
    pre = np.zeros((len(full),30,16))
    padded = np.concatenate([pre, full],axis=1)
    # All hypotheses explain one common observation at b+29.
    displacements = np.stack([padded[:,30+d:60+d] - padded[:,d:30+d] for d in range(30)],axis=1)
    shifted = dict(modes_hz=templates["modes_hz"], signatures=displacements.reshape(-1,30,16),
                   ids=np.repeat(templates["ids"],30), families=np.repeat(templates["families"],30))
    paths = sorted((study.TMP / "fit").glob("*.npz"))
    assert all(study.digest(p)==old["fit_cal_inputs"][p.relative_to(study.TMP).as_posix()] for p in paths)
    train = [study.unpack(p) for p in paths]
    seals = {}
    for arm in study.ARMS:
        mixed = estimator.fit(shifted,train,arm)
        fixed = joblib.load(study.RESULT / (arm+".joblib"))
        np.testing.assert_allclose(mixed.matched[::30], fixed.matched, rtol=1e-8, atol=1e-6)
        p=RESULT/(arm+".joblib")
        joblib.dump(mixed,p,compress=3)
        seals[p.name]=study.digest(p)
    study.save(target,dict(models=seals, upstream=study.digest(study.RESULT/"freeze.json"),
                           files={f:study.digest(HERE/f) for f in ("PROTOCOL.md","trial.py")}, seed=5796071))


def verify():
    study.verify()
    f=study.read(RESULT/"freeze.json")
    assert f["upstream"]==study.digest(study.RESULT/"freeze.json")
    for base, group in ((RESULT,"models"),(HERE,"files")):
        assert all(study.digest(base/k)==v for k,v in f[group].items())
    return f


def init_new():
    data.TMP = TMP
    data.SEEDS["test"] = 5796071
    data.sim.initialize()


def generate(workers):
    verify()
    (TMP/"test").mkdir(parents=True, exist_ok=False)
    truth={}
    with ProcessPoolExecutor(workers, initializer=init_new) as pool:
        for rows in pool.map(data.parent,[("test",i) for i in range(96)]):
            truth.update(rows)
    assert len(truth)==192
    study.save(TMP/"truth.json",truth)
    (TMP/"target.sha256").write_text(study.digest(TMP/"truth.json"),encoding="ascii")


def predict():
    verify()
    fixed={a:joblib.load(study.RESULT/(a+".joblib")) for a in study.ARMS}
    mixed={a:joblib.load(RESULT/(a+".joblib")) for a in study.ARMS}
    limit=study.read(study.RESULT/"freeze.json")["thresholds"]["modal"]["value"]
    calls={}
    for path in sorted((TMP/"test").glob("*.npz")):
        y,clear=study.unpack(path)
        reports,scores,family,site=fixed["modal"].scan(y,clear)
        hits=np.flatnonzero(scores>limit)
        labels={}
        b=None
        if len(hits):
            k=hits[0]
            b=int(reports[k])
            labels["immediate"]=[str(family[k]),str(site[k])]
            if b+29<len(y):
                for delay,models in (("fixed",fixed),("mixed",mixed)):
                    for arm,m in models.items():
                        _,_,f,s=m.scan(y[b-30:b+30],0)
                        labels[arm+"_"+delay]=[str(f[0]),str(s[0])]
        calls[path.stem]=dict(alarm=b,labels=labels,sha=study.digest(path))
    assert len(calls)==192
    study.save(RESULT/"predictions.json",dict(calls=calls,freeze_sha=study.digest(RESULT/"freeze.json"),
                                              target_sha=(TMP/"target.sha256").read_text(encoding="ascii")))


def paired(x,y):
    plus=int((x & ~y).sum())
    minus=int((y & ~x).sum())
    return dict(wins=plus, losses=minus, exact_p=float(binomtest(plus,plus+minus).pvalue) if plus+minus else 1.)


def score():
    verify()
    pred=study.read(RESULT/"predictions.json")
    assert pred["freeze_sha"]==study.digest(RESULT/"freeze.json")
    assert pred["target_sha"]==study.digest(TMP/"truth.json")
    truth=study.read(TMP/"truth.json")
    assert set(pred["calls"])==set(truth)
    pos=sorted(k for k,t in truth.items() if t["family"]!="none")
    neg=sorted(set(truth)-set(pos))
    assert len(pos)==len(neg)==96
    calls=pred["calls"]
    flags={tag:{field:[] for field in ("family","site","in_time")} for tag in TAGS}
    for key in pos:
        t,a=truth[key],calls[key]
        b=a["alarm"]
        for tag, fields in flags.items():
            label=a["labels"].get(tag)
            timely=bool(label and t["on"]<=b/30 and (b+(0 if tag=="immediate" else 29))/30<t["off"])
            fields["in_time"].append(timely)
            fields["family"].append(bool(timely and label[0]==t["family"]))
            fields["site"].append(bool(timely and label[1]==t["source"]))
    totals={tag:{k:sum(v) for k,v in fields.items()} for tag,fields in flags.items()}
    comparisons={tag:paired(np.array(flags["modal_mixed"]["family"]),np.array(flags[tag]["family"]))
                 for tag in TAGS if tag!="modal_mixed"}
    pvals=sorted((comparisons[t]["exact_p"],t) for t in ("mean_mixed","quadratic_mixed"))
    adj_first=min(1.,pvals[0][0]*2)
    holm={pvals[0][1]:adj_first,pvals[1][1]:max(adj_first,pvals[1][0])}
    by_family={f:sum(ok and truth[k]["family"]==f for k,ok in zip(pos,flags["modal_mixed"]["family"]))
               for f in ("load","line")}
    study.save(RESULT/"truth.json",truth)
    value=dict(predictions_sha=study.digest(RESULT/"predictions.json"),truth_sha=study.digest(RESULT/"truth.json"),
               n=96,normal_twins_with_alarm=sum(calls[k]["alarm"] is not None for k in neg),
               totals=totals,paired_family=comparisons,holm=holm,modal_mixed_by_family=by_family)
    study.save(RESULT/"scores.json",value)
    print(json.dumps(value,indent=2))


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("stage",choices=("fit","generate","predict","score"))
    p.add_argument("--workers",type=int,default=8)
    args=p.parse_args()
    if args.stage in ("fit","generate"):
        {"fit":fit,"generate":generate}[args.stage](args.workers)
    else:
        {"score":score,"predict":predict}[args.stage]()

"""Learn a causal likelihood correction for the weak BUS31 alternative on disclosed twins."""
from robust import TMP, CONDITIONS, Errors, records, phase_data, study, joblib
from adaptive import is_quiet, weak_scores
from benchmark import call
from metrics import outcomes
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier


def features(weights,y,c):
    bg, gate, _=weights
    lr,r=weak_scores(y,c,weights)
    ix=gate.length-1+np.arange(len(lr))
    # The conditional evidence may be sustained during recovery even at a healthy bus.
    # Retain the recent path of the weak-source likelihood and the observed recovery size.
    seq=[lr[np.maximum(np.arange(len(lr))-k,0)] for k in (0,3,6,10,16,24)]
    v=r[:,16:23]
    mag=r[:,:16]/gate.scale[:16]
    def mean_block(v, lag, width):
        sums=np.vstack((np.zeros((1,v.shape[1])),np.cumsum(v,axis=0)))
        end=ix+1-lag
        return (sums[end]-sums[end-width])/width
    for width in (6,15,29):
        seq.append(mean_block(v,0,width)-mean_block(v,width,width))
    seq.extend((np.log1p(abs(mean_block(mag,0,12))).mean(axis=1),
                np.log1p(abs(mean_block(mag,25,12))).mean(axis=1),
                np.repeat(np.log1p(np.linalg.norm(mag[:30],axis=1).mean()),len(lr))))
    return np.column_stack(seq)


def fit():
    weights=joblib.load(TMP/"history_joint.joblib")
    base=phase_data.HERE.parent/"clock_stress/results"
    catalog=study.read(base/"inputs.json")["records"]
    truth=study.read(base/"truth.json")
    data=[]; labels=[]; rng=np.random.default_rng(583712)
    for key,t in sorted(truth.items()):
        weak=t["source"]=="BUS31"
        # A dedicated earlier BUS31 panel supplies harder positive examples.
        # All earlier null twins remain eligible, including recovery after large outages.
        p=study.ROOT/"tmp/clock_stress/pmu"/(key+".npz")
        assert study.digest(p)==catalog[key]["sha"]
        y,c=study.unpack(p)
        stream=catalog[key]["stream"]
        err=Errors(641000+stream,len(y),c)
        for cond in list(CONDITIONS.values())[1:]:
            f=features(weights,err.apply(y,cond),c)
            offsets=2*(np.arange(len(f))+c+59)
            if weak:
                ok=np.flatnonzero((offsets>=round(t["on"]*60)+12)&(offsets<=min(round(t["on"]*60)+85,round(t["off"]*60)-60)))
                if len(ok):
                    chosen=rng.choice(ok,10)
                    data.extend(f[chosen]); labels.extend([1]*len(chosen))
            if t["on"] is None or not weak:
                chosen=rng.integers(len(f),size=14)
                data.extend(f[chosen]); labels.extend([0]*len(chosen))
    clf=HistGradientBoostingClassifier(max_iter=120,max_leaf_nodes=11,l2_regularization=8,random_state=571).fit(data,labels)
    joblib.dump(clf,TMP/"odds.joblib",compress=3)


def weak_decision(y,c,weights,clf,threshold,base):
    features_y=features(weights,y,c)
    score=clf.decision_function(features_y)
    hits=np.flatnonzero(score>threshold)
    if len(hits):
        b=c+59+int(hits[0])
        if base["alarm"] is None or b<base["alarm"]:
            return dict(alarm=b,label=["load","BUS31"] if b+29<len(y) else None)
    return base


def evaluate():
    from stress_plan import frozen
    from adaptive import learn_quality
    local=joblib.load(TMP/"local.joblib")
    joint=joblib.load(TMP/"history_joint.joblib")
    clf=joblib.load(TMP/"odds.joblib")
    quality=learn_quality()
    angular,tau=frozen.arms()["angles"]
    strong=study.read(TMP/"local_paired_selection.json")[-1]["tau"]
    peaks=[]
    for i,_,y,c in records("cal"):
        e=Errors(480000+i,len(y),c)
        peaks.append(max(float(clf.decision_function(features(joint,e.apply(y,s),c)).max()) for s in list(CONDITIONS.values())[1:]))
    truth=study.read(phase_data.TMP/"dev/targets.json")
    opts=[dict(name="odds",tau=sorted(peaks)[i],strong_tau=strong,quality=quality,
               scenarios={s:dict(detection=0,family=0,exact=0,false=0,bus31=0) for s in CONDITIONS}) for i in (311,317,319)]
    for _,k,y,c in records("dev"):
        t=truth[k]
        e=Errors(490000+t["parent"],len(y),c)
        for name,s in CONDITIONS.items():
            z=e.apply(y,s)
            quiet=is_quiet(z,quality)
            (bg,g,h),th=(angular,tau) if quiet else (local,strong)
            base=call(bg.residual(z,c),c,g,h,th)
            scores=None if quiet else clf.decision_function(features(joint,z,c))
            for row in opts:
                pred=base
                if scores is not None:
                    hits=np.flatnonzero(scores>row["tau"])
                    if len(hits):
                        b=c+59+int(hits[0])
                        if base["alarm"] is None or b<base["alarm"]:
                            pred=dict(alarm=b,label=["load","BUS31"] if b+29<len(y) else None)
                v=outcomes(t,pred)
                dst=row["scenarios"][name]
                if t["on"] is None:
                    dst["false"]+=v["control_alarm"]
                else:
                    for m in ("detection","family","exact"):
                        dst[m]+=v[m]
                    dst["bus31"]+=v["detection"] and t["source"]=="BUS31"
    study.save(TMP/"odds_paired_selection.json",opts)
    print(opts,flush=True)


if __name__=="__main__":
    fit()
    evaluate()

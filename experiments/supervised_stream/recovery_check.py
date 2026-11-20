"""Development-only physical recovery residual. Preserve all published times and classes."""
import hashlib
import json
import numpy as np

from larger import OUT, STORE, WAIT, candidates, telemetry, family_features, ranking, first
from online import load_model


def history(z,on):
    # The last four reports are excluded to tolerate onset-estimation error.
    values=z[on-64:on-4,:,:4].reshape(12,5,32).mean(1,dtype=float)
    return np.r_[values.ravel(),1.]


def fit(model):
    obs=np.load(STORE/"train/observations.npy",mmap_mode="r")
    truth=json.loads((STORE/"train/truth.json").read_text())
    xx=np.zeros((385,385))
    xy=np.zeros((385,WAIT*32))
    xs,ys=[],[]
    for rid,(r,events) in enumerate(zip(obs,truth)):
        z=first.normalized(r,model["scales"])
        for t in range(66+rid%11,len(z)-WAIT,15):
            # Avoid interventions in the prediction horizon or history used for estimation.
            if any(e["onset"]<t+WAIT and e["end"]>t-64 for e in events):
                continue
            x=history(z,t)
            y=z[t:t+WAIT,:,:4].reshape(-1).astype(float)
            w=1/max(1.,np.sqrt(np.mean(x[:-1]**2)))
            xs.append(w*x)
            ys.append(w*y)
        if len(xs)>1000 or rid==len(truth)-1:
            if xs:
                x,y=np.asarray(xs),np.asarray(ys)
                xx+=x.T@x
                xy+=x.T@y
                xs,ys=[],[]
    return np.linalg.solve(xx+np.diag(.001*np.diag(xx)+1.),xy)


def main():
    model=load_model()
    reg=fit(model)
    records=[]
    tau,cf=model["thresholds"]
    for r in np.load(STORE/"dev/observations.npy",mmap_mode="r"):
        z=first.normalized(r,model["scales"])
        alerts=[]
        for start,when in candidates(telemetry(z,model["trigger"],model["clock"]),tau):
            prefix=z[:when+1]
            p=model["family"].predict_proba(family_features(prefix,start)[None,:])[0]
            if 1-p[0]<cf:
                continue
            c=int(np.argmax(p[1:])+1)
            def asset(obs):
                x=ranking(obs,start,c,model)
                return model["catalog"][c][np.argmax(model["rankers"][c].predict_proba(x)[:,1])]
            old=asset(prefix)
            new=old
            if alerts and start>=64 and c not in (5,7):
                pred=(history(prefix,start)@reg).reshape(WAIT,8,4)
                residual=prefix.copy()
                residual[:start,:,:4]=0
                residual[start:,:,:4]-=pred
                new=asset(residual)
            alerts.append(dict(published=when,code=c,old=old,new=new))
        records.append(alerts)
    path=OUT/"dev_recovery_predictions.json"
    path.write_text(json.dumps(records))
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    truth=json.loads((STORE/"dev/truth.json").read_text())
    n=baseline=updated=gain=loss=0
    for es,alerts in zip(truth,records):
        for e in es:
            n+=1
            a=next((k for k in alerts if 0<=k["published"]-e["onset"]<=45),None)
            if a and a["code"]==e["code"]:
                old=a["old"]==e["source"]
                new=a["new"]==e["source"]
                baseline+=old
                updated+=new
                gain+=new and not old
                loss+=old and not new
    summary=dict(records=len(records),events=n,baseline=baseline,updated=updated,
                 gains=gain,losses=loss,release_eligible=bool(updated/n>.95 and updated>baseline),
                 predictions_sha256=digest)
    (OUT/"dev_recovery.json").write_text(json.dumps(summary,indent=2))
    print(summary)


if __name__=="__main__":
    main()

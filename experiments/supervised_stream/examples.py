"""Independent scripted checks against the user's normal and repeated-fault examples."""
import hashlib
import json
import numpy as np
import joblib

from larger import OUT, WAIT, Generator, candidates, telemetry, family_features, ranking, first


def monitor(measurements,m):
    z=first.normalized(measurements,m["scales"])
    tau,cf=m["thresholds"]
    out=[]
    for start,when in candidates(telemetry(z,m["trigger"],m["clock"]),tau):
        prefix=z[:when+1]
        p=m["family"].predict_proba(family_features(prefix,start)[None,:])[0]
        if 1-p[0]>=cf:
            code=int(np.argmax(p[1:])+1)
            r=m["rankers"][code].predict_proba(ranking(prefix,start,code,m))[:,1]
            out.append(dict(frame=when,time_s=round(when/30,3),code=code,
                            source=m["catalog"][code][int(np.argmax(r))]))
    return out


def main():
    file=OUT/"model.joblib"
    assert hashlib.file_digest(open(file,"rb"),"sha256").hexdigest()==json.loads((OUT/"model_freeze.json").read_text())["model_sha256"]
    model=joblib.load(file)
    plant=Generator()
    def fault(frame,bus):
        return dict(onset=frame,end=frame+8,code=1,source=f"BUS{bus}",sensors=[2,5],strength=1.)
    cases={"normal":[], "one_fault":[fault(144,2)],
           "same_fault_twice":[fault(144,2),fault(417,2)],
           "two_fault_locations":[fault(144,2),fault(417,10)]}
    report={}
    for i,(name,events) in enumerate(cases.items()):
        obs=plant.simulate(events,np.random.default_rng(718831+i))
        controls=OUT/"controls"
        controls.mkdir(exist_ok=True)
        np.save(controls/f"{name}.npy",obs)
        alerts=monitor(obs,model)
        report[name]=dict(truth=[dict(time_s=e["onset"]/30,code=e["code"],source=e["source"]) for e in events],
                          alarms=alerts)
        # Change every subsequent sample; earlier publications must remain identical.
        end=330
        changed=obs.copy()
        changed[end:]=obs[:len(obs)-end][::-1]
        assert [a for a in monitor(changed,model) if a["frame"]<end]==[a for a in alerts if a["frame"]<end]
    (OUT/"scripted_controls.json").write_text(json.dumps(report,indent=2))
    print(json.dumps(report))


if __name__=="__main__":
    main()

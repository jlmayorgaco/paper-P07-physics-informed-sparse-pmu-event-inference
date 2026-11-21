"""Counterfactual replay of the six misses and six early alarms from the prior trial."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
import data
import study
import joblib
import numpy as np


def switches(parent):
    rng=np.random.default_rng([5796071,parent])
    def choose(family, exclude=None):
        items=[a for a in data.sim.assets if a["family"]==family and a["id"]!=exclude]
        return items[int(rng.integers(len(items)))]
    first=data.sim.event(rng,choose(("load","line")[parent%2]),2*int(rng.integers(52,69)),
                         2*int(rng.integers(60,121)))
    rng.integers(1,2**31)
    second=data.sim.event(rng,choose(("load","line")[parent//2%2],first["source"]),
                          first["off_tick"]+int(rng.integers(75,241)),int(rng.integers(120,241)))
    return first,second


def main():
    prior=study.HERE/"fixed_lag/results"
    metrics=study.read(prior/"scores.json")
    for name in ("predictions","truth"):
        assert study.digest(prior/(name+".json"))==metrics[name+"_sha"]
    calls=study.read(prior/"predictions.json")["calls"]
    truth=study.read(prior/"truth.json")
    twins={t["parent"]:k for k,t in truth.items() if t["on"] is None}
    model=joblib.load(study.RESULT/"modal.joblib")
    threshold=study.verify()["thresholds"]["modal"]["value"]
    data.sim.initialize()
    failures=[]
    for key,t in truth.items():
        alarm=calls[key]["alarm"]
        if t["on"] is None or (alarm is not None and alarm/30>=t["on"]):
            continue
        twin=twins[t["parent"]]
        obs=[]
        for obs_id in (key,twin):
            path=study.ROOT/"tmp/modal_recovery_lag/test"/(obs_id+".npz")
            assert study.digest(path)==calls[obs_id]["sha"]
            y,clear=study.unpack(path)
            obs.append(y)
        y,control=obs
        first,second=switches(t["parent"])
        assert (first["source"],first["off_tick"]//2,second["source"],second["onset_s"],second["off_s"])==(
            t["first"],clear,t["source"],t["on"],t["off"])
        _,clean=data.sim.physical(dict(duration_s=clear/30+9,events=[first]))
        recovery=data.channels(clean)
        baseline=recovery[0]
        before=np.arange(len(y))/30<t["on"]
        np.testing.assert_array_equal(y[before],control[before])
        traces={"event":y,"twin":control,"recovery_only":recovery,"noise_only":control-recovery+baseline,
                "increment_only":y-control+baseline,"increment_plus_noise":y-recovery+baseline}
        detail={}
        for name,trace in traces.items():
            reports,scores,families,sources=model.scan(trace,clear)
            active=(t["on"]<=reports/30)&(reports/30<t["off"])
            hits=np.flatnonzero(scores>threshold)
            first_hit=int(reports[hits[0]]) if len(hits) else None
            item=dict(active_peak=float(scores[active].max()),pre_onset_peak=float(scores[reports/30<t["on"]].max())
                      if np.any(reports/30<t["on"]) else None,first_crossing=first_hit)
            if alarm is not None:
                at=int(np.flatnonzero(reports==alarm)[0])
                item.update(at_early=float(scores[at]), family_at_early=str(families[at]),site_at_early=str(sources[at]))
            if name in ("event","twin"):
                assert first_hit==calls[key if name=="event" else twin]["alarm"]
            detail[name]=item
        if alarm is not None:
            assert detail["event"]["at_early"]==detail["twin"]["at_early"] and alarm==detail["twin"]["first_crossing"]
        failures.append(dict(id=key,parent=t["parent"],category="miss" if alarm is None else "early",
                             first=t["first"],second=t["source"],amplitude=second["amplitude"],
                             lead_seconds=t["on"]-alarm/30 if alarm is not None else None,
                             first_clearance_to_second=t["on"]-clear/30,signals=detail))
    assert sum(r["category"]=="miss" for r in failures)==sum(r["category"]=="early" for r in failures)==6
    study.save(HERE/"diagnosis.json",dict(threshold=threshold,cohort=metrics["predictions_sha"],cases=failures))
    for r in failures:
        print(r["category"],r["first"],r["second"],r["amplitude"],r["lead_seconds"],
              {k:round(v["active_peak" if r["category"]=="miss" else "at_early"],2) for k,v in r["signals"].items()})


if __name__=="__main__":
    main()

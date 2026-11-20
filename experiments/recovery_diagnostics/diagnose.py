"""Post-hoc paired noise ablation on all two-event records of the frozen recovery test."""
import argparse
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import os
import sys
import tempfile
from unittest.mock import patch

import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"recovery_state"))
import design
from apply_recovery import frozen_observer
from recovery import RecoveryObserver
from operators import stream


def recover_rng_states():
    # Regenerate identical streams with the original sampler, retaining the RNG state
    # before any mechanical parameters or sensor disturbances have been drawn.
    states=[]
    class RecordedPlant(design.Generator):
        def simulate(self,events,rng):
            states.append(rng.bit_generator.state)
            return super().simulate(events,rng)
    frozen=design.load(design.RESULT/"test_manifest.json")
    temp_root=design.ROOT/"tmp"
    temp_root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=temp_root) as folder:
        root=Path(folder)
        with (patch.object(design,"Generator",RecordedPlant),patch.object(design,"DATA",root),
              patch.object(design,"RESULT",root/"manifests")):
            design.generate("test")
            if design.load(design.RESULT/"test_manifest.json")!=frozen:
                raise ValueError("Replay of original observations or schedules failed")
    return states


class SensorAblation:
    """Preserve the exact plant draws while replacing only instrument noise."""
    def __init__(self,state,noise_seed=None):
        self.plant=np.random.default_rng()
        self.plant.bit_generator.state=state
        self.sensor=np.random.default_rng(noise_seed) if noise_seed is not None else None

    def uniform(self,*args):
        return self.plant.uniform(*args)

    def normal(self,loc,scale,size):
        if self.sensor is None:
            return np.full(size,loc)
        return self.sensor.normal(loc,scale,size)

    def multivariate_normal(self,mean,cov,size):
        if self.sensor is None:
            return np.broadcast_to(mean,(size,len(mean))).copy()
        return self.sensor.multivariate_normal(mean,cov,size=size)


class ResidualObserver(RecoveryObserver):
    def __init__(self,*args):
        super().__init__(*args)
        self.residuals=[]

    def _continuation(self,z,v):
        r,var=super()._continuation(z,v)
        self.residuals.append(r.copy())
        return r,var


def init_worker():
    global plant, first, cfg
    from threadpoolctl import threadpool_limits
    threadpool_limits(1)
    plant=design.Generator()
    first=frozen_observer()
    cfg=design.load(design.LOCK)["config"]


def replay(record):
    observer=ResidualObserver(first.bank, first.model, cfg, first.physics)
    alarms=[a for sample in record for a in observer.step(sample)]
    return alarms,np.asarray(observer.residuals)


def classify(alarms,events):
    indices=set()
    joint=[]
    for event in events:
        i=next((j for j,a in enumerate(alarms) if j not in indices and
                0<=a["detected"]-event["onset"]<=45),None)
        if i is None:
            joint.append(False)
        else:
            indices.add(i)
            a=alarms[i]
            joint.append(a["published"]-event["onset"]<=45 and
                         (a["code"],a["source"])==(event["code"],event["source"]))
    return dict(joint=joint,extras=[a["detected"] for i,a in enumerate(alarms) if i not in indices])


def examine(task):
    i,events,state,archived=task
    clean=plant.simulate(events,SensorAblation(state))
    clean_predictions,_=replay(clean)
    baseline=classify(archived,events)
    row=dict(record=i,families=[e["code"] for e in events],original=baseline,
             noiseless=classify(clean_predictions,events))
    if baseline["extras"]:
        original_rng=np.random.default_rng()
        original_rng.bit_generator.state=state
        obs=plant.simulate(events,original_rng)
        alarms,residuals=replay(obs)
        if alarms!=archived:
            raise ValueError("Frozen observer replay mismatch")
        z,_=stream(obs,first.model)
        expected,_=stream(clean,first.model)
        # Compare the SAME centered, whitened innovations before the first spurious
        # publication, before whitening for the inherited per-family discrepancy.
        t=baseline["extras"][0]
        start=max(events[1]["onset"],t-11)
        frozen_err=residuals[start-30:t-30+1]
        oracle_err=z[start:t+1]-expected[start:t+1]
        row["prefix_rms"]={"reports":t+1-start,"frozen":float(np.mean(frozen_err**2)**.5),
                           "known_two_event_plant":float(np.mean(oracle_err**2)**.5)}
        row["resampled"]=[]
        for repeat in range(4):
            seed=np.random.SeedSequence([571039,i,repeat])
            other=plant.simulate(events,SensorAblation(state,seed))
            p,_=replay(other)
            row["resampled"].append(classify(p,events))
    return row


def main(workers):
    labels=design.RESULT/"test_truth.json"
    if design.sha(labels)!=design.load(design.RESULT/"test_manifest.json")["truth"]:
        raise ValueError("Published truth differs from the observation manifest")
    truth=design.load(labels)
    p=design.RESULT/"predictions.json"
    if design.sha(p)!=design.load(design.RESULT/"seal.json")["predictions"]:
        raise ValueError("Archived predictions differ from seal")
    archived=design.load(p)["recovery"]
    states=recover_rng_states()
    tasks=[(i,r,states[i],archived[i]) for i,r in enumerate(truth) if len(r)==2]
    with ProcessPoolExecutor(workers,initializer=init_worker) as pool:
        rows=list(pool.map(examine,tasks,chunksize=2))
    selected=[r for r in rows if r["original"]["extras"]]
    def summary(outcomes):
        return dict(records=len(outcomes),extras=sum(len(r["extras"]) for r in outcomes),
                    with_extras=sum(bool(r["extras"]) for r in outcomes),
                    second_joint=sum(r["joint"][1] for r in outcomes))
    totals={key:summary([r[key] for r in rows]) for key in ("original","noiseless")}
    totals["selected_noiseless"]=summary([r["noiseless"] for r in selected])
    totals["selected_resampled"]=summary([q for r in selected for q in r["resampled"]])
    design.save(HERE/"results.json",dict(freeze=design.sha(design.LOCK),totals=totals,rows=rows))
    print(totals,flush=True)


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workers",type=int,default=min(8,os.cpu_count() or 1))
    main(p.parse_args().workers)

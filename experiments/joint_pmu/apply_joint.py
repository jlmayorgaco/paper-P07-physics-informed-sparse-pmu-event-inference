"""Online entry point: emit alarms from a single synchronized eight-PMU record."""
import argparse
import json
from pathlib import Path
import numpy as np
import cohort_joint as c
from intervention_monitor import Bank
from joint_observer import JointObserver
from joint_physics import Physics


def frozen_observer():
    frozen=c.load(c.LOCK)
    for path in (c.HERE/"joint_physics.py",c.HERE/"joint_observer.py",c.HERE/"cohort_joint.py",
                 c.MODEL,c.DISC,c.common.GRAPH/"model.npz",c.common.GRAPH/"estimator.py",
                 c.design.PREVIOUS/"operators.py",c.design.PREVIOUS/"intervention_monitor.py",
                 c.REC/"recovery.py"):
        if c.sha(path)!=frozen["files"][path.relative_to(c.ROOT).as_posix()]:
            raise ValueError("Frozen monitor changed: "+path.name)
    operators,_=c.bind()
    operators.cache_bank()
    receipt=c.DATA/"bank/inputs.json"
    if c.sha(receipt)!=frozen["files"][receipt.relative_to(c.ROOT).as_posix()]:
        raise ValueError("Physical bank differs from freeze")
    with np.load(c.MODEL,allow_pickle=False) as f:
        model=dict(f)
    return JointObserver(Bank(),model,frozen["config"],Physics(model))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record",type=Path)
    args=parser.parse_args()
    observer=frozen_observer()
    for measurement in np.load(args.record,mmap_mode="r",allow_pickle=False):
        for alarm in observer.step(measurement):
            print(json.dumps(alarm))

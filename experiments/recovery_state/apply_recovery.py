"""Run the frozen causal observer on a single [time, 8 PMUs, 5 fields] NumPy record."""
import argparse
import json
from pathlib import Path
import numpy as np

import design
from recovery import RecoveryObserver, Dynamics
from intervention_monitor import Bank


def frozen_observer():
    operators,_=design.bind()
    cfg=design.load(design.LOCK)
    for name in (design.MODEL,design.DISC,design.common.GRAPH/"model.npz",
                 design.common.GRAPH/"estimator.py",design.HERE/"recovery.py",design.HERE/"design.py",
                 design.PREVIOUS/"intervention_monitor.py",design.PREVIOUS/"operators.py"):
        if design.sha(name)!=cfg["files"][name.relative_to(design.ROOT).as_posix()]:
            raise ValueError("Frozen observer changed: "+name.name)
    operators.cache_bank()
    receipt=design.DATA/"bank/inputs.json"
    if design.sha(receipt)!=cfg["files"][receipt.relative_to(design.ROOT).as_posix()]:
        raise ValueError("Derived templates differ from the frozen bank")
    with np.load(design.MODEL,allow_pickle=False) as arc:
        model=dict(arc)
    return RecoveryObserver(Bank(),model,cfg["config"],Dynamics(model))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record",type=Path)
    observer=frozen_observer()
    for row in np.load(parser.parse_args().record,mmap_mode="r",allow_pickle=False):
        for alarm in observer.step(row):
            print(json.dumps(alarm))

"""Run the frozen four-family intervention observer on a synchronized PMU record."""
import argparse
import json
from pathlib import Path
import numpy as np

from common import DATA, FREEZE, GRAPH, HERE, MODEL, ROOT, load, sha
from intervention_monitor import Bank, Observer
from operators import cache_bank


def frozen_observer():
    cfg = load(FREEZE)
    for file in (MODEL,HERE/"discrepancy.npz",HERE/"operators.py",HERE/"intervention_monitor.py",
                 GRAPH/"model.npz",GRAPH/"estimator.py"):
        if sha(file)!=cfg["files"][file.relative_to(ROOT).as_posix()]:
            raise ValueError(f"Frozen observer changed: {file.name}")
    cache_bank()
    receipt = DATA/"bank/inputs.json"
    if sha(receipt)!=cfg["files"][receipt.relative_to(ROOT).as_posix()]:
        raise ValueError("Derived physical responses differ from the frozen bank")
    with np.load(MODEL,allow_pickle=False) as archive:
        return Observer(Bank(),dict(archive),cfg["config"])


if __name__=="__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record",type=Path)
    args = parser.parse_args()
    monitor = frozen_observer()
    for sample in np.load(args.record,mmap_mode="r",allow_pickle=False):
        for alarm in monitor.step(sample):
            print(json.dumps(alarm))

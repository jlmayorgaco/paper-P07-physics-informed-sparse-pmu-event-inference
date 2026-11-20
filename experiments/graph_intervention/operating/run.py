"""Run the preregistered primary observer one synchronized report at a time."""
import argparse
import json
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from apply import frozen_observer
from common import FREEZE, load, sha


def primary_observer():
    p = load(HERE/"freeze.json")
    if (p["base"],p["source"],p["protocol"],p["development"])!=(
            sha(FREEZE),sha(HERE/"point.py"),sha(HERE/"PROTOCOL.md"),sha(HERE/"development.json")):
        raise ValueError("Primary decision differs from the freeze")
    obs = frozen_observer()
    if (obs.hazard,obs.identify)!=(p["config"]["hazard"],p["config"]["identify"]):
        raise ValueError("Secondary calibration may only change publication odds")
    obs.threshold=p["config"]["log_gate"]
    return obs


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record",type=Path)
    args=parser.parse_args()
    observer=primary_observer()
    for report in np.load(args.record,mmap_mode="r",allow_pickle=False):
        for alarm in observer.step(report):
            print(json.dumps(alarm))

"""Run the selected physical observer one report at a time from the distributed model."""
import argparse
import json
from pathlib import Path

import numpy as np

from estimator import EpisodeDecision
from phasors import LOCK, MODEL
from robust import StudentMonitor
from study import digest, read


class PhysicalMonitor:
    """Start one instance per independent trajectory. A step emits zero, one or two updates."""

    def __init__(self):
        selected = read(LOCK)
        if selected["primary"] != "phasor" or digest(MODEL) != selected["model"]:
            raise ValueError("The distributed model differs from the selected development model")
        with np.load(MODEL, allow_pickle=False) as arrays:
            self.model = dict(arrays)
        self.filter = StudentMonitor(self.model)
        self.decision = EpisodeDecision(self.model, selected["gate"], selected["identify"])
        self.frame = 0

    def step(self, report):
        scores = self.filter.step(report)
        updates = self.decision.step(self.frame, scores)
        self.frame += 1
        return updates


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path, help="NumPy array with shape (reports, 8, 5)")
    args = parser.parse_args()
    monitor = PhysicalMonitor()
    for report in np.load(args.record, mmap_mode="r", allow_pickle=False):
        for publication in monitor.step(report):
            print(json.dumps(publication))

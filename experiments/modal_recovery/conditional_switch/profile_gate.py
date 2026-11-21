"""Development ablation with source-wise positive-amplitude GLS profiles."""
from dataclasses import dataclass
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import study
import develop
import model
from cohort import TMP
import joblib
import numpy as np


@dataclass
class Profile:
    base: model.SwitchModel
    directions: np.ndarray

    @property
    def length(self):
        return self.base.length

    def scores(self, y):
        b = self.base
        blocks = model.contrasts(y, b.length, b.width, b.level)
        # The largest signed, standardized projection is monotone in the
        # largest Gaussian likelihood after profiling a nonnegative amplitude.
        return (((blocks-b.center)/b.scale) @ self.directions.T).max(axis=1)


def evaluate():
    gate = joblib.load(TMP/"short.joblib")
    with np.load(TMP/"templates.npz") as z:
        prior = np.repeat(z["probabilities"]/5, 5)
    norms = np.sqrt(2*(np.log(prior)-gate.offset))
    detector = Profile(gate, gate.filters/norms[:,None])
    joblib.dump(detector, TMP/"profile.joblib", compress=3)
    background = joblib.load(TMP/"background.joblib")
    readout = joblib.load(TMP/"conditional_readout.joblib")
    values = sorted(float(detector.scores(background.residual(y,c)).max()) for y,c in develop.inputs("cal"))
    records = []
    for k,y,c,t in develop.development_set():
        target = dict(t)
        if t["on"] is not None:
            target.update(on=t["on"]-c/30, off=t["off"]-c/30)
        records.append((k, background.residual(y,c), 0, target))
    rows = []
    for level in (.975,.99,.995):
        threshold = values[int(np.ceil(level*(len(values)+1)))-1]
        rows.append(dict(name="profile", level=level, threshold=threshold,
                         **develop.evaluate(records, detector, threshold, readout)))
    study.save(TMP/"profile_development.json", rows)
    print(rows)


if __name__ == "__main__":
    from profile_gate import evaluate
    evaluate()

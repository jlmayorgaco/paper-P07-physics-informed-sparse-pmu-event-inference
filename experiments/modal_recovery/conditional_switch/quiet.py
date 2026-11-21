"""Replay the same archived long normal traces as the current detector."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import study
import numpy as np


def scan(plant, split, background, detector, threshold=None):
    manifest = study.read(study.RUN / f"OBSERVATIONS_{plant}_{split}.json")
    rows = [row for row in manifest if row["reports"] == 18001]
    assert len(rows) == 36
    results = {}
    for row in rows:
        key = row["id"]
        path = study.RUN / "observations" / plant / split / (key + "_nominal.npz")
        assert study.digest(path) == row["files"]["nominal"]
        with np.load(path, allow_pickle=False) as z:
            y = np.column_stack((z["voltage_magnitude"] * np.sqrt(3) / 345000, z["current_magnitude"]))
        r = background.residual(y, 360)
        lag = detector.length - 1
        scores = np.concatenate([detector.scores(r[i:i+1024+lag]) for i in range(0, len(r)-lag, 1024)])
        assert len(scores) == len(r)-lag and np.isfinite(scores).all()
        out = dict(max=float(scores.max()), scored_reports=len(scores))
        if threshold is not None:
            above = scores > threshold
            out["episodes"] = int(np.count_nonzero(above & ~np.r_[False, above[:-1]]))
        results[key] = out
    return results


if __name__ == "__main__":
    import joblib
    from cohort import TMP
    name = sys.argv[1]
    rows = scan("F01", "CAL", joblib.load(TMP/"background.joblib"), joblib.load(TMP/(name+".joblib")))
    study.save(TMP/("quiet_cal_"+name+".json"), rows)
    print(name, max(v["max"] for v in rows.values()))

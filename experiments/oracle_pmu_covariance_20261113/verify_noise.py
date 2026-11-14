"""Independent impulse check of the joint observation and memory injection."""
import json
from pathlib import Path
import sys

import numpy as np
from scipy.linalg import block_diag

from noise_model import KEEP, maps, shift

ROOT = Path(__file__).resolve().parents[3]/"SGSMA26-Physics-Informed-AD"
RUNTIME = ROOT/"experiments/PAPER_NOISE_STRESS_N01/runtime_relaxed"
sys.path.insert(0, str(RUNTIME))
from instrument_parent import ColoredInstrument, FIELDS


def main():
    spec = json.loads((RUNTIME/"model/stochastic_model.json").read_text())
    filters = [ColoredInstrument(spec["families"][f], k) for f,k in zip(FIELDS,KEEP)]
    scales = np.repeat([spec["families"][f]["normalization_scale"] for f in FIELDS],
                       [8,8,8,7,8,8])
    magnitude = np.r_[np.full(8, 200000.), np.full(8, 1000.)]
    direct, lagged = maps(scales, magnitude)
    w = block_diag(*[f.W for f in filters])
    wh = block_diag(*[f.W @ f.H for f in filters])
    a = block_diag(*[f.A for f in filters])
    b = block_diag(*[f.B for f in filters])
    f, g = shift()
    state = np.zeros(160)
    instrument = np.zeros(len(a))
    time = np.arange(-20,1)/30
    design = np.column_stack([np.ones(21),time,time*time])
    max_error = 0.
    angles = np.zeros((21,8))
    rng = np.random.default_rng(2026111390)
    for _ in range(80):
        shock = rng.normal(size=31)*.0005
        angles[:-1] = angles[1:]
        angles[-1] = np.rad2deg(shock[8:16])
        coeff = np.linalg.lstsq(design, angles, rcond=None)[0]
        raw = np.r_[shock[:8]*magnitude[:8], np.rad2deg(shock[8:16]),
                    shock[16:24]*magnitude[8:], np.rad2deg(shock[24:]),
                    coeff[1]/360, 2*coeff[2]/360] / scales
        pos = 0
        expected = []
        for filt, indices in zip(filters,KEEP):
            expected.append(filt.process(raw[pos:pos+len(indices)]))
            pos += len(indices)
        modeled = w @ (direct @ shock + lagged @ state) - wh @ instrument
        max_error = max(max_error, float(np.max(np.abs(np.concatenate(expected)-modeled))))
        instrument = a @ instrument + b @ (direct @ shock + lagged @ state)
        state = f @ state + g @ shock
    assert max_error < 1e-8
    print(json.dumps(dict(reports=80, maximum_whitened_coordinate_error=max_error,
                          checks="Independent quadratic least squares and original observed-noise filter")))


if __name__ == "__main__":
    main()

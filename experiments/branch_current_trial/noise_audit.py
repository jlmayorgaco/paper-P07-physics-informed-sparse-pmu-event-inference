"""Compare executed noise models and retain checksums of the measurement operators."""
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

from run import ARCHIVE, HERE, REF, RUN, Experiment
sys.path.insert(0, str(ARCHIVE / "V5"))
from src.simulation.m9.calibration import extract_reference_statistics
from src.simulation.m9.exports import _safe_std
from noise import NoiseStream


def main():
    model = json.loads((REF / "stochastic_model.json").read_text())
    observed = NoiseStream(model, 81172).generate(12000)
    exp = Experiment()
    reference = extract_reference_statistics(ARCHIVE / "data/RAW0001")
    rows = []
    for i, bus in enumerate(exp.mapping.pmu_bus):
        for phase in "ABC":
            m9_mag = _safe_std(reference, f"BUS{bus}", f"I{phase}_MAG", 3., .05)
            m9_angle = _safe_std(reference, f"BUS{bus}", f"I{phase}_ANG", .10)
            rows.append(dict(bus=bus,phase=phase,m9_mag_sd=m9_mag,m9_angle_sd_deg=m9_angle,
                             b01_empirical_A=observed["current_magnitude"][:,i].std(ddof=1),
                             b01_empirical_deg=observed["current_angle"][:,i].std(ddof=1)))
    pd.DataFrame(rows).to_csv(HERE/"noise_check.csv", index=False)
    inputs = [REF/name for name in ("pmu_operator.py","noise.py","terminal_mapping.csv",
              "data/branch.csv","data/bus.csv","reporting_config.json","stochastic_model.json")]
    inputs += [RUN/"runtime/model/dae/measurement_network.json",
               ARCHIVE/"V5/src/simulation/m9/exports.py", ARCHIVE/"data/metadata/PMUbus_ Location.txt",
               ARCHIVE/"experiments/PAPER_ALLEVENTS_V1/physics/network.py",
               ARCHIVE/"data/metadata/IEEE_39_Bus_Power_System.raw", ARCHIVE/"data/topology/ieee39/ybus_full_complex.csv"]
    (HERE/"archive_inputs.json").write_text(json.dumps({p.relative_to(ARCHIVE).as_posix():
        hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},indent=2))


if __name__=="__main__":
    main()

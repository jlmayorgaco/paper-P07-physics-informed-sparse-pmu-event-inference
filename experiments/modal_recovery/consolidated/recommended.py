"""Public inference entry point for the frozen 30 s physical model."""
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/"long_horizon"))
from model_long import load
import extend_curves


def load_estimator():
    """Return a frozen estimator accepting the four measured phasor arrays and first clearance.

    predict(measurements, clearance) returns an absolute zero-based alarm report
    and the family/site after a further 29 reports. Supply a quiet first second,
    30 Hz reporting, and the documented eight-PMU order. The validated follow-up
    lasts 30 seconds after restoration.
    """
    extend_curves.UPSTREAM=HERE/"long_horizon/reference/recovery.npz"
    _,complete=load()
    return complete

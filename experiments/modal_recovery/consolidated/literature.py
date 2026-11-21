"""Frozen Li and Wang DMD/CNN-F adaptation for a common second-event trigger."""
import hashlib
from functools import lru_cache
from pathlib import Path
import sys
import numpy as np

SECOND_FAMILY = Path(__file__).resolve().parents[2] / "second_family"
CNN_PATH = SECOND_FAMILY / "cnn.pt"
CNN_SHA256 = "eaad70212d0f89d97f068c6410033073ead63be719ed009cc74531bc3c0faf13"


@lru_cache(maxsize=1)
def predictor():
    if hashlib.sha256(CNN_PATH.read_bytes()).hexdigest() != CNN_SHA256:
        raise RuntimeError("CNN-F checkpoint hash mismatch")
    sys.path.insert(0, str(SECOND_FAMILY))
    from classifier import Predict
    return Predict()


def li_wang(raw, restoration, b):
    """Use one quiet second for centering and publish from reports b through b+29."""
    if b is None or b+29 >= len(raw["frequency"]):
        return None
    from spectral import channels, alarm_features
    start, end = int(restoration), int(b)+30
    if not 30 <= start <= b:
        raise ValueError("Invalid restoration or trigger time")
    prefix = {k: value[:end] for k, value in raw.items()}
    x = channels(prefix, baseline=slice(5,30))
    if not np.isfinite(x[start:end]).all():
        raise ValueError("Nonfinite channel in the estimation window")
    return [predictor()(alarm_features(x,start,b,True)), None]

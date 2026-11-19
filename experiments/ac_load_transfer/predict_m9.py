"""Apply the physical load-only alternative to sealed family predictions, without labels."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
from run import PowerFlow, estimate
import numpy as np
from competition_response_bank import frames_from


def predict(root, data, out):
    raw = (root / "predictions.json").read_bytes()
    assert sha256(raw).hexdigest() == json.loads((root / "seal.json").read_text())
    plant = PowerFlow(data)
    columns = plant.dictionary()
    rows = {}
    for key, record in json.loads(raw).items():
        family, site = record["successor"]
        if family == 4:
            frames = frames_from(root / "observations" / key)
            ratios = []
            for bus, frame in frames.items():
                angles = frame[[f"BUS{bus}_V{p}_ANG" for p in "ABC"]].to_numpy()
                magnitude = frame[[f"BUS{bus}_V{p}_MAG" for p in "ABC"]].to_numpy()
                v = magnitude * np.exp(1j * np.deg2rad(angles))
                v[frame.DATA_PRESENT.to_numpy() != 1] = np.nan
                ratios.append(
                    np.nanmean(
                        np.nanmean(v[-300:], axis=0) / np.nanmean(v[:1800], axis=0) - 1
                    )
                )
            y = np.array(ratios)
            mask = np.isfinite(y)
            if mask.sum() >= 5:
                site = f"BUS{estimate(y[mask],columns[:,mask],plant.sites,True)}"
        rows[key] = [family, site]
    out.mkdir(parents=True, exist_ok=True)
    path = out / "ac_m9_predictions.json"
    path.write_text(json.dumps(rows, indent=2) + "\n")
    (out / "ac_m9_seal.json").write_text(
        json.dumps(sha256(path.read_bytes()).hexdigest()) + "\n"
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("root", "data", "out"):
        p.add_argument(name, type=Path)
    a = p.parse_args()
    predict(a.root, a.data, a.out)

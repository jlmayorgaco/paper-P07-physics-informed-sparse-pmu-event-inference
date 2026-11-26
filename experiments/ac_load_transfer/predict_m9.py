"""Apply the physical load-only alternative to sealed family predictions, without labels."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
from run import OBS, PowerFlow, estimate
from joint_current import terminal_matrix, whiten
import numpy as np
from competition_response_bank import frames_from


def displacement(frame, bus, quantity):
    angles = frame[[f"BUS{bus}_{quantity}{p}_ANG" for p in "ABC"]].to_numpy()
    magnitude = frame[[f"BUS{bus}_{quantity}{p}_MAG" for p in "ABC"]].to_numpy()
    v = magnitude * np.exp(1j * np.deg2rad(angles))
    v[frame.DATA_PRESENT.to_numpy() != 1] = np.nan
    return np.nanmean(np.nanmean(v[-300:], axis=0) / np.nanmean(v[:1800], axis=0) - 1)


def predict(root, data, out, with_current=False):
    raw = (root / "predictions.json").read_bytes()
    assert sha256(raw).hexdigest() == json.loads((root / "seal.json").read_text())
    plant = PowerFlow(data)
    full = plant.dictionary(full=True)
    columns = full[:, OBS]
    if with_current:
        terminal = terminal_matrix(data)
        current_columns = ((full * plant.v0) @ terminal.T) / (terminal @ plant.v0)
    rows = {}
    for key, record in json.loads(raw).items():
        family, site = record["successor"]
        if family == 4:
            frames = frames_from(root / "observations" / key)
            y = np.array([displacement(frames[k + 1], k + 1, "V") for k in OBS])
            mask = np.isfinite(y)
            if mask.sum() >= 5:
                samples, atoms = y[mask], columns[:, mask]
                if with_current:
                    i = np.array(
                        [
                            displacement(frames[b], b, "I")
                            for b in (2, 6, 10, 19, 22, 29)
                        ]
                    )
                    valid = np.isfinite(i)
                    if valid.sum() >= 2:
                        samples = np.r_[
                            whiten(samples, 0.0005), whiten(i[valid], 0.005)
                        ]
                        atoms = np.column_stack(
                            [
                                whiten(atoms, 0.0005),
                                whiten(current_columns[:, valid], 0.005),
                            ]
                        )
                site = f"BUS{estimate(samples,atoms,plant.sites,True)}"
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
    p.add_argument("--with-current", action="store_true")
    a = p.parse_args()
    predict(a.root, a.data, a.out, a.with_current)

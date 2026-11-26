from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
DEFAULT_SOURCE = Path(
    r"C:\Users\walla\Documents\Github\SGSMA26-Physics-Informed-AD\experiments\PAPER_RECOVERY_C03\run\work\F01\CAL\C03_a1adb9f9adcf_nominal\nominal\bank.npz"
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract minimal nominal P07 operators from a finished CAL bank.")
    parser.add_argument("--source-bank", type=Path, default=DEFAULT_SOURCE)
    args = parser.parse_args()
    source = args.source_bank.resolve()
    before = sha256(source)
    with np.load(source, allow_pickle=False) as d:
        if d["T"].shape != (46, 376, 376) or d["J"].shape != (46, 47, 376):
            raise ValueError("Unexpected C01/R11 nominal bank dimensions")
        if d["group"].shape != (91,) or int(d["group"][0]) != 0:
            raise ValueError("Unexpected operator ordering or null group")
        sinv = d["Sinv"][0, 0]
        s = np.linalg.solve(sinv, np.eye(47))
        s = (s + s.T) * 0.5
        j0 = d["J"][0]
        riccati_s = d["R"][0] + j0 @ d["P"][0] @ j0.T
        relative_error = float(np.max(np.abs(s - riccati_s)) / max(1.0, np.max(np.abs(s))))
        if relative_error > 1e-7:
            raise ValueError(f"Quiet/null covariance disagrees with R+JPJ': {relative_error:g}")
        compact = {
            "T": d["T"], "J": d["J"], "g": d["g"], "u": d["u"],
            "j": d["j"], "v": d["v"], "group": d["group"],
            "K0": d["K"][0, 0], "S": s, "Sinv0": sinv,
        }
        np.savez_compressed(HERE / "input_snapshot.npz", **compact)
    after = sha256(source)
    if before != after:
        raise RuntimeError("The read-only CAL source hash changed during extraction")
    out = HERE / "input_snapshot.npz"
    ready = json.loads((HERE / "source_CAL_READY.json").read_text(encoding="utf-8"))
    metadata = {
        "source_bank_sha256_before_and_after": before,
        "source_READY_bank_sha256": ready["bank_sha256"],
        "source_READY_truth_read": ready["truth_read"],
        "source_READY_prefix_reports": ready["prefix_reports"],
        "source_READY_nominal_only": ready["nominal_only"],
        "snapshot_sha256": sha256(out),
        "snapshot_bytes": out.stat().st_size,
        "included_arrays": {name: {"shape": list(value.shape), "dtype": str(value.dtype),
                                    "sha256": hashlib.sha256(np.ascontiguousarray(value).view(np.uint8)).hexdigest()}
                             for name, value in compact.items()},
        "quiet_null_covariance_identity_relative_max_error": relative_error,
        "source_was_read_only": True,
        "C03_code_executed": False,
        "TEST_truth_or_observations_read": False,
    }
    (HERE / "snapshot_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()

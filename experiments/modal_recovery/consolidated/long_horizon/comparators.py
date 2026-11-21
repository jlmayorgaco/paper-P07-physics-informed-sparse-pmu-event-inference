"""Run the frozen ZIP and MiniRocket comparators on a nested long-window set.

The long-horizon cohort is generated and sealed separately. This runner reads
only its opaque manifest and raw PMU NPZ files; it never opens target labels.
The ZIP comparison is prespecified on streams with ``stream % 8 < 4`` (48 of
96 parents, balanced over the four ordered first/second-family combinations).
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
CONSOLIDATED = HERE.parent
ROOT = HERE.parents[3]
RESULT = HERE / "results"
INPUTS = RESULT / "inputs.json"
PMU_DIR = ROOT / "tmp" / "consolidated" / "horizon" / "pmu"
PREDICTIONS = RESULT / "zip_predictions.json"
FROZEN_RESULT = CONSOLIDATED / "results"
SELECTED_STREAMS = frozenset(stream for stream in range(96) if stream % 8 < 4)
CONDITIONS = ("native", "joint")
ZIP_CLASS = {0: "none", 2: "line", 4: "load"}

for _name in (str(CONSOLIDATED), str(CONSOLIDATED.parent / "clock_stress")):
    if _name not in sys.path:
        sys.path.insert(0, _name)

import zip_runner  # noqa: E402


def _load_manifest():
    manifest = json.loads(INPUTS.read_text(encoding="utf-8-sig"))
    records = manifest.get("records")
    if not isinstance(records, dict) or len(records) != 192:
        raise ValueError("long_horizon inputs.json must contain exactly 192 records")

    by_stream: dict[int, list[tuple[str, dict]]] = {}
    for key, meta in records.items():
        if not isinstance(key, str) or not key or Path(key).name != key:
            raise ValueError(f"Invalid opaque input id: {key!r}")
        if not isinstance(meta, dict) or "sha" not in meta or "stream" not in meta:
            raise ValueError(f"Input {key!r} must provide only opaque sha/stream metadata")
        stream = int(meta["stream"])
        if stream != meta["stream"] or not 0 <= stream < 96:
            raise ValueError(f"Invalid parent stream for opaque input {key!r}")
        digest = meta["sha"]
        if not isinstance(digest, str) or len(digest) != 64:
            raise ValueError(f"Invalid input checksum for opaque input {key!r}")
        by_stream.setdefault(stream, []).append((key, {"sha": digest, "stream": stream}))

    if set(by_stream) != set(range(96)) or any(len(rows) != 2 for rows in by_stream.values()):
        raise ValueError("Expected two opaque records for each of 96 parent streams")
    selected = sorted(row for stream in SELECTED_STREAMS for row in by_stream[stream])
    if len(selected) != 96:
        raise AssertionError("The nested long-window subset must contain 96 records")
    return manifest, selected


def _validate_inputs(tasks):
    if not PMU_DIR.is_dir():
        raise FileNotFoundError(f"Missing fresh long-horizon PMU directory: {PMU_DIR}")
    for key, meta in tasks:
        path = PMU_DIR / f"{key}.npz"
        if zip_runner._sha256(path) != meta["sha"]:
            raise ValueError(f"Opaque long-horizon input checksum mismatch: {key}")
        raw, clearance = zip_runner._read_npz(path)
        if clearance + zip_runner.WINDOW_REPORTS > len(raw["frequency"]):
            raise ValueError(f"Input does not contain a full post-clearance window: {key}")


def _init_zip_worker():
    # _episode uses this module global to locate opaque NPZs.
    zip_runner.PMU_DIR = PMU_DIR
    zip_runner._init_worker()


def _rocket_prediction(raw, clearance, stream, detector, source, threshold, Errors, Setting, phase_data, rocket):
    y = phase_data.channels(raw)
    errors = Errors(631337 + stream, len(y), clearance)
    setting = Setting("nominal")
    if threshold is None:
        raise ValueError("Frozen MiniRocket threshold is missing")

    calls = {}
    for condition in CONDITIONS:
        if condition == "native":
            observed = errors.apply(y, setting)
        else:
            observed = errors.apply(y, Setting("joint", angle=0.005, jitter=0.25))
        z, reports, scores = rocket.scan(observed[:clearance+900], clearance, detector)
        hits = (scores > threshold).nonzero()[0]
        alarm = int(reports[hits[0]]) if len(hits) else None
        label = rocket.label(z, alarm, source)
        if label is None:
            event_class, site = ("none" if alarm is None else "unattributed"), None
        else:
            event_class, site = str(label[0]), str(label[1])
        calls[condition] = {"class": event_class, "site": site, "alarm_report": alarm}
    return calls


def run(workers: int = 6) -> Path:
    """Score the frozen comparison subset and create a new opaque prediction seal."""
    if workers < 1:
        raise ValueError("workers must be positive")
    if PREDICTIONS.exists():
        raise FileExistsError(f"Refusing to overwrite {PREDICTIONS}")

    # Check the frozen MiniRocket artifact and its pre-existing source seal.
    from freeze_final import verify as verify_frozen  # noqa: PLC0415
    verify_frozen()

    manifest, tasks = _load_manifest()
    _validate_inputs(tasks)

    # The ZIP's original submission wrapper requires the pinned sklearn 1.7.2
    # environment. Its unchanged _episode provides native and joint predictions.
    zip_runner.PMU_DIR = PMU_DIR
    zip_calls = {}
    with ProcessPoolExecutor(workers, initializer=_init_zip_worker) as pool:
        for key, calls in pool.map(zip_runner._episode, [(k,dict(v,stream=v["stream"]+101337)) for k,v in tasks], chunksize=1):
            zip_calls[key] = calls
            if len(zip_calls) % 16 == 0:
                print(f"ZIP scored {len(zip_calls)}/96 opaque records", flush=True)

    # MiniRocket is the original independently frozen model and threshold.
    import joblib  # noqa: PLC0415
    import numpy as np  # noqa: PLC0415
    from robust import Errors, phase_data, study  # noqa: PLC0415
    import rocket_arm as rocket  # noqa: PLC0415

    frozen = study.read(FROZEN_RESULT / "freeze.json")
    bundle = joblib.load(FROZEN_RESULT / "rocket.joblib")
    detector, source = bundle
    threshold = float(frozen["rocket_tau"])
    rocket.numba.set_num_threads(1)

    cases = {}
    for index, (key, meta) in enumerate(tasks, 1):
        path = PMU_DIR / f"{key}.npz"
        with np.load(path, allow_pickle=False) as archive:
            raw = {name: np.asarray(archive[name]) for name in zip_runner.SIGNAL_KEYS}
            clearance = int(np.asarray(archive["clearance"]).reshape(-1)[0])
        rocket_calls = _rocket_prediction(
            raw, clearance, meta["stream"], detector, source, threshold,
            Errors, zip_runner._load_robust()[1], phase_data, rocket,
        )
        row = {}
        for condition in CONDITIONS:
            zip_result = zip_calls[key][condition]
            event_code = int(zip_result["event"])
            row[condition] = {
                "zip": {
                    "class": ZIP_CLASS.get(event_code, "other"),
                    "event_code": event_code,
                    "site": None if zip_result["site"] is None else str(zip_result["site"]),
                },
                "minirocket": rocket_calls[condition],
            }
        cases[key] = row
        if index % 16 == 0:
            print(f"MiniRocket scored {index}/96 opaque records", flush=True)

    output = {
        "protocol": "long_horizon_native_joint_nested_zip_minirocket_v1",
        "input_manifest_sha256": study.digest(INPUTS),
        "zip_submission_sha256": zip_runner.ZIP_SHA256,
        "minirocket_freeze_sha256": study.digest(FROZEN_RESULT / "freeze.json"),
        "conditions": {
            "native": "Errors(631337 + stream) with nominal setting",
            "joint": "same Errors seed with angle=0.005 degrees and jitter=0.25 us",
        },
        "nested_parent_streams": sorted(SELECTED_STREAMS),
        "records_scored": len(cases),
        "cases": cases,
    }
    RESULT.mkdir(parents=True, exist_ok=True)
    with PREDICTIONS.open("x", encoding="utf-8") as stream:
        json.dump(output, stream, indent=2, allow_nan=False)
        stream.write("\n")
    return PREDICTIONS


if __name__ == "__main__":
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 6)

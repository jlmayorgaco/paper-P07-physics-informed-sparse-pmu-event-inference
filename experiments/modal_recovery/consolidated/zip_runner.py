"""Paired full-window evaluation against the original SGSMA ZIP model.

Run ``prepare`` before the cohort is frozen. Later, run ``infer`` after
``tmp/consolidated/inputs.json`` and its opaque NPZ observations are available.
Each observation is scored on exactly reports ``clearance:clearance + 900``
under native and joint angle conditions. No target/truth file is read.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import sys
import tempfile
import time
import warnings
from zipfile import ZipFile

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TMP = ROOT / "tmp" / "consolidated"
PMU_DIR = TMP / "pmu"
INPUTS = HERE / "results" / "inputs.json"
RESULT = HERE / "results"
ZIP_PATH = ROOT / "tmp" / "competition_original.zip"
RUNTIME_ROOT = TMP / "zip_submission"
ZIP_SHA256 = "e0bfc17e4c5ee9b595fa51fd94d736145c2f48755696c8d2eadcff00cb23a243"
SAMPLE_RATE_HZ = 30.0
WINDOW_REPORTS = 900
PMU_BUSES = (2, 5, 6, 10, 19, 22, 29, 39)
PHASES = ("A", "B", "C")
SIGNAL_KEYS = (
    "voltage_magnitude",
    "voltage_angle",
    "current_magnitude",
    "current_angle",
    "frequency",
    "rocof",
)
def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as src:
        for block in iter(lambda: src.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _zip_members() -> dict[str, bytes]:
    if _sha256(ZIP_PATH) != ZIP_SHA256:
        raise RuntimeError(f"Original submission ZIP hash mismatch: {ZIP_PATH}")
    selected: dict[str, bytes] = {}
    with ZipFile(ZIP_PATH) as archive:
        for info in archive.infolist():
            name = info.filename.replace("\\", "/")
            pure = PurePosixPath(name)
            if pure.is_absolute() or ".." in pure.parts:
                raise RuntimeError(f"Unsafe path in original ZIP: {name}")
            if pure.parts and pure.parts[0] in {"src", "models"}:
                if info.is_dir():
                    continue
                selected[name] = archive.read(info)
    if not any(name.startswith("src/") for name in selected):
        raise RuntimeError("Original ZIP has no src/ runtime")
    if "models/final_model_config.json" not in selected:
        raise RuntimeError("Original ZIP has no trained ML model bundle")
    return selected


def prepare() -> Path:
    """Verify the genuine ZIP and materialize its unchanged src/ and models/."""
    files = _zip_members()
    if RUNTIME_ROOT.exists():
        # Reuse an existing extraction only if every selected byte still matches.
        for name, content in files.items():
            path = RUNTIME_ROOT / Path(*PurePosixPath(name).parts)
            if not path.is_file() or path.read_bytes() != content:
                raise RuntimeError(f"Prepared runtime differs from original ZIP: {name}")
        actual = {
            p.relative_to(RUNTIME_ROOT).as_posix()
            for top in ("src", "models")
            for p in (RUNTIME_ROOT / top).rglob("*")
            if p.is_file() and p.suffix != ".pyc"
        }
        if actual != set(files):
            raise RuntimeError("Prepared runtime has added or missing files")
        return RUNTIME_ROOT

    TMP.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="zip_submission_", dir=TMP))
    try:
        for name, content in files.items():
            path = staging / Path(*PurePosixPath(name).parts)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        # Atomic rename keeps failed preparations from looking complete.
        staging.rename(RUNTIME_ROOT)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return RUNTIME_ROOT


def _load_original():
    root = prepare()
    root_string = str(root)
    if root_string not in sys.path:
        sys.path.insert(0, root_string)
    # This runner is standalone; reject a shadowed import if another package
    # called it in-process before the original runtime was installed.
    runtime = importlib.import_module("src.models.hybrid_submission")
    module_file = Path(runtime.__file__).resolve()
    if RUNTIME_ROOT.resolve() not in module_file.parents:
        raise RuntimeError(f"Loaded a non-ZIP runtime module: {module_file}")
    model_module = importlib.import_module("src.data_factory.final_model")
    model = model_module.SGSMAFinalModel(root / "models")
    return runtime, model


def _load_robust():
    stress_dir = HERE.parent / "clock_stress"
    relative_dir = HERE.parent / "relative_phase"
    for path in (str(HERE), str(stress_dir), str(relative_dir)):
        if path not in sys.path:
            sys.path.insert(0, path)
    from stress_plan import Errors, Setting

    return Errors, Setting


def _read_npz(path: Path) -> tuple[dict[str, np.ndarray], int]:
    with np.load(path, allow_pickle=False) as archive:
        missing = [name for name in (*SIGNAL_KEYS, "clearance") if name not in archive]
        if missing:
            raise ValueError(f"{path.name}: missing NPZ members {missing}")
        raw = {name: np.asarray(archive[name], dtype=float) for name in SIGNAL_KEYS}
        clearance_value = np.asarray(archive["clearance"])
        if clearance_value.size != 1:
            raise ValueError(f"{path.name}: clearance must be scalar")
        clearance_float = float(clearance_value.reshape(-1)[0])
        if not np.isfinite(clearance_float) or not clearance_float.is_integer():
            raise ValueError(f"{path.name}: clearance must be an integer report index")
        clearance = int(clearance_float)
    shape = raw["voltage_magnitude"].shape
    if len(shape) != 2 or shape[1] != len(PMU_BUSES):
        raise ValueError(f"{path.name}: expected eight aligned PMU channels, got {shape}")
    if clearance < 0 or clearance + WINDOW_REPORTS > shape[0]:
        raise ValueError(
            f"{path.name}: need exact reports [{clearance}:{clearance + WINDOW_REPORTS}], "
            f"available={shape[0]}"
        )
    if any(a.shape != shape for a in raw.values()):
        raise ValueError(f"{path.name}: all six raw arrays must share shape {shape}")
    if not all(np.isfinite(a[clearance:clearance+WINDOW_REPORTS]).all() for a in raw.values()):
        raise ValueError(f"{path.name}: raw arrays must be finite")
    # The official simulator exporter writes voltage in phase-neutral volts,
    # current in amperes, and both phasor angles in wrapped degrees.
    for key in ("voltage_angle", "current_angle"):
        if np.any(raw[key] < -180.000001) or np.any(raw[key] > 180.000001):
            raise ValueError(f"{path.name}: {key} must be in wrapped degrees [-180, 180]")
    if np.any(raw["voltage_magnitude"] <= 0) or np.any(raw["current_magnitude"] < 0):
        raise ValueError(f"{path.name}: magnitudes must be nonnegative and voltage positive")
    return raw, clearance


def _base_matrix(raw: dict[str, np.ndarray]) -> np.ndarray:
    """The clock-stress design matrix: 16 magnitudes then 16 wrapped angles."""
    return np.column_stack(
        (
            raw["voltage_magnitude"],
            raw["current_magnitude"],
            raw["voltage_angle"],
            raw["current_angle"],
        )
    )


def _balanced_abc(raw: dict[str, np.ndarray], start: int, stop: int):
    """Apply the official positive-sequence-to-balanced-ABC export convention.

    `simulate_pairs.physical` exports |V1| in volts phase-neutral, |I1| in A,
    angles from `numpy.angle(..., deg=True)` ([-180, 180]), frequency in Hz,
    and ROCOF in Hz/s. The balanced phase angles are theta, theta-120, theta+120.
    """
    import pandas as pd

    frames = {}
    sl = slice(start, stop)
    n = stop - start
    time_s = np.arange(n, dtype=float) / SAMPLE_RATE_HZ
    for j, bus in enumerate(PMU_BUSES):
        vm = raw["voltage_magnitude"][sl, j]
        va = raw["voltage_angle"][sl, j]
        im = raw["current_magnitude"][sl, j]
        ia = raw["current_angle"][sl, j]
        frame = {"TIMESTAMP": time_s}
        for key, mag, theta in (
            ("V", vm, va),
            ("I", im, ia),
        ):
            for phase, shift in zip(PHASES, (0.0, -120.0, 120.0)):
                # Magnitudes remain the exported physical RMS magnitudes.
                angle = (theta + shift + 180.0) % 360.0 - 180.0
                frame[f"BUS{bus}_{key}{phase}_MAG"] = mag
                frame[f"BUS{bus}_{key}{phase}_ANG"] = angle
        frame[f"BUS{bus}_Freq"] = raw["frequency"][sl, j]
        frame[f"BUS{bus}_ROCOF"] = raw["rocof"][sl, j]
        frame["DATA_PRESENT"] = np.ones(n, dtype=np.int8)
        frames[bus] = pd.DataFrame(frame)
    return frames


def _fast_prediction(runtime, model, frames) -> tuple[int, str]:
    base, dynamic = runtime._build_feature_rows(frames)
    pred = model.predict_from_features(base, dynamic).iloc[0]
    return int(pred["pred_event"]), str(pred["pred_location"])


def _score_full_wrapper(runtime, input_dir: Path, model_dir: Path, output_csv: Path):
    # Execute the submitted CSV loader, _run_ml_windows, and output postprocessing.
    started = time.perf_counter()
    frames = runtime._load_frames(input_dir)
    model_module = importlib.import_module("src.data_factory.final_model")
    model = model_module.SGSMAFinalModel(model_dir)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")
        predictions, diagnostics = runtime._run_ml_windows(
            frames, model, output_csv, input_dir, 30.0, started
        )
    if diagnostics["n_windows"] != 1:
        raise AssertionError(f"Expected one 30 s window, got {diagnostics['n_windows']}")
    if len(predictions) != WINDOW_REPORTS * len(PMU_BUSES):
        raise AssertionError(f"Full wrapper emitted {len(predictions)} rows for the 900-report window")
    event_values = predictions["Predicted_Event"].unique()
    site_values = predictions["Predicted_Location"].unique()
    if len(event_values) != 1 or len(site_values) != 1:
        raise AssertionError("Baseline postprocessing did not broadcast one decision per window")
    return int(event_values[0]), str(site_values[0]), diagnostics


def _write_frames(frames, folder: Path):
    folder.mkdir(parents=True, exist_ok=True)
    for bus, frame in frames.items():
        frame.to_csv(folder / f"Bus{bus}_Competition_Data.csv", index=False)


def dev_smoke() -> dict:
    """Exercise native/joint physical inputs and assert exact full-wrapper parity."""
    runtime, model = _load_original()
    Errors, Setting = _load_robust()
    n, clearance = 1200, 120
    t = np.arange(n, dtype=float) / SAMPLE_RATE_HZ
    buses = len(PMU_BUSES)
    voltage_magnitude = np.broadcast_to(345000.0 / np.sqrt(3.0), (n, buses)).copy()
    current_magnitude = np.broadcast_to(np.linspace(460.0, 880.0, buses), (n, buses)).copy()
    voltage_angle = np.broadcast_to(np.linspace(-14.0, 14.0, buses), (n, buses)).copy()
    current_angle = np.broadcast_to(np.linspace(-36.0, 28.0, buses), (n, buses)).copy()
    frequency = 60.0 + 0.002 * np.sin(2 * np.pi * 0.7 * t[:, None]) * np.ones((1, buses))
    rocof = np.gradient(frequency, 1.0 / SAMPLE_RATE_HZ, axis=0)
    # A bounded physical-family change begins at the decision boundary.
    voltage_magnitude[clearance:, :] *= 0.998
    current_magnitude[clearance:, :] *= 1.015
    raw = dict(
        voltage_magnitude=voltage_magnitude,
        voltage_angle=voltage_angle,
        current_magnitude=current_magnitude,
        current_angle=current_angle,
        frequency=frequency,
        rocof=rocof,
    )
    reports = {}
    with tempfile.TemporaryDirectory(prefix="zip_runner_dev_", dir=TMP) as tmp_name:
        scratch = Path(tmp_name)
        for condition in ("native", "joint"):
            physical = raw
            if condition == "joint":
                errors = Errors(530000, n, clearance)
                matrix = errors.apply(_base_matrix(raw), Setting("joint", angle=0.005, jitter=0.25))
                physical = dict(raw)
                physical["voltage_angle"] = (matrix[:, 16:24] + 180.0) % 360.0 - 180.0
                physical["current_angle"] = (matrix[:, 24:32] + 180.0) % 360.0 - 180.0
            frames = _balanced_abc(physical, clearance, clearance + WINDOW_REPORTS)
            fast = _fast_prediction(runtime, model, frames)
            source = scratch / condition
            _write_frames(frames, source)
            full = _score_full_wrapper(
                runtime,
                source,
                RUNTIME_ROOT / "models",
                scratch / f"{condition}.csv",
            )
            expected = (full[0], full[1])
            if fast != expected:
                raise AssertionError(
                    f"Fast _build_feature_rows/model differs from full ZIP wrapper "
                    f"for {condition}: fast={fast!r}, wrapper={expected!r}"
                )
            reports[condition] = {"event": fast[0], "site": fast[1], "rows": WINDOW_REPORTS * buses}
    return reports


def _manifest_records(manifest: dict) -> dict[str, dict]:
    records = manifest.get("records")
    if not isinstance(records, dict) or not records:
        raise ValueError("inputs.json must contain a nonempty records object")
    clean = {}
    for opaque_id, meta in records.items():
        if not isinstance(opaque_id, str) or not opaque_id or Path(opaque_id).name != opaque_id:
            raise ValueError(f"Invalid opaque observation id: {opaque_id!r}")
        if not isinstance(meta, dict) or "sha" not in meta or "stream" not in meta:
            raise ValueError(f"Record {opaque_id!r} must include sha and stream")
        stream = int(meta["stream"])
        if stream < 0 or stream != meta["stream"]:
            raise ValueError(f"Record {opaque_id!r} has invalid stream index")
        clean[opaque_id] = {**meta, "stream": stream}
    return clean


def _init_worker():
    global runtime, model, Errors, Setting
    # Load the same sklearn version that serialized the June estimators.
    if (TMP/"zip_site").is_dir():
        sys.path.insert(0,str(TMP/"zip_site"))
    import sklearn
    if sklearn.__version__!="1.7.2":
        raise RuntimeError("The ZIP runtime requires scikit-learn 1.7.2")
    runtime, model = _load_original()
    Errors, Setting = _load_robust()


def _episode(task):
    key, meta = task
    path=PMU_DIR/(key+".npz")
    assert _sha256(path)==meta["sha"]
    raw,c=_read_npz(path)
    noise=Errors(530000+meta["stream"],len(raw["frequency"]),c)
    y=_base_matrix(raw)
    results={}
    for condition in ("native","joint"):
        settings=Setting("nominal") if condition=="native" else Setting("joint",angle=.005,jitter=.25)
        z=noise.apply(y,settings)
        frame=_balanced_abc(dict(raw,voltage_angle=z[:,16:24],current_angle=z[:,24:32]),c,c+900)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore",category=UserWarning)
            event,site=_fast_prediction(runtime,model,frame)
        results[condition]=dict(event=event,site=site)
    return key,results


def infer(workers=6):
    from concurrent.futures import ProcessPoolExecutor
    manifest=json.loads(INPUTS.read_text(encoding="utf8"))
    tasks=sorted((k,v) for k,v in manifest["records"].items() if v["long"])
    assert len(tasks)==96 and {v["stream"] for k,v in tasks}==set(range(48))
    result={}
    with ProcessPoolExecutor(workers,initializer=_init_worker) as pool:
        for k, v in pool.map(_episode,tasks,chunksize=1):
            result[k]=v
            if len(result)%12==0:
                print(len(result),"of 96 paired ZIP episodes",flush=True)
    path=RESULT/"zip_predictions.json"
    with path.open("x",encoding="utf8") as f:
        json.dump(result,f,indent=2,allow_nan=False)
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("prepare", "dev-smoke", "infer"))
    args = parser.parse_args()
    if args.stage == "prepare":
        print(prepare())
    elif args.stage == "dev-smoke":
        print(json.dumps(dev_smoke(), indent=2))
    else:
        print(infer())


if __name__ == "__main__":
    main()

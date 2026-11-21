"""Extend the frozen relative-phase recovery library through report 900.

Only the 630 reports after the frozen 271-report prefix are stored.  Each
physical trajectory is checked against its frozen upstream prefix before its
tail is admitted to a shard.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from hashlib import sha256
import json
import os
from pathlib import Path
import sys

for _name in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS", "BLIS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_name] = "1"

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE.parents[1] / "relative_phase"))
import phase_data  # noqa: E402

UPSTREAM = ROOT / "tmp/relative_phase/recovery.npz"
RESULTS = HERE / "results"
MANIFEST = RESULTS / "tail_manifest.json"
PREFIX_REPORTS = 271
TOTAL_REPORTS = 901
TAIL_REPORTS = TOTAL_REPORTS - PREFIX_REPORTS
SHARD_ROWS = 48
MAX_SHARD_BYTES = 45_000_000


def digest(path: Path) -> str:
    h = sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _tasks(assets):
    """Preserve library.py's asset-major, increasing-dwell task order."""
    tasks = []
    for asset in assets:
        if asset["family"] == "load":
            dwells = range(60, 121, 3)
            amplitude = 0.10
        else:
            dwells = range(60, 121)
            amplitude = None
        tasks.extend((asset, amplitude, dwell) for dwell in dwells)
    return tasks


def _initialize_worker():
    global _SIM, _UPSTREAM_CURVES
    phase_data.data.sim.initialize()
    _SIM = phase_data.data.sim
    with np.load(UPSTREAM, allow_pickle=False) as archive:
        _UPSTREAM_CURVES = archive["curves"].copy()


def _simulate(task):
    index, asset, amplitude, dwell = task
    start = 60
    event = _SIM.event(np.random.default_rng(0), asset, start, 2 * dwell)
    event["amplitude"] = amplitude
    clearance = start // 2 + dwell
    end_report = clearance + TOTAL_REPORTS - 1
    duration_s = max(end_report, event["off_tick"] // 2 + 2) / 30
    row = {"duration_s": duration_s, "events": [event]}

    # Match relative_phase/library.py's high-precision physical report path.
    t, voltage, current, status = _SIM.plant.simulate(row, _SIM.sim.MAP)
    if not status["valid"]:
        raise RuntimeError(f"invalid P2 simulation at library index {index}: {status}")
    mapping = _SIM.sim.MAP
    pmus = np.asarray(_SIM.sim.REPORT["pmus"]) - 1
    voltage = voltage[:, pmus]
    base = 100e6 / (np.sqrt(3) * 1000 * _SIM.sim.KV[mapping.terminal.to_numpy() - 1])
    y = np.column_stack((np.abs(voltage), np.abs(current) * base * mapping.gain.to_numpy(),
                         np.angle(voltage, deg=True), np.angle(current, deg=True)))
    features = np.column_stack((y[:, :16], phase_data.angular(y)))
    if len(features) <= end_report:
        raise RuntimeError(f"short simulation at index {index}: {len(features)} reports, need {end_report + 1}")
    centered = features[clearance:clearance + TOTAL_REPORTS] - features[:30].mean(axis=0)
    expected = _UPSTREAM_CURVES[index]
    np.testing.assert_allclose(centered[:PREFIX_REPORTS], expected,
                               rtol=2e-6, atol=2e-7,
                               err_msg=f"upstream prefix mismatch at index {index}")
    return index, centered[PREFIX_REPORTS:].astype(np.float32), float(np.max(np.abs(centered[:PREFIX_REPORTS] - expected)))


def _save_shard(number, indices, tails):
    path = RESULTS / f"tail_{number}.npz"
    with path.open("xb") as stream:
        np.savez_compressed(stream, indices=np.asarray(indices, dtype=np.int32),
                            tail=np.stack(tails).astype(np.float32, copy=False))
    size = path.stat().st_size
    if size >= MAX_SHARD_BYTES:
        raise RuntimeError(f"shard exceeds 45 MB: {path.name} ({size} bytes)")
    return {"file": path.name, "sha256": digest(path), "bytes": size,
            "verified_indices": list(map(int, indices))}


def build(workers=6):
    if workers != 6:
        raise ValueError("This extension is specified to run with exactly six workers")
    RESULTS.mkdir(parents=True, exist_ok=True)
    if MANIFEST.exists() or any(RESULTS.glob("tail_*.npz")):
        raise FileExistsError(f"refusing to overwrite existing long-horizon outputs in {RESULTS}")
    with np.load(UPSTREAM, allow_pickle=False) as archive:
        upstream_curves = archive["curves"]
        upstream_ids = archive["ids"].astype(str)
    upstream_sha = digest(UPSTREAM)

    # Initialize the canonical asset ordering in the parent, then give the
    # same immutable task records to six independent physical workers.
    phase_data.data.sim.initialize()
    tasks0 = _tasks(phase_data.data.sim.assets)
    ids = np.asarray([asset["id"] for asset, _, _ in tasks0])
    assert len(tasks0) == 738 and np.array_equal(ids, upstream_ids)
    tasks = [(i, asset, amplitude, dwell) for i, (asset, amplitude, dwell) in enumerate(tasks0)]

    shards, pending_indices, pending_tails = [], [], []
    max_prefix_error = 0.0
    with ProcessPoolExecutor(max_workers=6, initializer=_initialize_worker) as pool:
        for completed, (index, tail, error) in enumerate(pool.map(_simulate, tasks, chunksize=1), 1):
            pending_indices.append(index)
            pending_tails.append(tail)
            max_prefix_error = max(max_prefix_error, error)
            if len(pending_indices) == SHARD_ROWS or completed == len(tasks):
                shards.append(_save_shard(len(shards) + 1, pending_indices, pending_tails))
                pending_indices, pending_tails = [], []
            if completed % 48 == 0 or completed == len(tasks):
                print(f"verified {completed}/{len(tasks)}; max prefix abs error {max_prefix_error:.3g}", flush=True)

    manifest = {
        "format": "relative-phase-long-horizon-tail-v1",
        "upstream_library": "tmp/relative_phase/recovery.npz",
        "upstream_sha256": upstream_sha,
        "upstream_shape": list(upstream_curves.shape),
        "total_reports_after_clearance": TOTAL_REPORTS,
        "frozen_prefix_reports": PREFIX_REPORTS,
        "tail_reports": TAIL_REPORTS,
        "tail_frame_range_inclusive": [PREFIX_REPORTS, TOTAL_REPORTS - 1],
        "shape": [738, TAIL_REPORTS, int(upstream_curves.shape[2])],
        "dtype": "float32",
        "order": "relative_phase/library.py recovery task order: assets outermost; load dwell 60..120 step 3 at amplitude +0.10; line dwell 60..120 step 1",
        "workers": 6,
        "blas_threads": 1,
        "prefix_check": {"rtol": 2e-6, "atol": 2e-7, "verified_indices": list(range(738)),
                         "max_absolute_error": max_prefix_error},
        "shards": shards,
    }
    payload = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    with MANIFEST.open("xb") as stream:
        stream.write(payload)
    loaded = load_tail()
    assert loaded.shape == (738, 630, 31) and loaded.dtype == np.float32
    print(f"wrote {len(shards)} shards; load_tail() -> {loaded.shape} {loaded.dtype}", flush=True)


def load_tail() -> np.ndarray:
    """Load and authenticate the staged tail, in frozen library order."""
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if digest(UPSTREAM) != manifest["upstream_sha256"]:
        raise ValueError("frozen upstream library SHA-256 changed")
    output = np.empty(manifest["shape"], dtype=np.float32)
    seen = np.zeros(output.shape[0], dtype=bool)
    for shard in manifest["shards"]:
        path = RESULTS / shard["file"]
        if digest(path) != shard["sha256"]:
            raise ValueError(f"shard SHA-256 mismatch: {path.name}")
        with np.load(path, allow_pickle=False) as archive:
            indices, values = archive["indices"], archive["tail"]
        if values.shape != (len(indices), output.shape[1], output.shape[2]):
            raise ValueError(f"invalid tail shape in {path.name}")
        if list(map(int, indices)) != shard["verified_indices"] or np.any(seen[indices]):
            raise ValueError(f"invalid or repeated indices in {path.name}")
        output[indices] = values
        seen[indices] = True
    if not np.all(seen):
        raise ValueError("tail shards do not cover all upstream indices")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()
    build(args.workers)

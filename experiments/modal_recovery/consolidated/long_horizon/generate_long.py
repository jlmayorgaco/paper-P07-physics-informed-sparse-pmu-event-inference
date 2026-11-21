"""Generate the sealed 30-second long-horizon modal-recovery cohort.

Run from any working directory with ``python path/to/cohort.py``.
The P2 physical model and signal construction are the same as
``consolidated/make_cohort.py``; only the prespecified cohort design differs.
"""

from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import shutil
import sys
from zipfile import ZIP_STORED, ZipFile

import numpy as np


HERE = Path(__file__).resolve().parent
CONSOLIDATED = HERE.parent
# robust.py adds clock_stress to sys.path before importing its P2 dependencies.
if str(CONSOLIDATED) not in sys.path:
    sys.path.insert(0, str(CONSOLIDATED))

from robust import TMP, phase_data, study  # noqa: E402

data = phase_data.data


SEED = 94026173
PARENTS_PER_GROUP = 48
RECORD_COUNT = 4 * PARENTS_PER_GROUP
DURATION_S = 30.0
FAMILY_PAIRS = (("load", "load"), ("load", "line"),
                ("line", "load"), ("line", "line"))
PMUS = (2, 5, 6, 10, 19, 22, 29, 39)
FIELDS = (
    "voltage_magnitude",
    "voltage_angle",
    "current_magnitude",
    "current_angle",
    "frequency",
    "rocof",
)
MAX_ARCHIVE_BYTES = 44_000_000

OUTPUT = TMP / "horizon"
OBSERVATIONS = OUTPUT / "pmu"
TRUTH = OUTPUT / "targets.json"
RESULT = HERE / "results"
FREEZE = RESULT / "freeze.json"
MANIFEST = RESULT / "inputs.json"
STAGED = OUTPUT / "staged_archives"


def initialize():
    """Initialize the exact P2 model used by the consolidated cohort maker."""
    data.TMP = TMP / "horizon"
    data.sim.initialize()
    if tuple(data.sim.sim.REPORT["pmus"]) != PMUS:
        raise ValueError("The positive-sequence PMU order changed")


def _family_schedule():
    """Make a deterministic schedule with 12 of each pair in both groups."""
    rng = np.random.default_rng(SEED)
    schedule = []
    for group in ("early", "late"):
        for _ in range(12):
            for j in rng.permutation(4):
                schedule.append((group, FAMILY_PAIRS[int(j)]))
    return schedule


def _assets_for(family, assets, exclude=None):
    options = [asset for asset in assets
               if asset["family"] == family and asset["id"] != exclude]
    if not options:
        raise ValueError(f"No registered {family} source remains after exclusion")
    return options


def simulate(task):
    """Build one parent and its matched positive/control NPZ observations."""
    index, group, (first_family, second_family) = task
    rng = np.random.default_rng([SEED, index])
    assets = data.sim.assets

    first_options = _assets_for(first_family, assets)
    first_asset = first_options[int(rng.integers(len(first_options)))]
    first = data.sim.event(
        rng,
        first_asset,
        2 * int(rng.integers(52, 69)),
        2 * int(rng.integers(60, 121)),
    )
    clearance = first["off_tick"] // 2
    duration = clearance / 30 + DURATION_S

    second_options = _assets_for(second_family, assets, exclude=first["source"])
    second_asset = second_options[int(rng.integers(len(second_options)))]
    if group == "early":
        second_on_tick = first["off_tick"] + int(rng.integers(75, 241))
    elif group == "late":
        # Simulator event ticks run at 60 Hz; 30 reports per second.
        delay_reports = int(rng.integers(14 * 30, 24 * 30 + 1))
        second_on_tick = first["off_tick"] + 2 * delay_reports
    else:
        raise ValueError(f"Unknown horizon group: {group}")
    second = data.sim.event(
        rng,
        second_asset,
        second_on_tick,
        int(rng.integers(120, 241)),
    )

    # One native simulator noise stream is applied unchanged to both twins.
    noise_seed = int(rng.integers(1, 2**31))
    noise = data.sim.sim.NoiseStream(data.sim.sim.NOISE, noise_seed).generate(
        round(duration * 30) + 1
    )
    targets = {}
    records = {}
    control = None
    for event in (None, second):
        key = rng.bytes(12).hex()
        events = [first] if event is None else [first, event]
        _, raw = data.sim.physical(dict(duration_s=duration, events=events))
        measured = data.sim.sim.apply_noise(raw, noise)
        arrays = {field: np.asarray(measured[field]) for field in FIELDS}
        n = len(arrays["voltage_magnitude"])
        if any(values.shape != (n, len(PMUS)) for values in arrays.values()):
            raise ValueError("Expected six raw positive-sequence fields shaped (reports, 8)")

        if event is None:
            control = arrays
        else:
            before = 2 * np.arange(n) < event["onset_tick"]
            for field in FIELDS:
                np.testing.assert_allclose(
                    arrays[field][before],
                    control[field][before],
                    rtol=0,
                    atol=0,
                    equal_nan=True,
                )

        path = OBSERVATIONS / (key + ".npz")
        with path.open("xb") as output:
            np.savez_compressed(output, **arrays, clearance=np.int32(clearance))
        targets[key] = dict(
            group=group,
            parent=index,
            first=first["source"],
            clearance=clearance,
            on=event["onset_s"] if event else None,
            off=event["off_s"] if event else None,
            family=event["family"] if event else "none",
            source=event["source"] if event else None,
        )
        records[key] = dict(
            stream=index,
            sha=study.digest(path),
        )
    return targets, records


def _archive_batches(paths):
    """Group raw NPZ members into ZIP shards that remain below the byte cap."""
    batches = []
    current = []
    estimated = 0
    for path in paths:
        member_size = path.stat().st_size + 1024
        if member_size > MAX_ARCHIVE_BYTES:
            raise ValueError(f"Observation is larger than the archive limit: {path.name}")
        if current and estimated + member_size > MAX_ARCHIVE_BYTES:
            batches.append(current)
            current, estimated = [], 0
        current.append(path)
        estimated += member_size
    if current:
        batches.append(current)
    return batches


def generate(workers=8):
    """Create the prospective cohort after the long-horizon freeze exists."""
    from benchmark_long import verify
    verify()
    if not FREEZE.is_file():
        raise FileNotFoundError(f"Required prospective freeze is missing: {FREEZE}")
    if MANIFEST.exists() or any(RESULT.glob("cohort_pmus_*.zip")):
        raise FileExistsError("Refusing to replace existing long-horizon results")
    if OBSERVATIONS.exists() or STAGED.exists():
        raise FileExistsError(f"Refusing to reuse horizon staging: {OUTPUT}")
    if TRUTH.exists():
        raise FileExistsError(f"Refusing to replace {TRUTH}")

    OBSERVATIONS.mkdir(parents=True)
    STAGED.mkdir(parents=True)
    RESULT.mkdir(parents=True, exist_ok=True)
    schedule = _family_schedule()
    tasks = [(index, group, pair)
             for index, (group, pair) in enumerate(schedule)]
    targets, records = {}, {}
    with ProcessPoolExecutor(max_workers=workers, initializer=initialize) as pool:
        for completed, (labels, observed) in enumerate(
                pool.map(simulate, tasks, chunksize=2), 1):
            targets.update(labels)
            records.update(observed)
            if completed % 24 == 0:
                print("simulated", completed, "parents", flush=True)

    if len(targets) != RECORD_COUNT or len(records) != RECORD_COUNT:
        raise ValueError("Expected exactly 192 opaque records")
    study.save(TRUTH, targets)

    paths = sorted(OBSERVATIONS.glob("*.npz"))
    if len(paths) != RECORD_COUNT:
        raise ValueError(f"Expected {RECORD_COUNT} staged observations, found {len(paths)}")
    archives = {}
    for number, batch in enumerate(_archive_batches(paths), 1):
        staged_path = STAGED / f"cohort_pmus_{number}.zip"
        final_path = RESULT / staged_path.name
        if final_path.exists():
            raise FileExistsError(f"Refusing to replace {final_path}")
        with ZipFile(staged_path, "x", compression=ZIP_STORED) as archive:
            for path in batch:
                if study.digest(path) != records[path.stem]["sha"]:
                    raise ValueError(f"Staged observation hash changed: {path.name}")
                archive.write(path, arcname=path.name)
        if staged_path.stat().st_size >= MAX_ARCHIVE_BYTES:
            raise ValueError(f"Staged archive must be smaller than 44 MB: {staged_path.name}")
        archive_sha = study.digest(staged_path)
        with staged_path.open("rb") as source, final_path.open("xb") as destination:
            shutil.copyfileobj(source, destination)
        if study.digest(final_path) != archive_sha:
            raise ValueError(f"Published archive hash differs: {final_path.name}")
        archives[final_path.name] = archive_sha

    study.save(
        MANIFEST,
        dict(
            seed=SEED,
            records=records,
            archives=archives,
            targets_sha=study.digest(TRUTH),
            freeze_sha=study.digest(FREEZE),
        ),
    )
    print("sealed", len(records), "opaque traces in", len(archives), "archives", flush=True)


if __name__ == "__main__":
    generate()

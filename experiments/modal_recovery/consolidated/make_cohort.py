"""Create opaque, matched raw positive-sequence PMU traces for modal recovery."""

from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from zipfile import ZIP_STORED, ZipFile
import shutil

from robust import RESULT, TMP, phase_data, study
import numpy as np

data = phase_data.data


SIZES = {"catalog": 240, "bus31": 60}
SEEDS = {"catalog": 64971191, "bus31": 82036117}
FIELDS = (
    "voltage_magnitude",
    "voltage_angle",
    "current_magnitude",
    "current_angle",
    "frequency",
    "rocof",
)
PMUS = (2, 5, 6, 10, 19, 22, 29, 39)
MAX_ARCHIVE_BYTES = 44_000_000
OBSERVATIONS = TMP / "pmu"
STAGED = TMP / "modal_cohort" / "staged_archives"
TRUTH = TMP / "targets.json"
MANIFEST = RESULT / "inputs.json"


def initialize():
    data.TMP = TMP / "modal_cohort"
    data.sim.initialize()
    if tuple(data.sim.sim.REPORT["pmus"]) != PMUS:
        raise ValueError("The positive-sequence PMU order changed")


def simulate(task):
    panel, index = task
    rng = np.random.default_rng([SEEDS[panel], index])
    families = ("load", "line")
    first_family = families[index % 2]
    second_family = families[index // 2 % 2] if panel == "catalog" else "load"
    assets = data.sim.assets

    first_options = [
        asset for asset in assets
        if asset["family"] == first_family
        and (panel == "catalog" or asset["id"] != "BUS31")
    ]
    first_asset = first_options[int(rng.integers(len(first_options)))]
    first = data.sim.event(
        rng,
        first_asset,
        2 * int(rng.integers(52, 69)),
        2 * int(rng.integers(60, 121)),
    )
    clearance = first["off_tick"] // 2
    long_record = panel == "catalog" and index < 48
    duration = clearance / 30 + (30 if long_record else 9)

    second_options = [
        asset for asset in assets
        if asset["family"] == second_family
        and asset["id"] != first["source"]
        and (panel == "catalog" or asset["id"] == "BUS31")
    ]
    second_asset = second_options[int(rng.integers(len(second_options)))]
    second = data.sim.event(
        rng,
        second_asset,
        first["off_tick"] + int(rng.integers(75, 241)),
        int(rng.integers(120, 241)),
    )

    noise_seed = int(rng.integers(1, 2**31))
    noise = data.sim.sim.NoiseStream(data.sim.sim.NOISE, noise_seed).generate(
        round(duration * 30) + 1
    )
    targets = {}
    observations = {}
    stream = index if panel == "catalog" else SIZES["catalog"] + index

    twin = None
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
            twin = arrays
        else:
            before = 2 * np.arange(n) < event["onset_tick"]
            for field in FIELDS:
                np.testing.assert_allclose(
                    arrays[field][before],
                    twin[field][before],
                    rtol=0,
                    atol=0,
                    equal_nan=True,
                )

        path = OBSERVATIONS / (key + ".npz")
        with path.open("xb") as output:
            np.savez_compressed(output, **arrays, clearance=np.int32(clearance))
        targets[key] = dict(
            panel=panel,
            parent=index,
            first=first["source"],
            clearance=clearance,
            on=event["onset_s"] if event else None,
            off=event["off_s"] if event else None,
            family=event["family"] if event else "none",
            source=event["source"] if event else None,
        )
        observations[key] = dict(
            stream=stream,
            long=long_record,
            sha=study.digest(path),
        )
    return targets, observations


def _archive_batches(paths):
    """Pack by staged NPZ size with room for ZIP headers, then enforce the cap."""
    batches = []
    current = []
    estimated = 0
    for path in paths:
        # ZIP_STORED adds only headers; 1 KiB per member leaves ample margin.
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
    from freeze_final import verify
    verify()
    if MANIFEST.exists():
        raise FileExistsError(f"Refusing to replace {MANIFEST}")
    if any(RESULT.glob("cohort_pmus_*.zip")):
        raise FileExistsError("Refusing to replace an existing cohort archive")
    if OBSERVATIONS.exists() or STAGED.exists():
        raise FileExistsError(f"Refusing to reuse existing cohort staging: {OBSERVATIONS.parent}")
    if TRUTH.exists():
        raise FileExistsError(f"Refusing to replace {TRUTH}")

    OBSERVATIONS.mkdir(parents=True)
    STAGED.mkdir(parents=True)
    RESULT.mkdir(parents=True, exist_ok=True)
    tasks = [(panel, index) for panel, size in SIZES.items() for index in range(size)]
    truth, records = {}, {}
    with ProcessPoolExecutor(workers, initializer=initialize) as pool:
        for completed, (labels, observed) in enumerate(pool.map(simulate, tasks, chunksize=2), 1):
            truth.update(labels)
            records.update(observed)
            if completed % 50 == 0:
                print("simulated", completed, "parents", flush=True)

    assert len(truth) == len(records) == 2 * sum(SIZES.values())
    study.save(TRUTH, truth)
    paths = sorted(OBSERVATIONS.glob("*.npz"))
    assert len(paths) == len(records)
    archives = {}
    for number, batch in enumerate(_archive_batches(paths), 1):
        staged_path = STAGED / f"cohort_pmus_{number}.zip"
        final_path = RESULT / staged_path.name
        if final_path.exists():
            raise FileExistsError(f"Refusing to replace {final_path}")
        with ZipFile(staged_path, "x", compression=ZIP_STORED) as archive:
            for path in batch:
                expected = records[path.stem]["sha"]
                if study.digest(path) != expected:
                    raise ValueError(f"Staged observation hash changed: {path.name}")
                archive.write(path, arcname=path.name)
        if staged_path.stat().st_size > MAX_ARCHIVE_BYTES:
            raise ValueError(f"Staged archive exceeds 44 MB: {staged_path.name}")
        archive_sha = study.digest(staged_path)
        with staged_path.open("rb") as source, final_path.open("xb") as destination:
            shutil.copyfileobj(source, destination)
        if study.digest(final_path) != archive_sha:
            raise ValueError(f"Published archive hash differs: {final_path.name}")
        archives[final_path.name] = archive_sha

    study.save(
        MANIFEST,
        dict(
            targets_sha=study.digest(TRUTH),
            freeze_sha=study.digest(RESULT/"freeze.json"),
            records=records,
            archives=archives,
        ),
    )
    print("sealed", len(records), "opaque traces in", len(archives), "archives", flush=True)


if __name__ == "__main__":
    generate()

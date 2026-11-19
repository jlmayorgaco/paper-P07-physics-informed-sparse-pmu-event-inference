"""Generate or predict the prespecified successor replay. Score in a separate process."""

import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from pathlib import Path

import predict_paired_m9_stream as prior
from benchmark_competition_windows import save, check_dynamic_startup
from pmu_window_correction import corrected, distance_signatures, electrical
from prepare_paired_m9_stream import prepare

OUT = Path("experiments/paired_m9_successor")
TEST_SITES = {
    1: ["BUS5", "BUS17"],
    2: ["BUS6-BUS7", "BUS16-BUS19"],
    3: ["BUS31"],
    4: ["BUS29"],
    6: ["BUS31"],
    8: ["BUS6", "BUS10"],
}


def init(archive, submitted, admissions):
    global dictionary, selected
    prior.initialize(archive, submitted, admissions)
    dictionary = distance_signatures(submitted / "data")
    selected = json.loads((OUT / "model.json").read_text())["selected"]


def infer(folder):
    key, row = prior.infer(folder)
    frames = electrical.prior.native.api._load_frames(folder)
    row["successor"] = corrected(frames, row["electrical"], dictionary, selected)
    return key, row


def predict(root, archive, submitted):
    check_dynamic_startup(root, archive)
    admissions = json.loads((root / "dynamic_admission.json").read_text())
    with ProcessPoolExecutor(
        max_workers=8, initializer=init, initargs=(archive, submitted, admissions)
    ) as pool:
        rows = dict(pool.map(infer, sorted((root / "observations").iterdir())))
    path = root / "predictions.json"
    save(path, rows)
    save(root / "seal.json", hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("stage", choices=["prepare", "predict"])
    p.add_argument("root", type=Path)
    p.add_argument("archive", type=Path)
    p.add_argument("submitted", type=Path)
    args = p.parse_args()
    if args.stage == "prepare":
        prepare(
            args.root,
            args.archive.resolve(),
            seed=47023613,
            repetitions=6,
            sites=TEST_SITES,
            instrument_sites=["BUS2", "BUS5", "BUS19", "BUS22", "BUS29", "BUS39"],
        )
    else:
        predict(args.root, args.archive.resolve(), args.submitted.resolve())

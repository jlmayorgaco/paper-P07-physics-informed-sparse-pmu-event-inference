"""Blind paired replay of three frozen nine-class window procedures."""

import argparse
from concurrent.futures import ProcessPoolExecutor
from hashlib import sha256
import json
from pathlib import Path
import sys

import competition_electrical_localizer as electrical
from benchmark_competition_windows import check_dynamic_startup, save


def initialize(archive, submitted, admissions):
    global expert, integrity, raw_io
    electrical.init(submitted, admissions)
    sys.path.insert(0, str(archive / "experiments/PAPER_ALLEVENTS_V1/frozen_v2"))
    import attribute_v2
    import integrity
    import raw_io

    expert = attribute_v2.Attributor()


def infer(folder):
    case, row = electrical.infer(folder)
    obs = raw_io.load(folder)
    flags = integrity.flags(obs, expert.net)
    _, episodes = expert.run(folder, flags)
    window = obs["t"] >= 60
    missing = (~obs["present"][window]).sum(axis=0)
    corrupt = flags[window].sum(axis=0)
    physical = [
        e for e in episodes if 60 <= e["onset_s"] < 90 and e.get("cls") in (1, 2, 3, 4)
    ]
    prediction = (
        [physical[0]["cls"], physical[0]["location"]] if physical else [0, "none"]
    )
    if missing.max():
        prediction = (
            [6, prediction[1]]
            if physical
            else [5, f"PMU{raw_io.PMUS[missing.argmax()]}"]
        )
    elif corrupt.max():
        prediction = [7, f"PMU{raw_io.PMUS[corrupt.argmax()]}"]
    return case, dict(
        submitted=row["submitted"], electrical=row["electrical"], physical=prediction
    )


def predict(root, archive, submitted, out):
    out.mkdir(parents=True, exist_ok=True)
    if not (root / "dynamic_admission.json").exists():
        check_dynamic_startup(root, archive)
    admissions = json.loads((root / "dynamic_admission.json").read_text())
    with ProcessPoolExecutor(
        max_workers=4, initializer=initialize, initargs=(archive, submitted, admissions)
    ) as pool:
        rows = dict(pool.map(infer, sorted((root / "observations").iterdir())))
    save(out / "predictions.json", rows)
    save(out / "seal.json", sha256((out / "predictions.json").read_bytes()).hexdigest())


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("root", "archive", "submitted"):
        p.add_argument(name, type=Path)
    p.add_argument("--out", type=Path)
    args = p.parse_args()
    predict(
        args.root,
        args.archive.resolve(),
        args.submitted.resolve(),
        args.out or args.root,
    )

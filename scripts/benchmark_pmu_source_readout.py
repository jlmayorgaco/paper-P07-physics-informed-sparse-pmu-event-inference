"""Paired replay with the decision stream frozen and only its site readout changed."""

import argparse
from concurrent.futures import ProcessPoolExecutor
from hashlib import sha256
import json
from pathlib import Path
import random

import numpy as np
from benchmark_competition_windows import save, check_dynamic_startup
from prepare_paired_m9_stream import prepare
from pmu_source_readout import localize
from pmu_window_correction import corrected, distance_signatures, electrical

DIR = Path("experiments/pmu_source_readout")


def test_sites(data, seed=992181):
    rng = random.Random(seed)
    sites = {}
    for family, candidates in sorted(electrical.network_signatures(data).items()):
        selected = rng.sample(sorted(candidates), 8)
        if family == 2:
            selected = ["BUS" + s[4:].replace("-", "-BUS") for s in selected]
        sites[family] = selected
    return sites


def init(data, admissions):
    global bank, distances, selected
    bank = dict(np.load(DIR / "bank.npz", allow_pickle=False))
    electrical.init(data, admissions)
    distances = distance_signatures(data / "data")
    selected = json.loads(
        Path("experiments/paired_m9_successor/model.json").read_text()
    )["selected"]


def infer(folder):
    case, row = electrical.infer(folder)
    frames = electrical.prior.native.api._load_frames(folder)
    decision = corrected(frames, row["electrical"], distances, selected)
    family, old = decision
    source = localize(frames, decision, bank)
    # The call is published at the same window close, using only this buffer.
    return case, dict(baseline=[family, old], registered=[family, source])


def predict(root, archive, submitted):
    check_dynamic_startup(root, archive)
    admissions = json.loads((root / "dynamic_admission.json").read_text())
    with ProcessPoolExecutor(
        max_workers=8, initializer=init, initargs=(submitted, admissions)
    ) as pool:
        pred = dict(pool.map(infer, sorted((root / "observations").iterdir())))
    save(root / "predictions.json", pred)
    save(
        root / "seal.json", sha256((root / "predictions.json").read_bytes()).hexdigest()
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("stage", choices=["prepare", "predict"])
    for name in ("root", "archive", "submitted"):
        p.add_argument(name, type=Path)
    a = p.parse_args()
    if a.stage == "prepare":
        prepare(
            a.root,
            a.archive.resolve(),
            seed=82006731,
            repetitions=8,
            sites=test_sites(a.submitted / "data"),
            instrument_sites=[
                "BUS2",
                "BUS5",
                "BUS6",
                "BUS10",
                "BUS19",
                "BUS22",
                "BUS29",
                "BUS39",
            ],
            registered_sites=True,
            vary_target=True,
        )
    else:
        predict(a.root, a.archive.resolve(), a.submitted.resolve())

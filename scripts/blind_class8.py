"""Sealed independent replay of the conditional class-8 readout."""

import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from pathlib import Path
import random

import numpy as np
import benchmark_pmu_source_readout as previous
from benchmark_competition_windows import check_dynamic_startup, save
from prepare_paired_m9_stream import prepare
from joint_class8 import posterior, BUSES


def infer(folder):
    key, old = previous.infer(folder)
    family, site = old["registered"]
    row = dict(registered=[family, site], joint=[family, site])
    if family == 8:
        frames = previous.electrical.prior.native.api._load_frames(folder)
        prob = posterior(frames, previous.bank)
        if prob is not None:
            sites = previous.bank["sites8"]
            row["joint"] = [family, str(sites[np.argmax(prob)])]
            row["probability"] = {str(k): float(p) for k, p in zip(sites, prob)}
    return key, row


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("stage", choices=["prepare", "predict"])
    for k in ("root", "archive", "submitted"):
        p.add_argument(k, type=Path)
    a = p.parse_args()
    if a.stage == "prepare":
        rng = random.Random(305471)
        sensors = [f"BUS{b}" for b in BUSES]
        pairs = [rng.sample(sensors, 2) for _ in range(8)]
        prepare(
            a.root,
            a.archive.resolve(),
            seed=27981403,
            repetitions=8,
            sites=previous.test_sites(a.submitted / "data", seed=951672),
            instrument_sites=sensors,
            registered_sites=True,
            vary_target=True,
            composite_instruments=pairs,
        )
        return
    check_dynamic_startup(a.root, a.archive.resolve())
    admissions = json.loads((a.root / "dynamic_admission.json").read_text())
    with ProcessPoolExecutor(
        max_workers=8,
        initializer=previous.init,
        initargs=(a.submitted.resolve(), admissions),
    ) as pool:
        rows = dict(pool.map(infer, sorted((a.root / "observations").iterdir())))
    save(a.root / "predictions.json", rows)
    save(
        a.root / "seal.json",
        hashlib.sha256((a.root / "predictions.json").read_bytes()).hexdigest(),
    )


if __name__ == "__main__":
    main()

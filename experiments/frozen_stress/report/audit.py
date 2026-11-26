"""Verify experiment seals and independently recount all methods. Optional raw PMU replay."""

import argparse
from concurrent.futures import ProcessPoolExecutor
from itertools import product
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from design_stress import c, RESULT, DATA, SEED, CONDITIONS


def recount(events, alerts):
    # Exhaustively enumerate the small (at most three-episode) assignment,
    # independent of the Hungarian solver used for the registered analysis.
    options = [
        [None] + [j for j, a in enumerate(alerts) if 0 <= a["detected"] - e["onset"] <= 45] for e in events
    ]
    best = None
    optimal_tables = set()
    for indices in product(*options):
        picked = [j for j in indices if j is not None]
        if len(set(picked)) != len(picked):
            continue
        joint = family = site = delay = 0
        cells = np.zeros((5, 6), int)
        for e, j in zip(events, indices, strict=True):
            code = e["code"]
            if j is None:
                cells[code, 0] += 1
                continue
            a = alerts[j]
            timely = a["published"] is not None and a["published"] - e["onset"] <= 45
            f = int(timely and a["code"] == code)
            s = int(timely and a["source"] == e["source"])
            family += f
            site += s
            joint += f * s
            delay += a["detected"] - e["onset"]
            cells[code, min(a["code"] or 0, 5) if timely else 0] += 1
        for j, a in enumerate(alerts):
            if j not in picked:
                cells[0, min(a["code"] or 0, 5)] += 1
        key = (len(picked), joint, family, site, -delay)
        if best is None or key > best:
            best = key
            optimal_tables = {tuple(cells.flat)}
        elif best == key:
            optimal_tables.add(tuple(cells.flat))
    return best, optimal_tables


def audit():
    from score_stress import contributions

    seal = c.load(RESULT / "seal.json")
    manifest = c.load(RESULT / "observations.json")
    for k, f in [
        ("registration", "registration.json"),
        ("observations", "observations.json"),
        ("predictions", "predictions.json"),
    ]:
        assert c.sha(RESULT / f) == seal[k]
    assert c.sha(RESULT / "test_truth.json") == manifest["truth"]
    assert c.sha(RESULT / "equilibria.json") == manifest["equilibria"]
    truth = c.load(RESULT / "test_truth.json")
    pred = c.load(RESULT / "predictions.json")
    scores = c.load(RESULT / "scores.json")
    ambiguous = 0
    for cond in CONDITIONS:
        for name, rows in pred[cond.name].items():
            tab = np.zeros((5, 6), int)
            nsite = 0
            for e, p in zip(truth[cond.timing], rows, strict=True):
                key, tables = recount(e, p)
                if len(tables) > 1:
                    ambiguous += 1
                    # Equal-quality solutions can differ in their family counts.
                    # Accept the registered tie-break only after confirming that
                    # its matrix is in the independently enumerated optimal set.
                    cells = tuple(contributions(e, p)[:30])
                    assert cells in tables
                else:
                    cells = next(iter(tables))
                nsite += key[3]
                tab += np.reshape(cells, (5, 6))
            s = scores[cond.name][name]
            assert (int(np.trace(tab[1:, 1:5])), nsite, int(tab[0].sum())) == (
                s["family"],
                s["site"],
                s["extras"],
            )
            f1 = np.mean([2 * tab[k, k] / (tab[k].sum() + tab[:, k].sum()) for k in range(1, 5)])
            np.testing.assert_allclose(f1, s["macro_f1"], atol=1e-12, rtol=0)
    print(
        "Independently verified all condition/method scores. Tied records with different optimal tables:",
        ambiguous,
    )


def initialize_simulator(folder):
    import run_stress

    run_stress.DATA = folder
    run_stress.init_sim()


def regenerate(folder, workers):
    """Generate a fresh copy without overwriting any observation or seal."""
    from design_stress import cases, change_timing
    from run_stress import simulate

    rows = cases()
    blank = np.zeros((len(rows), 720, 8, 5), dtype="float32")
    for condition in CONDITIONS:
        np.save(folder / (condition.name + ".npy"), blank)
    labels = c.load(RESULT / "test_truth.json")
    for timing, schedules in labels.items():
        assert [change_timing(r, timing) for r in rows] == schedules
    with ProcessPoolExecutor(workers, initializer=initialize_simulator, initargs=(folder,)) as pool:
        logs = list(pool.map(simulate, enumerate(rows), chunksize=2))
    assert logs == c.load(RESULT / "equilibria.json")


def replay(folder):
    import joblib
    from stress_plant import StressPlant
    from design_stress import cases, change_timing

    plant = StressPlant()
    from apply_joint import frozen_observer
    from joint_observer import JointObserver
    from study import supervised

    first = frozen_observer()
    cfg = c.load(c.LOCK)["config"]
    models = [joblib.load(path) for path in (c.common.FROZEN_TREES, c.TREES)]
    schedules = cases()
    i = next(i for i, r in enumerate(schedules) if len(r) == 3)
    j = next(i for i, r in enumerate(schedules) if len(r) == 2 and r[0]["code"] == 2 and r[1]["code"] == 3)
    pred = c.load(RESULT / "predictions.json")
    manifest = c.load(RESULT / "observations.json")
    for s in CONDITIONS:
        raw = np.load(folder / (s.name + ".npy"), allow_pickle=False)
        assert c.sha(folder / (s.name + ".npy")) == manifest["observations"][s.name]
        for k in (i, j):
            opens, _ = plant.outages(schedules[k], k)
            regenerated = plant.simulate(
                change_timing(schedules[k], s.timing),
                s.load,
                opens[: s.outages],
                np.random.SeedSequence([SEED, 6719, k]),
            )
            np.testing.assert_array_equal(regenerated, raw[k])
            if k == i and s.name in ("reference", "topo1", "load98", "load110", "over25", "combined"):
                observer = JointObserver(first.bank, first.model, cfg, first.physics)
                assert [a for x in regenerated for a in observer.step(x)] == pred[s.name]["joint"][k]
                for name, model in zip(("trees", "trees_refit"), models):
                    assert supervised(regenerated, model) == pred[s.name][name][k]
    print("Verified all raw hashes, regenerated 48 signals and replayed three monitors on six arms")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    raw = parser.add_mutually_exclusive_group()
    raw.add_argument("--raw", action="store_true", help="Read saved PMU traces from the original run")
    raw.add_argument(
        "--regenerate", action="store_true", help="Recompute all observations in a temporary directory"
    )
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()
    audit()
    if args.regenerate:
        with TemporaryDirectory() as folder:
            regenerate(Path(folder), args.workers)
            replay(Path(folder))
        print("Reproduced all 24 PMU observation hashes and equilibrium logs")
    elif args.raw:
        replay(DATA)

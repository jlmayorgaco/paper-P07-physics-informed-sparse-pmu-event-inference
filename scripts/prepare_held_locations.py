"""Prepare the held-location M9 cohort in an empty directory without fitting models."""
import argparse
from pathlib import Path

from benchmark_competition_windows import prepare, check_dynamic_startup
from competition_response_bank import CATALOG

GENERATORS = ("BUS33", "BUS35", "BUS38")
SITES = {1: ("BUS9", "BUS14", "BUS26"), 2: ("BUS1-BUS2", "BUS13-BUS14", "BUS25-BUS26"),
         3: GENERATORS, 4: ("BUS15", "BUS21", "BUS28"), 6: GENERATORS,
         8: ("BUS15", "BUS21", "BUS28")}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    assert all(set(sites).isdisjoint(CATALOG[k]) for k, sites in SITES.items())
    for name, seed, count in (("primary", 7821649, 12), ("quiet", 9154207, 48)):
        split = args.root / name
        prepare(split, args.archive.resolve(), seed=seed, repetitions=count, move_integrity=True,
                asset_catalog=SITES, vary_physical=True, normal_only=name == "quiet")
        check_dynamic_startup(split, args.archive.resolve())

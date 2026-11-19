"""Generate the prospective electrical-localizer test. Prediction never imports the site list."""
import argparse
from pathlib import Path

from benchmark_competition_windows import check_dynamic_startup, prepare
from prepare_held_locations import CATALOG, SITES

GEN = ("BUS30", "BUS34", "BUS37")
NEW = {1: ("BUS1", "BUS11", "BUS13"),
       2: ("BUS5-BUS8", "BUS17-BUS18", "BUS26-BUS29"),
       3: GEN, 4: ("BUS18", "BUS23", "BUS27"), 6: GEN,
       8: ("BUS12", "BUS24", "BUS25")}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("archive", type=Path)
    p.add_argument("root", type=Path)
    a = p.parse_args()
    known = {site for table in (CATALOG, SITES) for group in table.values() for site in group}
    assert all(known.isdisjoint(group) for group in NEW.values())
    for split, seed, n in (("primary", 41890273, 12), ("quiet", 67329503, 48)):
        out = a.root / split
        prepare(out, a.archive.resolve(), seed=seed, repetitions=n, move_integrity=True,
                asset_catalog=NEW, vary_physical=True, normal_only=split=="quiet")
        check_dynamic_startup(out, a.archive.resolve())

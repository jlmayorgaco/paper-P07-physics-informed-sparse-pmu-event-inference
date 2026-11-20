"""Prepare paired continuous M9 records and export causal, anonymous 90-s views."""

import argparse
import hashlib
import json
from pathlib import Path
import random
import sys

from benchmark_competition_windows import save
from prepare_electrical_sites import NEW, CATALOG, SITES

SITES_TEST = {1: "BUS22", 2: "BUS4-BUS5", 3: "BUS36", 4: "BUS3", 6: "BUS36", 8: "BUS8"}


def prepare(
    root,
    archive,
    *,
    seed=208153,
    repetitions=3,
    sites=None,
    instrument_sites=None,
    registered_sites=False,
    vary_target=False,
    composite_instruments=None,
):
    sys.path.insert(0, str(archive / "V5"))
    from src.simulation.m9.generator import (
        apply_cyber_events,
        build_observed_pmu_frames,
        extract_reference_statistics,
        generate_physical_truth,
        get_template,
        list_templates,
    )

    known = {
        site
        for catalog in (NEW, CATALOG, SITES)
        for group in catalog.values()
        for site in group
    }
    if sites is None:
        sites = {code: [site] for code, site in SITES_TEST.items()}
    else:
        known.update(SITES_TEST.values())
        known.add("BUS4")
    if not registered_sites:
        assert all(known.isdisjoint(group) for group in sites.values())
    rng = random.Random(seed)
    meta = archive / "data/metadata"
    raw = meta / "IEEE_39_Bus_Power_System.raw"
    stats = extract_reference_statistics(archive / "data/RAW0001")
    truth, checksums = {}, {}
    names = sorted(n for n in list_templates() if n.startswith("TEMPLATE_EVENT"))
    assert len(names) == 9
    for code, name in enumerate(names):
        for repetition in range(repetitions):
            seed, onset = rng.randrange(1, 2**31), rng.uniform(91, 95)
            strength = rng.uniform(0.8, 1.2) if vary_target else 1
            duration = rng.uniform(0.85, 1.15) if vary_target else 1
            for condition in ("isolated", "consecutive"):
                spec = get_template(name)
                physical, quality = spec["physical_events"], spec["cyber_events"]
                if code == 8 and composite_instruments is not None:
                    for event, sensor in zip(
                        quality, composite_instruments[repetition], strict=True
                    ):
                        event["target_pmus"] = [sensor]
                source = "none"
                if physical:
                    site = sites[code][repetition % len(sites[code])]
                    field = "target_line" if code == 2 else "target_bus"
                    physical[0][field] = site
                    if vary_target:
                        physical[0]["severity"] *= strength
                        physical[0]["duration_s"] *= duration
                        physical[0]["end_time_s"] = (
                            physical[0]["start_time_s"] + physical[0]["duration_s"]
                        )
                    source = (
                        (
                            "LINE"
                            + "-".join(
                                str(b)
                                for b in sorted(
                                    int(bus.removeprefix("BUS"))
                                    for bus in site.split("-")
                                )
                            )
                        )
                        if code == 2
                        else site
                    )
                elif quality:
                    if instrument_sites:
                        for event in quality:
                            event["target_pmus"] = [
                                instrument_sites[repetition % len(instrument_sites)]
                            ]
                    source = quality[0]["target_pmus"][0].replace("BUS", "PMU")
                for event in physical + quality:
                    event["start_time_s"] += onset - 4
                    event["end_time_s"] += onset - 4
                if condition == "consecutive":
                    fault = get_template(names[1])["physical_events"][0]
                    fault.update(
                        target_bus="BUS4",
                        start_time_s=89.5 - fault["duration_s"],
                        end_time_s=89.5,
                        event_id="previous",
                    )
                    physical.insert(0, fault)
                state = generate_physical_truth(
                    raw, meta / "PMUbus_ Location.txt", spec, seed=seed, duration_s=120
                )
                pmus = build_observed_pmu_frames(state, raw, stats, seed=seed)
                pmus = apply_cyber_events(
                    pmus, quality, state.event_by_frame, seed=seed
                )
                for end in (90, 120):
                    case = f"{rng.getrandbits(96):024x}"
                    folder = root / "observations" / case
                    folder.mkdir(parents=True, exist_ok=False)
                    for bus, frame in pmus.items():
                        fields = [
                            "TIMESTAMP",
                            "DATA_PRESENT",
                            bus + "_Freq",
                            bus + "_ROCOF",
                        ]
                        fields += [
                            f"{bus}_{q}{p}_{a}"
                            for q in "VI"
                            for p in "ABC"
                            for a in ("MAG", "ANG")
                        ]
                        view = frame.loc[
                            frame.TIMESTAMP.between(end - 90, end, inclusive="left"),
                            fields,
                        ].copy()
                        assert len(view) == 2700
                        view["TIMESTAMP"] = (view.TIMESTAMP - (end - 90)).round(6)
                        path = folder / f"Bus{bus[3:]}_Competition_Data_nanmask.csv"
                        view.to_csv(path, index=False)
                        checksums[f"{case}/{path.name}"] = hashlib.sha256(
                            path.read_bytes()
                        ).hexdigest()
                    preceding = end == 90 and condition == "consecutive"
                    truth[case] = dict(
                        pair=f"{code}-{repetition}",
                        condition=condition,
                        end=end,
                        code=code if end == 120 else int(preceding),
                        source=(
                            source if end == 120 else ("BUS4" if preceding else "none")
                        ),
                        onset=(
                            (onset if code else None)
                            if end == 120
                            else (89.28 if preceding else None)
                        ),
                    )
    save(root / "truth.json", truth)
    save(root / "observations_sha256.json", checksums)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    prepare(args.root, args.archive.resolve())

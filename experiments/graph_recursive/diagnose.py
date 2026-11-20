"""Retrospective error decomposition and zero-current representation check on frozen decisions."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

import numpy as np

from audit import read, sha
from evaluate import evaluate


def diagnostic(truth, predictions):
    matched_only, without_recovery_extras = [], []
    errors, misses, histories = Counter(), Counter(), Counter()
    post_delays = []
    for events, alarms in zip(truth, predictions, strict=True):
        matched = set()
        for event in events:
            i = next((i for i, a in enumerate(alarms) if i not in matched
                      and 0 <= a["detected"] - event["onset"] <= 45), None)
            if i is None:
                errors["missed"] += 1
                misses[f'{event["code"]}/{event["source"]}'] += 1
                continue
            a = alarms[i]
            matched.add(i)
            if a["published"] is None or a["published"] - event["onset"] > 45:
                errors["no_timely_diagnosis"] += 1
            elif a["code"] != event["code"]:
                errors["family"] += 1
            elif a["source"] != event["source"]:
                errors["site_only"] += 1
            else:
                errors["joint"] += 1
        retained = []
        for i, a in enumerate(alarms):
            previous = [e for e in events if e["onset"] <= a["detected"]]
            if i not in matched and previous and previous[-1]["end"] <= a["detected"]:
                histories[previous[-1]["code"]] += 1
                post_delays.append((a["detected"] - previous[-1]["end"]) / 30)
            else:
                retained.append(a)
        without_recovery_extras.append(retained)
        matched_only.append([a for i, a in enumerate(alarms) if i in matched])
    return dict(episode_outcomes=errors, missed_by_family_site=misses, extras_after=histories,
                recovery_extra_median_s=float(np.median(post_delays)),
                recovery_extras_after_4s=sum(t > 4 for t in post_delays),
                oracle_f1_remove_recovery_extras=evaluate(truth, without_recovery_extras)["macro_f1"],
                oracle_f1_remove_all_extras=evaluate(truth, matched_only)["macro_f1"])


def instrument_replay(path, truth, predictions):
    from monitor import PhysicalMonitor
    with path.open("rb") as f:
        if hashlib.file_digest(f, "sha256").hexdigest() != read("test_manifest.json")["observations"]:
            raise ValueError("Unexpected observations")
    observations = np.load(path, mmap_mode="r", allow_pickle=False)
    rows = []
    for rid, events in enumerate(truth):
        for e in events:
            if (e["code"], e["source"]) not in ((2, "LINE2-3"), (3, "BUS39")):
                continue
            on, off = e["onset"], e["end"]
            deadline = on + 45
            prefix = observations[rid, :deadline + 1]
            original = [a for a in predictions[rid] if on <= a["detected"] <= deadline]
            row = dict(record=rid, source=e["source"], original=original)
            if e["code"] == 2:
                during = observations[rid, on:off, 0]
                row["terminal_current_median_A"] = float(np.median(during[:, 2]))
                row["abs_current_angle_median_deg"] = float(np.median(abs(during[:, 3])))
                prefix = prefix.copy()
                mask = prefix[:, :, 2] == 0
                # All complex currents r*exp(i*phase) are identical before and after this recoding.
                prefix[:, :, 3][mask] = 0.
            monitor = PhysicalMonitor()
            output = {}
            max_event = 0.
            for tick, report in enumerate(prefix):
                for update in monitor.step(report):
                    output[update["detected"]] = update
                if tick >= on:
                    event_mass = float(np.exp(monitor.filter.log_mass[1:]).sum())
                    max_event = max(max_event, event_mass)
            if e["code"] == 2:
                row["zero_current_recoding"] = [
                    a for a in output.values() if on <= a["detected"] <= deadline
                ]
            else:
                row["peak_event_mass_in_deadline"] = max_event
            rows.append(row)
    return rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--observations", type=Path, help="Optional sealed PMU array for instrument replay")
    args = parser.parse_args()
    if (sha("phasor_predictions.json") != read("phasor_seal.json")["predictions"]
            or sha("test_truth.json") != read("test_manifest.json")["truth"]):
        raise ValueError("Unexpected test labels or predictions")
    truth, predictions = read("test_truth.json"), read("phasor_predictions.json")
    result = diagnostic(truth, predictions)
    if args.observations:
        result["replay"] = instrument_replay(args.observations, truth, predictions)
    print(json.dumps(result, indent=2))

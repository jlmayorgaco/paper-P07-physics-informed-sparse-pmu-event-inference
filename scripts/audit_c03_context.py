"""Matched C03 nominal records. Compare short-gap with first-event history gains."""

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments/paired_m9_stream/c03_context.json"


def main():
    data = json.loads(
        (ROOT / "generated/frozen/recovery_c03/TEST_RESULTS.json").read_text()
    )
    results = {}
    for plant in ("F01", "P2"):
        data_plant = data["results"][plant]["nominal"]

        def parents(arm):
            return {p["id"]: p for p in data_plant[arm]["rows"] if p["kind"] == "event"}

        history, carry = parents("history"), parents("carry")
        assert history.keys() == carry.keys() and len(history) == 36
        results[plant] = {}
        gains = []
        for label in ("first", "short_gap"):
            paired = []
            counts = {
                a: dict(timely=0, detected=0, delays=[]) for a in ("history", "carry")
            }
            for parent in sorted(history):
                maps = [
                    {e["id"]: e for e in records[parent]["rows"]}
                    for records in (history, carry)
                ]
                assert maps[0].keys() == maps[1].keys()
                chosen = [
                    k
                    for k, e in maps[0].items()
                    if (k.endswith("_E1") if label == "first" else e["short_gap"])
                ]
                assert len(chosen) == (1 if label == "first" else 4)
                delta = 0
                for k in chosen:
                    assert maps[0][k]["short_gap"] == maps[1][k]["short_gap"]
                    if label == "first":
                        assert not maps[0][k]["short_gap"]
                    for arm, ev in zip(counts, maps):
                        row = ev[k]
                        counts[arm]["timely"] += int(row["timely"])
                        counts[arm]["detected"] += int(row["detected"])
                        if row["detected"]:
                            counts[arm]["delays"].append(row["delay_s"])
                    delta += int(maps[0][k]["timely"]) - int(maps[1][k]["timely"])
                paired.append(delta / len(chosen))
            for row in counts.values():
                delays = row.pop("delays")
                row["median_reported_delay_s"] = (
                    float(np.median(delays)) if delays else None
                )
            results[plant][label] = counts
            gains.append(np.array(paired))
        # Same parent supplies the first event and four short-gap events.
        difference = gains[1] - gains[0]
        rng = np.random.default_rng(208153)
        boot = rng.choice(difference, size=(20000, len(difference)), replace=True).mean(
            axis=1
        )
        results[plant]["gain_short_minus_first_pp"] = (100 * difference.mean()).item()
        results[plant]["paired_percentile_interval_pp"] = (
            100 * np.quantile(boot, [0.025, 0.975])
        ).tolist()
    OUT.write_text(json.dumps(results, indent=2) + "\n")


if __name__ == "__main__":
    main()

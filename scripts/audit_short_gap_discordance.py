#!/usr/bin/env python3
"""Descriptive paired discordance audit; this is not a causal ablation."""
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "generated/frozen/recovery_c03/TEST_RESULTS.json"
OUT = ROOT / "experiments/recovery_discordance_20261119"
ARMS = ("history", "carry", "reset")
EXPECTED_CORRECT = {"F01": {"history": 144, "carry": 90, "reset": 17},
                    "P2": {"history": 67, "carry": 65, "reset": 20}}
FIELDS = ("both_correct", "gained", "lost", "neither")


def collect(records):
    parents = {}
    for record in records:
        if record["kind"] != "event":
            continue
        assert record["available"], f"unavailable parent {record['id']}"
        parent = record["id"]
        assert parent not in parents, f"duplicate parent {parent}"
        episodes = {}
        for episode in record["rows"]:
            eid = episode["id"]
            assert eid not in episodes, f"duplicate episode {parent}/{eid}"
            assert episode["family"] in ("line", "load")
            assert isinstance(episode["short_gap"], bool)
            assert isinstance(episode["timely"], bool)
            episodes[eid] = episode
        parents[parent] = episodes
    return parents


def totals(old, new, family=None):
    counts = Counter()
    for parent in old:
        for eid, before in old[parent].items():
            if family is not None and before["family"] != family:
                continue
            a, b = before["timely"], new[parent][eid]["timely"]
            key = ("both_correct" if a and b else "gained" if b else
                   "lost" if a else "neither")
            counts[key] += 1
    return counts


def main():
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    output = []
    macros = {}
    for plant in ("F01", "P2"):
        arms = {arm: collect(data["results"][plant]["nominal"][arm]["rows"])
                for arm in ARMS}
        reference = arms["history"]
        assert len(reference) == 36, (plant, "event parents", len(reference))
        for arm in ARMS[1:]:
            assert set(arms[arm]) == set(reference), (plant, arm, "parent sets")
            for parent in reference:
                assert set(arms[arm][parent]) == set(reference[parent]), (
                    plant, arm, parent, "episode sets")
                for eid, base in reference[parent].items():
                    other = arms[arm][parent][eid]
                    assert (base["short_gap"], base["family"]) == (
                        other["short_gap"], other["family"]), (
                            plant, arm, parent, eid, "episode metadata")
        short = {p: {e: row for e, row in eps.items() if row["short_gap"]}
                 for p, eps in reference.items()}
        short = {p: eps for p, eps in short.items() if eps}
        assert sum(map(len, short.values())) == 144, (plant, "short episodes")
        selected = {arm: {p: {e: eps[p][e] for e in short[p]} for p in short}
                    for arm, eps in arms.items()}
        for arm, expected in EXPECTED_CORRECT[plant].items():
            correct = sum(row["timely"] for eps in selected[arm].values()
                          for row in eps.values())
            assert correct == expected, (plant, arm, correct, expected)
        for old_name, new_name in (("carry", "history"), ("reset", "carry")):
            for family in ("line", "load", "pooled"):
                c = totals(selected[old_name], selected[new_name],
                           None if family == "pooled" else family)
                output.append([plant, old_name, new_name, family] +
                              [c[k] for k in FIELDS] + [sum(c.values())])
                if new_name == "history" and family == "pooled":
                    macros[(plant, "Gained")] = c["gained"]
                    macros[(plant, "Lost")] = c["lost"]
    with (OUT / "paired.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["plant", "old_arm", "new_arm", "family", *FIELDS, "denominator"])
        writer.writerows(output)
    names = {"F01": "FOne", "P2": "PTwo"}
    with (OUT / "macros.tex").open("w", encoding="utf-8") as f:
        for plant in ("F01", "P2"):
            for suffix in ("Gained", "Lost"):
                f.write(r"\newcommand{" + chr(92) + names[plant] + "History" + suffix +
                        "}{" + str(macros[(plant, suffix)]) + "}\n")


if __name__ == "__main__":
    main()
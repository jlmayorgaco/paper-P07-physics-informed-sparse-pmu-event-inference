"""Describe which episodes were missed and when unmatched alerts were raised."""

from collections import Counter
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from design_stress import c, CONDITIONS, RESULT
from score_stress import matches


def diagnose(schedules, predictions):
    positions = [Counter() for _ in range(3)]
    alarms = Counter()
    after_clearance = 0
    late_after_clearance = 0
    per_record = []
    for events, alerts in zip(schedules, predictions, strict=True):
        pairs = matches(events, alerts)
        for i, event in enumerate(events):
            position = positions[i]
            position["events"] += 1
            if i in pairs:
                alert = alerts[pairs[i]]
                position["detected"] += 1
                timely = alert["published"] is not None and alert["published"] <= event["onset"] + 45
                position["joint_correct"] += int(
                    timely and alert["code"] == event["code"] and alert["source"] == event["source"]
                )
        extras = [a for j, a in enumerate(alerts) if j not in pairs.values()]
        per_record.append(len(extras))
        for a in extras:
            if not events:
                alarms["quiet"] += 1
            elif a["detected"] < events[0]["onset"]:
                alarms["before_first_onset"] += 1
            else:
                alarms["after_first_onset"] += 1
                last_clearance = max(event["end"] for event in events)
                after_clearance += a["detected"] >= last_clearance
                late_after_clearance += a["detected"] >= last_clearance + 45
    return dict(
        by_schedule_position=positions,
        extra_timing=alarms,
        extras_after_final_clearance=after_clearance,
        extras_at_least_1p5s_after_final_clearance=late_after_clearance,
        records_with_extras=sum(n > 0 for n in per_record),
        max_extras_per_record=max(per_record),
    )


if __name__ == "__main__":
    truth = c.load(RESULT / "test_truth.json")
    predictions = c.load(RESULT / "predictions.json")
    scores = c.load(RESULT / "scores.json")
    result = {}
    for condition in CONDITIONS:
        result[condition.name] = {}
        for method, rows in predictions[condition.name].items():
            d = diagnose(truth[condition.timing], rows)
            assert sum(d["extra_timing"].values()) == scores[condition.name][method]["extras"]
            result[condition.name][method] = d
    c.save(RESULT / "diagnostics.json", result)

"""One-to-one scoring with separate publication times and complete episode denominators."""
import numpy as np


def evaluate(truth, predictions, bootstrap=False):
    if len(truth) != len(predictions):
        raise ValueError("Missing trajectory")
    # Rows: extra, families 1..4. Columns: absent/late, families 1..4, other.
    confusion = np.zeros((5, 6), dtype=int)
    by_family = np.zeros((4, 4), dtype=int)  # missed detection, wrong/late family, wrong site, joint
    delays, diagnostic_delays = [], []
    quiet_records = quiet_extras = 0
    per_record = []
    for events, alarms in zip(truth, predictions):
        if any(a["published"] is not None and not a["detected"] <= a["published"] < 720 for a in alarms):
            raise ValueError("Invalid publication time")
        if [a["detected"] for a in alarms] != sorted(a["detected"] for a in alarms):
            raise ValueError("Unordered detections")
        used = set()
        successes = 0
        for e in events:
            code = e["code"]
            index = next((i for i, a in enumerate(alarms)
                          if i not in used and 0 <= a["detected"] - e["onset"] <= 45), None)
            if index is None:
                confusion[code, 0] += 1
                by_family[code - 1, 0] += 1
                continue
            used.add(index)
            a = alarms[index]
            delays.append((a["detected"] - e["onset"]) / 30)
            timely = a["published"] is not None and a["published"] - e["onset"] <= 45
            label = min(a["code"], 5) if timely else 0
            confusion[code, label] += 1
            if timely:
                diagnostic_delays.append((a["published"] - e["onset"]) / 30)
            joint = label == code and a["source"] == e["source"]
            category = 1 if label != code else (3 if joint else 2)
            by_family[code - 1, category] += 1
            successes += int(joint)
        for i, a in enumerate(alarms):
            if i not in used:
                confusion[0, min(a["code"] or 0, 5)] += 1
        if not events:
            quiet_records += 1
            quiet_extras += len(alarms)
        per_record.append((len(events), successes))
    f1s = []
    for c in range(1, 5):
        denominator = confusion[c, :].sum() + confusion[:, c].sum()
        f1s.append(2 * confusion[c, c] / denominator if denominator else 0)
    n, correct = np.sum(per_record, axis=0)
    quiet_hours = quiet_records * (720 - 30) / (30 * 3600)
    result = dict(events=int(n), detected=len(delays), family=int(np.trace(confusion[1:, 1:5])),
                  joint=int(correct), macro_f1=float(np.mean(f1s)),
                  extras=int(confusion[0].sum()), quiet_extras=quiet_extras, quiet_hours=quiet_hours,
                  fa_normal_per_hour=quiet_extras / quiet_hours if quiet_hours else None,
                  event_record_extras=int(confusion[0].sum()) - quiet_extras,
                  median_detection_s=float(np.median(delays)) if delays else None,
                  median_diagnosis_s=float(np.median(diagnostic_delays)) if diagnostic_delays else None,
                  confusion=confusion.tolist(), by_family=by_family.tolist())
    if bootstrap and n:
        rng = np.random.default_rng(9812)
        indices = rng.integers(len(per_record), size=(4000, len(per_record)))
        total = np.asarray(per_record)[indices].sum(axis=1)
        total = total[total[:, 0] > 0]
        result["joint_ci95"] = np.quantile(total[:, 1] / total[:, 0], [.025, .975]).tolist()
    return result

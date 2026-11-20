"""One-to-one time-only matching and paired uncertainty on all second events."""

import numpy as np
from scipy.stats import binomtest, chi2
from shared import RESULT, TMP, digest, read, save

ARMS = ("original", "lag", "cnn", "cnn_no_sub", "carry", "reset", "native")


def compare(a, b, indices):
    diff = a.astype(int) - b.astype(int)
    wins, losses = int(sum(diff > 0)), int(sum(diff < 0))
    return dict(
        wins=wins,
        losses=losses,
        difference=float(diff.mean()),
        ci95=np.quantile(diff[indices].mean(axis=1), [0.025, 0.975]).tolist(),
        p=binomtest(wins, wins + losses).pvalue if wins + losses else 1.0,
    )


def score(truth, pred):
    per = []
    extras = 0
    for r in truth:
        alerts = pred["events"][r["id"]]
        matched = []
        for j, e in enumerate(r["events"]):
            cutoff = min(e["onset_tick"] + 1800, r["events"][j + 1]["onset_tick"] if j == 0 else 2401)
            idx = next(
                (
                    i
                    for i, a in enumerate(alerts)
                    if i not in matched and e["onset_tick"] <= 2 * a["report"] < cutoff
                ),
                None,
            )
            matched.append(idx)
        extras += len(alerts) - sum(i is not None for i in matched)
        e = r["events"][1]
        a = alerts[matched[1]] if matched[1] is not None else None
        outcomes = {}
        for name in ARMS:
            tick = (a["report"] if name == "native" else a.get("readout")) if a else None
            label = a.get("original" if name == "native" else name) if a else None
            timely = tick is not None and 2 * tick < e["off_tick"]
            outcomes[name] = dict(
                correct=bool(timely and label == e["family"]), label=label if timely else None
            )
        per.append(
            dict(
                id=r["id"],
                families=[t["family"] for t in r["events"]],
                matched=a is not None,
                outcomes=outcomes,
            )
        )
    rng = np.random.default_rng(869151)
    groups = sorted(set(tuple(r["families"]) for r in per))
    strata = [np.array([i for i, r in enumerate(per) if tuple(r["families"]) == g]) for g in groups]
    assert [len(x) for x in strata] == [9] * 4
    boot = np.column_stack([rng.choice(x, size=(10000, len(x))) for x in strata])
    acc = {k: np.array([r["outcomes"][k]["correct"] for r in per]) for k in ARMS}
    summary = {}
    for k, ok in acc.items():
        classes = {}
        for family in ("load", "line"):
            rows = [r["outcomes"][k] for r in per if r["families"][1] == family]
            classes[family] = {
                c: sum(z["label"] == v for z in rows)
                for c, v in (("load", "load"), ("line", "line"), ("miss_late_abstain", None))
            }
        summary[k] = dict(correct=int(ok.sum()), by_family=classes)
    pairs = {
        a + "_vs_" + b: compare(acc[a], acc[b], boot)
        for a, b in (
            ("original", "cnn"),
            ("lag", "cnn"),
            ("lag", "original"),
            ("carry", "reset"),
            ("cnn", "cnn_no_sub"),
        )
    }
    quiet = {}
    for split, rows in pred["normal"].items():
        n = sum(r["alarms"] for r in rows)
        hours = sum((r["reports"] - 1) / 30 - 12 for r in rows) / 3600
        quiet[split] = dict(alarms=n, hours=hours, upper95=float(chi2.ppf(0.95, 2 * (n + 1)) / 2 / hours))
    return dict(
        n=len(per),
        matched=sum(r["matched"] for r in per),
        event_extras=extras,
        summaries=summary,
        paired=pairs,
        quiet=quiet,
        records=per,
    )


def main():
    lock = read(RESULT / "prediction_seal.json")
    assert all(digest(RESULT / (k + ".json")) == v for k, v in lock.items())
    truth = TMP / "truth.json"
    assert digest(truth) == read(RESULT / "observations.json")["truth_sha"]
    truth = read(truth)
    result = score(truth, read(RESULT / "predictions.json"))
    save(RESULT / "truth.json", truth)
    save(RESULT / "scores.json", result)
    print({k: v for k, v in result.items() if k != "records"})


if __name__ == "__main__":
    main()

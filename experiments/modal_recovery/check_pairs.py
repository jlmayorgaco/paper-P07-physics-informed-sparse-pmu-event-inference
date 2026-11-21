"""Verify simulated counterfactual pairs and replay PMU-only decisions on both cohorts."""
from collections import defaultdict
from pathlib import Path

import study
import joblib
import numpy as np


def check(root, results, confirmation):
    calls = study.read(results / "predictions.json")["calls"]
    truth = study.read(results / "truth.json")
    parents = defaultdict(dict)
    for key, t in truth.items():
        parents[t["parent"]][t["family"] != "none"] = key
    models = {a: joblib.load(study.RESULT / (a + ".joblib")) for a in study.ARMS}
    cuts = study.verify()["thresholds"]
    mixed = {a: joblib.load(results / (a + ".joblib")) for a in study.ARMS} if confirmation else {}
    for i, pair in parents.items():
        control, event = pair[False], pair[True]
        ys = []
        for key in (control, event):
            path = root / "test" / (key + ".npz")
            assert study.digest(path) == calls[key]["sha" if confirmation else "observation_sha"]
            y, clearance = study.unpack(path)
            ys.append(y)
        e = truth[event]
        assert e["source"] != e["first"] and truth[control]["first"] == e["first"]
        assert e["clearance"] == truth[control]["clearance"] == clearance
        before = np.arange(len(y)) / 30 < e["on"]
        np.testing.assert_array_equal(ys[0][before], ys[1][before])
        assert np.any(ys[0][~before] != ys[1][~before])
        if i not in (0, 31, 63, 95):
            continue
        for key, y in zip((control,event), ys):
            for arm, model in models.items():
                reports, score, family, site = model.scan(y, clearance)
                hits = np.flatnonzero(score > cuts[arm]["value"])
                b = int(reports[hits[0]]) if len(hits) else None
                expected = calls[key]
                if confirmation:
                    if arm == "modal":
                        assert expected["alarm"] == b
                        if b is not None:
                            assert expected["labels"]["immediate"] == [family[hits[0]], site[hits[0]]]
                    trigger = expected["alarm"]
                    if trigger is not None and trigger + 29 < len(y):
                        for label, m in (("fixed",model),("mixed",mixed[arm])):
                            _,_,f,s = m.scan(y[trigger-30:trigger+30],0)
                            assert expected["labels"][arm+"_"+label] == [f[0],s[0]]
                else:
                    result = None if b is None else dict(report=b,family=family[hits[0]],source=site[hits[0]])
                    assert result == expected["arms"][arm]
    assert len(parents)==96
    print("Verified 96 counterfactual prefixes and replayed eight records:", results)


if __name__ == "__main__":
    check(study.TMP, study.RESULT, False)
    check(study.ROOT / "tmp/modal_recovery_lag", Path(__file__).parent / "fixed_lag/results", True)

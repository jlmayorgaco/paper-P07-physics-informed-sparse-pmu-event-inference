"""Recalculate published metrics and optionally simulate all PMUs and replay the frozen estimator."""
import argparse
from collections import Counter
from pathlib import Path
import subprocess
import sys
import tempfile
import numpy as np
import cohort_joint as c


def audit():
    p=c.RESULT/"predictions.json"
    truth_path=c.RESULT/"test_truth.json"
    manifest=c.RESULT/"test_manifest.json"
    if c.load(c.RESULT/"seal.json")!=dict(predictions=c.sha(p),freeze=c.sha(c.LOCK),manifest=c.sha(manifest)):
        raise ValueError("Prediction seal differs")
    if c.sha(truth_path)!=c.load(manifest)["truth"]:
        raise ValueError("Published labels differ from manifest")
    truth=c.load(truth_path)
    scores=c.load(c.RESULT/"scores.json")
    target_counts=Counter(e["code"] for row in truth for e in row)
    for name,predictions in c.load(p).items():
        reported,good=Counter(),Counter()
        site=extras=0
        for events,alerts in zip(truth,predictions,strict=True):
            remaining=list(alerts)
            for e in events:
                a=next((a for a in remaining if 0<=a["detected"]-e["onset"]<=45),None)
                if a is None:
                    continue
                remaining.remove(a)
                if a["published"] is not None and a["published"]<=e["onset"]+45:
                    reported[a["code"]]+=1
                    good[e["code"]]+=a["code"]==e["code"]
                    site+=a["source"]==e["source"]
            extras+=len(remaining)
            reported.update(a["code"] for a in remaining)
        macro=np.mean([2*good[k]/(reported[k]+target_counts[k]) for k in range(1,5)])
        s=scores[name]
        assert (sum(good.values()),site,extras)==(s["family"],s["exact_site"],s["extras"])
        np.testing.assert_allclose(macro,s["macro_f1"],rtol=0,atol=1e-12)
        print(name,"macro-F1",macro,"family",sum(good.values()),"site",site,"extras",extras)


def fresh_replay():
    from apply_joint import frozen_observer
    from joint_observer import JointObserver
    root=c.ROOT/"tmp"
    root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=root) as tmp:
        snippet=("import sys; from pathlib import Path; sys.path.insert(0,sys.argv[1]); "
                 "import cohort_joint as c; c.DATA=Path(sys.argv[2])/'raw'; "
                 "c.RESULT=Path(sys.argv[2])/'manifests'; c.generate('test')")
        subprocess.run([sys.executable,"-c",snippet,str(c.HERE),tmp],check=True)
        if c.load(Path(tmp)/"manifests/test_manifest.json")!=c.load(c.RESULT/"test_manifest.json"):
            raise ValueError("Fresh simulation differs from sealed observations")
        raw=np.load(Path(tmp)/"raw/test/pmu.npy",allow_pickle=False)
        published=c.load(c.RESULT/"predictions.json")["joint"]
        first=frozen_observer()
        cfg=c.load(c.LOCK)["config"]
        ids=np.sort(np.random.default_rng(97123).choice(len(raw),24,replace=False))
        for i in ids:
            obs=JointObserver(first.bank,first.model,cfg,first.physics)
            alarms=[a for row in raw[i] for a in obs.step(row)]
            if alarms!=published[i]:
                raise ValueError("Online replay differs at record "+str(i))
        print("Reproduced the full simulation hash and causal alarms on records",ids.tolist())


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--regenerate",action="store_true")
    args=p.parse_args()
    audit()
    if args.regenerate:
        fresh_replay()

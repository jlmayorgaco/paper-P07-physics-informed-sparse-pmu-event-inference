"""Recalculate scores offline, or regenerate all PMUs and replay four causal monitors."""
import argparse
from pathlib import Path
import subprocess
import sys
import tempfile
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
import design


def offline():
    seal=design.load(HERE/"seal.json")
    for field,name in (("freeze","freeze.json"),("predictions","predictions.json"),("manifest","test_manifest.json")):
        if design.sha(HERE/name)!=seal[field]:
            raise ValueError("Invalid seal: "+field)
    if design.sha(HERE/"test_truth.json")!=design.load(HERE/"test_manifest.json")["truth"]:
        raise ValueError("Truth differs from manifest")
    truth=design.load(HERE/"test_truth.json")
    scores=design.load(HERE/"scores.json")
    for name,episodes in design.load(HERE/"predictions.json").items():
        total=sum(map(len,truth))
        actual=np.bincount([e["code"] for r in truth for e in r],minlength=5)
        tp=np.zeros(5,dtype=int)
        labels=np.zeros(5,dtype=int)
        site=joint=detected=extras=normal=0
        for events,alerts in zip(truth,episodes,strict=True):
            consumed=set()
            for e in events:
                hits=[i for i,a in enumerate(alerts) if i not in consumed and 0<=a["detected"]-e["onset"]<=45]
                if not hits:
                    continue
                i=hits[0]
                consumed.add(i)
                detected+=1
                a=alerts[i]
                if a["published"] is not None and a["published"]<=e["onset"]+45:
                    if 1<=a["code"]<=4:
                        labels[a["code"]]+=1
                    correct=a["code"]==e["code"]
                    tp[e["code"]]+=correct
                    site+=a["source"]==e["source"]
                    joint+=correct and a["source"]==e["source"]
            for i,a in enumerate(alerts):
                if i not in consumed:
                    extras+=1
                    normal+=not events
                    if 1<=a["code"]<=4:
                        labels[a["code"]]+=1
        f1=np.mean(2*tp[1:]/(actual+labels)[1:])
        s=scores[name]
        assert (total,detected,tp.sum(),site,joint,extras,normal)==tuple(s[k] for k in
            ("events","detected","family","exact_site","joint","extras","quiet_extras"))
        np.testing.assert_allclose(f1,s["macro_f1"],atol=1e-12,rtol=0)
        print(name,total,detected,tp.sum(),site,joint,f1,extras,normal)
    # Sensitivity to counting the common first intervention once for each twin:
    # retain quiet records, standalone singles and the intervention arm of each pair.
    from trial import metrics
    names=design.load(HERE/"test_manifest.json")["clusters"]
    keep=[i for i,(name,row) in enumerate(zip(names,truth,strict=True))
          if not name.startswith("pair-") or len(row)==2]
    for name,p in design.load(HERE/"predictions.json").items():
        s=metrics([truth[i] for i in keep],[p[i] for i in keep])
        print("One copy of each first event",name,s["events"],s["macro_f1"],s["family"],s["exact_site"],s["extras"])


def rerun(folder):
    import joblib
    from apply_recovery import frozen_observer
    from recovery import RecoveryObserver
    from intervention_monitor import run
    from study import supervised
    if design.sha(folder/"test/pmu.npy")!=design.load(HERE/"test_manifest.json")["observations"]:
        raise ValueError("Regenerated PMUs differ")
    x=np.load(folder/"test/pmu.npy",mmap_mode="r")
    frozen=design.load(design.LOCK)
    predictions=design.load(HERE/"predictions.json")
    trees=[joblib.load(p) for p in (design.common.FROZEN_TREES,design.TREES)]
    first=frozen_observer()
    indices=np.sort(np.random.default_rng(506928).choice(len(x),24,replace=False))
    for i in indices:
        obs=RecoveryObserver(first.bank,first.model,frozen["config"],first.physics)
        row=[a for sample in x[i] for a in obs.step(sample)]
        assert row==predictions["recovery"][i]
        assert run(x[i],first.bank,first.model,frozen["previous"])==predictions["previous"][i]
        for t,key in zip(trees,("trees","trees_refit")):
            assert supervised(x[i],t)==predictions[key][i]
    print("All 480 regenerated streams matched the hash. Four monitors matched on records",indices.tolist())


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--regenerate",action="store_true")
    args=parser.parse_args()
    offline()
    if args.regenerate:
        temp_root=design.ROOT/"tmp"
        temp_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temp_root) as tmp:
            # Use a fresh interpreter to isolate the legacy simulator's module imports.
            snippet=("import sys; from pathlib import Path; sys.path.insert(0,sys.argv[1]); "
                     "import design; design.DATA=Path(sys.argv[2]); "
                     "design.RESULT=design.DATA/'manifests'; design.generate('test')")
            subprocess.run([sys.executable,"-c",snippet,str(HERE.parent),tmp],check=True)
            if design.load(Path(tmp)/"manifests/test_manifest.json")!=design.load(HERE/"test_manifest.json"):
                raise ValueError("Regenerated manifest differs")
            rerun(Path(tmp))

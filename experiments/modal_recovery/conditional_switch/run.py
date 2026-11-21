"""Freeze, predict from unlabeled observations, and score in separate processes."""
import argparse
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import study
from fixed_lag import trial
from cohort import TMP, SPLITS
from metrics import counts
import quiet
import joblib
import numpy as np

RESULT = HERE / "results"


def freeze():
    trial.verify()
    from freeze import verify as verify_science
    verify_science()
    assert not (TMP/"test").exists() and not (RESULT/"freeze.json").exists()
    RESULT.mkdir(parents=True,exist_ok=True)
    candidates = study.read(TMP/"short_development_final.json")+study.read(TMP/"reference_development.json")
    viable = [v for v in candidates if v["false"]<.05*192]
    choice = max(viable,key=lambda v:(v["site"],v["family"],v["detect"],-v["false"],-abs(v["level"]-.99)))
    ref = choice["name"]=="reference"
    models = {"background":"quiet_reference" if ref else "background","detector":choice["name"],
              "source":"reference_readout" if ref else "conditional_readout"}
    for dest, src in models.items():
        shutil.copyfile(TMP/(src+".joblib"), RESULT/(dest+".joblib"))
    development = dict(finalists=candidates, chosen=choice,
                       postclearance_grid=study.read(TMP/"conditional_development_ticks.json"),
                       profiled_amplitude=study.read(TMP/"profile_development.json"))
    study.save(RESULT/"development.json",development)
    shutil.copyfile(TMP/("quiet_cal_"+choice["name"]+".json"), RESULT/"quiet_calibration.json")
    for split in ("fit","cal"):
        shutil.copyfile(TMP/(split+"_manifest.json"), RESULT/(split+"_manifest.json"))
    files = sorted(HERE.glob("*.py"))+[HERE/"PROTOCOL.md",HERE/"diagnosis.json"]
    artifacts = sorted(RESULT.iterdir())
    study.save(RESULT/"freeze.json",dict(threshold=choice["threshold"], choice=choice["name"],
               sources={p.name:study.digest(p) for p in files}, artifacts={p.name:study.digest(p) for p in artifacts},
               upstream_lag=study.digest(trial.RESULT/"freeze.json"),
               upstream_science=study.digest(study.ROOT/"experiments/second_family/results/freeze.json"),
               prior_threshold=study.verify()["thresholds"]["modal"]["value"], splits=SPLITS))
    print(choice,flush=True)


def verify():
    trial.verify()
    f = study.read(RESULT/"freeze.json")
    assert study.digest(trial.RESULT/"freeze.json")==f["upstream_lag"]
    assert study.digest(study.ROOT/"experiments/second_family/results/freeze.json")==f["upstream_science"]
    for folder, entries in ((HERE,f["sources"]),(RESULT,f["artifacts"])):
        for name, expected in entries.items():
            if study.digest(folder/name)!=expected:
                raise ValueError(f"Changed frozen file {name}")
    return f


def old_label(source, y, b):
    if b is None or b+29 >= len(y):
        return None
    _,_,family,site = source.scan(y[b-30:b+30],0)
    return [str(family[0]), str(site[0])]


def infer(y, clear, old_gate, old_source, background, gate, source, freeze):
    reports, scores, _, _ = old_gate.scan(y,clear)
    hits = np.flatnonzero(scores>freeze["prior_threshold"])
    old = int(reports[hits[0]]) if len(hits) else None
    r = background.residual(y,clear)
    hits = np.flatnonzero(gate.scores(r)>freeze["threshold"])
    b = clear+gate.length-1+int(hits[0]) if len(hits) else None
    label = None
    if b is not None and b+29<len(y):
        end = b+29-clear
        label = source.classify(r[end-source.length+1:end+1])
    return dict(current=dict(alarm=old,label=old_label(old_source,y,old)),
                adjusted_gate=dict(alarm=b,label=old_label(old_source,y,b)), adjusted=dict(alarm=b,label=label))


def models():
    return (joblib.load(study.RESULT/"modal.joblib"), joblib.load(trial.RESULT/"modal.joblib"),
            *(joblib.load(RESULT/(n+".joblib")) for n in ("background","detector","source")))


def predict():
    f = verify()
    assert not (RESULT/"predictions.json").exists()
    manifest_path = TMP/"test_manifest.json"
    manifest = study.read(manifest_path)
    assert manifest["parents"]==240 and manifest["seed"]==SPLITS["test"][0] and len(manifest["hashes"])==480
    estimator = models()
    calls = {}
    for i,(key,digest) in enumerate(sorted(manifest["hashes"].items())):
        p = TMP/"test"/(key+".npz")
        assert study.digest(p)==digest
        y,c = study.unpack(p)
        calls[key] = infer(y,c,*estimator,f)
        # Replay short prefixes for a deterministic subset without using labels.
        if i%17==0:
            for arm, row in calls[key].items():
                b = row["alarm"]
                if b is None:
                    continue
                prefix = infer(y[:b+1],c,*estimator,f)[arm]
                assert prefix["alarm"]==b and prefix["label"] is None
                if b+29<len(y):
                    assert infer(y[:b+30],c,*estimator,f)[arm]==row
    normal = quiet.scan("P2","TEST",estimator[2],estimator[3],f["threshold"])
    prior = study.read(study.RESULT/"predictions.json")["quiet"]
    assert prior.keys()==normal.keys()
    for key in normal:
        assert normal[key]["scored_reports"]==prior[key]["modal"]["scored_reports"]
        normal[key]["current_episodes"] = prior[key]["modal"]["episodes"]
    shutil.copyfile(manifest_path,RESULT/"test_manifest.json")
    study.save(RESULT/"predictions.json",dict(freeze_sha=study.digest(RESULT/"freeze.json"),
               manifest_sha=study.digest(manifest_path),targets_sha=manifest["targets_sha"],calls=calls,quiet=normal))
    print("Sealed calls:",study.digest(RESULT/"predictions.json"),flush=True)


def score():
    verify()
    p = RESULT/"predictions.json"
    pred = study.read(p)
    assert pred["freeze_sha"]==study.digest(RESULT/"freeze.json")
    assert pred["manifest_sha"]==study.digest(RESULT/"test_manifest.json")
    labels = TMP/"test_truth.json" if (TMP/"test_truth.json").exists() else RESULT/"truth.json"
    assert pred["targets_sha"]==study.digest(labels)
    truth = study.read(labels)
    result = counts(truth,pred["calls"])
    normal = pred["quiet"].values()
    result["long_quiet"] = dict(hours=sum(r["scored_reports"] for r in normal)/108000,
                                current=sum(r["current_episodes"] for r in normal),
                                adjusted=sum(r["episodes"] for r in normal))
    result.update(predictions_sha=study.digest(p),truth_sha=study.digest(labels))
    if (RESULT/"scores.json").exists():
        assert result==study.read(RESULT/"scores.json")
    else:
        shutil.copyfile(labels,RESULT/"truth.json")
        study.save(RESULT/"scores.json",result)
    print(result["counts"],result["long_quiet"],result["adjusted_by_second_family"],flush=True)


if __name__ == "__main__":
    cli = argparse.ArgumentParser()
    cli.add_argument("stage",choices=("freeze","predict","score","verify"))
    args = cli.parse_args()
    {"freeze":freeze,"predict":predict,"score":score,"verify":verify}[args.stage]()

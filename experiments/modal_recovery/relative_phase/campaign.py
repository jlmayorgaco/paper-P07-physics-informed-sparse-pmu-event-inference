"""Freeze before generation; seal both predictors before opening targets."""
import argparse
from hashlib import sha256
from io import BytesIO
from zipfile import ZipFile,ZIP_STORED
import shutil
from phase_data import HERE,RESULT,TMP,SPLITS,folder,study,angular
from benchmark import call,quiet,report
import run as previous
import joblib
import numpy as np

WEIGHTS = ("background","detector","source")


def freeze():
    previous.verify()
    from freeze import verify as verify_physics
    verify_physics()
    selected = study.read(RESULT/"development.json")["selected"]
    assert selected and selected["qualifies"] and not (TMP/"test").exists()
    assert not (RESULT/"freeze.json").exists()
    for name in WEIGHTS:
        shutil.copyfile(TMP/(name+".joblib"),RESULT/(name+".joblib"))
    for split in ("fit","cal","dev"):
        shutil.copyfile(TMP/split/"manifest.json",RESULT/(split+"_manifest.json"))
    shutil.copyfile(TMP/"quiet_cal.json",RESULT/"quiet_cal.json")
    sources = list(HERE.glob("*.py"))+[HERE/"PROTOCOL.md"]
    study.save(RESULT/"freeze.json",dict(threshold=selected["threshold"],seed=SPLITS["test"][0],
        preceding=study.digest(previous.RESULT/"freeze.json"),sources={p.name:study.digest(p) for p in sources},
        weights={p.name:study.digest(p) for p in RESULT.iterdir()},hashes={name:study.digest(TMP/(name+".npz"))
        for name in ("switch","recovery")}))


def verify_freeze():
    previous.verify()
    f = study.read(RESULT/"freeze.json")
    assert f["preceding"]==study.digest(previous.RESULT/"freeze.json")
    for root,key in ((HERE,"sources"),(RESULT,"weights")):
        for name,digest in f[key].items():
            assert study.digest(root/name)==digest, name
    return f


def arms():
    old = previous.verify()
    return {arm:([joblib.load(base/(name+".joblib")) for name in WEIGHTS],limit)
            for arm,base,limit in (("magnitudes",previous.RESULT,old["threshold"]),
                                   ("angles",RESULT,verify_freeze()["threshold"]))}


def inference(y,c,models):
    calls = {}
    for name,((bg,gate,source),threshold) in models.items():
        z = y[:,:16] if name=="magnitudes" else y
        calls[name] = call(bg.residual(z,c),c,gate,source,threshold)
    return calls


def predict():
    f = verify_freeze()
    models = arms()
    path = TMP/"test/manifest.json"
    manifest = study.read(path)
    assert manifest["seed"]==f["seed"] and manifest["parents"]==240 and len(manifest["hashes"])==480
    historical = set(study.read(RESULT/"dev_manifest.json")["hashes"])
    assert not historical.intersection(manifest["hashes"])
    calls = {}
    archive_path = RESULT/"blind_pmus.zip"
    with ZipFile(archive_path,"x",compression=ZIP_STORED) as archive:
        for j,(k,expected) in enumerate(sorted(manifest["hashes"].items())):
            p = folder("test")/(k+".npz")
            assert study.digest(p)==expected
            y,c = study.unpack(p)
            calls[k] = inference(y,c,models)
            if j%17==0:
                # Any time-dependent common rotation of the voltage and current phasors cancels.
                rotated = y.copy()
                rotated[:,16:] += (np.arange(len(y))*1.7)[:,None]
                np.testing.assert_allclose(angular(y),angular(rotated),rtol=1e-8,atol=1e-9)
                for arm,v in calls[k].items():
                    b = v["alarm"]
                    if b is not None:
                        assert inference(y[:b+1],c,models)[arm]==dict(alarm=b,label=None)
                        if b+29<len(y):
                            assert inference(y[:b+30],c,models)[arm]==v
            archive.write(p,arcname=p.name)
    (bg,gate,_),threshold = models["angles"]
    normal = quiet("P2","TEST",bg,gate,threshold)
    archived = study.read(previous.RESULT/"predictions.json")["quiet"]
    for k,v in normal.items():
        assert v["reports"]==archived[k]["scored_reports"]
        v["magnitudes_alarms"]=archived[k]["episodes"]
    shutil.copyfile(path,RESULT/"test_manifest.json")
    study.save(RESULT/"predictions.json",dict(freeze_sha=study.digest(RESULT/"freeze.json"),
               manifest_sha=study.digest(path),zip_sha=study.digest(archive_path),targets_sha=manifest["targets_sha"],
               calls=calls,quiet=normal))
    print("Sealed",len(calls),"anonymous predictions per arm.",flush=True)


def replay():
    models = arms()
    pred = study.read(RESULT/"predictions.json")
    hashes = study.read(RESULT/"test_manifest.json")["hashes"]
    archive_path = RESULT/"blind_pmus.zip"
    assert study.digest(archive_path)==pred["zip_sha"]
    with ZipFile(archive_path) as archive:
        assert set(archive.namelist())=={k+".npz" for k in hashes} and len(archive.namelist())==480
        for k,digest in hashes.items():
            payload = archive.read(k+".npz")
            assert sha256(payload).hexdigest()==digest
            with np.load(BytesIO(payload),allow_pickle=False) as z:
                assert inference(z["y"],int(z["clearance"]),models)==pred["calls"][k]
    print("All 960 calls reproduced from archived input.",flush=True)


def score():
    verify_freeze()
    pred = study.read(RESULT/"predictions.json")
    assert pred["freeze_sha"]==study.digest(RESULT/"freeze.json")
    assert pred["manifest_sha"]==study.digest(RESULT/"test_manifest.json")
    source = RESULT/"truth.json" if (RESULT/"truth.json").exists() else TMP/"test/targets.json"
    assert study.digest(source)==pred["targets_sha"]
    out = report(study.read(source),pred["calls"])
    del out["improved_in_development"]
    normal = pred["quiet"].values()
    out.update(predictions_sha=study.digest(RESULT/"predictions.json"),targets_sha=study.digest(source),
               quiet=dict(hours=sum(v["reports"] for v in normal)/108000,angles=sum(v["alarms"] for v in normal),
                          magnitudes=sum(v["magnitudes_alarms"] for v in normal)))
    if (RESULT/"scores.json").exists():
        assert out==study.read(RESULT/"scores.json")
    else:
        shutil.copyfile(source,RESULT/"truth.json")
        study.save(RESULT/"scores.json",out)
    print(out["totals"],out["sources"].get("BUS31"),out["quiet"],flush=True)


if __name__=="__main__":
    cli = argparse.ArgumentParser()
    cli.add_argument("stage",choices=("freeze","verify","predict","score","replay"))
    a=cli.parse_args()
    {"freeze":freeze,"verify":verify_freeze,"predict":predict,"score":score,"replay":replay}[a.stage]()

"""Record the development choice, immutable weights and predeclared blind design."""
from robust import TMP, RESULT, HERE, CONDITIONS, study
from stress_plan import frozen
from pathlib import Path
import shutil
import sys

CANDIDATES=("local","joint","history_local","history_joint","adaptive","odds")


def rank(candidate):
    rows=list(candidate["scenarios"].values())
    worst_false=max(v["false"] for v in rows)
    return (worst_false<=1,-max(worst_false-1,0),min(v["exact"] for v in rows),
            min(v["bus31"] for v in rows),-sum(v["false"] for v in rows),
            sum(v["exact"] for v in rows),candidate["tau"])


def freeze():
    if (RESULT/"inputs.json").exists() or (TMP/"pmu").exists() or (RESULT/"freeze.json").exists():
        raise FileExistsError("Weights must be sealed before blind generation")
    all_options=[v for name in CANDIDATES for v in study.read(TMP/(name+"_paired_selection.json"))]
    winner=max(all_options,key=rank)
    if winner["name"]=="adaptive" and winner["tau"]>1e6:
        winner["weak_disabled"]=True
    chosen=winner["name"]
    components=["local","history_joint"] if chosen in ("odds","adaptive") else [chosen]
    if winner.get("weak_disabled"):
        components=["local"]
    files=components+["rocket"]+(["odds"] if chosen=="odds" else [])
    for stem in files:
        shutil.copyfile(TMP/(stem+".joblib"),RESULT/(stem+".joblib"))
    for src,dest in (("rocket_calibration.json","rocket_calibration.json"),("hydra_fit.json","hydra_fit.json")):
        shutil.copyfile(TMP/src,RESULT/dest)
    study.save(RESULT/"final_selection.json",dict(candidates=all_options,winner=winner,
               positives=240,controls=240,bus31=19))
    # weights selected on earlier cohorts; every prospective observation is generated later.
    prior=frozen.verify_freeze()
    weights={p.name:study.digest(p) for p in sorted(RESULT.iterdir()) if p.is_file()}
    sources={p.name:study.digest(p) for p in sorted(HERE.iterdir())
             if (p.suffix==".py" and p.name!="score_final.py") or p.name=="PROTOCOL.md"}
    study.save(RESULT/"freeze.json",dict(winner=winner,physical_components=components,
        rocket_tau=study.read(TMP/"rocket_calibration.json")["tau"],weights=weights,sources=sources,
        upstream=study.digest(frozen.RESULT/"freeze.json"),scenarios={k:vars(v) for k,v in CONDITIONS.items()},
        catalog_seed=64971191,bus31_seed=82036117,prior_angle_threshold=prior["threshold"]))
    print(chosen,winner["tau"],flush=True)


def verify():
    f=study.read(RESULT/"freeze.json")
    for folder,field in ((HERE,"sources"),(RESULT,"weights")):
        for k,v in f[field].items():
            assert study.digest(folder/k)==v,k
    assert f["upstream"]==study.digest(frozen.RESULT/"freeze.json")


if __name__=="__main__":
    (freeze if sys.argv[1]=="freeze" else verify)()

"""Verify the blind scorecard from versioned decisions, scope and labels without the simulator."""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/"graph_recursive"))
from evaluate import evaluate


def read(name):
    return json.loads((HERE/name).read_text(encoding="utf8"))


def check_hash(name,expected):
    if hashlib.sha256((HERE/name).read_bytes().replace(b"\r\n",b"\n")).hexdigest()!=expected:
        raise ValueError(f"Changed {name}")


def audit():
    seal = read("seal.json")
    check_hash("predictions.json",seal["predictions"])
    check_hash("freeze.json",seal["freeze"])
    check_hash("test_manifest.json",seal["manifest"])
    check_hash("test_truth.json",read("test_manifest.json")["truth"])
    check_hash("development.json",read("freeze.json")["development"])
    y,pred,report = read("test_truth.json"),read("predictions.json"),read("scores.json")
    primary = read("../operating/seal.json")
    check_hash("../operating/predictions.json",primary["predictions"])
    check_hash("../operating/freeze.json",primary["primary"])
    check_hash("test_manifest.json",primary["manifest"])
    check_hash("freeze.json",read("../operating/freeze.json")["base"])
    pred["graph_primary"] = read("../operating/predictions.json")
    report["graph_primary"] = read("../operating/scores.json")
    held = {e["source"] for row in y for e in row}
    assert held==set(read("freeze.json")["held"])
    for manifest in ("train_manifest.json","dev_manifest.json","tree_fit.json"):
        sites = read(manifest)
        pools = sites.get("sites",sites.get("labels_by_family"))
        if held & set().union(*pools.values()):
            raise ValueError(f"Source labels overlap in {manifest}")
    for name,alerts in pred.items():
        scores = evaluate(y,alerts)
        if any(scores[k]!=report[name][k] for k in scores):
            raise ValueError(f"Cannot reproduce {name}")
        site = second = nsecond = 0
        for row,actions in zip(y,alerts,strict=True):
            for pos,e in enumerate(row):
                # The trial guarantees strictly disjoint 45-frame scoring deadlines.
                if pos and row[pos-1]["onset"]+45>=e["onset"]:
                    raise ValueError("Overlapping scoring windows")
                a = next((a for a in actions if 0<=a["detected"]-e["onset"]<=45),None)
                correct = bool(a and a["published"] is not None and a["published"]<=e["onset"]+45
                               and a["source"]==e["source"])
                site+=correct
                nsecond+=pos==1
                second+=bool(pos==1 and correct and a["code"]==e["code"])
        if site!=report[name]["exact_site"] or [second,nsecond]!=report[name]["second_joint"]:
            raise ValueError("Cannot reproduce location or second events")
        print(name, f"F1={scores['macro_f1']:.5f}, site={site}/{scores['events']}, "
                    f"joint={scores['joint']}, extras={scores['extras']}, quiet={scores['quiet_extras']}")


if __name__=="__main__":
    audit()

"""Paths, split and integrity checks for the four-family blind trial."""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = ROOT / "tmp/graph_intervention"
RESULT = HERE / "results"
GRAPH = HERE.parent / "graph_recursive"
SUP = HERE.parent / "supervised_stream"
for directory in (GRAPH, SUP):
    sys.path.insert(0, str(directory))

HELD = set("BUS6 BUS14 BUS16 BUS21 BUS24 BUS27 BUS32 BUS35 BUS38 LINE1-39 LINE10-11 LINE11-12 LINE16-24 LINE21-22 LINE26-29 LINE5-6 LINE7-8".split())
FROZEN_TREES = SUP / "successor/model.joblib"
REFIT = DATA / "trees_refit.joblib"
MODEL = HERE / "model.npz"
FREEZE = RESULT / "freeze.json"


def sha(path):
    with path.open("rb") as file:
        if path.suffix in (".py", ".json", ".md"):
            return hashlib.sha256(file.read().replace(b"\r\n", b"\n")).hexdigest()
        return hashlib.file_digest(file, "sha256").hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf8"))


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+"\n", encoding="utf8")


def artifacts():
    names = [*HERE.glob("*.py"), HERE/"PROTOCOL.md", MODEL, HERE/"discrepancy.npz", GRAPH/"model.npz", GRAPH/"physical.py",
             GRAPH/"estimator.py", GRAPH/"evaluate.py", GRAPH/"study.py", SUP/"plant.py",
             SUP/"larger.py", SUP/"learner.py", SUP/"online.py", FROZEN_TREES, REFIT,
             RESULT/"tree_fit.json", RESULT/"train_manifest.json", RESULT/"dev_manifest.json",
             RESULT/"calibration.json", DATA/"bank/inputs.json",
             HERE.parent/"branch_current_trial/run.py", HERE.parent/"history_conditioning/dynamics.py"]
    return {p.relative_to(ROOT).as_posix():sha(p) for p in names}


def verify():
    config = load(FREEZE)
    if config["files"] != artifacts():
        raise ValueError("Frozen inputs or code changed")
    return config

from pathlib import Path
import hashlib
import json
import os
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = Path(os.environ.get("P07_SCIENCE_ARCHIVE", "U:/academic/SGSMA26-Physics-Informed-AD"))
CAMPAIGN = ARCHIVE / "experiments/PAPER_RECOVERY_C03"
RUN = CAMPAIGN / "run"
TMP = ROOT / "tmp/second_family"
RESULT = HERE / "results"
FIELDS = (
    "voltage_magnitude",
    "voltage_angle",
    "current_magnitude",
    "current_angle",
    "frequency",
    "rocof",
)


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save(path, value):
    path.parent.mkdir(exist_ok=True, parents=True)
    path.write_bytes((json.dumps(value, indent=2, allow_nan=False) + "\n").encode())


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        if path.suffix in (".py", ".md", ".json"):
            h.update(f.read().replace(b"\r\n", b"\n"))
        else:
            return hashlib.file_digest(f, "sha256").hexdigest()
    return h.hexdigest()


def archive_imports():
    os.environ["P07_SCIENCE_ARCHIVE"] = str(ARCHIVE)
    sys.path.insert(0, str(CAMPAIGN))
    import common

    common.PAPER = ROOT

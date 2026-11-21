"""Preserve and replay the exact 480 anonymous PMU inputs without the simulator."""
from hashlib import sha256
from io import BytesIO
from zipfile import ZipFile, ZIP_STORED
import sys

from cohort import TMP
from run import RESULT, infer, models, verify
import study
import numpy as np

ARCHIVE = RESULT/"blind_pmus.zip"


def pack():
    manifest = study.read(TMP/"test_manifest.json")
    assert len(manifest["hashes"])==480
    with ZipFile(ARCHIVE, "x", compression=ZIP_STORED) as archive:
        for key, expected in sorted(manifest["hashes"].items()):
            source = TMP/"test"/(key+".npz")
            assert study.digest(source)==expected
            archive.write(source, arcname=source.name)


def replay():
    f = verify()
    estimators = models()
    pred = study.read(RESULT/"predictions.json")
    manifest = study.read(RESULT/"test_manifest.json")
    assert pred["manifest_sha"]==study.digest(RESULT/"test_manifest.json")
    assert pred["freeze_sha"]==study.digest(RESULT/"freeze.json")
    assert pred["calls"].keys()==manifest["hashes"].keys()
    with ZipFile(ARCHIVE) as archive:
        assert len(archive.namelist())==len(set(archive.namelist()))==480
        for key, expected in sorted(manifest["hashes"].items()):
            raw = archive.read(key+".npz")
            assert sha256(raw).hexdigest()==expected
            with np.load(BytesIO(raw),allow_pickle=False) as z:
                call = infer(z["y"], int(z["clearance"]), *estimators, f)
            assert call==pred["calls"][key], key
    print("Reproduced every call for all three arms on all 480 sealed PMU observations.")


if __name__ == "__main__":
    {"pack":pack,"replay":replay}[sys.argv[1]]()

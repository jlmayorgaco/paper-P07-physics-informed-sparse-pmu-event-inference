"""Pin executable inputs and confirm the manuscript bank's archived dependency seals."""

import hashlib
import sys
from shared import ARCHIVE, CAMPAIGN, HERE, RESULT, ROOT, RUN, digest, read, save


def raw(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def files():
    local = [
        *HERE.glob("*.py"),
        HERE / "PROTOCOL.md",
        HERE / "cnn.pt",
        RESULT / "training.json",
        ROOT / "experiments/history_conditioning/dynamics.py",
    ]
    archive = [CAMPAIGN / (k + ".py") for k in ("common", "worker", "simulate", "plant2", "design")]
    archive.extend(
        RUN / (k + ".json")
        for k in (
            "METHOD_FREEZE",
            "DEPENDENCIES",
            "EXECUTION_FREEZE",
            "CAL_SELECTION",
            "TEST_P2_SEAL",
            "CAL_PREDICTIONS_SEAL",
            "OBSERVATIONS_P2_TEST",
            "OBSERVATIONS_F01_CAL",
        )
    )
    for file in (
        "noise.py",
        "pmu_operator.py",
        "terminal_mapping.csv",
        "reporting_config.json",
        "stochastic_model.json",
    ):
        archive.append(ARCHIVE / "SIM0001_JuliaPD_F01/runtime/reference" / file)
    archive.extend(
        [
            ARCHIVE / "data/topology/ieee39/branches_physical.csv",
            ARCHIVE / "experiments/PAPER_ALLEVENTS_V1/physics/network.py",
        ]
    )
    return dict(
        project={p.relative_to(ROOT).as_posix(): digest(p) for p in local},
        science={p.relative_to(ARCHIVE).as_posix(): raw(p) for p in archive},
    )


def historical_bank():
    for file in (
        "METHOD_FREEZE",
        "CAL_SELECTION",
        "EXECUTION_FREEZE",
        "DEPENDENCIES",
        "TEST_P2_SEAL",
        "CAL_PREDICTIONS_SEAL",
    ):
        archived = RUN / (file + ".json")
        local = ROOT / "generated/frozen/recovery_c03" / archived.name
        if local.is_file():
            assert read(archived) == read(local), file
    assert read(RUN / "METHOD_FREEZE.json")["selection"] == raw(RUN / "CAL_SELECTION.json")
    deps = read(RUN / "DEPENDENCIES.json")
    for rel, h in deps.items():
        if rel.startswith(("runtime/", "frozen_R11/observer/", "s01/")):
            assert raw(RUN / "dependencies" / rel) == h, rel


def verify():
    assert files() == read(RESULT / "freeze.json")


if __name__ == "__main__":
    if sys.argv[1] == "register":
        if (RESULT / "freeze.json").exists() or (RESULT / "observations.json").exists():
            raise FileExistsError("Experiment already frozen")
        historical_bank()
        save(RESULT / "freeze.json", files())
    verify()

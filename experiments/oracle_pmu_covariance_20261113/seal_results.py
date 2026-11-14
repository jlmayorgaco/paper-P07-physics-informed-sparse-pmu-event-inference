"""Export compact, hash-traceable results after both partitions complete."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN = HERE.parents[1]/"build/oracle_pmu_covariance_20261113"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    cfg = json.loads((HERE/"protocol.json").read_text())
    frozen = json.loads((HERE/"EXECUTION_FREEZE.json").read_text())
    for name, expected in frozen.items():
        assert digest(HERE/name) == expected
    calibration = json.loads((RUN/"CAL_LOCK.json").read_text())
    test = json.loads((RUN/"TEST_RESULTS.json").read_text())
    hashes = {}
    for split, groups in cfg["split"].items():
        for kind, ids in groups.items():
            for record in ids:
                for pct in cfg["sigma_percent"]:
                    for arm in cfg["arms"]:
                        path = RUN/split/f"{record}_{pct:g}_{arm}.json"
                        row = json.loads(path.read_text())
                        assert (row["record"],row["arm"],row["split"],row["kind"],row["sigma_percent"]) == (
                            record,arm,split,kind,pct)
                        assert row["riccati_residual"] < 1e-6
                        hashes[path.relative_to(RUN).as_posix()] = digest(path)
    for key, cal in calibration.items():
        assert test["arms"][key]["threshold"] == cal["threshold"]
        if cal["threshold"] is not None:
            assert cal["far"] <= cfg["budget_per_hour"]
    paths = ["CAL_LOCK.json", "TEST_RESULTS.json"]
    hashes.update({name:digest(RUN/name) for name in paths})
    results = dict(calibration=calibration, test=test, files=hashes, execution=frozen)
    (HERE/"RESULTS.json").write_text(json.dumps(results, indent=2, allow_nan=False)+"\n")


if __name__ == "__main__":
    main()

"""Render audited CAL/TEST totals into the supplementary comparison table."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    record = json.loads((HERE/"RESULTS.json").read_text())
    for name, expected in record["execution"].items():
        assert hashlib.sha256((HERE/name).read_bytes()).hexdigest() == expected, name
    labels = {"family": "Family scale", "shrinkage": "Shrinkage",
              "structured": "Structured", "oracle": "Oracle"}
    rows = []
    for key, outcome in record["test"]["arms"].items():
        sigma, arm = key.split("_")
        name = labels[arm]
        if outcome["threshold"] is None:
            rows.append(f"{sigma} & {name} & \\multicolumn{{4}}{{c}}{{No feasible CAL threshold}} " + r"\\")
            continue
        rows.append(" & ".join((sigma, name,
                                f'{outcome["load_hits"]}/{outcome["loads"]}',
                                f'{outcome["line_hits"]}/{outcome["lines"]}',
                                str(outcome["extras"]),
                                str(outcome["normal_count"]))) + r" \\")
    (ROOT/"tables/generated/oracle_pmu_covariance_rows.tex").write_text("\n".join(rows)+"\n")


if __name__ == "__main__":
    main()

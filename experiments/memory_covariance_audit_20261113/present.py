"""Regenerate the manuscript macros from the audited outputs."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
for name, expected in json.loads((HERE/"RESULTS_SEAL.json").read_text()).items():
    assert hashlib.sha256((HERE/name).read_bytes()).hexdigest() == expected, name

summary = json.loads((HERE/"toy_reproduced.json").read_text())
nominal = next(row for row in summary["results"] if row["scenario"] == "nominal_colored")
values = {}
for name, arm in (("Mean","mean_only"), ("Moments","moment_gaussian"), ("Mixture","unlabeled_mixture")):
    values["Mem"+name] = 100*nominal["methods"][arm]["event_source_coverage"]
for row in json.loads((HERE/"covariance_results.json").read_text()):
    if row["local_variance"] == 1 and row["prefix"] == 300:
        key = "IID" if row["ar"] == 0 else "AR"
        for name, arm in (("Scale","scaled_nominal"), ("Sample","sample"), ("Shrink","shrinkage")):
            values["Cov"+key+name] = row["arms"][arm]["median_kl"]
target = HERE.parents[1]/"generated/memory_covariance_macros.tex"
target.write_text("".join(f"\\newcommand{{\\{key}}}{{{value:.3g}}}\n" for key,value in values.items()))

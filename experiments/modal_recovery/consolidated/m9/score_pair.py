"""Seal and score the paired June-versus-frozen-M9 spatial264 predictions."""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import platform
import sys

import numpy
import pandas
import sklearn
from sklearn.metrics import confusion_matrix, f1_score


REPO = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
COHORT = REPO / "tmp/spatial264"
SUCCESSOR = REPO / "experiments/competition_spatial_264"
SUBMISSION = REPO / "tmp/competition_zip_verified"
ARCHIVE = REPO / "tmp/competition_original.zip"
CLASSES = range(9)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def json_file(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def cohort_fingerprint() -> tuple[str, int, int]:
    files = []
    for split in ("primary", "quiet"):
        root = COHORT / split
        files.extend(root.rglob("*.csv"))
        files.extend((root / "truth.json", root / "dynamic_admission.json"))
    h = hashlib.sha256()
    total_bytes = 0
    for path in sorted(files, key=lambda p: p.relative_to(COHORT).as_posix()):
        relative = path.relative_to(COHORT).as_posix().encode("utf-8")
        content_hash = sha256(path)
        size = path.stat().st_size
        total_bytes += size
        h.update(len(relative).to_bytes(4, "big"))
        h.update(relative)
        h.update(size.to_bytes(8, "big"))
        h.update(bytes.fromhex(content_hash))
    return h.hexdigest(), len(files), total_bytes


def score_arm(predictions, truth, quiet_ids):
    ids = sorted(truth)
    labels = [truth[case]["code"] for case in ids]
    called = [predictions[case][0] for case in ids]
    positives = [case for case in ids if truth[case]["code"] != 0]
    primary_quiet = [case for case in ids if truth[case]["code"] == 0]
    total_quiet = primary_quiet + list(quiet_ids)
    return {
        "macro_f1": float(f1_score(labels, called, labels=list(CLASSES),
                                   average="macro", zero_division=0)),
        "exact_family": sum(a == b for a, b in zip(labels, called)),
        "primary_windows": len(ids),
        "positive_windows": len(positives),
        "exact_source_positive": sum(predictions[i][1] == truth[i]["source"]
                                      for i in positives),
        "exact_source_denominator": len(positives),
        "exact_family_and_source_positive": sum(
            predictions[i] == [truth[i]["code"], truth[i]["source"]]
            for i in positives),
        "primary_quiet_false_alarms": sum(predictions[i][0] != 0 for i in primary_quiet),
        "primary_quiet_windows": len(primary_quiet),
        "added_quiet_false_alarms": sum(predictions[i][0] != 0 for i in quiet_ids),
        "added_quiet_windows": len(quiet_ids),
        "total_quiet_false_alarms": sum(predictions[i][0] != 0 for i in total_quiet),
        "total_quiet_windows": len(total_quiet),
        "confusion_0_to_8": confusion_matrix(labels, called,
                                               labels=list(CLASSES)).tolist(),
    }


def main() -> None:
    original = json_file(HERE / "june_predictions.json")
    successor_file = SUCCESSOR / "predictions.json"
    successor_digest = sha256(successor_file)
    if successor_digest != json_file(SUCCESSOR / "seal.json"):
        raise SystemExit("Frozen spatial264 successor predictions fail their saved seal")
    successor_raw = json_file(successor_file)
    primary_truth = json_file(COHORT / "primary/truth.json")
    added_truth = json_file(COHORT / "quiet/truth.json")
    if Counter(row["code"] for row in primary_truth.values()) != {c: 24 for c in CLASSES}:
        raise SystemExit("Primary cohort is not the expected balanced 216-record spatial264 set")
    if len(added_truth) != 48 or any(row["code"] != 0 for row in added_truth.values()):
        raise SystemExit("Added quiet cohort is not the expected 48 all-quiet records")
    if set(primary_truth) & set(added_truth):
        raise SystemExit("Primary and added quiet case IDs overlap")
    if set(original) != set(primary_truth) | set(added_truth):
        raise SystemExit("June predictions do not cover exactly the spatial264 cohort")
    if set(successor_raw) != set(original):
        raise SystemExit("Frozen successor predictions do not cover exactly the same cases")
    if any("response" not in row for row in successor_raw.values()):
        raise SystemExit("Frozen spatial264 artifact does not contain response decisions")

    successor = {case: row["response"] for case, row in successor_raw.items()}
    predictions = {
        case: {"june_original": original[case], "m9_response_successor": successor[case]}
        for case in sorted(original)
    }
    pred_path = HERE / "paired_predictions.json"
    pred_path.write_text(json.dumps(predictions, sort_keys=True,
                                    separators=(",", ":")) + "\n", encoding="utf-8")
    prediction_digest = sha256(pred_path)
    (HERE / "paired_predictions.sha256").write_text(
        prediction_digest + "  paired_predictions.json\n", encoding="ascii")

    truth = primary_truth
    quiet_ids = list(added_truth)
    june_all = {**original}
    successor_all = {**successor}
    cohort_hash, cohort_files, cohort_bytes = cohort_fingerprint()
    results = {
        "scope": "retrospective paired evaluation on the original released spatial264 cohort",
        "methods": {
            "june_original": score_arm(june_all, truth, quiet_ids),
            "m9_response_successor": score_arm(successor_all, truth, quiet_ids),
        },
        "provenance": {
            "python": platform.python_version(),
            "python_executable": sys.executable,
            "numpy": numpy.__version__,
            "pandas": pandas.__version__,
            "scikit_learn_runtime": sklearn.__version__,
            "scikit_learn_serialized_estimators": "1.7.2 (as reported by sklearn load warnings)",
            "cohort_root": "tmp/spatial264",
            "primary_records": len(primary_truth),
            "added_quiet_records": len(added_truth),
            "positive_primary_records": sum(r["code"] != 0 for r in primary_truth.values()),
            "cohort_file_count_including_truth_and_admission": cohort_files,
            "cohort_bytes_including_truth_and_admission": cohort_bytes,
            "cohort_sha256": cohort_hash,
            "primary_truth_sha256": sha256(COHORT / "primary/truth.json"),
            "added_quiet_truth_sha256": sha256(COHORT / "quiet/truth.json"),
            "june_submission_archive_sha256": sha256(ARCHIVE),
            "june_extracted_model_sha256": sha256(
                SUBMISSION / "models/classifiers/physical_event_classifier.joblib"),
            "june_predictions_sha256": sha256(HERE / "june_predictions.json"),
            "successor_predictions_sha256": successor_digest,
            "successor_saved_seal": json_file(SUCCESSOR / "seal.json"),
            "successor_bank_sha256": sha256(REPO / "experiments/competition_response_156/bank.json"),
            "successor_spatial_model_sha256": sha256(SUCCESSOR / "spatial.json"),
            "wrapper_sha256": sha256(REPO / "scripts/competition_held_locations.py"),
            "response_wrapper_sha256": sha256(REPO / "scripts/competition_spatial_contrast.py"),
            "response_bank_code_sha256": sha256(REPO / "scripts/competition_response_bank.py"),
            "official_june_model_code_sha256": sha256(
                SUBMISSION / "src/models/hybrid_submission.py"),
            "paired_predictions_sha256": prediction_digest,
        },
    }
    (HERE / "results.json").write_text(json.dumps(results, indent=2) + "\n",
                                        encoding="utf-8")
    write_report(results)


def write_report(results) -> None:
    june = results["methods"]["june_original"]
    successor = results["methods"]["m9_response_successor"]
    p = results["provenance"]
    report = f"""# June ExtraTrees vs frozen M9 response successor

## Result

Retrospective paired evaluation on exactly the released `tmp/spatial264` records: 216 primary records (24 per class, 192 positive) and 48 added quiet records. Both arms receive the same opaque case IDs and source CSVs. Each decision uses the final 30-second window after the 60-second quiet prefix. No traces were generated and no model was refit.

| Metric | June original | Frozen M9 response successor |
|---|---:|---:|
| Nine-class macro-F1 | {june['macro_f1']:.4f} | {successor['macro_f1']:.4f} |
| Exact family | {june['exact_family']}/216 | {successor['exact_family']}/216 |
| Exact source on positive records | {june['exact_source_positive']}/{june['exact_source_denominator']} | {successor['exact_source_positive']}/{successor['exact_source_denominator']} |
| Exact family and source on positives | {june['exact_family_and_source_positive']}/192 | {successor['exact_family_and_source_positive']}/192 |
| False alarms among primary class-0 windows | {june['primary_quiet_false_alarms']}/{june['primary_quiet_windows']} | {successor['primary_quiet_false_alarms']}/{successor['primary_quiet_windows']} |
| False alarms among 48 added quiet windows | {june['added_quiet_false_alarms']}/{june['added_quiet_windows']} | {successor['added_quiet_false_alarms']}/{successor['added_quiet_windows']} |
| False alarms across all quiet windows | {june['total_quiet_false_alarms']}/{june['total_quiet_windows']} | {successor['total_quiet_false_alarms']}/{successor['total_quiet_windows']} |

The denominator for exact source includes every positive primary record, including family misses. The quiet total combines the 24 class-0 primary records and 48 added quiet records.

## Reproduction

From the repository root, using the verified extracted June submission and the already sealed successor predictions:

```powershell
python experiments/modal_recovery/consolidated/m9/predict_june.py --workers 4
python experiments/modal_recovery/consolidated/m9/score_pair.py
```

`predict_june.py` calls the June model through the same API and final-window feature path used by `scripts/competition_held_locations.py`; model code and weights are loaded from `tmp/competition_zip_verified`. `score_pair.py` checks the saved successor prediction seal, validates exact case-set equality and cohort balance, then writes opaque paired predictions, their SHA-256, `results.json`, and this report.

The frozen successor arm is the saved `response` decision from `experiments/competition_spatial_264/predictions.json`; its response bank and spatial localizer were frozen before this retrospective scoring. No alternate method was tested. This remains an M9 cohort result, not an official hidden competition score.

## Provenance

- Python: `{p['python']}` (`{p['python_executable']}`)
- Runtime packages: NumPy `{p['numpy']}`, pandas `{p['pandas']}`, scikit-learn `{p['scikit_learn_runtime']}`
- Compatibility note: the June joblib estimators report serialization under scikit-learn `{p['scikit_learn_serialized_estimators'].split(' ')[0]}`; the installed scikit-learn `{p['scikit_learn_runtime']}` emitted version-mismatch warnings during model loading. This runtime meets the ZIP's unpinned `scikit-learn>=1.3` requirement, but the warning is a reproducibility limitation.
- Cohort: `{p['cohort_root']}`, {p['cohort_file_count_including_truth_and_admission']} source/truth/admission files, {p['cohort_bytes_including_truth_and_admission']:,} bytes
- Cohort SHA-256: `{p['cohort_sha256']}`
- June ZIP SHA-256: `{p['june_submission_archive_sha256']}`
- June extracted classifier SHA-256: `{p['june_extracted_model_sha256']}`
- June decisions SHA-256: `{p['june_predictions_sha256']}`
- Frozen successor decisions SHA-256: `{p['successor_predictions_sha256']}`
- Paired opaque predictions SHA-256: `{p['paired_predictions_sha256']}`

Full input, code, model, prediction, and split-truth hashes are recorded in `results.json`.
"""
    (HERE / "README.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()

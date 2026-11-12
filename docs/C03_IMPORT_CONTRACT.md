# C03 sealed-result import contract

`python scripts/import_c03_results.py` defaults to a read-only check. It may report `PENDING` with exit code 2 while the campaign or single-use evaluation is incomplete. This state causes no writes. `--import` is an explicit local import operation; it is accepted only after the complete result lock and all validation checks pass. It never edits the article or inserts anything into `main.tex`. Root/coordinator review is required before any import.

## Source and evidence boundary

The default source is the sibling scientific repository at
`SGSMA26-Physics-Informed-AD/experiments/PAPER_RECOVERY_C03/run`; use
`--source-run PATH` only for an explicitly selected completed run. The importer
reads source code/schema and, after closure, the JSON result, evaluation lock,
CAL selection, execution/method/scenario seals, and prediction seal manifests.
It does not read private TEST truth. In `--check`, it does not open prediction
files; it verifies the sealed manifest chain and records the hashes that the
later import must check. In `--import`, after `COMPLETE_SINGLE_USE` is verified,
it checks every file digest named by the two per-plant prediction manifests.
Raw predictions and truth are never copied into P07.

The chain must establish:

1. Frozen scenario state, fixed execution source hashes, dependency/scenario/
   plant-2/runtime seals, and no active `execution.lock`.
2. `METHOD_FREEZE.json` hashes matching execution freeze, CAL selection, and
   detectability freeze, including the assertion that TEST observations were
   not accessed before freeze.
3. Each plant prediction seal is named and hashed by
   `TEST_PREDICTIONS_SEAL.json`, which in turn names the matching method freeze.
4. The evaluation lock is `COMPLETE_SINGLE_USE`; its result SHA-256 matches
   `TEST_RESULTS.json`, and its prediction seal hash matches the combined seal.
5. Each prediction file digest matches its per-plant manifest before import.

Any mismatch is `INVALID` with exit code 1. It is never repaired, re-scored,
or silently omitted by the importer.

## Denominators and summary rules

For each plant and each arm (history, carry, reset), retain all 36 event and
36 normal parents, including unavailable/rejected parents. Arms must have the
same ordered paired parent IDs. Each event parent must retain six scored
interventions, four of which are the prespecified primary short-gap cases:
144 primary and 216 total event records per plant. Across both plants the
checks expect 288 primary and 432 total event rows. The importer fails closed
if these counts, pairings, explicit availability fields, or per-parent exposure
fields are absent. It recomputes timely counts, extras, normal alarms, event
and normal exposure, and the event extra rate from every arm's rows, then
compares them with the sealed aggregate.

The imported CAL selection reports feasibility and selected threshold per
arm. CAL exposure and planned CAL exposure remain separate fields. For TEST,
normal alarms, actual monitored normal hours, planned exposure, and the
one-sided Poisson upper 95% bound remain distinct. Event-record extras and
extra-alarm rates are not normal false-alarm rates. Unavailable parents remain
in the coverage denominator and contribute zero realized exposure, never an
assumed zero-alarm hour.
The generated table prints each arm's CAL feasibility as PASS/FAIL; a FAIL arm
must not be described as meeting the common calibration target. Normal-hour
exposures print actual/planned hours to two decimal places.

Paired contrasts are taken only from the sealed result. Coverage differences
are stored as fractions and emitted in percentage points (multiply by 100);
extra-rate differences retain their source units. The generated summary does
not recalculate outcomes or bootstrap intervals. The result's decision is
preserved, including negative/stop outcomes, and submission readiness remains
false.

## Imported bundle and regeneration

After successful validation, a single immutable compact snapshot is created at
`generated/frozen/recovery_c03/`. It contains the sealed result, evaluation
lock, result/prediction seal chain, selected thresholds, method/execution/
scenario/detectability seals, an import validation record, and derived TeX.
It excludes TEST truth and raw predictions. Existing destination files cause a
hard failure; no prior snapshot is overwritten.

The importer writes `tables/generated/recovery_c03.tex` and
`generated/recovery_c03_macros.tex` from the validated result. It does not add
an `\\input` to `main.tex`. After import, `--verify-bundle` verifies every
snapshot file hash and regenerates the table/macros from the compact snapshot,
then compares those bytes with both the snapshot copies and workspace outputs.
This verification requires no access to the C03 run directory.

## Operator commands

- `python scripts/import_c03_results.py --check` — default, read-only; `PENDING`
  exits 2, a valid closed source exits 0, invalid evidence exits 1.
- `python scripts/import_c03_results.py --source-run PATH --import` — explicit
  import, only after root review of the completed source and validation output.
- `python scripts/import_c03_results.py --verify-bundle` — verify an existing
  compact import and its generated TeX without reading source run artifacts.

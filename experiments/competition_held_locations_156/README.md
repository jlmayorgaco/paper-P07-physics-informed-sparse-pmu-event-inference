# Nine-class test at held-out physical sites

Each of 108 primary records supplies one 30-second decision after 60 seconds of normal startup. There are 12 independent noise/event realizations per class and three held-out physical assets per physical class, with shared M9 templates. Class 0 plus 48 additional normal records supply 60 negative windows (30 minutes). For classes 5 and 7 the target is a PMU on the same fixed installation. Newness refers to the family-specific physical site catalog of the spatial bank. The original submission's own training locations are not known to be disjoint.

The submitted ZIP, the previous spatial hybrid, and the residual hybrid see the same input reports. The latter fits a separate complex admittance per phase and PMU on the quiet prefix, estimates expected local current as Y times measured voltage, and compares normalized current mismatch to the contemporary median across PMUs. It canonicalizes the input angles before the window classifier. This is a local equivalent model. Instrument-current inconsistency alone does not establish a simultaneous physical intervention. The new detector retains the source bank and the native window classifier; the catalog was not expanded with test assets. The shifted-angle check reruns the window pipeline with one turn added to every angle and the original startup admission held fixed.

Protocol and model commit e51ec8e. The initial invariance check compared floating-point arrays bit for bit and stopped at a rounding boundary before predictions were sealed or scored. Commit 67680da replaces that check with a rerun comparing both final outputs; inputs, decision rules and test membership stay fixed.

## Reproduction

Run from the repository root with the archived science repository, the original extracted competition ZIP and an empty work directory. The preparation and inference programs run in separate processes. The prediction stage reads only measurements, frozen models and startup admission. All methods have a family and a source for every record. The score treats silent event windows as errors. Exact source counts all nonnormal records; joint additionally requires the correct family.

    python scripts/prepare_held_locations.py ARCHIVE FRESH_DIR
    python scripts/competition_held_locations.py predict FRESH_DIR --submitted EXTRACTED_ZIP
    python scripts/competition_held_locations.py score FRESH_DIR

For a quick independent recount on the archived predictions, run:

    python scripts/competition_held_locations.py verify experiments/competition_held_locations_156

The provenance manifest records SHA-256 hashes of all 1,248 observation files and both source models. The extracted bundle was compared byte for byte with the original ZIP entries. The results contain raw confusion matrices with true classes on rows and predictions on columns, ordered 0 through 8.

## Sealed result

The residual and spatial hybrids made identical decisions on all 156 records. Each scored 0.990725 macro-F1, 107/108 correct families, 23/96 exact locations and 0/60 false alarms. The submitted classifier scored 0.193266, 32/108, 0/96 and 0/60 respectively. For the residual hybrid, every held-out physical intervention had the correct family (72/72) and the wrong location (0/72). All 23 exact hits were instrument-only events. The residual hybrid gave identical family and location under the shifted angle convention on 156/156 records. Every record failed dynamic-bank startup. The 0.96 localization target failed. This comparison does not evaluate the hidden competition records.

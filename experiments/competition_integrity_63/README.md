# Paired integrity correction on new M9 records

The decision rule and the split were committed in `3bfd03d` before generating the test records. The earlier 27-window pilot served as development data. The test contains seven new noise seeds and onset shifts for each of the nine M9 templates. Each missing-only, composite missing/physical, and single-PMU corruption template visits seven sites other than its development site. Physical intervention templates and network are shared with development.

The successor wraps the submitted ZIP. From each record's quiet first 60 s it estimates the scale of 12-report fluctuations. During the final 30 s it tests for sustained missing measurements or an isolated three-phase voltage magnitude imbalance, checking frequency and voltage changes across PMUs before issuing an integrity-only correction. The decision thresholds were chosen using the development cohort. Methods see the same signals and deadline. The window-level original ZIP path reproduced the archived family and location for all 27 development records. Predictions on the new records were sealed before scoring.

| Method | Nine-class macro-F1 | Correct family | Exact source on positive windows |
|---|---:|---:|---:|
| Original ZIP | 0.2169 | 21/63 | 11/56 |
| ZIP plus integrity correction | 0.4815 | 35/63 | 25/56 |

The successor fixed seven missing-only and seven corruption decisions, including their locations, and preserved the other 49 predictions. All generation, load and line windows were still classified as normal. The frozen dynamic bank's separate startup check rejected the voltage-angle noise scale in 63/63 records. The measured increment belongs to the integrity correction. Generator templates and the balanced class distribution limit generalization.

To reproduce, run scripts/competition_integrity_successor.py with stages prepare, predict, score using a fresh directory, the scientific archive and the extracted original ZIP identified in the pilot provenance. Run scripts/benchmark_competition_windows.py startup against that directory to reproduce the admission audit. Each confusion matrix has truth on rows and predictions on columns, ordered 0 through 8.

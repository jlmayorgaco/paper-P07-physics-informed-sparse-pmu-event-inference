# V1 inference-manifest isolation deviation

V1 is preserved without changing its plan, source, predictions, seals or evaluation.
Its cohort plan included per-record `kind=normal/event` and group-membership
metadata for the overlap audit. The inference process read that plan, although
`extract` and `predict_features` received only the six observation matrices,
timestamps and frozen model; no kind/group field influenced features, votes,
publication or any conditional branch selecting a prediction.

Under the stricter requirement that the inference process not even read such
ground-truth metadata, V1's `truth_read:false` flags are too broad. They should
be understood as no truth consumed by prediction, not as a metadata-isolated
process. This is a documented isolation deviation, not hidden by overwriting V1.

The authorized audit replay is in `../ml_h04_v2/`, with
`protocol/ML_H04_V2_PLAN.json`. Its inference roster contains only record IDs,
observation paths/hashes, report counts and durations. Per-record kind and group
are first inspected in its separate post-seal evaluator. The same frozen model,
feature extraction and publication code are used without tuning or retraining.
All 12 records have exactly equal output arrays and emitted event objects in
V1 and V2; `../ml_h04_v2/EVALUATION.json` records the individual parity checks.
Use V2 for integration. It is an audit replay, not an additional independent
experiment.

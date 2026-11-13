# Corrected OFF-operator diagnostic

Replaces `../adaptive_innovation_20261113`, whose OFF index was wrong. All old
sealed files are retained there and its README marks the findings withdrawn.
The correct ordering, from the archived builder, is stay, ON-end, OFF-end,
ON-mid, OFF-mid. OFF at report end is `3+5*cell`, not `4+5*cell`.
This successor changes only that index in both recursions and uses fresh
CAL/TEST/covariance/bootstrap seeds. Settings were fixed before generation;
CAL thresholds were selected before TEST. No tuning follows TEST.

Inherited covariance: 279/360 to 343/360 source identifications, +17.78 pp,
95% paired bootstrap [13.89, 21.94], 10,000 resamples. Onset, amplitude and
recovery mean are known. This is a correct-model Gaussian fixture, not R11.

Noise learning: all arms identify 20/72 loads. Fixed/continuous/guarded
thresholds are 3/0/3. Normal TEST alarms: 6/8/5 over 5.88 h; extras: 44/50/44
over 1.08 h. Fixed and continuous exceed the one-normal-alarm/hour target
on TEST. No attribution gain or equal achieved FAR is established. The guard
admits 8.34% of monitored normal reports. Continuous minus fixed coverage:
0 pp, paired 95% interval [-8.33, 6.94], bootstrap by 36 event records.
All 36 normal CAL, 36 normal TEST and 36 event TEST records are retained.
No simulation or inference failed.

Audit/regenerate from paper root:
`python scripts/build_adaptive_diagnostic_tables.py`.
The independent auditor checks OFF semantics against the builder ordering,
all saved prediction publications, threshold selection, denominator counts,
hashes and the supplied nominal snapshot. Full reruns require a fresh copy
of this folder and its sibling snapshot folder, with only the original
EXECUTION_FREEZE.json placed in a new run directory; then run `study.py`.
Never replace the historical freeze or overwrite these completed files.

These are nominal innovation-coordinate diagnostics, not nonlinear plant
transfer, physical PMU TVE noise or full history-bank performance. No C03
file is modified or executed. The original source archive is already local.

# P07 closure status

Updated automatically: 2026-11-02T17:28:02-05:00 (America/Bogota).

- **P0:** complete; baseline and protected figure hashes verified.
- **P1:** complete; claim/evidence and reviewer-response registers staged.
- **P2:** complete; restoration, timing and domain summaries generated from authorized/frozen sources as aggregated outputs.
- **P3:** complete; method normalization/replay explanation, measurement contract and bounded claims staged.
- **P5:** complete; editorial pass and source review.
- **P6:** complete for isolated pre-A01 preview: article 18 pp, supplement 16 pp, one-page review brief. References resolve; closure labels/floats occur once; protected figures verified; listed pages visually reviewed.
- **P4:** pending A01. Latest read-only progress is stage=inference, task=34, tasks=72, record=S063, arm=PROFILE_MEMORY. No partial outcomes were interpreted.
- **P7:** pre-A01 review package prepared; final post-A01 integration and publication readiness remain pending.

## Additional bounded metric audit — 2026-11-02

- Read frozen C01 summary/record/event exports and evaluation audit in P07; spot-checked C01 completion marker, per-report score schema, and source prediction records in SCIENCE. Did not inspect A01 partial outputs or alter any experiment/evaluator.
- Added `METRIC_COVERAGE_AND_CLOSURE.md` with file-level evidence and ready/missing/not-applicable decisions for ROC/PR, localization, alarms/exposure, delay/restoration, parent-cluster uncertainty, H0/p-values, and PMU sparsity.
- Recommendation: close on existing frozen endpoints and interval estimates; do not introduce ROC/PR or posthoc p-values without a declared unit/score/null contract. Top-1 is optional and conditional on emitted/matched events; current Top-3 is already supported.
- “90/30” remains undefined in the metric contract; do not infer its meaning. A01 remains the outstanding gate; final integration follows its completion.
- At the user's further direction, added `scripts/derive_c01_metrics.py` and descriptive outputs under `derived_c01/`: report-level F1 by condition, event timely/joint/Top-3 fractions by family-condition, and a two-panel figure. The script reads only tracked frozen C01 exports; it checks per-noise F1 and pooled event-count parity against frozen `SUMMARY.csv`, retains missed-event denominators, availability/abstentions/censor counts, and records zero C01 rejection/failure counts from the frozen audit.
- Added the distinction between physical event/no-event hypotheses and a statistical H0, plus why no p-value is reported and what a future parent-level paired contrast would require. This is a descriptive restatement, not a new test. No paper source or Git history was changed.
- Revised the two-panel figure per visual review: full 0–1.03 axes reveal low ET load coverage; descriptive method names; points only for categorical conditions; PNG plus vector PDF. Script asserts all plotted values are finite and within both axes. Removed the derived record-level CSV; only aggregate outputs remain shareable.

The review PDF/source hashes are in `PRE_A01_PACKAGE_MANIFEST.json`. ZIP excludes `staging/inputs/`, including record/event data and auxiliary checks.

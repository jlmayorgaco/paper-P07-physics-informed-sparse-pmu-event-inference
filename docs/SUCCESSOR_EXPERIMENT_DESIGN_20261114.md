# C03 audit and smallest bank successor

**14 November 2026.** Read-only audit of the imported C03 bundle and the
P07 covariance/memory diagnostics. This document does not alter or reopen
the source campaign, its private truth, or raw TEST predictions.

## Imported evidence audit

`python -B scripts/import_c03_results.py --verify-bundle` returned
`BUNDLE_OK 16 files`; `--check` returned `COMPLETE_VALID`, decision
`HISTORY_ADVANTAGE_F01_ONLY`, with 528 prediction files verified by the
import chain. The sealed result digest is
`00f36cf49996bbdf8865bbfdbf51052c5aecb604c5e066180078bd8a3342ddfc`.
The import retains the intended denominators: 36 event and 36 normal parents
per plant and arm; 216 interventions, including 144 primary short-gap cases;
all arms available. The arms are paired by parent. P2 is the independently
implemented classical model on the IEEE-39 topology; its frozen validation
checks report timing, KCL, state continuity at switching, terminal current
through an open branch, and numerical refinement. No private truth or raw
prediction was opened during this audit.

| Plant | Arm | Primary timely | All timely | Event extras | Early OFF | Orphan OFF | Normal alarms / 5.88 h |
|---|---|---:|---:|---:|---:|---:|---:|
| F01 | History | 144/144 | 216/216 | 1 | 0 | 0 | 0 |
| F01 | Carry | 90/144 | 147/216 | 38 | 2 | 19 | 0 |
| F01 | Reset | 17/144 | 56/216 | 636 | 49 | 608 | 0 |
| P2 | History | 67/144 | 119/216 | 87 | 8 | 73 | 0 |
| P2 | Carry | 65/144 | 123/216 | 132 | 19 | 112 | 0 |
| P2 | Reset | 20/144 | 60/216 | 931 | 57 | 902 | 0 |

The primary history-minus-carry coverage contrast is +37.5 percentage
points (paired 95% interval 25.0 to 49.3) in F01 and +1.4 points (-12.5
to 16.0) in P2. The latter does not support a coverage advantage. The
paired extra-rate differences are -34.3/h (-43.5 to -25.0) and -41.7/h
(-74.1 to -10.2), respectively. Carry-minus-reset coverage is +50.7
points (38.2 to 63.2) in F01 and +31.2 (18.8 to 43.8) in P2, alongside
large extra reductions. The result supports state continuity against reset
in both tested plants, and a history-over-carry gain only in F01. It does
not establish a cross-plant history benefit or isolate history labels from
all procedure differences.

Each arm passed CAL feasibility. Selected thresholds were 6.9068 for
history and carry, 5.2933 for reset; CAL had zero alarms in 5.88 normal
hours per arm. TEST also had zero normal alarms in 5.88 h per arm; the
one-sided Poisson upper 95% bound is 0.51/h. This exposure does not establish
a long-run 1/h guarantee. Event extras are not normal false alarms.

### Stress and unavailable noise replay

At the frozen nominal thresholds, dropout stress has 24 parents and 72
interventions per plant (48 primary short-gap cases). F01: 24/72 timely,
8 extras (22.22/h), zero early/orphan restorations, and 12 normal alarms
over 1.96 h (upper bound 9.92/h). P2: 20/72 timely, 16 extras (44.44/h),
one early and eight orphan restorations, and 12 normal alarms over 1.96 h.
The paired stress-versus-nominal summary uses the same subset of parents;
the extra-rate contrast can be negative even as coverage declines, so both
outcomes must be shown. These stress normal-alarm counts do not meet the
nominal operating point.

The independent-noise stress cohort has zero available parents in both
plants (24 planned parents each), zero realized exposure, and zero runtime.
Read-only inspection of the immutable rejection metadata in the C03 run
found the same prefix-fit failure in every arm: `Noise estimate outside
support: voltage_angle`. This is an estimator support failure triggered by
the configured 0.05% TVE perturbation; it is neither a measured 0/48
coverage outcome nor evidence of robustness. Keep these rows in the planned
denominator and label performance unavailable. Do not widen the bound and
reuse the old TEST scores.

An isolated diagnostic may copy the already generated noisy observation
files into a *new* candidate and replay only the prefix fit with an expanded
support. It must preserve observation hashes and report whether this resolves
the prefix rejection. Because this reuses C03 TEST inputs and changes the
estimator after observing the failure, it is debugging only and cannot
produce confirmatory accuracy, FAR, or paper claims. A performance study
requires fresh independent CAL/TEST parents, support fixed from development
or CAL, and threshold selection redone before TEST inference.

## Existing covariance/memory evidence

The covariance audit in `experiments/memory_covariance_audit_20261113/`
is a 128-replicate statistical covariance diagnostic, not a physical bank
test. Its `toy_reproduced.json` matches the archived design to numerical
precision and nine reproduction checks. `unknown_onset_bridge_20261114/`
uses a synthetic swing graph, four onset candidates and per-arm 5% false
alarms per normal window; on both seeds moment-matched Gaussian improves
over within-component covariance, while mixture-minus-moment changes sign
or includes zero. Neither study uses the P07 plant, real 47-channel output,
normal FAR per hour, or the C03 publisher. They motivate controls but do not
resolve the C03 mechanism.

## Smallest confirmatory bank successor, conditional on a stronger claim

C03 already supports the bounded statement above. No successor is needed
if the manuscript adopts that boundary. If the paper wishes to claim that
an explicit history mixture adds value beyond a Gaussian state carrying
comparable uncertainty, the minimum fair experiment is a new candidate with
three arms:

1. **Nominal shared covariance:** same C03 continuation/reference arm,
   preserving the existing within-component covariance only.
2. **Moment-matched Gaussian:** one Gaussian per compatible future dynamic
   mode; include both within-component state/severity variance and
   between-component spread. Never merge modes with different future
   transition operators into one transition model.
3. **History mixture:** keep the corresponding conditional components and
   weights, with the same represented state and severity moments as arm 2.

Fix identical parent cohorts, admission/search, report clock, likelihood and
severity representation, beam/pruning budget, OFF commitment/publication,
integrity state, and evaluator. Record compression decisions and OFF / next
onset outcomes. CAL must be distinct from TEST; choose all three thresholds
under the same one-normal-alarm-per-hour rule. Use new event and normal
parent IDs and fresh seeds, stratified by source/family and the frozen
0.5--3 s gap design; preserve failed/unavailable parents in the intended
denominator.
Predeclare `history mixture - moment Gaussian` timely correct-source
coverage as the primary paired contrast, with parent-level 95% interval;
extras per event-hour, normal alarms and their exposure bound, detection
delay, early/orphan restorations, calibration feasibility, cost and peak
memory are co-reported. Keep all other outcomes descriptive. Run both F01
and P2 only if retaining a transfer claim; an F01-only test can only support
an F01-scoped mechanism claim.

Use a new successor directory and freeze scenario, code/dependency hashes,
metric, exclusions, thresholds, and CAL selection before TEST. Do not tune
on C03 outcomes. First do a small synthetic and one-record bank parity /
cost gate; do not launch the campaign if the moment projection fails mass,
covariance, or dynamics-mode checks.

### Feasibility and schedule

C03 nominal summaries record roughly 10.2--10.7 thousand accumulated
worker-seconds per plant-arm, peak sampled RSS around 0.40--0.41 GiB, and
six plant-arm combinations. These imply about 17--18 serial wall-hours for
the existing 3-arm, 2-plant TEST inference scope, before setup, CAL retries,
bootstrap and auditing. The three-arm successor on both plants has 432
plant-arm-parent TEST evaluations, plus separate CAL scoring, and should be
budgeted at **at least 24 wall-hours**
to accommodate moment-projection overhead, CAL threshold passes, and
failures; execution depends on available host capacity and is not started
by this design. Peak RSS should remain sub-GiB per serial worker based on
C03, but allow 16 GiB free working storage as the source campaign required.
The main feasibility risk is method engineering and support/calibration
behavior, not raw RAM. A measured one-record timing and CAL pilot must update
the forecast before the full run.

## Submitted-artifact integration

`scripts/build_c03_figures.py` reads only the immutable imported bundle,
checks the TEST result SHA-256 and denominator/contrast consistency, then
builds the coverage/extras/paired-contrast figure. It emits
`generated/c03_extended_macros.tex` and `supplement/c03_results.tex` from
that validated result. `scripts/import_c03_results.py --verify-bundle` and
the figure generator are the reproduction commands for these imported
artifacts. The source campaign, `C03`, and unrelated experiment folders are
not modified.

# C01 metric coverage and bounded closure recommendations

Read-only audit prepared 2026-11-02 for the pre-A01 editorial close. Scope is
the frozen C01 evidence already exported to P07 and a spot-check of sealed
per-report prediction artifacts in the science repository. No C01 evaluator,
threshold, model, cohort, or prediction was changed; no A01 partial outcomes
were inspected or used. This is an audit and a recommendation, not a new
confirmatory analysis.

## Evidence inventory

The tracked P07 snapshot is `generated/frozen/c01_20261029/`; its summary,
record/event tables and evaluation audit agree with the C01 completion contract
(342/342 observed records, 171 physical trajectories, all intended denominators,
predictions sealed before truth, 10,000 paired parent-cluster bootstrap
replicates). The source execution is
`SCIENCE/experiments/PAPER_CONFIRMATORY_C01/run/`; its `COMPLETE.json` records
`COMPLETE_WITH_ALL_INTENDED_DENOMINATORS` and `models_retuned: false`. Its
per-report prediction stores include ExtraTrees `prediction.npz` arrays
`time_s`, `source_label`, `raw_source_label`, and `class_scores` (spot-checked
shape 3601 x 19), R11 event/diagnosis/restoration records with source and top-3
lists, and Chen score traces. These source artifacts are not all included in
the compact P07 frozen export. Availability of a score array alone does not
define a valid ROC/PR endpoint or an equivalent score across methods.

| Metric / question | Existing evidence (exact files) | Coverage | Closure decision |
|---|---|---|---|
| Event-level timely detection and joint attribution | `generated/frozen/c01_20261029/SUMMARY.csv` (`events`, `timely`, `joint`, `top3`, `event_extras`, method/lane/condition/noise); `EVENTS.csv`; `PAIRED_INTERVALS.csv` | **Ready.** Event denominator and strata are present; paired uncertainty uses physical parent as cluster. | Keep as the primary result. State it as coverage of catalog events attributed before OFF under the frozen procedures, not general classification accuracy. Keep method-specific alarm thresholds visible. |
| Report-level confusion and abstention | `generated/frozen/c01_20261029/RECORDS.csv` (`tp`, `fp`, `fn`, `abstentions`, `monitored_reports`); source `run/results/RECORDS.csv` | **Ready at the frozen operating point.** Counts are available by record and method. | Retain counts and fixed-point F1. Do not treat the 30-fps report rows as independent observations for uncertainty. |
| ROC / PR | Sealed per-report score artifacts exist for some C01 models under `SCIENCE/.../run/data/predictions/` (e.g. ExtraTrees `prediction.npz`); the compact P07 export does not contain all report scores. `RECORDS.csv` has only decisions/counts. R11 exports selected event/diagnosis/restoration records, not one score for every report. | **Not a paper-ready endpoint across the four methods.** A ROC/PR curve does not require calibrated scores or the same numerical scale between methods: each curve varies its method's own ranking score. It does require a defined positive sample/interval, aligned truth and scores on the same report/cohort rows, an explicit mask for unavailable/censored rows, and a score per row for every method. `class_scores` availability is not the same as the frozen publisher threshold/persistence decision. Tree votes are uncalibrated; R11 event support is selected at emitted events, not a dense per-report series. | Do not add a four-method ROC/PR figure from the present exports. If developed later, predeclare event-vs-report unit, positive window, row alignment/mask, per-method score and interpolation/aggregation rule, and parent-cluster uncertainty. Label curves as threshold sweeps over method-specific rankings, not publisher operating points or calibrated probabilities. |
| Localization Top-1 / Top-3 | `SUMMARY.csv` has event-level `top3`; `EVENTS.csv` has the Top-3 correctness flag; source prediction JSONs include selected `source` and `top3` lists. `RECORDS.csv` does not provide a Top-1 confusion table. | **Top-3 ready; Top-1 partially derivable** for emitted/matched diagnoses from source prediction artifacts. | Existing Top-3 is adequate for closure. Top-1 can be a clearly conditional descriptor only if the frozen match map is reused exactly; it must count missed/unmatched events separately and must not be framed as a new overall endpoint. Do not infer electrical distance from bus labels alone. |
| Graph-compatible localization error | Event source labels and the protected IEEE-39 topology exist; no frozen C01 metric or export specifies distance, endpoint treatment, or line-edge distance. | **Missing / not applicable to the current claimed result.** | No new graph distance metric. A future metric needs a predeclared topology distance for bus nodes and line edges, plus an explicit definition for exact versus adjacent localization. It is not required to support current Top-3 claims. |
| False alarms per hour / exposure | `generated/frozen/c01_20261029/SUMMARY.csv` includes `event_extras`, `extras_per_event_hour`, `normal_FA`, `normal_FA_hour`, normal available/planned seconds, and Poisson upper bound for zero events. `RECORDS.csv` includes normal exposure/monitoring fields. | **Ready.** Event extras and normal false-alarm exposure are distinct denominators. | Report absolute exposure/rates alongside any relative difference. Keep the caveat that zero alarms yield a process-model upper bound, not proof of zero risk. Do not equate event extras with normal false alarms. |
| Detection / restoration delay and missed closures | `EVENTS.csv` contains onset/OFF truth, alarm/detection/diagnosis times, signed `off_delay_s`, availability and Top-3 flags; `SUMMARY.csv` includes median delays, `false_restorations`, `open_eof`. Independent audit: `docs/editorial_closure/staging/inputs/R2_CHECKS.json`. | **Ready descriptively.** Includes missed alarms and restoration-availability counts, but the median alone hides signed early tails. | Preserve the existing table; label the old “False OFF” count as restorations of unmatched episodes. The already-reviewed signed-delay summary and “no associated restoration” count can clarify tail/censoring without rematching C01. Avoid describing missing restoration as an open event. |
| Monte Carlo / uncertainty unit | `generated/frozen/c01_20261029/EVALUATION_AUDIT.json` (10,000 paired parent-cluster bootstrap resamples); `PAIRED_INTERVALS.csv`; design and denominators in the C01 `PLAN.json`/`FREEZE.json` at the SCIENCE path. | **Ready for paired interval estimates.** These 10,000 draws are resamples of the existing physical parents, not new simulated events or extra independent observations. | Use the frozen parent-cluster intervals for comparative claims. State the number of parents in each lane. Avoid frame-wise or event-wise standard errors and do not describe bootstrap draws as a new Monte Carlo campaign. |
| H0 tests / p-values | No confirmatory p-value table in the frozen C01 summary or audit; the restoration re-read is explicitly descriptive and not a significance test (`R2_CHECKS.json`). | **Not reported; no p-value is required to close the current bounded claims.** Posthoc tests are not intrinsically invalid, but they would be exploratory here because endpoint/contrast selection and multiplicity were not frozen as a confirmatory testing family. | Do not retrofit a confirmatory p-value. If a descriptive test is later useful, state its null, parent-level unit, paired contrast, assumptions (including exchangeability/symmetry if using sign flips), and multiplicity; do not promise or select for a `p<0.05` outcome. Clustering alone does not justify sign flipping. |
| PMU sparsity / placement | Protected unifilar and measurement contract list the evaluated eight PMUs; C01 evaluates the frozen sparse-PMU configuration. Existing observability, sparsity and stress analyses are separate archived evidence, not a C01 sweep of sensor counts/placements. | **Configuration stated; no C01 sparsity-response curve.** | State the exact eight-PMU map and limit inference to it. Do not imply robustness across PMU counts or placements. A new sparsity ablation is outside closure. |

## Explanation and visual close

The main text should show the operational chain already implemented: report and
measurement model → candidate history likelihoods → prior/hazard weighting →
normalization over admitted hypotheses including null → persistence/decision
rules → event association and restoration. Keep the equations aligned with the
actual implementation and point to the detailed supplement. In particular,
distinguish report-level scores, selected event support, and calibrated
probabilities; avoid suggesting a complete unpruned Markov posterior.

Use the existing approved method-phase diagram and event/topology figures. A
small evaluation schematic may label the units and denominators (report rows,
event realizations, normal exposure seconds, physical parent clusters), but it
must not introduce new outcomes. Do not redraw protected Figure 2 or the IEEE-39
single-line. The strict review has already checked the staged equations and
phase diagram; after A01 import, the final active PDFs still need the repository
figure-preservation checks and visual review required by `AGENTS.md`.

## Bounded closure recommendation

1. Close on the frozen C01 endpoints, event-level parent-cluster intervals,
   existing fixed-operating-point report confusion counts, rates/exposure, and
   signed restoration coverage. Do not add ROC/PR or p-values merely to fill a
   checklist.
2. If the final article needs one additional localization number, consider a
   supplementary Top-1 count conditional on emitted/matched alarms only, using
   the sealed prediction JSON and exact existing event match. Keep misses in a
   separate denominator and mark it descriptive/posthoc. This is optional; the
   current Top-3 outcome is already supported.
3. The author's “90/30” clarification refers to the retrospective grouped
   ExtraTrees development study summarized as approximately 70/30: 56% fit,
   14% internal validation and 30% reserved development holdout by connected
   physical groups. It is not 90%/30 fps or a threshold. This study froze a
   distinct SHORT model; C01 instead uses its separately frozen R09
   `ET_REFERENCE` and `ET_CANDIDATE` models. The grouped study is not a clean
   external test and does not validate the C01 ExtraTrees models. See
   `docs/editorial_closure/ML_70_30_PROTOCOL_STATUS.md` for the source audit.
   The 30 reports/s value remains the acquisition rate.
4. No new ML/GNN, training, threshold adjustment, further 70/30 split, bus sweep,
   PMU-placement sweep, RAW0002 read, or second experiment is needed to close
   the bounded article. Resume only after A01 completion/import, then do the
   already planned final integration, PDF visual review, protected-figure
   checks, and readiness update.

## Statistical H0 versus physical hypotheses

The inference model's physical hypotheses (for example, a candidate load or
line event versus the model's physical null/no-event state) are alternatives
scored from the PMU observations at each report. Normal-control exposure and
the model's no-event state concern physical event detection. They are not a
statistical null hypothesis about whether one method has higher average
performance than another. A statistical comparison would instead define, for
example, a parent-level paired
difference in event timely-attribution fraction, `Delta_p = m_A,p - m_B,p`,
and test a sampling statement such as `H0: E_p[Delta_p] = 0`. The physical
parent, not the event replay or 30-fps report, is the resampling unit.

C01's methods, thresholds, catalog and evaluation procedure were frozen before
the confirmatory cohort was evaluated. The comparisons now visible span four
methods, three R/X conditions, two noise strata and several outcomes; selecting
one pair/endpoint after seeing this table would itself be selection. The current
article should therefore present the frozen estimates and their already
specified parent-cluster intervals without adding p-values. If a later analysis
reports a test, a concrete contrast is R11 versus ET_CANDIDATE on parent-level
timely fraction in MATCH; state whether it is exploratory or confirmatory,
specify how the other conditions/metrics and multiplicity are handled, and
justify the paired-null distribution from the cohort-generation design. A
sign-flip test needs an exchangeability or symmetry argument for the
parent-level differences under the null; clustering alone is not such an
argument. Do not treat failure to meet a chosen significance threshold as a
reason to alter the frozen metric or method.


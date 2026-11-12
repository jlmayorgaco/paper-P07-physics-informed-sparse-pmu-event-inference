# Adversarial/editorial closure audit — 12 November 2026

Scope: read-only review of the active `main.tex` inputs, current closure and submission-pending notes, history-conditioning disposition, prior final/writing reviews, and rendered pages 2, 7, and 13. No source, experiment, or protected figure files were changed. The PDF has 19 pages. Figures 1, 4, and 7 are legible at final size; no evident clipping or layout defect requires a redraw. Figure 4's smallest coordinate-count text is tight but readable at normal zoom; retain its current layout unless print-size proofing shows otherwise.

## Ranked scientific/editorial blockers

### 1. C03 is not a result and must remain outside the claims (critical, scientific)

`docs/P07_CLOSURE_CURRENT.md` says CAL was still running at 53/72 at 16:11 Bogota on Nov. 12, and the selection/test/lock files do not exist. The active article appears not to claim a C03 result. Preserve that boundary in any final polishing: do not describe the short-gap/two-plant experiment as completed, evidence, validation, or transfer. In particular, no second-plant generation check can be described as attribution or transfer performance. Before any later C03 integration, require the selection, reserved TEST result, and `COMPLETE_SINGLE_USE` evaluation lock, then audit fusion/reset, alarm costs, and admission failures separately.

### 2. C02 supports a complete-procedure contrast, not a mechanism attribution (critical, scientific)

The intro and interpretation state that C02 compares complete procedures. C03 adds history/fusion/reset controls, but its mean fusion also discards mixture uncertainty and resets proposal histories; it cannot isolate removal of historical labels alone. Keep this caveat adjacent to any interpretation of a C03 gain. Avoid wording that says recovery histories alone cause the C02 gain or that the method is generally superior. C02 covers one simulator family and a known catalog, with sequential nonoverlapping interventions. The 18 physical parents, not 108 events, are the independent resampling units.

Suggested compact wording if a result sentence is shortened: “In this held-out, single-family simulation, the complete history-bank procedure exceeded the calibrated GLR on timely attribution; this contrast does not isolate the contribution of recovery-history retention.”

### 3. “Common calibration budget” can be mistaken for equal realized alarm rates (high, scientific/editorial)

C02 calibrates each procedure against the same target of one normal alarm/hour, but the observed normal set yields zero alarms for all methods and only a one-sided upper bound. Figure 7 also shows very different unmatched alarms per event-record hour (8/0.54 h vs 85/0.54 h). Retain “common calibration budget/target”; do not call it equal empirical operating points or equal false-alarm rates. The event-record extras are not normal false alarms. State both denominators wherever these outcomes are juxtaposed.

Suggested local wording: “Thresholds were selected separately on calibration data to the same target (one normal alarm/h); the held-out normal cohort produced zero alarms for each method, so realized normal rates are bounded rather than matched.”

### 4. Clarify what “before OFF” and “timely” mean (high, scientific)

The primary endpoint is correct family-and-source output before true physical OFF; it is not merely detection, nor a guarantee that all alarms are correct. Keep late/absent decisions distinct from unmatched alarms and report false restorations/open episodes where relevant. The abstract says “attributed … interventions before restoration,” which is understandable but could be read as successful detection of every intervention. Prefer “made a timely correct family-and-source attribution for … of 108 interventions, before true OFF.”

### 5. Retrospective diagnostics, causal replay, and real-time operation are distinguished, but keep the distinction explicit (medium, scientific)

The method and compute-cost section appropriately call the implementation an offline causal replay and report amortized processing rate rather than per-report latency. Preserve this exact limitation in the abstract/conclusion and avoid “real-time” or online-deployable claims. The theory section's nominal signature/separation quantities are diagnostics under assumed plant/noise; they do not establish empirical error rates, account for independent per-PMU noise, or certify a general detectability guarantee. Keep those qualifications beside references to signature strength.

### 6. Measurement/noise limits are substantive, not a minor robustness footnote (medium, scientific)

The protocol explains that very small differential angle noise in the reference record comes from a strong common factor. The independent-noise stress test at 0.05% vector error sharply degrades load attribution, and the selected operating-point estimate remains fixed while noise estimation has a widened startup bound. Keep this failure visible in the abstract/Discussion/conclusion; do not summarize it as generic robustness to noisy PMUs. State that this perturbation is independent per-PMU noise and that measured field error may differ.

### 7. State/history scope and startup assumptions (medium, scientific)

The active method retains continuous state through ON/OFF, but starts from an intervention-free prefix and fixed startup/warmup contract. Histories are finite and pruned, outer model-density weights are not reweighted by inner history updates, and reported cause masses are approximate rather than calibrated posterior probabilities. Current method text states these limitations. Avoid shorthand such as “the posterior probability of the cause” or claims that the algorithm searches all 300 prior reports; use “approximate cause mass” and the stated proposal/retention mechanism.

## Editorial and visual notes

- **Figure 1 / page 2:** clear causal example and separate recovery/new-event innovation paths. Captions correctly call traces schematic. No change needed.
- **Figure 4 / page 7:** clear separation of physical switch, continuous dynamic state, algebraic re-solve, and report formation. The coordinate count and BUS39 angle exclusion are useful; small text is the tightest part of the three figures but remains readable in the rendered page. Do not add another diagram.
- **Figure 7 / page 13:** aligned absolute and paired panels distinguish coverage from extra-alarm cost. The sign convention is stated. Ensure prose retains that parent-cluster intervals use 18 parents, and distinguish event-hour extras from normal-record false alarms.
- The line under the Figure 7 caption (“Normal records: 0 alarms in 3.92 h per method …”) is dense. A small readability improvement is to split it into two short lines/sentences, explicitly naming the one-sided Poisson upper bound. It can be moved to the paragraph below if a line is needed.
- In Results prose near Table 5, “method” vs “procedure” is occasionally used interchangeably. Use “procedure” for whole-arm comparisons and reserve “method” for the physical model/filter component.

## Author-only submission blockers (not scientific blockers)

Keep these separate from scientific conclusions and do not imply that the paper is ready to submit until resolved:

1. Authors must review/complete journal-required declarations: authorship, affiliations, funding, conflicts, code/data availability, and the AI-assistance declaration. See `docs/SUBMISSION_DECLARATIONS_PENDING.md`; the current absence of a disclosure is not evidence that no assistance occurred.
2. Follow the author's Git synchronization route to Overleaf; local isolated compilation does not establish an observed remote build. Do not open a new login flow.
3. Obtain author/coauthor approval.
4. Complete the final post-C03 scientific review only if/when the locked C03 test is actually available. If it remains unavailable, submit decisions must not imply C03 validation.

## Bounded page-count plan (stay at or below 19 pages)

Current PDF: 19 pages. Do not add diagrams, a second-plant schematic, or a new table before the page budget is known. First make only the short sentence/caption edits above. If they push a float or reference onto page 20, recover space in this order: (1) shorten repeated scope sentences in intro/discussion while preserving one explicit limitation statement per topic; (2) reduce redundant prose that repeats Figure 7/Table 5 counts; (3) move secondary per-condition detail already present in the supplement out of the main text. Keep Figures 1, 4, 7 and both protected figures unchanged. Recompile and inspect final-size placements after any author-approved edit; do not solve overflow by shrinking figure text or removing caveats.

## Recommended minimal wording changes

1. Abstract: change “the bank attributed N interventions before restoration” to “the bank made a timely correct family-and-source attribution for N of 108 interventions, before true OFF.”
2. C02 summary: append “This comparison evaluates complete procedures and does not isolate the effect of recovery-history retention.”
3. Alarm calibration: replace any “equal alarm budget/rate” shorthand with “same calibration target (one normal alarm/h); held-out normal alarm rates were zero-observed and bounded.”
4. Noise limitation: say “independent per-PMU noise” and retain the observed degradation next to any robustness summary.
5. Real-time wording: retain “offline causal replay” and “amortized processing rate”; avoid turning these into per-report latency or deployment claims.

No experimental claim in this audit should be read as validation of C03 or as a fresh reanalysis of sealed predictions.

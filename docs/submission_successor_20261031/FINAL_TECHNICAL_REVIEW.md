# Final technical review of the current submission changes

Date: 2026-10-31. Scope: `main.tex`, `sections/article_submission_checks.tex`, `sections/article_signature_summary.tex`, `supplement/appendix_single_state.tex`, `supplement/appendix_submission_contract.tex`, their H04 generated table/macros, and the repaired M1–M7 statements in the historical theory/estimator appendices. No TeX was edited. No C01 partial output, truth or RAW0002 was inspected.

**Decision: the H04 numbers and the principal mathematical/claim boundaries pass. Two small but required implementation-description corrections remain in the reviewed text. There is no new theorem-level veto from M1–M7. This is not an approval of the whole submission package, whose C01, editorial and RAW successor work remain separately pending.**

## Required technical corrections

### T1 — Restrict profiled load amplitude to ON alternatives

**Location:** `supplement/appendix_single_state.tex:13`–25; related shorthand in `sections/article_submission_checks.tex:8`.

The appendix introduces the clipped profile estimator as applying to “a load alternative.” The executed comparator profiles amplitude for **load ON** alternatives only. A load OFF alternative inherits the committed amplitude at its birth and keeps that amplitude fixed while propagating its switched trajectory. The implementation explicitly sets `fit = kind == 'on' and family == 'load'` and chooses between the profile and `fixed_amplitude` in `SGSMA26-Physics-Informed-AD/experiments/PAPER_SUBMISSION_S01/runtime/single_state.py:216` and `:253`.

The formula itself is correct; its stated domain is too broad. An implementer following the present wording could fit a fresh OFF severity and obtain different scores/states.

**Minimal repair:** write “For a load ON alternative” before the quadratic profile, and add: “A load OFF alternative fixes severity at the committed estimate when that alternative is born; it does not refit severity from the OFF suffix.” This is an implementation-description correction, not a reason to rerun the already executed comparator.

### T2 — Specify which comparison shares the nominal operators

**Locations:** `sections/article_submission_checks.tex:13`–15 and `:22`–24; `supplement/appendix_single_state.tex:4`–5.

The single-state comparator loads the nominal H04 particle (`runtime/compare_single_state.py:37`). The nominal history bank uses that corresponding conditional model, while the five-model history bank additionally averages fixed R/X hypotheses. “The same fitted nominal operators” / “as the history bank” can be read as saying all three procedures have only that one plant hypothesis. The five-model 51/54 versus single-state 37/54 contrast therefore differs in static network uncertainty as well as history/search/severity treatment.

The surrounding text already correctly calls this a complete-procedure comparison and denies a pure memory ablation. No result is invalidated. The shared-model statement should nevertheless identify its actual pair.

**Minimal repair:** specify “The single-state procedure uses the same fitted nominal operators as the nominal history-bank arm; the five-model arm additionally averages its fixed R/X hypotheses.” Include that mixture among the differences preventing exclusive attribution to history averaging. The nominal 44/54 versus single-state 37/54 result already appears in the table and need not be changed.

These are narrow reproducibility corrections of moderate priority, not a claim that the observed performance ordering is false. No additional physical evaluation is required merely to repair the wording.

## Verified H04 evidence and limitations

The source `SGSMA26-Physics-Informed-AD/experiments/PAPER_SUBMISSION_S01/run/single_state_h04/EVALUATION.json` is byte-identical to the manuscript import `generated/frozen/submission_s01_controls_20261031/single_state_evaluation.json`. All 15 H04 macros for timely decisions, denominators, extras, premature restoration and missing restoration match that source. `tables/generated/single_state_control.tex:8`–10 matches it:

| Procedure | Timely | Extras | Premature matched restorations | Missing restoration, including missed event |
|---|---:|---:|---:|---:|
| Single state, short GLR | 37/54 | 37 | 0 | 4 |
| Nominal history bank | 44/54 | 6 | 0 | 10 |
| Five-model history bank | 51/54 | 3 | 0 | 3 |

The evaluation has 12 records, three event calendars with repeated conditions, and one normal parent represented under three conditions. The reported normal monitoring exposure is 204 seconds for each method, with zero alarms. `sections/article_submission_checks.tex:25`–27 correctly denies an established low operational false-alarm rate. No confidence interval or independent-54-events claim is made; the evaluation's confidence intervals are null.

The table retains every intended event replay; it is an aggregate table, not a per-record listing. The sentence at `sections/article_submission_checks.tex:18` would be more exact as “aggregates all 12 records” instead of “reports every record.” This is a minor presentation correction.

The source also records **32, 5 and 3 orphan restorations** for single state, nominal history bank and five-model history bank, respectively. Those are distinct from the zero premature restorations of matched events. `supplement/appendix_submission_contract.tex:57`–65 correctly distinguishes the definitions. Consider a table note or a compact additional line giving orphan-restoration counts so “Early OFF = 0” cannot be misread as absence of all restoration errors. This is a transparency recommendation; the existing mathematical definitions and table entries are not false.

## State preservation, likelihood and clock semantics

`supplement/appendix_single_state.tex:43`–46 correctly states that commitment selects the candidate's **current conditional state**, which may differ from the previously committed estimate. It expressly distinguishes this estimate revision from assigning equilibrium or a zero physical state. That distinction must survive future editing. A hypothesis-dependent jump in an estimate does not demonstrate a reset in the simulated energy-storage state, and continuity of the physical state does not require a posterior mean to remain unchanged after new evidence or hypothesis selection.

The suffix contrast `C + a*U - a^2*G/2 - C_ref` is correct under the implemented affine innovation recursion, with the T1 ON/OFF scope correction. The reference log densities are pre-update densities using the previous severity estimate, not a separately refitted joint reference likelihood on every suffix. The current text states that correctly. Alternatives cannot modify the committed predictor before commitment.

`supplement/appendix_single_state.tex:33`–38 and `sections/article_submission_checks.tex:15`–17 correctly distinguish a maximized/penalized GLR score from Bayesian attribution masses. The fixed penalties are not presented as posterior normalizers, a Bonferroni probability calculation or an end-to-end false-alarm guarantee. The common numerical threshold and six-report publication rule are not claimed to equalize operating points. For R11, `M_cause(c)*P(OFF|c)` correctly reconstructs restored source mass under the defined conditional fraction before taking log odds.

The preceding-regime and post-OFF quiet-run descriptions at `supplement/appendix_single_state.tex:50`–54 agree with the reviewed runner: current observations do not select their own predictive regime, missing/active reports clear the quiet run, and the normal counterfactual innovation uses the preceding committed state. Missingness preserves state/mode without measurement correction and contributes no clock evidence. H04 has no post-startup missing observations, so those synthetic paths are not presented as an empirical H04 missing-data result.

One small precision is advisable at `supplement/appendix_single_state.tex:7`: “each available report” should mean each report **after the proposal startup barrier**. The implementation begins proposals at index 300 and monitoring/publication after the fixed warmup of 360 reports. This restriction does not change the reported H04 results.

## RAW and signature-experiment claim boundaries

`sections/article_submission_checks.tex:54`–57 is consistent with `RAW_PREFIX_REVIEW.md`: the physical frozen prefix failure is not merely a low ROCOF scale. ROCOF `alpha4=0.000997176626315` is outside `(0.1,10)`, and the unchanged stationarity construction also rejects voltage angle (2605.81), current angle (6720.27) and ROCOF (11243.54), against its limit 8. The first exception masks those later failures in the original gate. Multiplying ROCOF by 1000 would put its scale inside the support but leave the standardized stationarity failure and scale-free shape discrepancies unchanged. The manuscript correctly avoids a units-only explanation or a claim that relaxing one gate validates transfer.

The initial 300-report diagnosis does not identify the producer's true ROCOF units, estimator or causal mechanism. The proposed IR01 common-reference/39-observation design has synthetic algebraic support only and is **not** a demonstrated transfer result. It is absent from the executed claims reviewed here, which is appropriate. Do not silently replace the 47-channel R11 description or its unavailable RAW outcome with that successor.

The current RAW source/actuation-scoring qualification is a known moving boundary because physical metadata have now been recovered. Per the assignment, this review did not re-investigate that metadata or turn its pending successor analysis into a new veto. The present text must be updated when that analysis is incorporated; neither the present event-code-only analysis nor the found spreadsheet alone establishes new scored outcomes. No independent audit of the full cyber evaluation was attempted in this technical subreview.

`main.tex:43`–47 and `sections/article_signature_summary.tex:5`–13 explicitly state known onset/load family and evaluate severity error at the generating source. They correctly avoid promoting this oracle-context component experiment to an unknown-onset detector result or claiming a source-accuracy gain when only severity improved. Current imported numbers are 1.2% versus 0.329%, with equal reference-only/conditioned source counts in the macros. The detailed section's nominal-condition counterexample remains visible. This check verifies the claim scope and current imported values, not a fresh rerun of that separate campaign.

The `main.tex:36` C01 conditional branch was reviewed only as source text. No C01 macro contents, partial results, predictions or truth were inspected or approved. This review does not authorize treating an unfinished campaign as confirmation.

## M1–M7: repairs remain intact

The two current appendix SHA-256 values match the sources recorded by `docs/submission_successor_20261031/checks/math_corrected_claims.json`; the check script hash also matches. Its previous checks passed. Because the tested sources are unchanged, the numerical suite was not rerun merely to overwrite its existing evidence record.

| Repair | Current location | Review result |
|---|---|---|
| M1 | `supplement/appendix_d_theory.tex:660` | Nontrivial closed-cone minimum separation is correctly declared symmetric; the compact unit-section/scale optimization proof supports it. |
| M2 | `supplement/appendix_e_estimator.tex:419` | Cone-Laplace has positive cone mass, dominating envelope and localization assumptions before a multiplicative equivalent; the zero-mass cusp remains excluded. |
| M3 | `supplement/appendix_e_estimator.tex:503` | Fiber reduction requires invariance of the complete conditional law, including Gaussian covariance. |
| M4 | `supplement/appendix_e_estimator.tex:531` | Mixed regular/higher-order constant is restricted to centered data and a bilateral interior amplitude, with rank and localization stated. |
| M5 | `supplement/appendix_e_estimator.tex:165` | The historical single-source `1/(2*pi)` factor and effective cardinality prior remain disclosed. No corrected-prior physical outcome is claimed; this is distinct from R11's causal integral. |
| M6 | `supplement/appendix_d_theory.tex:773` | Restricted margin uses the Gram minimum eigenvalue, counting wide-map null spaces; stability requires positive margin. |
| M7 | `supplement/appendix_d_theory.tex:308`, `:333`, `:352`, `:703` | Inverse-order comparisons use common positive-definite nuisance coordinates; scalar matched/projection/onset divisions require their nonzero-information domains. |

Moving these proofs into the separately compiled historical notes does not mathematically strengthen the active R11 method, and the current supplement says so. The historical normalization defect is not falsely attributed to the active causal filter. Local geometry and Gaussian identities are not presented as calibrated full-stream probabilities or all-family transfer guarantees.

## Release recommendation

Apply T1 and T2 as small factual text repairs, preserve the already-correct state/score/scope qualifiers, and integrate the known pending RAW metadata analysis separately. No new empirical or mathematical defect requiring the H04 comparator to be discarded was found. The optional orphan-restoration and startup clarifications improve reproducibility and should fit in the supplement.

This review covers mathematical/technical consistency, not the final PDF, figures, citations, authorship metadata or completion of independent C01. The repository's required build, visual review and protected-figure verification remain the principal agent's integration responsibility. Overall submission readiness remains pending for the reasons already recorded by the principal task.

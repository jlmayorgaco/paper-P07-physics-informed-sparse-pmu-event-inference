# Audit of “both methods” and the claimed new method

**Scope.** This note resolves the terminology in the four supplied texts against the active P07 article, its supplement, the declared claims boundary, and the imported C03 evidence. It is an audit, not a new scientific result. Attachment 3 and attachment 4 are duplicates; attachment 1 is a method/originality assessment, and attachment 2 is a reviewer-style submission audit. The proposed four-paradigm/SOTA rewrite is a proposal, not the implemented paper.

## What is implemented in the current P07 article

The article's evaluated sequential method is the recovery-aware physical history bank described in `sections/article_method.tex` and its implementation walkthrough in `supplement/appendix_causal_walkthrough.tex`. It takes the fixed eight-PMU stream and the admitted catalog of nine load and nine line sources; uses five fixed network hypotheses; scores switched DAE-derived predictor histories; integrates bounded load severity conditionally; retains conditional histories through physical OFF; and reports active mass \(M\), originating-cause mass \(\Gamma\), and timestamped alarm/diagnosis/restoration messages. IMM/M3H is the established recursion underlying the mode/history update, not a newly derived filter. The paper's defensible contribution is its particular electrical intervention/recovery construction and tested output contract, not a new filtering family.

The article also reports a continuous GLR comparator and ExtraTrees adapters. These are complete-procedure comparisons with separate search, scoring, and publication behavior. Their C02 contrast does not isolate history retention. The reset ablation in `sections/article_controlled_ablation.tex` is a separate fixed-threshold component contrast; it shows state reset is harmful but does not test recovery-history retention against an otherwise matched state-carrying bank.

The publication procedure is more specific than the original short description of “0.99 for six reports; OFF for 15.” The supplement's `supplement/appendix_publication_rules.tex` specifies a 30-report (one-second) conditional-innovation source screen for load qualification, the fixed F-statistic threshold 24.0115, pending-episode logic, diagnosis counters, and a public six-report joint cause/restoration OFF rule. The internal mixture's 15-report retirement logic is distinct from public OFF. `sections/article_method.tex` now includes the screen and the key public/internal distinctions, and the per-report algorithm points to those gates. This follows the executed publisher; it does not change or regenerate its results.

## What is proposed, adjacent, or a different estimator

The source-resolution/estimator material explicitly distinguishes the implemented batch load estimator \(\mathcal E_{\mathrm B}\) from the specified but unexecuted joint Hybrid-DAE estimator \(\mathcal E_{\mathrm J}\) (`CLAIMS.md`, “Supported theory and design claims”; `supplement/appendix_causal_walkthrough.tex`). \(\mathcal E_{\mathrm B}\) is a known-context, known-onset batch load-support study with a frozen quadratic response manifold and GH31 amplitude integration. \(\mathcal E_{\mathrm J}\) is a proposed joint inference object over state, operating nuisance, family, onset, support, amplitude, and integrity. The restriction \(\mathcal R_0\) requiring it to reduce to \(\mathcal E_{\mathrm B}\) is a design regression condition, not an experiment. Neither name refers to the sequential recovery-history bank \(R11\), and neither is a synonym for the C03 arms.

The attachments' suggested four-paradigm “unified framework,” 20-plus-method taxonomy, public 648-replay benchmark, 22-theorem package, four-way ablation, and “reference/SOTA” conclusion are not the scope of the current main article and are not established by its implementation. They also assign theoretical and data-driven roles (including benchmark release and a matched IMM baseline) that the current evidence does not support. Do not insert these as executed contributions. The current paper narrows its claim to sequential load/line attribution from the fixed catalog in a specified simulator setup, with the observed coverage/alarm trade-off and the explicit C03 transfer limitation.

## Meaning of “both methods” in the current C03 comparison

For C03, the meaningful head-to-head is **history versus carry**:

- **history:** retain explicit recovery histories and their conditional states;
- **carry:** merge retired histories into a carried physical-state mean while sharing the nominal conditional covariance;
- **reset:** reset the physical coordinates and serve as a deliberately adverse continuity control.

These are C03 experimental arms, not two general-purpose algorithms or “the old and new method.” The comparison holds the frozen admission, reporting, severity, and instrumental-state rules fixed. The carry arm does not preserve the full covariance of the mixture. Consequently, a positive history-minus-carry contrast supports explicit history retention over this specified mean-merging control; it does not establish that semantic labels alone cause the gain or that retained histories outperform all IMM/M3H variants. Reset addresses the separate value of state continuity and cannot substitute for the history-versus-carry comparison.

The imported one-use C03 artifacts report 144/144 versus 90/144 timely primary events on F01 (paired difference 37.5 percentage points, 95% interval 25.0–49.3), and 67/144 versus 65/144 on P2 (1.4 points, interval −12.5–16.0). History reduced event-record extras in both plants. Thus the held-out result supports a coverage gain on F01, does not establish a coverage gain on P2, and shows that the coverage result does not transfer as a general plant-independent claim. Both carry arms materially outperform reset on coverage, supporting continuity under these tested contracts. Normal exposures are only 5.88 h per arm and the dropout cohort exceeds the nominal alarm budget; neither supports a long-run false-alarm guarantee. See `sections/article_c03.tex`, `tables/generated/recovery_c03.tex`, and `generated/frozen/recovery_c03/VALIDATION.json`.

## Comparisons required for any stronger novelty claim

1. **Mechanism claim:** report history versus carry as the primary matched comparison, at the preselected common calibration budget, with parent-paired uncertainty, timely primary events, total events, event-record extras, normal alarms/exposure, unavailable records, latency, and restoration outcomes. Keep reset as the separate state-continuity control.
2. **Scope:** state plant-specific outcomes and the P2 non-significant coverage contrast. Do not translate F01 success into transfer across plant families, nor call 5.88 h zero observed alarms a verified one-alarm/hour guarantee.
3. **Baseline language:** C02's GLR/ExtraTrees comparisons establish relative performance only for the complete procedures and common evaluated protocol; they do not isolate retention. C03 is not a matched IMM/M3H comparator, and no numerical Yang/Warner comparison was run.
4. **Estimator boundaries:** keep \(\mathcal E_{\mathrm B}\), proposed \(\mathcal E_{\mathrm J}\), and sequential R11/C03 separate. Never pool their outcomes or imply that proposed virtual-PMU outputs or joint state/event/source inference have been executed.
5. **Algorithm reproducibility:** preserve the explicit 30-report source screen, 0–25 screen lags versus separate 0–18 birth proposals, pending-episode/public alarm conditions, diagnosis, and public OFF rule in the method and supplement. Distinguish approximate inference masses from calibrated posterior probabilities.
6. **Originality language:** identify DAE reduction, conditional Gaussian filtering, bounded severity integration, beam pruning, and multiple-model filtering as established ingredients. Limit novelty to the specified power-network intervention histories through recovery, the active/cause output distinction as implemented, and the measured comparisons actually performed.

## Attachments and source pointers

| Source | Use in this audit |
|---|---|
| `ee5a649f-f6d5-4ff5-b0df-3333c5c378e6/Texto pegado.txt` | Describes the existing bank and argues the novelty is recovery-aware attribution / active versus cause mass, while acknowledging standard filtering machinery. Treats an IMM-matched comparison as still needed. |
| `7d0c82c9-e03a-4aa3-a79c-df8f2ade7504/Texto pegado.txt` | Reviewer-style audit: incomplete public decision algorithm, extra load qualification, public OFF mismatch, unresolved citations, and comparisons that do not isolate mechanism. |
| `e52bd18b-8e0d-4bfe-9fb0-28fbd2b36027/Texto pegado.txt` and `c5ff5a78-2df8-43b2-aba3-dd5516271ea8/Texto pegado.txt` | Duplicate proposal to reframe the manuscript as a four-paradigm SOTA framework. The suggested taxonomy, benchmark claim, theorem count, and ablations are proposals and must not be described as implemented without separate evidence. |
| `sections/article_method.tex`; `supplement/appendix_publication_rules.tex`; `supplement/appendix_causal_walkthrough.tex` | Active method, public source and episode gates, execution order and approximations. |
| `sections/article_c03.tex`; `generated/frozen/recovery_c03/VALIDATION.json`; `generated/frozen/recovery_c03/METHOD_FREEZE.json`; `generated/frozen/recovery_c03/TEST_F01_SEAL.json`; `generated/frozen/recovery_c03/TEST_P2_SEAL.json` | C03 arms, imported validation summary, method freeze and held-out seals. Runtime source is recorded in `VALIDATION.json` as the separate research checkout under `experiments/PAPER_RECOVERY_C03/run`; this audit did not run or modify that runtime. |
| `CLAIMS.md`; `docs/P07_SUBMISSION_GATE_20261114.md` | Existing estimator boundaries, claims contract, and submission-gate interpretation. |

## Present audit conclusion

The current manuscript's “method” is the implemented sequential recovery-aware DAE history bank. “The new method” in the attached four-paradigm plan is an aspirational reorganization and scope expansion, not an implementation. “Both methods” should be replaced by the names of the particular procedures under comparison. Where the intended contrast is C03, call it **history versus carry**, list reset separately, and state the plant-specific result and its limits.

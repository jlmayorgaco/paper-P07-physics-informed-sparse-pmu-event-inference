# Evidence-driven paper outline

## Five-sentence research map

1. **Problem:** Sparse PMUs leave the voltage field incomplete and may not distinguish physical source assets, especially when measurement failures coexist with grid events.
2. **Gap:** Existing state estimators, partial-observation reconstruction methods, and sparse-PMU localizers solve overlapping subsets, but the exact source-disjoint joint state/physical-event/integrity contract remains insufficiently tested.
3. **Insight:** Treat each physical event as a counterfactual DAE intervention, keep measurement integrity separate, and compare candidate-specific affine manifolds after profiling state and integrity nuisance.
4. **Test:** First evaluate all zero-, one-, and two-source supports in the 16-bus load bank on fresh nonlinear trajectories, then compare learned-only, physics-only, physics-plus-discrepancy, and diagnosability-aware inference on common source-disjoint parents under PMU loss/join and physical shift.
5. **Consequence:** The current evidence establishes sparse-PMU state reconstruction and a 137-hypothesis load-intervention inference contract, while showing quantitatively where weak simultaneous sources remain unresolved; it does not establish the multi-family end-to-end result.

## Section logic

| Section | Scientific role |
| --- | --- |
| I. Introduction | Exact joint problem, defensible gap, contributions, and evidence boundary. |
| II. Related Work | State estimation, sparse-PMU localization, partial-observation reconstruction, and capability matrix. |
| III. State, Event, and Source Problem | One physical model, two inverse questions, sparse-PMU geometry, and separate physical/integrity variables. |
| IV. What Sparse Measurements Can Determine | Functional target recovery, candidate-manifold separation, and sparse event injectivity before any estimator is selected. |
| V. Evaluated Components and Two Estimator Contracts | B0--B3 as a separate state component; implemented batch event estimator $\mathcal E_{\mathrm B}$; proposed joint Hybrid-DAE estimator $\mathcal E_{\mathrm J}$; and the mandatory reduction test between them. |
| VI. Experimental Questions and Frozen Evidence | Four research questions, one independent unit per question, and no pooling across incompatible contracts. |
| VII. State Evidence From Recovery to Model Failure | RQ1 nominal recovery followed by RQ2 physical mismatch and constrained recentering. |
| VIII. Event Evidence From Detection to Source Ambiguity | RQ3 cardinality then exact support, weak-case geometry, observation time, and RQ4 source holdout. |
| IX. Discussion | Mechanisms, competing explanations, limitations, and next frozen common-contract campaign. |
| X. Conclusion | Established component evidence and explicit end-to-end completion gate. |

## Main-paper and supplement boundary

The main paper carries only the definitions, propositions, numbers, and figures needed to answer the four research questions. Supplementary Appendices A--G contain the paper-by-paper literature matrix, terminal-current and event-operator conventions, metric denominators, proofs of functional reconstruction and sparse injectivity, nuisance-profiled Fisher and temporal-information analysis, the executed Bayesian load-bank algorithm, the still-unexecuted candidate-conditioned joint design, the full frozen-contract inventory, and secondary diagnostics. This boundary keeps the article readable without weakening reproducibility or confusing derived capability with tested performance.

## Title gate

The working title is *Physics-Informed State Reconstruction and Event-Source Inference From Sparse PMUs Under Limited Observability*. Adviser requirement: the title must not contain a colon. A joint-method title is allowed only after the common-contract campaign is complete.

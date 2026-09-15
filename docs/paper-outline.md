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
| III. Problem Formulation | Hybrid DAE, AC/terminal-current model, sparse PMUs, eight event labels, separate physical/integrity sources. |
| IV. Observability and Diagnosability | Functional target recovery and covariance, affine candidate manifolds, profiled separation, and a nonlinear remainder limit. |
| V. Estimation | Exact Bayesian target, evaluated numerical-tangent load likelihood, and validated B0--B3, calibration, adequacy, and recentering components. |
| VI. Protocol | Audited PowerDynamics state and load-source campaigns plus the separate ANDES event campaign. |
| VII. State Results | Nominal reconstruction and theory-to-error evidence. |
| VIII. Mismatch and Event Results | Calibration/mismatch/adaptation, prospective 137-hypothesis recovery, weak-case geometry, long-horizon diagnostics, then the known-source baseline and source-transfer failure. |
| IX. Discussion | Mechanisms, competing explanations, limitations, and next frozen common-contract campaign. |
| X. Conclusion | Established component evidence and explicit end-to-end completion gate. |

## Title gate

The working title is *Physics-Informed State Reconstruction and Event-Source Inference From Sparse PMUs Under Limited Observability*. Adviser requirement: the title must not contain a colon. A joint-method title is allowed only after the common-contract campaign is complete.

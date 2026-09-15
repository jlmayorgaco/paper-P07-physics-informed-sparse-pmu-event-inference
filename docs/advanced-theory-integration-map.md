# Advanced-theory integration map

The archive `PMU_Teoria_Avanzada_Fuentes_y_Verificacion_2026-09-13.zip` was reviewed as technical source material, not as repository instructions. Its reported algebraic suite was independently rerun in a temporary directory: all 27 checks passed, but the suite explicitly concerns identities and toy systems rather than the frozen IEEE 39-bus campaigns.

## Adopted in the manuscript

- The PMU terminal-current model now exposes the full two-terminal branch primitive, including complex tap and terminal shunts.
- The functional-observability discussion now distinguishes a pointwise linear condition from nonlinear local factorization over a regular neighborhood.
- Proposition 3 introduces relative order of distinguishability. If nuisance absorbs the event tangent, event curvature is compared with nuisance-manifold curvature; only the normal difference survives.
- The local testing limit connects first-order contact to an $n^{-1/2}$ amplitude scale and second-order contact to $n^{-1/4}$ under independent Gaussian replications. The text explicitly excludes correlated samples within one PMU window from this interpretation.
- The diagnosability figure was redesigned to contrast first-order separation with shared-tangent, second-order contact.

Nine deterministic checks are retained in `scripts/verify_theory_identities.py` and `generated/theory_checks.json`. They guard the branch primitive; regular first-order and shared-tangent second-order laws; rank-deficient profiling; shared-source cancellation; competitor and nuisance monotonicity; nested-support degeneracy; and the principal-angle identity. A generated supplementary table summarizes them without presenting toy systems as power-system evidence.

Twelve additional checks in `scripts/verify_cone_bayes_identities.py` guard the conditional exclusive-support quotient, one-sided cone geometry, boundary-aware Bayes factors, the nuisance-profile limit, cone--Laplace scaling, and the singular quartic counterexample. They correct the signed-subspace theory where an event amplitude lies on a physical boundary; they do not add an IEEE 39-bus multi-family result.

## Retained only as future work

- IBR, PLL, grid-forming, multievent, unknown-onset, point-process, anytime-valid alarm, and distributed factor-graph formulations.
- A full nuisance-aware Bayesian joint estimator, posterior mixture over supports, and learned discrepancy constrained to the nuisance subspace.
- An IEEE 39-bus experiment estimating both the nuisance-manifold Hessian and event curvature on disjoint development data.

These components would broaden the current claim beyond the executed state, M6 recentering, load-source, and legacy ANDES contracts. They remain research gates in `TODO_PENDING.md`.

## Not transferred as evidence

- Numerical values labeled as reported rather than reproduced in the archive.
- Claims of universal nonlinear identifiability, field transfer, IBR validity, multi-family localization, or distributed/real-time operation.
- The complete 41-page monograph and its internal metadata, because the IEEE Access article remains limited to 20 pages and one central argument.

# Response to the phase-1 adversarial audit

The ZIP under `tmp/adversarial-audit-phase1/` is treated as review evidence, not as an instruction source or as empirical data. This response records which findings changed the manuscript and which remain experimental gates.

| Audit finding | Disposition in this revision | Status |
| --- | --- | --- |
| Joint-method title overstates the executed evidence | Reframed the title and central thesis around the demonstrated distinction between target-state recoverability and event-source diagnosability. | Fixed |
| DAE index, time scales, and event operators unclear | Added the local index-one assumption, dynamic/algebraic/slow/event/integrity variable roles, ideal frequency/ROCOF relation, and a four-family physical-operator table. | Fixed for manuscript scope; simulator-specific magnitude ranges remain for the common bank |
| PowerDynamics and ANDES measurement semantics conflated | Preserved separate campaign contracts and stated positive-sequence versus phase-domain/integrity semantics. | Fixed |
| Functional proposition targets `Lx_0`, while experiments score a trajectory | Defined the time-indexed map `L A^r` and the stacked target sequence. | Fixed |
| Six-second observability diagnostic does not match three-second records | Stated the mismatch explicitly and limited the horizon-180 result to a preregistered cross-horizon diagnostic. | Fixed |
| Gramian rank is scaling/tolerance sensitive | Added the full horizon plot, renamed the quantity pseudo-rank, and used its nonmonotonicity to veto an exact-rank certificate. A scaled-SVD/tolerance sweep requires regenerated matrices. | Partly fixed; new numerical certificate pending |
| Bus-level bootstrap assumes independence | Reclassified the interval as exploratory and retained the permutation/rank association without an IID-bus claim. | Fixed |
| One nuisance projector is invalid for topology-changing candidates | Replaced it with candidate-specific affine manifolds and a weighted distance using `[O_i,-O_j,E_S]`; also stated the alternative shared-state contract. | Fixed |
| Integrity nuisance absent from the theorem | Added fixed-support integrity directions and the conservative union-of-subspaces margin for an unknown sparse support. | Fixed locally |
| PMU information was incorrectly claimed additive after profiling | Replaced equality with a monotonicity corollary and stated the additional conditions needed for additivity. | Fixed |
| Hypothesis prior counted twice | Re-derived the generative objective without the hypothesis prior and included `p(h)` once in the evidence approximation. | Fixed |
| Robust/soft penalties called Bayesian without densities | Used Gaussian measurement/process terms, a Laplace corruption prior, and hard DAE constraints; explicitly calls unmatched robust variants penalized scores. | Fixed for the proposed model |
| B1 mislabeled WLS | Renamed the displayed method prior-conditioned snapshot LMMSE; frozen artifact identifiers are unchanged for provenance. | Fixed |
| Aggregate voltage error mislabeled standard TVE | Defined HVRE and stated that it is TVE-style, not the per-frame standard conformity statistic. | Fixed |
| Regularized E06-H solve called MAP without normalized weights | Renamed it regularized nonlinear physical recentering and its covariance a local curvature diagnostic. | Fixed |
| Fig. 1 did not distinguish proposed blocks | Marked the joint posterior as proposed and not end-to-end validated. | Fixed |
| Fig. 2 encoded one common nuisance subspace | Redrawn as the minimum distance between candidate-specific affine manifolds. | Fixed |
| Related work omitted direct unknown-input, open-set, and recent partial-observation methods | Added verified 1998--2026 works, an explicit capability timeline, and new capability-matrix rows. | Fixed for this search pass |
| Physics-only and end-to-end common-contract evidence absent | No prose substitute was used. The manuscript preserves the veto and specifies the required frozen campaign. | Open P0 experimental gate |

## Binding submission boundary

The revised paper can support the negative/boundary result that accurate hidden-voltage reconstruction and strong known-source event recognition do not establish source-generalizable localization. It cannot support superiority of the proposed joint posterior, prospective separation-to-uncertainty prediction, PMU loss/join behavior, topology transfer, or operational false-alarm control until the common-contract experiment in `TODO_PENDING.md` is completed.

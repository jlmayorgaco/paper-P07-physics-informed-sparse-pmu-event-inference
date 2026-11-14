# C04: recovery covariance fusion

The user authorized adding full recovery-covariance fusion. The implementation
and campaign are in the scientific repository under
`experiments/PAPER_RECOVERY_C04`, local commit `bef6ed345` (branch
`exp/T2_static_vs_dynamic`). C03 remains unchanged.

## Matched comparison

The primary arms use the same covariance-aware filter, public OFF clock,
eligible restored histories, pooled probability mass and pooled state mean.
`conditional_mean` carries the weighted conditional covariance;
`moment` additionally retains between-history dispersion and severity variance,
including physical/instrument cross-covariances. Active and incompatible
histories remain separate. The covariance enters subsequent innovations,
gains, log determinants and Riccati updates. It is a full 376-state covariance
for the retained approximation, not an exact posterior over all histories.

The original history bank and mean-carry procedure are secondary references.
They do not isolate the covariance terms because their filtering approximation
differs. An initially considered retained-history control was rejected for the
primary comparison: its restored mass was not eligible for new births in the
same way as the fused H0 mass.

## Verified so far

- Eight code tests pass, with independent dense covariance/likelihood checks
  agreeing at approximately machine precision.
- Both new arms completed the normal 900-report development replay and the
  fresh 600-report event replay. A separate short end-to-end serialization
  check passed. Earlier incomplete development attempts remain recorded.
- Full 3,601-report event development replays are running. They have exercised
  six public OFF actions and six successful fusions per arm. They are not yet
  complete, so causal-prefix and full-development gates are still pending.
- P2 physical validation passed: sample clock, switch continuity, Kirchhoff
  residual, terminal currents and integration refinement.
- Sixteen C03 code/result/freeze hashes remain equal to the read-only baseline.

## Execution

Fresh DEV data for both plants are exported. F01 CAL physics generation is
running for 36 event and 36 normal parents. TEST observations/inference have
not started. The hidden supervisor (PID 37076 at launch) waits for completed
development outputs and CAL export, validates the gates, runs a legacy smoke,
then calibrates, freezes thresholds and runs the two-plant TEST. It stops on
failed gates, changed sources, unclassified failures or infeasible calibration.
Inference is bounded to four parent workers with one BLAS thread each.

Current state is recorded in the scientific repository at
`experiments/PAPER_RECOVERY_C04/run/SUPERVISOR.json`; detailed progress and logs
are under `run/PROGRESS.json` and `run/logs/`. The supervisor is an active local
process; it needs this computer to remain running. Its initial wait timeout is
12 hours, not a deadline for completing the full campaign.

The pilot shows substantial computational cost, including event replay slower
than the incoming 30-fps stream. Full calibration and TEST may take several
days. Report-clock attribution must not be described as demonstrated real-time
deployment. No covariance-fusion advantage is established yet; the article's
existing C03 conclusions remain unchanged pending this independent comparison.

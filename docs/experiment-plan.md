# Frozen experiment contracts and next gates

## Evidence already integrated

| Study | Independent unit | Split and denominator | Selection rule |
| --- | --- | --- | --- |
| Nominal reconstruction | nonlinear trajectory | 20 DEV / 100 TEST; 91 frames at 30 Hz | B0--B3 frozen before TEST. |
| Functional diagnostic | hidden bus | 31 buses; horizon-180 ranking preregistered | Correlation evaluated only after ranking export. |
| Nominal calibration/discrepancy | nonlinear trajectory | 30 CAL / original 100 TEST | Temperature and rank selected on CAL, frozen for TEST. |
| Physical mismatch | rebuilt nonlinear plant | 7 families x 7 scales x 20 seeds = 980; 175 refinement cases | Nominal estimator/calibration frozen. |
| Causal recentering | rebuilt nonlinear plant | 160 DEV seeds 101--110 / 320 TEST seeds 201--220 | Window, cadence, qd, lambda, and gate selected on DEV. |

Simulation failures remain in planned denominators. All reported main-grid and refinement plants passed the documented power-flow, initialization, and trajectory checks.

## Next falsifiable gate

Implement a causal nonlinear AC recentering step using observed PMU voltage/current measurements only, then rebuild the local Jacobians and covariance. Freeze solver tolerances, window, regularization, activation policy, and failure handling on DEV. Evaluate once on the existing disjoint E06-E TEST manifest against:

1. frozen B2;
2. oracle recentering (mechanistic upper reference);
3. failed R2-A offset proxy; and
4. nonlinear recentering with and without Jacobian rebuilding.

Primary metrics are hidden-bus TVE, oracle-gap closure, nominal degradation, solver acceptance, latency, and rejected-case accounting. A learned discrepancy model is justified only after this physical adaptive baseline is available.

Event/source inference, PMU join/loss, continuous false alarms/hour, cross-simulator transfer, and field/HIL validation require separate manifests and are not completion conditions for the current paper revision.

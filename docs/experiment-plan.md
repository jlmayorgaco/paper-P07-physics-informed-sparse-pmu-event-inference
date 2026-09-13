# Frozen experiment contracts and next gates

## Evidence already integrated

| Study | Independent unit | Split and denominator | Selection rule |
| --- | --- | --- | --- |
| Nominal reconstruction | nonlinear trajectory | 20 DEV / 100 TEST; 91 frames at 30 Hz | B0--B3 frozen before TEST. |
| Functional diagnostic | hidden bus | 31 buses; horizon-180 ranking preregistered | Correlation evaluated after ranking export. |
| Nominal calibration/discrepancy | nonlinear trajectory | 30 CAL / original 100 TEST | Temperature and rank selected on CAL, frozen for TEST. |
| Physical mismatch | rebuilt nonlinear plant | 7 families x 7 scales x 20 seeds = 980; 175 refinement cases | Nominal estimator/calibration frozen. |
| Causal grouped-offset recentering | rebuilt nonlinear plant | 160 DEV / 320 TEST rebuilt cases | Window, cadence, qd, lambda, and gate selected on DEV; retained as a negative ablation. |
| Regularized physical recentering | rebuilt nonlinear M6 snapshot | 30 DEV / 60 TEST; 20 cases per shift scale | qd=1, lambda=0.01, and continuation initialization frozen after DEV. |
| Legacy event hierarchy | physical trajectory/event parent | 690 trajectories from 138 source configurations x 5 replicas | Grouped train/dev/test by event parent; detector/classifier thresholds selected before evaluation. |
| Complete physical-source holdout | held physical source parent | 101 held-source cases x 3 seeds = 303 decisions | Physical source absent from source-labeled training and tuning; event family supplied. |
| Independent RAW0001 transfer | annotated event episode | 12 event episodes, including 5 physical episodes | Candidate model selected before inspecting the record-level outcome. |

Simulation failures remain in planned denominators. The state-estimation campaigns and imported legacy event campaign remain separate evidence contracts; the manuscript does not average their metrics or imply a single end-to-end run.

## Completed falsifiable findings

- The corrected E06-H estimator solves a regularized nonlinear AC physical-recentering problem from observed PMU voltage/current measurements only. It yields strong M6 target-state recovery despite a rank-deficient nuisance vector, but its curvature covariance is jointly under-dispersed.
- The legacy physics-guided hierarchy performs strongly for detection and event family classification under known-source training, but nearly collapses under complete physical-source holdout and transfers weakly to RAW0001.
- Together these results motivate candidate-conditioned physical intervention inference; they do not validate the proposed joint estimator.

## Submission-critical next gate

Run one preregistered common-contract campaign with:

1. physical hypotheses `(event family, source, onset, magnitude)` and separate integrity masks/corruptions;
2. ML-only, physics-only, physics plus engineered residual features, and full uncertainty/abstention baselines;
3. grouped event-parent splits and complete held-source splits;
4. PMU loss/join, operating/parameter shift, topology outage, and cross-simulator blocks;
5. long normal exposure with false alarms per hour, event recall, detection delay, exact Top-1/Top-3 source accuracy, candidate-set coverage/size, and calibration metrics;
6. frozen manifests, thresholds, seeds, failed-solve accounting, paired intervals, runtime, and hardware metadata.

Until this gate is complete, title and abstract must retain the explicit component-evidence boundary.

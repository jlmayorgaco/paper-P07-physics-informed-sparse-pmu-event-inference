# E06-E — online operating-point recentering

## Scope

Fresh PowerDynamics IEEE-39 trajectories use seeds 101–110 (DEV, 160 cases) and 201–220 (TEST, 320 cases), disjoint from E04/E06 STANDARD/E06-D. No E04-B, events, or ML were started.

## Breakpoint audit

The canonical definition is `median_i(TVE_i(m)/median_nominal_TVE)`, with B2 hidden-31 TVE, all E-A…E-D strata, and main-grid seeds. The old M7 refinement label mixed direct medians with the main grid and is not retained as a canonical breakpoint.

## R2-A contract

The online center is an 8-dimensional grouped observed-bus voltage correction (four fixed bus areas, real/imag P/Q-like columns), ridge/MAP regularized with `qd=2.5e-3`, `lambda=1e-2`, and a causal trailing window of 60 frames, updated every 1 frames. It uses only PMU measurements and nominal matrices. The nominal AC residual proxy is reported in `e06e_center_error.csv`; hidden truth is used only for evaluation.

The present Python-side R2-A implementation is the preregistered linearized static-MAP proxy: its admissibility residual is the component of the observed correction outside the fixed nominal voltage basis (median family residuals are approximately 0.0015–0.0024). It is not a new nonlinear PowerDynamics PF/KKT solve; this limitation is material and is reflected in the FAIL result rather than being hidden behind an AC-closure claim.

## Results

Median TEST oracle closure for M1/M6/M7, m>0: **0.004**. M2 is retained as a negative control. Nominal R2-A relative TVE change: **0.00%**; nominal adaptive false activation: **4.95%**.

R2-B was not implemented because it is gated on materially incomplete R2-A closure. Dynamic A relinearization and nonlinear fixed-lag MAP were not started. Runtime and uncertainty outputs include the explicit approximation that center/state cross-covariance is neglected.

## Statuses

- BREAKPOINT_AUDIT = **CORRECTED**
- ONLINE_RECENTERING = **FAIL**
- ORACLE_RECOVERY_CAPTURED = **WEAK**
- NOMINAL_SAFETY = **PASS**
- STATIC_JACOBIAN_UPDATE_NEEDED = **NO**
- FULL_RELINEARIZATION_NEEDED = **PARTIAL**
- NONLINEAR_DAE_FIXED_LAG_NEEDED = **NOT_YET_JUSTIFIED**

# E06-H — corrected real-M6 static recentering gate

Fresh physical M6 splits were frozen before fitting: **30 DEV** cases (seeds 601–610) and **60 TEST** cases (seeds 611–630), at m=0.5, 1.0, 1.5. No E06-F/E06-G cases were reused.

## Corrected physical basis

The solve uses ΔP/ΔQ on the 17 admissible PQ loads, ΔP on PV generator buses, explicit PV magnitude constraints, solved PV-Q, and bus 31 as Slack. Bus 39 remains PV. The basis has 43 nuisance coordinates and is leakage-safe.

DEV selected `qd=1`, `lambda=0.01`, initialization `I1`. Selection used PMU residual, AC residual, convergence/stability, and only secondarily hidden-voltage diagnostics.

## Convergence and metrics

TEST convergence rate: **1.000**. Median solver time: **61.733 ms**; p95: **76.047 ms**. The AC convergence tolerance is **5e-05**, materially below the old E06-F ~1e-3 residual. Rejections are explicit in `e06h_rejections.csv`.

Corrected MAP median hidden TVE by scale: m=0.5 **0.00526%**, m=1.0 **0.00749%**, m=1.5 **0.00974%**. Nominal medians are 0.19885%, 0.38834% and 0.57795%, respectively. Static closure by scale with bootstrap 95% intervals is in `e06h_closure.csv`; overall median closure is **0.9809**.

## Functional identifiability and uncertainty

The local information rank/nullspace and hidden-voltage functional residual are in `e06h_identifiability.csv`. Median rank is **25/43**, with nullspace dimension **18**. The nuisance remains non-unique; success is scored on hidden voltage, not exact d recovery. Nullspace-aware pseudoinverse covariance gives 95% marginal coverage ≈ **1.00**, but NEES-like values are large (about 112, 183 and 294 by scale), so uncertainty is conservatively **PARTIAL**, not certified calibrated.

## Independent solver

The preregistered subset contains 2 TEST cases per scale. Results are in `e06h_solver_subset.csv`; consistency status is **PARTIAL**.

## Claim cleanup

The old E06-F result is preserved historically but marked `SUPERSEDED_BY_E06G`. The interim marker `WITHDRAWN_FOR_M6_PENDING_E06H` is now resolved as `WITHDRAWN_FOR_M6_AFTER_E06H`: the corrected gate passes and no M6 network-parameter-estimation stage is justified (`e06h_claim_cleanup.csv`).

## Final statuses

`CORRECTED_M6_BASIS = PASS`  
`MAP_SOLVER_CONVERGENCE = PASS`  
`8PMU_STATIC_FUNCTIONAL_IDENTIFIABILITY = PARTIAL`  
`REAL_M6_STATIC_RECENTERING = STRONG`  
`UNCERTAINTY = PARTIAL`  
`SOLVER_CONSISTENCY = PARTIAL`  
`ONLINE_RECENTERING_JUSTIFIED = YES`  
`NONLINEAR_DAE_FIXED_LAG_NEEDED = NOT_YET_JUSTIFIED`

No online recentering, E04-B, events, ML or network-parameter estimation was executed. No push was performed.

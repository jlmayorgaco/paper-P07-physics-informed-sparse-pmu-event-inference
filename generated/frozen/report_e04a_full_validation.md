# E04-A full validation

Overall status: **E04-A = PASS_WITH_CALIBRATION_LIMITATION**;
E04-A-RECONSTRUCTION = **PASS**; E04-A-UNCERTAINTY = **OVERCONSERVATIVE**.

B0/B1/B2 were scored on all 100 frozen TEST trajectories.  The final B3 batched
sweep also used all 100 trajectories and lags `0,1,3,5,10,15,30,60`; covariance
sequences were precomputed once and all means were processed in batch.

Best B3 lag by TVE: **0 frames (0 s)**.  B3 per-case, per-bus,
paired, uncertainty, runtime, and summary tables are in `output/results/`.

Minimum useful lag uses a documented practical-equivalence gate of 1% relative
TVE, 1e-4 degrees angle RMSE, and 2e-7 pu |V| RMSE versus the best lag.  The
overall minimum is **0 frames (0 s)**; the smallest
non-zero equivalent lag is **1**
frame(s), and no positive lag improves the best causal result.

The dense-vs-cached oracle remains exact at lags 1/3/10/30/60 on TEST_1.  The
reconstruction status is PASS.  Uncertainty status is OVERCONSERVATIVE when
coverage is materially above 95%; no Q/R recalibration was performed on TEST.

The lag covariance sequences were precomputed exactly once from the shared
Riccati/RTS recursion and are measurement-independent; exact lag means are
fully batched.  Coverage remains materially above the nominal 95% level, so
the uncertainty classification is OVERCONSERVATIVE and is not promoted to
CALIBRATED by this run.

Against the frozen E03 functional-residual ranking, best-B3 Spearman rho is
0.562500 for TVE and 0.336290 for angle RMSE (B1: 0.556/0.335;
B2: 0.563/0.336), indicating no structural change.

Top five buses at the best lag: [{'hidden_bus': 33, 'TVE_fraction': 0.00038278161197939506}, {'hidden_bus': 34, 'TVE_fraction': 0.0003805237987026524}, {'hidden_bus': 20, 'TVE_fraction': 0.00031745140166934433}, {'hidden_bus': 37, 'TVE_fraction': 0.0001500775387339058}, {'hidden_bus': 38, 'TVE_fraction': 0.00011808329225729444}].

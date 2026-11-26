# E04-A4 colored Gauss–Markov discrepancy

Only CAL_NOMINAL_V1 was used to fit PCA basis U, diagonal AR(1) F_c, Q_c and
shrunk residual R_epsilon. TEST remained frozen and was evaluated after rank
selection. No events, ML, B3 or physical benchmark changes were performed.

Selected model: **D2 GM-DIAG rank 4**, state dimension 118.
Selection rule: smallest rank within 0.20 NLL of the CAL minimum and within 10%
of the minimum ACF1.

CAL candidate table: `output/results/e04a4_model_selection.csv`.
The selected latent modes and dominant measurement channels are in
`output/results/e04a4_latent_modes.csv`.

D0 TEST raw/normalized NIS = 0.244929/0.00765403; D2 =
0.392343/0.0122607. D0 ACF1=0.6017,
D2 ACF1=0.5398; Ljung–Box p-values are
0 and 0.

D0/D1/D2 reconstruction, NLL, coverage and whiteness metrics are in
`output/results/e04a4_test_metrics.csv`. The augmented state changes only the
measurement model; hidden voltage remains `V0 + L_hidden x`.

The selected D2 changes TEST TVE from 0.0096344% to
0.0097879% and hidden-output NLL from -13.4766 to
14.991; reconstruction is therefore preserved within a small
perturbation, but marginal coverage is degraded by the uncalibrated augmented
covariance. Statuses: LOW_RANK_STRUCTURE = **SUPPORTED**;
GAUSS_MARKOV_DISCREPANCY = **PARTIAL**; INNOVATION_WHITENESS =
**IMPROVED_BUT_COLORED**; RECONSTRUCTION = **PRESERVED**. The residual is not
perfectly white and D2 is not a final probabilistic certificate.

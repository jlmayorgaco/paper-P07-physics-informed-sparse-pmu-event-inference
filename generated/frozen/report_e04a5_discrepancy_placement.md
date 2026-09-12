# E04-A5 — covariance audit and physical discrepancy placement

All fitting used only the disjoint `CAL_NOMINAL_V1` records. The frozen TEST
records and PowerDynamics benchmark were not modified. D2-M (measurement-space,
rank 4) is preserved as the baseline; D2-P uses a fixed sparse `B_phys` built
from the exported differential state inventory and fits only `G`, diagonal
`F_c` and `Q_c`.

## Covariance audit

Hidden covariance is computed as `L_hidden Pxx L_hidden'`, where `Pxx` is the
marginal physical block of the augmented covariance. No Schur complement is
used. In the deterministic toy, marginal trace = **3** while the
conditional trace = **2.63**, proving the audit distinguishes them.
The CAL D2-M component audit is in `e04a5_covariance_audit.csv`; aggregate
NEES-like ratio = **35.36**. Status: **COVARIANCE_BOOKKEEPING = PASS**;
the low hidden coverage is therefore a model-structural failure, not a
covariance extraction bug.

## CAL-only model selection

Candidate ranks 1/2/4 and selection are in `e04a5_model_selection.csv`.
Selected **D2-P rank 1**. The physical dictionary and dominant modes
are in `e04a5_physical_input_dictionary.csv` and
`e04a5_latent_physical_modes.csv`. No dense unconstrained `B_c` was fitted.

## Frozen TEST comparison

Metrics, hidden NEES and innovation ACF are in `e04a5_test_metrics.csv`,
`e04a5_hidden_nees.csv` and `e04a5_innovation_acf.csv`. D0 TVE =
0.0096344%; D2-M = 0.0097879%; D2-P =
0.00963785%. D2-M hidden NLL = 14.991; D2-P hidden
NLL = -13.475. D2-P raw/normalized NIS = 0.244928/
0.00765399; ACF1/ACF10 = 0.6021/0.1978.

Statuses: **MEASUREMENT_DISCREPANCY = SUPPORTED** (D2-M remains a useful
colored residual baseline); **PROCESS_DISCREPANCY = PARTIAL**;
    **JOINT_DISCREPANCY = NOT_NEEDED**; **HIDDEN_UNCERTAINTY = IMPROVED**;
**INNOVATION_WHITENESS = FAIL**; **RECONSTRUCTION = PRESERVED**.
Runtime and covariance size are in `e04a5_runtime.csv`.

Recommended next action (not executed): independently export/validate the
PowerDynamics input Jacobian before considering any joint D2-PM extension.

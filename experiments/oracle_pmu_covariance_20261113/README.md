# Independent PMU noise in the recurrent history bank

This replay uses the nominal R11 history bank on archived B01 MATCH parents.
The selected records are fixed in `protocol.json`. Each split has four
event parents (24 interventions) and two 600-s normal parents. Physical
linearizations are the archived clean-prefix fits shared across the four
arms. A new constant observational intercept is estimated from the first
300 reports of each noisy replay. This is a retrospective mechanism check.
The archived B01 results were available before this replay was designed.

Independent Gaussian innovations are added to each retained polar channel
at each report. Magnitude standard deviations are relative to the
clean-prefix reference and angle standard deviations use radians.
The 0.05% and 0.10% values denote the component scale, approximately
0.071% and 0.141% added RMS TVE for phasors at the magnitude reference.
This fixed-scale construction differs from N01's signal-dependent
magnitude perturbation. The added voltage angle errors are propagated
through the same 21-report ordinary causal quadratic difference weights
into frequency and ROCOF. Original B01 observations retain their archived
noise and model discrepancy. Noise draws are paired across arms and
scales. The addition models the observed channel contract after BUS39
current angle exclusion.

The family arm fits six variances from the 240 post-warmup filtered
prefix vectors. The shrinkage arm fits a Ledoit–Wolf correlation on the
same vectors after per-channel scaling and restores the estimated
marginal scales. Both use white observation covariance in the bank's
innovation coordinates. The structured arm estimates eight added
noise scales from voltage-angle differences after subtracting the
nominal angle difference variance. The oracle supplies those eight
scales from the generator. Structured and oracle both use the
corresponding full added-noise dynamics. The oracle is exact for the
added law, while the baseline instrumental and plant discrepancy
models remain approximations.

For the structured arms a shift register carries the previous 20
voltage-angle innovations. The current innovations contribute to the
observation and the next state. The correlated-noise Riccati equations
retain their cross covariance. In successor-state indexing the gain is
`(T P J.T + N) (J P J.T + R)^(-1)`, with `N = Cov(w,v)`.
Each arm rebuilds the four stationary regime covariances, the
mode-specific gains, and the conditional likelihood factors. The
boundary proposal keeps its original archived noise scaling. The
continuous recovery proposals and posterior use each arm's rebuilt
gains. External publication clocks read the bank's causal scores
without feedback into the bank. The bank's internal episode state
and confirmation parameters are shared.

The calibration threshold maximizes timely joint attribution subject
to at most one alarm per monitored normal hour, with extras and then
the threshold as tie breakers. Each arm has 0.3267 normal hours per
split, so a feasible arm must have zero calibration alarms. With no
TEST alarms, the one-sided 95% Poisson upper bound is still about
9.17 alarms/h. Report measured counts and exposure with that
uncertainty. Resample whole event parents for exploratory differences.

Run with the archived B01 read-only dependencies and Python packages
already used by the nominal runtime plus scikit-learn:

```powershell
python -B experiments/oracle_pmu_covariance_20261113/verify_noise.py
python -B experiments/oracle_pmu_covariance_20261113/run.py CAL
python -B experiments/oracle_pmu_covariance_20261113/run.py TEST
```

The runner writes under `build/oracle_pmu_covariance_20261113`. It verifies
bank and observation hashes against their READY records. The evaluator
reads event truth only after all predictions of that stage complete.
To verify and export compact results after TEST, run
`python -B experiments/oracle_pmu_covariance_20261113/seal_results.py`.
The export checks that every expected record finished and every TEST
threshold matches its CAL selection. The prediction hashes refer to
the per-record files retained under `build`.

`NUMERICAL_CHECK.json` records the completed numerical smoke. The
independent verifier compares the 21-report quadratic fit and original
observation filters against the augmented state equations over 80
reports. One full 120-s oracle replay checks the Riccati solution and
the recurrent inference path. Quantitative attribution comparisons
require the final CAL lock and TEST summary.

The 0.05% stratum completed its own calibration and TEST replay before
the 0.10% stratum. Its locked selection and all 48 job hashes are available
in `RESULTS_LOW.json`. The publication table uses that completed stratum
until the full result is exported.

# Relinearized recovery predictor: completed development comparison

**Question:** can a state-based refresh reduce the 3.19-degree phase error
after line restoration without observing subsequent hidden plant states?
The fixed predictor expands around the initial operating point; this can
misrepresent a finite excursion. The candidate refreshes its local DAE
reduction at its own predicted state every three reports and at known switches.
A nonlinear-observation-only control separates the dynamic and output changes.
Failure to halve recovery phase RMSE in any line case would reject the selected
candidate for this diagnostic. A passing result supports a predictor component,
not a detection, localization, Bayesian calibration or false-alarm claim.

## Frozen contract and result

`protocol.json` and all Julia code were hashed before execution. The Python
analyzer was hashed before trajectory comparisons. No coefficient or interval
was retuned after results. Julia ran with one computational/BLAS thread and
BelowNormal priority; C03 processes, locks, thresholds and outputs were not
changed. The actual frozen initial state, parameters and library hashes come
from the shared Hamiltonian reproduction capsule, not nominal inventory values.

Seven 12-s nonlinear trajectories and all predictor arms succeeded. Eight PMUs,
30 reports/s, exact post-switch samples, constant-impedance load law, provisional
BUS5 terminal 5-6 and BUS39 current-angle omission remain unchanged.

| Event | Fixed polar | Fixed dynamics, nonlinear output | Refresh 0.1 s | Refresh 1/30 s* |
|---|---:|---:|---:|---:|
| Line 23-24, 1 s | 3.190959 | 3.190878 | 0.138789 | 0.015520 |
| Line 23-24, 0.5 s | 2.541980 | 2.541306 | 0.246228 | 0.027945 |
| Line 23-24, 1.5 s | 3.389541 | 3.390431 | 0.180748 | 0.020301 |
| Line 26-28, 1 s | 3.211251 | 3.211849 | 0.150208 | 0.016919 |
| Bus 7, +10% | 0.118894 | 0.118893 | 0.00006589 | 0.00000749 |
| Bus 7, -10% | 0.119342 | 0.119341 | 0.00006641 | 0.00000755 |

Values are voltage-phase RMSE in degrees over eight PMUs, from OFF through
12 s, including the restored report. All events start at 2 s; load OFF is
6 s and line OFF follows the stated duration. *The one-report refresh is
a predeclared convergence diagnostic, not the selected primary arm.*

All 11 gates pass. The 1-s reference line improves by 95.65%; all four line
cases exceed the 50% gate. Changing only the observation does not fix the
dynamic phase error. Both load controls pass the 10% no-regression gate;
the normal control stays below 1e-8 pu. The old 3.19095895-degree baseline
is reproduced to the preset 1e-6-degree tolerance. Neither local recentering
nor switching resets the differential state.

The previously inspected reference line and load controls are development
replications. The two additional durations and other line were fixed before
their trajectories were generated. They are deterministic numerical checks,
not independent random parents. No p-values, confidence intervals or
population-level superiority claims are appropriate.

All 47 report coordinates are retained in `report_errors.csv`, by channel
family, active/recovery window and arm. The baseline uses first-order polar
observations; the others solve the nonlinear algebraic constraints at their
own states. Frequency and ROCOF all use the same ordinary 21-report polynomial
prediction, compared with the plant's frozen robust report generator.

`SUMMARY.json` contains per-case timings. For the reference line the 0.1-s
refresh physical predictor averaged 1.47 ms/report (p95 4.85 ms, max 12.33 ms)
in this execution. This excludes bank search, uncertainty and PMU report
formation, and includes encountered JIT overhead. It is not a controlled
hardware benchmark or a real-time claim for a bank of many hypotheses.

## Reproduction and seal

`RESULTS_SEAL.json` hashes 113 files, including shared Julia/reference inputs,
the old baseline metric and the new numerical outputs. This README and the
presentation builder are not part of that result seal. No C03 prediction or
outcome is used. Source code in `predict.jl` reads only the model, protocol and
initial state; `analyze.py` is the first component that compares predictions
with the nonlinear truth. There is no measurement correction or state oracle
after initialization. Failures would remain explicit cases in the denominator.

From the paper root, in a new isolated copy to preserve the sealed outputs:

```powershell
$env:JULIA_NUM_THREADS = '1'
julia --project=experiments/hamiltonian_f01_20261113/reproduction/environment experiments/relinearized_recovery_20261113/run_truth.jl
julia --project=experiments/hamiltonian_f01_20261113/reproduction/environment experiments/relinearized_recovery_20261113/predict.jl
python -B experiments/relinearized_recovery_20261113/analyze.py
python -B experiments/relinearized_recovery_20261113/check_supplied_claims.py
```

The Julia library setup is documented in the shared capsule. NumPy, SciPy,
pandas and Python versions are in `ENVIRONMENT.json`. To rebuild the table,
macros and figure directly from sealed results:

```powershell
python -B scripts/build_relinearized_recovery.py
```

New truth solves use the original tolerance and maximum step; the comparison
does not alter F01, C03 or any previous study. All gate values and the finer
refresh are specified in the immutable protocol.

## What integration still requires

The tested object is the conditional physical predictor. The full bank would
need covariance propagation for the state-dependent numerical flow, coherent
state/severity dependence, pre-update evidence and an unknown-event comparison
under newly calibrated alarm budgets. Replacing a Gaussian severity integral
with nonlinear prediction without changing the integration would be invalid.
It is therefore not enabled in R11 or C03. Graph screening, Hamiltonian model
reduction, IEKF updates and noise adaptation are separate hypotheses, not
explanations for this result.

The supplied theoretical claims are audited in `SUPPLIED_CLAIM_CHECKS.json`:
profiled sensor separation need not be submodular; latent spread can be
unobservable; the proposed KL bound fails for a covariance-matched mixture;
decaying event signatures need not supply unlimited information; and one-step
pruning mass does not bound future error after new evidence. These small
counterexamples prevent invalid guarantees from being imported into P07.

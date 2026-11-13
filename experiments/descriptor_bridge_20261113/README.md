# Verified descriptor bridge: nonlinear F01 to local PMU predictions

Development diagnostic, 13 November 2026. Six known-event, deterministic
trajectories; no CAL/TEST records, detector scoring, or C03 modification.

## What the supplied derivation establishes

`verify_three_bus.py` independently reconstructs the attachment's three-bus
constant-power AC model. Its closed/open equilibria, reduced A/B/C/D and
closed-mode exact discretization agree with the quoted numbers. Analytic DAE
Jacobian blocks agree with central differences to 7.85e-10 maximum absolute
error. This verifies the pedagogical example only. The supplied Kalman demo
was not rerun; it cannot establish IEEE39 detection performance. The document's
lossless potential is not the total Hamiltonian of F01's lossy controlled DAE.
Attachment identity is recorded in `ATTACHMENT_PROVENANCE.json`.

The linked historical descriptor exporter loads the library's example, not
our archived F01 operating point. The new extractor uses the frozen state,
parameters and library-source hashes via the existing reproduction capsule.
No prior extractor, frozen model, campaign or initial state was changed.

## Executed results

- 192 native coordinates split into 114 differential and 78 algebraic variables.
- Native and reduced derivative checks pass in intact and open-line modes:
  maximum relative directional discrepancy 3.9143e-8, gate 1e-5.
- Independent Python reconstruction of A/B/C/D from exported native blocks:
  largest absolute entry discrepancy 4.2633e-14.
- All six 12-s solves succeed, 1441 samples each, exact 0/12-s endpoints,
  no differential-state jump; maximum algebraic residual 8.7568e-11.
- Frozen terminal rows agree with selected native terminal currents to
  4.5212e-13 pu. BUS5 5-6 remains provisional; BUS39 current angle is excluded.
- Complex-voltage relative RMSE over eight PMUs during recovery is about
  1.48% for +/-1% loads, 14.8% for +/-10% loads, and 30.70% for line 23-24.
- These are NOT errors of the full bank's predicted polar PMU channels.
  The first-order polar observation avoids a spurious second-order magnitude
  change caused by converting a tangent complex voltage to polar exactly.
  For +10% load recovery its voltage-magnitude RMSE is 1.82e-6 pu and phase
  RMSE is 0.1189 degrees. Line recovery remains imperfect: 7.78e-4 pu and
  3.1910 degrees. Complete metrics for both signs, all sizes, both observation
  maps, ON/OFF windows and six channel families are in `run_v2/report_errors.csv`.

All events start at 2 s. Loads restore at 6 s; line restores at 3 s.
Active windows are [ON, OFF); recovery windows include OFF through 12 s.
RMS averages uniformly over reports and eight PMUs (seven current phases).
Relative complex RMSE divides by the nonlinear deviation from the matching
normal trajectory. It includes common phase motion; it is not magnitude
error, TVE from added noise, or a whitened likelihood metric. Normal has zero
event-response denominator and therefore no relative-error value.

The local predictor receives true source, times, magnitude and initial state.
It does not receive subsequent hidden states or measurements. No fitting or
error threshold was chosen after seeing trajectories. Trajectory selection and
derivative gates were frozen before solving; the analysis implementation was
frozen after derivative/solver status was available and before inspecting the
trajectory errors. The figure selects +10% and line cases descriptively; the
table and CSV retain every case. No independent replicates or significance
claim are available. No adaptation, Hamiltonian prior, unknown-event inference,
source discrimination or second-plant transfer is tested here.

## Failure ledger and provenance

The first extraction attempt failed its B/D derivative gates before any
trajectory was run. Julia captured a surrounding parameter vector in an inner
function; explicit local variables correct it in `extract_operators_v2.jl`.
Original code, log, freeze and failed outputs remain in `run/`. Version 2 passes
the original gates and writes separate `run_v2/` results. Do not use the failed
first extraction as evidence. Legacy energy/coordinate gate fields inherited
in `protocol.json` do not apply to this descriptor diagnostic; the applicable
gates are `derivative_gates` and solver/continuity checks stated above.

`RESULTS_SEAL.json` hashes 114 inputs/outputs, including the shared frozen
reference and Julia environment. It excludes this explanatory README and the
presentation-only figure builder. The saved arrays allow reconstruction without
Julia; the native state ordering and mass matrix are explicit.

## Reproduction

From the paper root (Julia 1.11.9, NumPy, SciPy, pandas and Matplotlib):

```powershell
python -B experiments/descriptor_bridge_20261113/verify_three_bus.py
julia --project=experiments/hamiltonian_f01_20261113/reproduction/environment experiments/descriptor_bridge_20261113/run_study_v2.jl
python -B experiments/descriptor_bridge_20261113/analyze_bridge.py
python -B scripts/build_descriptor_bridge.py
```

Run simulations only in an isolated copy: timings and floating-point results
may differ and the sealed run must remain intact. Instantiation and the frozen
Julia library requirements are documented in the Hamiltonian capsule README.
To regenerate the current table/figure only, run the last command; it checks all
sealed hashes and needs no simulation or scientific repository. Source ZIPs
include this study and its shared reference; ZIPs remain outside Git because
of Overleaf's per-file limit.

## Scientific consequence

The derivation now has an executable check against the actual plant. It also
exposes finite-event error, especially for the line. This strengthens the
method's traceability and limits; it is not a new accuracy result or novelty
claim. The next independent model-improvement comparison would need to freeze
a gauge-aware/nonlinear observation or relinearization variant, propagate its
uncertainty consistently, and compare at a calibrated alarm budget on new data.
That work is not silently added to C03.

# Rotor Hamiltonian, graph power ports, and inference: executed F01 controls

Problem: explain recovery and source attribution without adding redundant PMU evidence.
Gap: a lossless swing Hamiltonian is not the full Sauer–Pai/AVR/TGOV1 DAE.
Mechanism: exact mechanical torque ports and graph terminal powers, with a canonical
rotor-coordinate representation of the same predictor.
Falsifying controls: full-plant work/power/continuity checks and native-versus-scaled
nominal predictor comparisons with unchanged observation likelihood.
Consequence: retain valid mechanical interpretation; claim no attribution gain from
an invertible coordinate change and add no independent energy factor.

## Scope and evidence

- Four **new nonlinear F01** trajectories: normal, bus-7 P/Q setpoints +10% and
  -10% at 2–6 s, line 23–24 (edge 38) open at 2–3 s. Duration 12 s each.
  ZIP loads remain voltage-dependent. Each starts from the exact archived state
  and parameter vector; no retuning, no dynamic resets. 1,441 samples per case
  at 120 Hz, solver maximum step 1/240 s, tolerances 1e-10.
- All four solvers pass. Mechanical torque residual max 1.010e-15; electrical
  generation/load/loss mismatch max 4.129e-11 system pu; no dynamic-state jump.
  Kinetic work discrepancy max 0.010594 MJ with trapezoidal integration on smooth
  segments (no interpolation across switching). This is a consistency audit,
  not four independent statistical replicates or a PMU detection experiment.
- Canonical rotor coordinates preserve all 18 nominal source predictions to
  relative error 1.530e-14; no source decision differs in 180 paired Gaussian
  known-signature draws. This is not a full-bank rerun. The maximum absolute
  log-likelihood difference 1.907e-6 **fails** the preset 1e-6 gate; it is not
  hidden or relaxed. The longdouble follow-up also fails: this Windows NumPy
  build has 64-bit longdouble, so it did not increase precision. See
  `run/NUMERICAL_LIMITATION.json`. Posterior differences were negligible, but
  no all-gates-pass claim is made for the coordinate control.

No global Hamiltonian or Lyapunov function is claimed for the full lossy DAE.
The kinetic subsystem retains electromagnetic and governor torque as ports.
No energy prior, learned correction or extra likelihood was added to R11.
Current results do not establish a detector accuracy or false-alarm benefit.
C03 was neither modified nor run; its TEST was not read. The nominal predictor
snapshot is the pre-existing paper-local archive, not a new C03 extraction.

## Reproduction

From the paper root:

```
python experiments/hamiltonian_f01_20261113/audit_physics.py
python scripts/build_hamiltonian_results.py
```

The builder verifies `RESULTS_SEAL.json`. Frozen sources, initial conditions,
parameters, network, dynamic-state ordering and the Julia environment are bundled.
Numerical audits require Python, NumPy, pandas, SciPy; the plot adds Matplotlib.
For a full nonlinear repeat, use a **fresh copy** of this directory, preserving
the original run elsewhere, and create `reproduction/diagnostics`. Install the
Julia 1.11.9 environment dependencies from the included Project/Manifest, then:

```
$env:P07_HAMILTONIAN_RUN = '<absolute fresh copy>/reproduction'
$env:JULIA_NUM_THREADS = '1'
julia --project='<absolute fresh copy>/reproduction/environment' '<absolute fresh copy>/run_physics_v3.jl'
```

The initializer checks the IEEE39 package source hashes and recovers the archived
state and parameters before using their exact saved values. The first runner
failed on a controlled-machine namespace lookup; the second failed on Julia's
ambiguous `0.=>` syntax. Both failed before any trajectory, are preserved, and
did not cause a scenario to be dropped. V3 changes only those runner errors;
the physical protocol is unchanged. Original freezes and failure logs remain.

For the coordinate control, use a fresh copy with the archived sibling
`channel_information_20261112/input_snapshot.npz` and without its prior
COORDINATE_FREEZE files. Execute `check_coordinates.py`; its nonzero exit is the
recorded absolute-tolerance failure, not a hidden test success.

## Relation to the supplied Kirchhoff derivation

The supplied three-bus constant-power/classical-machine example is pedagogical;
its numeric A/B/C/D matrices were not imported as IEEE39 operators. F01 uses
114 differential states, per-unit absolute rotor speed, a mass-normalized DAE,
impedance loads, transformer/charging terminal stamps and instrument memory.
For a moving expansion trajectory, the affine term must include minus its time
derivative; the paper's derivation uses a fixed physical reference per mode.
Rotor speed must not replace bus-voltage-phase frequency. These distinctions
are stated in the manuscript and the actual frozen implementation is retained.

# Conditional decision bounds and attachment audit

This is a mathematical implementation check, not a detection campaign.
The 11 supplied attachments contain seven distinct SHA-256 contents; the
Kirchhoff derivation is identical to the previously verified attachment.
`INPUT_PROVENANCE.json` maps all copies without reproducing their text.

## Executed checks

To reproduce, use a new isolated copy and run from its repository root:

```powershell
python -B experiments/decision_bounds_20261113/check_v2.py
```

The protocol, seed, tolerances, code and four saved native-operator inputs
are hashed before the numerical run. `RESULTS.json` records seven passing
gates, 2,000 Gaussian perturbation checks with zero bound violations,
918 certified winners in a separate synthetic interval fixture with zero
wrong certificates, and exact agreement of event-mass/quadrature intervals
with exhaustive corner enumeration. These counts are implementation checks,
not empirical attribution coverage, confidence intervals or a theorem proof.

`bounds.py` implements a mean-and-covariance Gaussian score radius, strict
winner certification, normalized event-group mass intervals, and positive
quadrature intervals. It accepts error bounds; it does not produce them
from a DAE. Relative covariance error at least one returns an unbounded
radius, no winner and an uninformative mass interval. It cannot certify
omitted hypotheses, quadrature discretization error or a publication clock.

The native F01 operators are read from the previously sealed descriptor
study. They are not regenerated. Their 114-by-114 dynamics are nonsymmetric;
the rectangular-voltage observation matrix is 78-by-114. Neither is an
undirected graph Laplacian. Both topologies have one eigenvalue numerically
near zero. A strict full-state decay rate is therefore not established;
no positive-rate Lyapunov certificate is asserted. Reference/gauge handling
and the actual PMU observation map must be checked before reducing modes.

The other checks show that labelled sensors remain distinguishable when
an automorphism permutes them, a full pi-line stamp can have complex rank
two, a constant independent bias accumulates Gaussian information linearly
in the number of reports, and clock-difference variance depends on covariance.
The recovery-information identity is checked with singular state covariance
using its factor form, without inverting that covariance.

## Failure ledger

The first run of `check.py` completed calculations but failed to serialize
NumPy boolean gates (`TypeError: Object of type bool is not JSON serializable`).
Its code and `EXECUTION_FREEZE.json` are preserved. `check_v2.py` converts
those booleans before JSON output; `EXECUTION_FREEZE_V2.json` records the
change before rerunning. Mathematical inputs, checks and thresholds are
unchanged. No failed physical simulation or observation was discarded.

## Integration boundary

Appendix U states the conditional score bound and the distinction between
preserving a winner and preserving normalized publication mass. The complete
proof and review decisions are in `docs/IDEAS_SECOND_WAVE_AUDIT_20261113.md`.
There is no new calibration, attribution result, automatic memory deletion,
graph screening, IEKF, Hamiltonian reduction or C03 modification.

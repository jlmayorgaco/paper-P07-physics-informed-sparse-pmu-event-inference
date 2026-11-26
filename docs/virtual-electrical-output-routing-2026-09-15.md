# Virtual electrical output routing on 2026-09-15

## Scientific decision

The pasted proposal is adopted as an output-map clarification, not as a new empirical result or a change of title. The estimator should recover a consistent physical state and derive electrical quantities from that state and the candidate network mode. It should not train independent regressors for voltage magnitude, angle, current, power, frequency, and ROCOF.

The phrase “eight physical PMUs to 39 virtual PMUs” is retained only as an internal intuition. In the manuscript, “candidate-conditioned virtual electrical outputs” is more accurate because the current campaigns validate hidden complex voltage, not every channel a standards-conforming PMU would report.

## Integrated in the main paper

- Rectangular complex voltage is the primary estimated electrical target.
- Bus injection, oriented branch-terminal current, and complex power are deterministic candidate-conditioned state functionals.
- Derived outputs share the joint posterior and do not require separate learned estimators.
- Model averaging must include within-candidate state uncertainty and between-candidate event ambiguity.
- The empirical boundary remains explicit: only hidden voltage is validated by the state-reconstruction campaigns.

## Integrated in the supplement

- The electrical model defines one candidate-conditioned output map for voltage, current, power, and smooth-mode phase derivatives.
- Model-implied frequency and ROCOF are distinguished from the output of a particular causal PMU estimation algorithm.
- A positive-sequence phasor can synthesize a balanced ABC waveform for visualization, but not three independent phase states.
- Conditional output covariance may be propagated by posterior samples or a local Jacobian; total covariance then adds the between-support term.
- Complex phasors are averaged in rectangular coordinates before converting to magnitude and phase.

## Deliberately not promoted

- No title or abstract claim of 39 validated virtual PMUs.
- No current, active/reactive power, frequency, or ROCOF accuracy number without a frozen test.
- No use of ideal phase derivatives as evidence for a standards-conforming PMU frequency channel.
- No differentiation across a fault or topology switch, where algebraic variables may jump.
- No independent ABC reconstruction claim from a positive-sequence plant.
- No current-relative-error metric without an absolute or base-normalized companion near zero current.

## Required evidence

1. Freeze bus and branch orientations, base quantities, and candidate-dependent topology for every derived output.
2. Score branch-terminal current, bus injection, active/reactive power, frequency, and ROCOF on disjoint nonlinear trajectories.
3. Reproduce the causal PMU backend filtering when evaluating frequency and ROCOF.
4. Report trajectory-level error intervals and coverage, including near-zero-current safeguards.
5. Compare candidate-winning and model-averaged outputs to quantify the cost of source ambiguity.
6. Use a sequence-complete or phase-domain plant before claiming unbalanced phase reconstruction.

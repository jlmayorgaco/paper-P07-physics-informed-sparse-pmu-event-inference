# Routing of constrained geometry and boundary-aware evidence

## Scientific diagnosis

The update closes a real gap in the previous theory. Signed/interior event
coordinates produce tangent subspaces, but one-sided fault, trip, shedding, and
outage-severity coordinates produce tangent cones at the nominal boundary. The
span calculation remains a useful relaxation: a positive relaxed margin
certifies physical separation, while a zero relaxed margin does not prove a
one-sided ambiguity. This distinction also limits earlier shared-source,
principal-angle, dimensional, and spark interpretations.

The Bayesian consequence is equally specific. Nested supports cannot be
separated by best-fit distance because the added amplitude can be zero. Proper
spike-and-slab evidence supplies the missing volume penalty. For one local
Gaussian amplitude, a half-normal slab gives the exact directional correction
`BF_plus = 2 Phi(z) BF_signed`; for a nonlinear identifiable model, the leading
cone--Laplace evidence also contains a Gaussian cone probability. Neither result
is presented as an evaluated multi-family IEEE 39-bus estimator.

## Routing decision

| Material | Main article | Supplement | Deferred or excluded |
| --- | --- | --- | --- |
| Tangent cone versus tangent span | Compact physical-margin equation and inequality | Local cone-distance theorem and proof | IEEE 39-bus cone margins remain unexecuted |
| Conditional support geometry | Interpretation of non-nested support difficulty | Exclusive-support quotient, conditional matrix, eigenvalue and principal-angle results | Nearest-competitor composition remains empirical |
| Shared one-sided sources | Qualification of the cancellation claim | Exact feasible difference set and counterexample mechanism | No universal amplitude-independence claim |
| Enrichment and nested supports | Retained cardinality argument | Cone-aware statements | Prior calibration is not implied |
| One-sided Bayes factor | Boundary-aware design statement only | Exact half-normal formula and proof | Not an evaluated fault/outage/trip result |
| Cone--Laplace evidence | No new empirical claim | Explicit assumptions, proof, orthant factor, and singular counterexample | Joint Hybrid-DAE evidence remains unexecuted |
| Supplied numerical files | No | No | `sandbox:/mnt/data` CSV and figures are unavailable as repository evidence |
| Independent toy checks | No | Two generated compact tables | Explicitly labeled non-IEEE-39 evidence |

## Corrections to earlier wording

1. Shared-source cancellation is amplitude independent only for signed/interior
   coordinates or when the relaxed optimum is physically feasible.
2. A zero principal angle from a literal shared source is removed before
   comparing exclusive components.
3. A dimensional span intersection or `spark <= 2K` does not by itself provide
   a feasible nonnegative ambiguity.
4. A zero span-relaxed margin is inconclusive for one-sided events; the cone
   margin can be positive.
5. Regular Laplace and regular chi-square asymptotics do not apply blindly at a
   one-sided or higher-order singular boundary.

## Verification added

`scripts/verify_cone_bayes_identities.py` regenerates twelve deterministic
checks. They cover the conditional quotient, worst coefficient direction,
conditional angle, cone versus span, shared-amplitude dependence, enrichment,
nested supports, signed and half-normal Bayes factors, the broad-nuisance
profile limit, the boundary likelihood-ratio mixture, first-order cone--Laplace
error, and quartic singular scaling. The build runs this script before LaTeX.

## Evidence still required

1. Declare the physical severity domain for every event family and simulator
   callback.
2. Build the actual IEEE 39-bus nuisance/event tangent dictionary and compare
   span and cone nearest competitors under the frozen covariance.
3. Test proper prior and slab-scale sensitivity on held-out nonlinear events.
4. Distinguish redundant coordinates from genuine higher-order singularity in
   every candidate Hessian.
5. Validate cone--Laplace evidence against exact or high-accuracy integration on
   representative nonlinear Hybrid-DAE candidates before using it operationally.

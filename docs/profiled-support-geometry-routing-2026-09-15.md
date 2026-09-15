# Routing of the profiled support-geometry update

## Scientific diagnosis

This update contains one result that materially sharpens the paper's central
argument: local geometry can distinguish non-nested physical explanations, but
best-fit distance cannot by itself select cardinality when support models are
nested. The corresponding support-to-support projection also separates two
failure mechanisms that were previously grouped together: low event visibility
after nuisance removal and aliasing between visible event signatures. These are
theoretical results with deterministic toy validation. They are not new IEEE
39-bus or ANDES empirical results.

The two pasted copies of the reported four-experiment summary are byte-identical.
Their links point to `sandbox:/mnt/data/...`, and the referenced CSV, code, and
figures are not present in the attachments, Downloads, the legacy repository, or
this paper repository. Their numerical values therefore were not imported as
evidence. The fully specified algebraic cases were instead independently
recomputed by the repository's deterministic validation script.

## Routing decision

| Material | Main paper | Supplement | Excluded or deferred |
| --- | --- | --- | --- |
| First-order support-to-support margin | Compact equation in Section IV | General theorem, proof, PSD support matrix, and rank-deficient interpretation | IEEE 39-bus coefficient remains unvalidated |
| Shared-source cancellation | Short interpretation tied to weak pair ambiguity | General intersection/exclusive-source corollary | Do not claim that the nearest competitor always shares a source |
| Visibility versus aliasing | Results interpretation | Single-source norm/angle decomposition | Requires future source-wise empirical classification |
| Nested supports | Explicit reason cardinality needs integrated evidence | Zero-infimum result and closure qualification | Pure distance must not be called a cardinality criterion |
| Bayesian Occam mechanism | One paragraph in the evaluated likelihood section | Existing exact Bayes factor and support-evidence integrals | No generic Laplace claim is needed for the evaluated GH31 estimator |
| Rank-deficient nuisance | No additional main-paper detail | Constant-rank chart and equivalence-class interpretation | Individual nuisance coordinates remain uninterpretable without rank evidence |
| Degenerate second order | Boundary sentence only | Intrinsic `gamma2` and the condition for vanishing second order | No IEEE 39-bus curvature mechanism claim |
| Controlled numerical values supplied through inaccessible links | No | No | Excluded as received evidence |
| Independently recomputed toy checks | No | Generated compact table | Explicitly labeled non-IEEE-39 evidence |

## Independent checks added

The repository now regenerates nine deterministic checks: the branch primitive,
the regular two-frame DAE coefficient and slope, the shared-tangent second-order
coefficient and slope, rank-deficient projection invariance, shared-source
cancellation, competitor-enrichment monotonicity, nested-support zero margin, the
principal-angle identity, and nuisance-enlargement monotonicity. All values flow
from `scripts/verify_theory_identities.py` to `generated/theory_checks.json` and
`tables/generated/theory_validation.tex`.

## Remaining development

1. Recover the exact nonlinear controlled-DAE definition, code, seeds, solver
   tolerances, CSV, and plots referenced by the pasted report before citing that
   experiment.
2. Construct the actual IEEE 39-bus nuisance Jacobian and event tangent dictionary
   under the audited callback--solve--sample semantics.
3. Freeze candidate pairs spanning large, small, and near-zero `gamma1`, then test
   distance, optimal nuisance motion, and normal-residual convergence jointly.
4. Evaluate the now-derived tangent-cone support margin on the IEEE 39-bus event
   families and record when the relaxed subspace optimum violates physical sign
   or amplitude constraints.
5. Test whether the two predicted mechanisms—nuisance invisibility and event
   aliasing—explain held-out nonlinear outcomes prospectively.
6. Preserve cardinality as integrated Bayesian model selection. Do not replace the
   existing GH31 evidence with a geometric threshold.

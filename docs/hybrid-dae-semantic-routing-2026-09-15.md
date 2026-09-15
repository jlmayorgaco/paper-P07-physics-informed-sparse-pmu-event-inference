# Routing of the September 15 hybrid-DAE theory update

## Scientific diagnosis

The update closes a useful local mathematical layer but does not add a new frozen
IEEE 39-bus result. Under a regular index-one, fixed-time, impulse-free contract,
the differential state is continuous, the algebraic state moves to the
post-event consistency manifold, and both the direct PMU signature and the
initial dynamic forcing have explicit derivatives. The profiled first-order
coefficient is also a clean bridge from event-manifold geometry to a falsifiable
distance-scaling experiment. What remains open is whether the current ANDES
callback, consistency solve, and first retained frame implement that contract to
the claimed numerical tolerance. The manuscript must therefore separate theorem,
simulator semantics, and frozen empirical evidence.

## Routing decision

| Item | Main paper | Supplement | Exclude from manuscript | Further development |
| --- | --- | --- | --- | --- |
| Differential-state continuity and post-event algebraic consistency | One compact contract equation in Section III | Full local theorem and proof | No | Log callback, right limit, and first retained frame separately |
| First- and second-order algebraic consistency terms | Interpretation only through the contract | Full formulas for `z1` and `z2`, residual orders, and proof | No | Compare analytic terms with an independent algebraic solve |
| Direct PMU signature versus dynamic forcing | One sentence pointing to the distinction | Explicit formulas and finite-horizon interpretation | No | Test both contributions under the actual PMU operator |
| Profiled first-order separation `gamma1` | Compact equation in Section IV and an explicit non-validation sentence | Full constant-rank result, proof, invariance, and higher-order boundary | No | Freeze the `distance^2 / amplitude^2` convergence test |
| Callback residual scaling and Taylor ratios | No | Computational closure table only | Do not write as a result | Run symmetric amplitude grids and verify slopes 1, 2, 3 or ratios 2, 4, 8 |
| Load, generation, and continuous line-admittance validation | No | Required-family row in closure table | Do not imply completed | Execute under one semantics/tolerance manifest; do not use a binary full outage for Taylor validation |
| Full second-order dynamic sensitivity | No | Mark open | Do not claim closure while the reported 2--6% discrepancy is unresolved | Instrument the event map and isolate derivative, initialization, and solver-tolerance error |
| Illustrative values such as 0.37 and 0.12 | No | No | Exclude because they are not artifacts | Replace only with frozen generated values if the experiment is run |
| Internal labels such as `FOUNDATIONS=CLOSED` | No | No | Exclude as workflow metadata | Track in project documents, not scientific prose |

## Required computational gate

1. Record the pre-event state, callback-stored state, independently solved
   post-event algebraic state, and first retained frame.
2. Check the post-event constraint residual against solver tolerance rather than
   against an arbitrary visual threshold.
3. Compute analytic `z1` and `z2` from the same equations and parameterization used
   by the simulator.
4. Use central finite differences on a decreasing symmetric amplitude grid; report
   absolute, relative, and physically normalized errors.
5. Verify residual and state-approximation orders before testing the full dynamic
   tangent.
6. Repeat for load change, generation change, and a continuous branch-admittance
   perturbation.
7. Freeze candidate pairs, operating points, whitening, nuisance space, tolerances,
   and the independent experimental unit before testing convergence to `gamma1`.

## Claim discipline

- The local consistency theorem is a specialized implicit-function result, not a
  claim of fundamental mathematical novelty.
- The current numerical load dictionary remains a simulator-derived finite
  difference tangent; it is not relabeled as an analytic descriptor-DAE tangent.
- Instantaneous invisibility at the retained PMUs does not imply finite-horizon
  nonidentifiability because the reduced dynamic forcing can remain nonzero.
- The retrospective profiled-distance association does not validate the local
  `gamma1` convergence law.
- No new quantitative result enters a table, figure, abstract, or conclusion until
  it has a frozen manifest and generated artifact.

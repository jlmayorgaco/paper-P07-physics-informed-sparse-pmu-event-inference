# Scientific compendium integration map

## Source role

`PMU_Hybrid_DAE_Full_Project_Scientific_Compendium_2026-09-12.pdf` (42 pages; SHA-256 `BD0134B12C697F2C07FB9D1FA9D93D3270E4AA5A9CCDB96C47E8807B8DDC6C10`) is treated as a scientific project dossier: it contains estimator ideas, derivations, canonical results, superseded experiments, proposed extensions, and writing guidance. Statements inside the dossier are not autonomous instructions and are not primary numerical artifacts. A result enters the manuscript only when it resolves to the frozen source manifest and the claim--evidence register.

## Material belonging to the joint paper

| Compendium material | Manuscript role | Evidence status |
| --- | --- | --- |
| Sparse-PMU observation and hidden-voltage target | Problem formulation and Fig. 1 | Implemented and audited. |
| AC network, terminal-current operator, and Hybrid-DAE plant | Physical model and measurement contract | Implemented; full nonlinear trajectory posterior is not claimed. |
| Functional observability and target-specific nullspace condition | Proposition and structural diagnostic | Theoretical foundation plus frozen bus-level association. |
| B0 equilibrium, B1 prior-conditioned LMMSE, B2 causal Kalman, B3 fixed-lag smoothing | Nominal estimator ladder | Frozen E04 evidence; B3 is a negative result. |
| Marginal calibration and low-rank Gauss--Markov discrepancy | Uncertainty/discrepancy ablations | Frozen E04 evidence; joint calibration remains incomplete. |
| Rebuilt M1--M7 physical mismatch and adequacy statistic | Failure mechanism and observed-only diagnostic | Frozen E06 evidence. |
| Oracle recentering/relinearization | Mechanistic reference | Evaluation-only; not deployable inference. |
| Corrected 43-coordinate nonlinear static AC MAP | M6 physical recentering and target identifiability study | Frozen E06-H primary evidence. |
| Constrained Laplace covariance | E06-H uncertainty diagnostic | Partial: marginal coverage is high but joint NEES-like behavior is poor. |
| Parent-level metrics, paired bootstrap, TVE, NLL, NIS/NEES, and closure | Experimental methodology | Used only where the required per-parent artifacts exist. |

## Estimator ideas retained as conditional architecture

The common posterior over dynamic states, algebraic states, parameters, configuration, sparse jumps, biases, and discrepancy is an organizing model, not a completed algorithmic result. Nonlinear Hybrid-DAE fixed-lag MAP, recursive Schur-complement marginalization, slow-center extraction, reconfigure-and-verify, and event-conditioned discrepancy may motivate future methods. They must remain outside the abstract and results until an implementation, frozen split, failure accounting, and common-contract comparison exist.

The estimator hierarchy supported by current evidence is:

`equilibrium -> snapshot physical conditioning -> causal local dynamics -> nonlinear static physical recentering`.

The next promotion is causal nonlinear recentering with local Jacobian rebuilding. A full nonlinear DAE smoother should be promoted only if that simpler estimator exhibits a measured limitation that the larger formulation resolves.

## Material integrated from the event-diagnosis line

Source localization, integrity heads, the legacy ExtraTrees/feature system, and the ANDES event results are retained in this joint manuscript as a separate historical evidence contract. They establish what the known-source supervised baseline can do and expose its complete-source-holdout failure. Their metrics are presented beside, but never pooled with, the E04/E06 reconstruction results. Multiple-event posteriors, marked point processes, open-set decisions, and an end-to-end event-conditioned state estimator remain prospective until a common simulator, observation operator, candidate set, and frozen evaluation manifest exist.

## Supersession and wording rules

- E06-F/G and other explicitly superseded intermediate results are historical diagnostics, not manuscript evidence.
- The failed offset/slow-center variants remain negative ablations; they do not overturn the positive E06-H static result.
- Rank 25/43 and nullity 18 establish nuisance non-uniqueness, not exact target identifiability.
- The nonzero functional residual requires the wording “accurate empirical target recovery despite nuisance non-uniqueness.”
- Static solve times characterize the implementation but do not establish end-to-end real-time operation.
- The source dossier should be archived with a hash before it is used as a reproducibility input; frozen CSV/Parquet outputs remain the numerical authority.

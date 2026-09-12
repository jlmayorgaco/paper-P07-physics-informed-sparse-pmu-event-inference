# Paper outline and evidence boundary

## Identity

- **Venue:** IEEE Access
- **Article type:** Research Article
- **Working title:** *Physics-Informed Bayesian Event Inference and Localization from Sparse PMU Measurements*
- **Central question:** Can a sparse, time-varying PMU network infer physical sources that were not learned as source labels, identify when its measurements cannot separate competing sources, and reuse validated physical knowledge across sensors without a fixed monolithic input architecture?

## Argument

The paper treats a disturbance as a physical intervention with PMU-projected consequences, rather than as a source label in a fixed feature space. This framing makes three distinctions explicit: event recovery is not alarm calibration, known-source classification is not source-generalizable physical inference, and a forced Top-1 source is not an honest decision under insufficient observability. The proposed hybrid layer is source-agnostic: it learns candidate-specific mismatch between a DAE prediction and PMU evidence rather than mapping an observation directly to a source label. A controlled knowledge-transfer concept remains conditional on Campaign C.

## Section plan

| Section | Role in the paper | Evidence status |
| --- | --- | --- |
| I. Introduction | State the operational problem, historical motivation, and falsifiable contributions. | Historical motivation is traceable only after archival sources are imported. |
| II. Related Work and Research Gap | Compare PMU diagnosis, model-based inference, observability, physics-informed learning, open-set/domain generalization, and edge intelligence by capability. | Dedicated literature matrix and verified citations required. |
| III. Problem Formulation | Define the DAE, physical intervention, measurement integrity, time-varying PMU set, and target outputs. | Conceptual and mathematical. |
| IV. Diagnosability | Define projected signatures, pairwise information, expected evidence, ambiguity, and candidate sets. | Theoretical under explicit assumptions; empirical bridge pending Campaign B. |
| V. Hybrid Causal Bayesian Inference | Specify causal screening, DAE refinement, source-agnostic learned discrepancy, fusion, posterior updating, and abstention. | Method contract; implementation evidence pending. |
| VI. Edge Knowledge | Define validated physical knowledge, provenance, and model-mediated transfer. | Include as a main contribution only after Campaign C. |
| VII. Experimental Protocol | State reproducible contracts for campaigns A--D, baselines, and metrics. | Design only until runs are frozen. |
| VIII. Results | Report question-by-question evidence and retain negative results. | No proposed-method numbers until experiments exist. |
| IX. Discussion | Separate principles, established evidence, unvalidated deployment work, and limitations. | Interpretive, bounded by results. |
| X. Conclusion | State the contribution and evidence boundary concisely. | No unearned deployment claim. |

## Page budget

The target is approximately 19--20 IEEE Access pages including references and any biographies. The intended allocation is 0.5 page for front matter, 1.25--1.5 for the introduction, 1.5--1.75 for related work, 1.25--1.5 for formulation, 1.5--1.75 for diagnosability, 1.75--2.0 for hybrid inference, 0.75--1.0 for conditional knowledge transfer, 1.4--1.6 for experimental methodology, 4.0--4.5 for results, 0.75--1.0 for discussion, 0.3--0.4 for the conclusion, about 2 for references, and about 0.5 for biographies. Results must occupy more space than Related Work and roughly as much as the main theory plus method. This is a planning target, not permission to add filler.

## Initial-draft baseline

This revision is an evidence-bounded first manuscript draft, not a completed empirical paper. It contains the problem statement, scoped local propositions, a hybrid method contract, and reproducible experiment design, but no proposed-method numerical result, performance chart, or completed results table. The current compiled length is therefore intentionally below the target; frozen Campaign A--D evidence, source-backed related-work table entries, figures, tables, final author metadata, and biographies are the appropriate ways for the paper to grow. [`PAPER_GUIDELINES.md`](PAPER_GUIDELINES.md) is the governing contract for those additions.

## Terminology commitments

- Call the proposed inference **Bayesian** only when a stated likelihood, prior, and posterior update are used.
- Call it **causal** only when every decision uses measurements available no later than its decision time.
- Describe computations as **distributed** only when local work and evidence fusion are genuinely partitioned.
- Call a source **held out** only when it was excluded from every source-labeled training and tuning set.
- Call a method **physics-informed learning** only when the learned component has an explicit, testable role relative to the physical model; in P07, it is a source-agnostic discrepancy likelihood rather than a source classifier.
- Call RAW0001 a known reference simulation and retrospective evaluation, never field data or independent validation.

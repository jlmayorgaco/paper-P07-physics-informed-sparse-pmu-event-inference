# Paper outline and evidence boundary

## Identity

- **Venue:** IEEE Access
- **Article type:** Research Article
- **Working title:** *Physics-Informed Bayesian Event Inference and Localization from Sparse PMU Measurements*
- **Central question:** Can a sparse, time-varying PMU network infer physical sources that were not learned as source labels, identify when its measurements cannot separate competing sources, and reuse validated physical knowledge across sensors without a fixed monolithic input architecture?

## Argument

The paper treats a disturbance as a physical intervention with PMU-projected consequences, rather than as a source label in a fixed feature space. This framing makes three distinctions explicit: event recovery is not alarm calibration, known-source classification is not source-generalizable physical inference, and a forced Top-1 source is not an honest decision under insufficient observability. A controlled knowledge-transfer concept is included only as a future contribution pending Campaign C.

## Section plan

| Section | Role in the paper | Evidence status |
| --- | --- | --- |
| I. Introduction | State the operational problem, historical motivation, and falsifiable contributions. | Historical motivation is traceable only after archival sources are imported. |
| II. Related Work and Research Gap | Compare PMU event identification, dynamic estimation, observability, imperfect data, and edge intelligence by capability. | Literature citations verified incrementally. |
| III. Problem Formulation | Define the DAE, physical intervention, measurement integrity, time-varying PMU set, and target outputs. | Conceptual and mathematical. |
| IV. Diagnosability | Define projected signatures, pairwise information, ambiguity, and candidate sets; prove the two stated local results. | Theoretical under explicit assumptions. |
| V. Causal Bayesian Inference | Specify causal screening, refinement, fusion, posterior updating, and abstention. | Architecture; implementation evidence pending. |
| VI. Edge Knowledge | Define validated physical knowledge, provenance, and model-mediated transfer. | Controlled proof of concept pending Campaign C. |
| VII. Experimental Protocol | State reproducible contracts for campaigns A--D, baselines, and metrics. | Design only until runs are frozen. |
| VIII. Results | Report question-by-question evidence and retain negative results. | No proposed-method numbers until experiments exist. |
| IX. Discussion | Separate principles, established evidence, unvalidated deployment work, and limitations. | Interpretive, bounded by results. |
| X. Conclusion | State the contribution and evidence boundary concisely. | No unearned deployment claim. |

## Page budget

The target is approximately 20 IEEE Access pages including references and any biographies. The intended body allocation is 0.5 page for front matter, 1.2 for the introduction, 1.3 for related work, 1.8 for formulation, 2.3 for diagnosability, 1.6 for inference, 1.2 for edge knowledge, 1.7 for protocol, 4.0 for results, 0.8 for discussion, and 0.3 for the conclusion. This is a planning target, not permission to add filler.

## Initial-draft baseline

This revision is an evidence-bounded first manuscript draft, not a completed empirical paper. It contains the problem statement, two explicitly scoped local propositions, method contract, and reproducible experiment design, but no proposed-method numerical result, performance chart, or completed results table. The current compiled length is therefore intentionally below the 20-page target; frozen Campaign A--D evidence, source-backed related-work table entries, figures, tables, final author metadata, and biographies are the appropriate ways for the paper to grow.

## Terminology commitments

- Call the proposed inference **Bayesian** only when a stated likelihood, prior, and posterior update are used.
- Call it **causal** only when every decision uses measurements available no later than its decision time.
- Describe computations as **distributed** only when local work and evidence fusion are genuinely partitioned.
- Call a source **held out** only when it was excluded from every source-labeled training and tuning set.
- Call RAW0001 a known reference simulation and retrospective evaluation, never field data or independent validation.

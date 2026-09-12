# P07 paper guidelines, v1.0

**Status:** binding manuscript contract for the next research and writing stages.
**Scope:** IEEE Access research article on source-generalizable PMU event inference.
**Evidence rule:** a design, planned baseline, or campaign is never reported as an implemented method or a measured result until its source, manifest, code revision, and frozen output are linked in [`claims-and-evidence.md`](claims-and-evidence.md).

## 1. Central claim and non-negotiable comparison

P07 asks whether a physics-informed hybrid inference system can localize physical sources that were absent from source-labeled training while being explicit about ambiguity under sparse, changing PMU membership. The final article must compare three paradigms under one frozen experimental contract:

1. **Data-driven diagnosis:** observations or engineered features mapped to an event/source label.
2. **Physics-only intervention inference:** a physical hypothesis drives a DAE prediction, residual, and likelihood.
3. **Hybrid physics-informed inference:** the DAE remains authoritative for candidate generation and trajectory prediction; a learned, source-agnostic discrepancy model represents structured mismatch in the candidate likelihood.

Legacy SGSMA feature-based systems are retained as reproducible baselines and as candidate residual-feature families. They are not the claimed new contribution. The paper must not equate a known-source classifier with source-generalizable inverse inference.

## 2. Research questions

| ID | Research question | Required evidence |
| --- | --- | --- |
| RQ1 | Can hybrid inference localize physical sources excluded from all source-labeled training and development data? | Frozen source-holdout Campaign A. |
| RQ2 | Does a learned model-discrepancy layer improve physical inference under operating-condition and simulator shift without losing held-out-source behavior? | Physics-only, ML-only, and hybrid comparison under one contract. |
| RQ3 | Does the stated diagnosability quantity predict empirical ambiguity and time to resolution as PMUs join or leave? | Campaign B, including failed predictions. |
| RQ4 | Does causal scanning retain useful precision, uncertainty behavior, and alarm burden under measurement degradation and long normal exposure? | Campaign D with false alarms per hour and complete denominators. |
| RQ5 (conditional) | Can a confirmed physical experience improve future inference from another PMU when the discovering PMU is unavailable? | Campaign C. It is a contribution only if this test succeeds. |

## 3. Proposed method contract

For each physical hypothesis $H_j$, a network model predicts the PMU trajectory $\hat y^{\mathrm{phys}}_{j,k}$. The hybrid method is specified by

$$
y_k = \hat y^{\mathrm{phys}}_{j,k} +
\delta_\phi(\Xi_{j,1:k},\chi_k,\mathcal P_k) + \epsilon_{j,k},
\qquad
\epsilon_{j,k}\sim\mathcal N(0,R_k+\Sigma_\phi).
$$

Here $\delta_\phi$ and $\Sigma_\phi$ are proposed learned discrepancy and uncertainty terms. They condition on candidate-specific residual evidence $\Xi$, operating context $\chi_k$, and the currently available PMU set $\mathcal P_k$. They must not receive a target source identity as a class label or replace the physical hypothesis bank. The posterior remains over physical hypotheses; a learned score alone is never called a posterior.

The runtime method specification must state: input and retained state; integrity gate; causal change statistic; hypothesis generator; fast score; $K$ selection; nuisance variables; nonlinear refinement objective; physical and hybrid likelihoods; prior; posterior update; candidate-set and abstention rule; output; and measured complexity. A single concise runtime algorithm is preferred once the implementation is frozen.

## 4. Event and measurement taxonomy

The model separates physical intervention $a_k$, PMU integrity state $m_{p,k}$, and an out-of-model hypothesis. The intended physical family is fault, line outage, generation change, and load change. The intended integrity family is nominal, missing, corrupt, and timing/quality issue. A concurrent event and PMU loss is represented compositionally, not as a synthetic combined class.

The following legacy-label mapping is a **planned manuscript table**, not yet a verified dataset fact. It may enter the paper only after its originating SGSMA label contract is versioned in this repository.

| Legacy label meaning | P07 representation |
| --- | --- |
| Normal | $a=0,\;m=\mathrm{nominal}$ |
| Fault | $a=\mathrm{fault}(\ell,\gamma)$ |
| Line outage | $a=\mathrm{outage}(i,j)$ |
| Generation or load change | $a=\Delta P_G,\Delta Q_G$ or $a=\Delta P_L,\Delta Q_L$ |
| Missing or bad data | $a=0$ with the appropriate $m_p$ state |
| Missing plus physical event | $a\ne0$ and $m_p=\mathrm{missing}$ |
| Unknown | out-of-model or unresolved hypothesis |

## 5. Legacy baselines and ablations

The baseline names below describe the planned comparison. Their availability, implementation revision, and eligibility must be recorded before any result is reported.

| ID | Planned role |
| --- | --- |
| B0 | Physics-guided hierarchical ExtraTrees (SGSMA legacy baseline). |
| B1 | Compact sequential ExtraTrees using the reduced legacy feature set. |
| B2 | Post-hackathon hybrid candidate ranker with learned compatibility and electrical residuals. |
| B3 | Physical residual or Zbus-style ranker. |
| B4 | EKF, UKF, MHE, or a documented dynamic-estimation equivalent. |
| B5 | Reproducible topology-aware, open-set, or graph-learning external baseline, if it can meet the common protocol. |
| P | Proposed DAE plus learned-discrepancy Bayesian inference. |

The required ingredient ablation is: A0 ML-only; A1 physics-only; A2 physics plus SGSMA-derived engineered residual features; A3 physics plus learned discrepancy; A4 A3 plus explicit Bayesian uncertainty; and A5 A4 plus diagnosability-aware candidate set or abstention. An unavailable baseline or ablation must be reported as unavailable, never silently omitted from a comparative claim.

## 6. Required article anatomy and page budget

The target is approximately 19--20 IEEE Access pages including references and biographies, without padding. Results must occupy more space than Related Work and roughly as much space as the main theory plus method.

| Component | Target | Purpose |
| --- | ---: | --- |
| Abstract and front matter | 0.5 p | One self-contained 180--220 word abstract; final version carries only 3--4 memorable numbers. |
| I. Introduction | 1.25--1.5 p | Operational problem, state of the art, gap, insight, contributions, and eventual headline results. |
| II. Related Work and Gap | 1.5--1.75 p | Comparative synthesis and capability matrix. |
| III. Problem Formulation | 1.25--1.5 p | DAE, interventions, integrity, dynamic PMU set, outputs. |
| IV. Diagnosability | 1.5--1.75 p | Signatures, information, formal bridge, candidate sets. |
| V. Hybrid Bayesian Inference | 1.75--2.0 p | Complete causal method and likelihood contract. |
| VI. Knowledge Transfer | 0.75--1.0 p | Included as a main contribution only if RQ5 is supported. |
| VII. Experimental Methodology | 1.4--1.6 p | Systems, splits, baselines, metrics, reproducibility. |
| VIII. Results | 4.0--4.5 p | The paper's largest section, organized by RQ rather than campaign name. |
| IX. Discussion and Limitations | 0.75--1.0 p | Meaning, failure modes, and scope. |
| X. Conclusion | 0.3--0.4 p | Two or three bounded paragraphs. |
| References and biographies | about 2.5 p | 50--65 verified references and author-provided biographies. |

Section II will synthesize: PMU event diagnosis; physics/model-based dynamic inference; sparse observability and source identifiability; physics-informed and graph learning; Bayesian/hybrid intervention inference; open-set/domain generalization; and edge/federated/continual learning. The final capability matrix must state each work's problem, assumptions, demonstrated generalization, unresolved failure mode, and role for P07 (baseline, component, or excluded alternative).

## 7. Theory discipline

Use approximately 15--25 numbered equations only when they define the plant or measurement model, intervention, likelihood/posterior, diagnosability, decision rule, or update/fusion mechanism. Do not add equations merely to restate standard Bayes, KL divergence, or metrics.

The intended formal hierarchy is one substantive proposition or theorem connecting expected Bayesian evidence to the dynamic information quantity, one scoped indistinguishability result, and an independent-sensor information-monotonicity corollary. The bridge is publishable only if its assumptions, proof, and empirical falsification test are explicit. The current monotonicity result must not be presented as a major theoretical contribution by itself.

## 8. Experimental and reporting rules

- All methods receive the same system, PMU, source-holdout, development, test, threshold, and temporal-exposure contract.
- Source holdout is at the physical asset level: test assets cannot occur as source labels in training, tuning, feature fitting, or threshold selection.
- Units of uncertainty are independent trajectories, scenarios, or parent records, never individual PMU samples. Use multiple learning seeds, confidence intervals over parent scenarios, and paired bootstrap for paired methods where appropriate.
- Select thresholds on development data, freeze them, and test once. Do not retune on the PowerDynamics.jl test set.
- Separate ANDES nominal, ANDES shift, PowerDynamics.jl transfer, and RAW0001. RAW0001 remains a retrospective organizer-provided reference simulation, not field or independent validation.
- Report known-source performance separately from RQ1. Report failures by physical family and asset type.
- A calibration, false-alarm-control, real-time, edge-validated, or distributed-deployment claim remains forbidden until its dedicated evidence gate is satisfied.

## 9. Results, figures, tables, and artifacts

Organize results by unseen-source inference; diagnosability versus ambiguity; PMU membership; model and measurement shift; conditional knowledge transfer; and runtime/communication. Each introduction claim must terminate in at least one results figure or table.

Target eight or nine high-information composite figures: sparse-PMU problem; complete architecture; DAE and integrity model; diagnosability geometry; held-out-source result; PMU loss/join; domain/cross-simulator shift; continuous-stream alarm/delay/source resolution; and conditional knowledge transfer or edge cost. Use vector graphics when possible. No numerical chart, table row, caption, or headline can be created before its source data and manifest are frozen.

Target six tables: related-work capability matrix; physical/integrity taxonomy; dataset/campaign/split contract; held-out-source comparison; PMU/diagnosability ablation; and runtime/memory/communication. Large hyperparameter grids, full confusion matrices, and all-subset results belong in supplementary material.

Every released figure or numerical table must be traceable as `manifest -> experiment output -> aggregation script -> figure/table script -> PDF`. The intended build surface is conceptually `data-manifests`, campaigns A--D, figures, tables, and paper; exact command names may differ.

## 10. Literature and completion gates

The next dedicated literature task must grow the bibliography to roughly 50--65 verified records, including 25--35 from 2022--2026 where relevant. Every candidate must be checked against a primary publisher, DOI, or official project record before entering `references.bib`. Build a source matrix with: problem; data/test system; PMU coverage; physical model; method; event families; source generalization; dynamic membership; uncertainty; causality; field/simulation status; metrics; limitations; and what P07 must add or beat.

P07 is ready for submission only when all applicable gates pass:

| Gate | Acceptance question |
| --- | --- |
| G1 Novelty | Does verified literature show that the exact problem contract is not already resolved? |
| G2 Theory | Does diagnosability explain or predict an observed outcome? |
| G3 Generalization | Are test sources wholly excluded from source-labeled training and development? |
| G4 Operational | Does continuous causal scanning report alarm burden instead of hiding it? |
| G5 Reproducibility | Can every result be rebuilt from manifests, code, and frozen outputs? |
| G6 Knowledge (conditional) | Does confirmed knowledge transfer after the discovering PMU is unavailable? |

## 11. House style

Write in the sequence **claim -> mechanism -> evidence -> limitation**. Every adjective must be paid for with evidence. Avoid ``novel'' or ``new'' in the title; ``groundbreaking,'' ``comprehensive,'' ``highly robust,'' and ``seamless'' in prose; ``real-time'' without end-to-end latency; ``Bayesian'' for uncalibrated scores; and ``distributed'' for a centralized simulation. The current manuscript remains a framework draft until its evidence gates are met.

# Experimental plan and reporting contracts

## Shared reproducibility record

Every campaign release must include a versioned manifest with:

- network, dynamic-model, topology, and simulator versions;
- PMU placement, channel configuration, measurement operator, quality flags, and sampling policy;
- event family, asset, onset, magnitude, operating point, parameter shift, and integrity model;
- source-holdout, development, and test partitions;
- random seeds, repetitions, threshold-selection policy, and implementation revision;
- baseline availability and exact hyperparameter or estimator configuration; and
- metric code, raw aggregate counts, units, and hardware specification.

Do not pool results from incompatible simulators, source-holdout rules, PMU memberships, or temporal exposures.

## Canonical campaigns

| Campaign | Primary question | Train/development/test contract | Required comparisons | Required outputs |
| --- | --- | --- | --- | --- |
| A — Source Generalization | Can the system identify a source never represented as a source label during training or tuning? | Test buses, lines, generators, and loads are excluded from every source-labeled train and development split. Freeze the asset manifest before tuning. | B0–B5 when implemented; P; known-source performance reported separately. | Exact and Top-3 localization, electrical distance where meaningful, joint correctness, candidate-set coverage/size, entropy, source-resolution delay, family/asset failure analysis. |
| B — Dynamic Observability | Does current PMU membership and the proposed information measure explain ambiguity? | Evaluate 8, 7, 6, and 4 PMUs plus at least one controlled addition. Hold event and operating-condition contracts fixed where possible. | Random loss versus information-critical loss; addition case; P and compatible baselines. | Pairwise/minimum information, candidate sets, entropy, coverage, localization, delay; before/after membership transition. |
| C — Knowledge Transfer | Does a validated physical knowledge object transfer across conditions and PMU perspectives? | Hold out a phenomenon/knowledge item, evaluate it as unknown, simulate trusted confirmation, then test new operating points, noise, and perspectives. Include discovering-PMU-disconnected condition. | No update; conventional update or FL/KD-style comparator if reproducible; physics-grounded transfer. | Forward transfer, retained old-event performance, forgetting, candidate-set behavior, performance without discovering PMU, provenance record. |
| D — Operational Robustness | Does the causal pipeline retain useful behavior under shift and long normal exposure? | Separate ANDES nominal, ANDES shift, PowerDynamics.jl transfer, noise, missing PMUs, and continuous stream exposure. RAW0001 is separate retrospective evidence only. | B0–B5 when implemented; P; nominal versus shift and simulator-specific comparisons. | Precision, recall, F1, macro-F1 where defined, false alarms/hour, joint precision/F1, delay, resource measurements, failure taxonomy. |

## Paradigm and ablation contract

Every campaign that reports a P07 comparison must distinguish data-driven diagnosis, physics-only intervention inference, and hybrid physics-informed inference. The hybrid learner receives candidate-specific residual information from the DAE prediction; it must not be trained to emit a held-out source identity.

| ID | Ingredient set | Question answered |
| --- | --- | --- |
| A0 | ML-only diagnosis | What does learned recognition achieve without the physical hypothesis bank? |
| A1 | Physics-only likelihood | What does DAE-based intervention inference achieve without learned mismatch correction? |
| A2 | Physics plus SGSMA-derived engineered residual features | Do the legacy feature families improve the residual evidence path? |
| A3 | Physics plus learned source-agnostic discrepancy | Does learned mismatch correction improve the physical likelihood? |
| A4 | A3 plus explicit Bayesian uncertainty | Does the uncertainty model improve decision quality under shift? |
| A5 | A4 plus diagnosability-aware candidate set or abstention | Does ambiguity-aware decision logic avoid unsupported exact-source claims? |

An ablation is reportable only when its training, development, threshold, and test partitions match the compared method. If an ingredient is unavailable, label it unavailable rather than treating a different method as a substitute.

## Baseline availability register

| Identifier | Baseline | Current manuscript status | Required record before reporting |
| --- | --- | --- | --- |
| B0 | Legacy physics-guided hierarchical ExtraTrees | External archive audited; not imported or reproduced under P07. | Feature schema, label contract, source split, availability handling, source hashes, version, and frozen P07 result manifest. |
| B1 | Compact sequential ExtraTrees | External archive audited; not imported or reproduced under P07. | Reduced feature specification, causal windowing, source split, source hashes, version, and frozen P07 result manifest. |
| B2 | Legacy hybrid candidate ranker | External archive audited; not imported or reproduced under P07. | Candidate generator, learned compatibility model, electrical residual definition, tuning split, source hashes, and result manifest. |
| B3 | Physical residual or Zbus-style ranker | Planned. | Network model, residual definition, candidate space, and operating-point assumptions. |
| B4 | EKF, UKF, MHE, or documented equivalent | Planned. | State definition, noise model, initialization, tuning, and failure handling. |
| B5 | Topology-aware, open-set, or graph-learning baseline | Planned and conditional on reproducibility. | Verified citation, implementation revision, source split, tuning procedure, license, and common-contract eligibility. |
| P | DAE plus learned-discrepancy Bayesian framework | Method specification only. | Candidate generator, source-agnostic discrepancy model, likelihood/uncertainty specification, fusion assumptions, abstention rule, and all campaign manifests. |

## Metric definitions

| Family | Metric | Numerator / denominator or unit |
| --- | --- | --- |
| Detection | Precision | Correct physical-event alarms / all physical-event alarms. State whether integrity-only alarms are excluded. |
| Detection | Recall | Correctly detected physical events / all physical events in the frozen test exposure. |
| Detection | F1 and macro-F1 | Harmonic mean of stated precision and recall; macro-F1 averages explicitly defined classes. |
| Localization | Top-1 / Top-3 | Correct exact physical asset in rank 1 / ranks 1–3, divided by localization-eligible events. |
| Localization | Electrical-distance error | Report the network-distance definition, units, and treatment of line sources. |
| Trustworthiness | Candidate-set coverage | Events whose true source lies in the emitted set / events for which a set is evaluated. |
| Trustworthiness | Candidate-set size | Mean, median, and distribution of emitted set cardinality; report abstentions separately. |
| Trustworthiness | Posterior entropy | State posterior normalization, logarithm base, and treatment of candidate pruning. |
| Temporal | False alarms/hour | False physical-event alarms divided by long-normal exposure in hours. |
| Temporal | Joint alarm precision | Alarms correct jointly in event family and source / all joint alarms. |
| Temporal | Delay | Decision timestamp minus declared onset; distinguish detection and exact-source delays. |
| Resources | Inference time / CPU / memory | Report quantiles, hardware, batch/window policy, and whether timing includes simulation or communication. |
| Resources | Bytes and messages | Bytes per message, messages per event, and total communication volume under a named serialization and membership scenario. |

## Planned manuscript tables

| Table | Content | Publication gate |
| --- | --- | --- |
| I | Related-work capability/gap matrix | Every method/capability cell supported by a verified source and qualified for its assumptions. |
| II | From the legacy nine-label contract to compositional physical and measurement-integrity states | Source label semantics are audited; obtain coauthor review and import a versioned source contract before reusing any numerical legacy result. |
| III | Campaigns and train/development/test contracts | Add after manifests have stable identifiers. |
| IV | Main held-out-source results | Campaign A is frozen and source exclusion independently checked. |
| V | PMU membership and knowledge-transfer ablations | Campaigns B and C are frozen. |
| VI | Runtime, memory, and communication cost | Hardware and implementation revision are fixed; measurements are repeatable. |

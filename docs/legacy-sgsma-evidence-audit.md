# Legacy PMU diagnosis evidence audit

## Purpose and scope

This audit turns the prior PMU-diagnosis work into a traceable P07 input. It is a source of benchmark definitions, baseline designs, feature families, and negative evidence. It is **not** a source of automatic performance claims for P07. The P07 paper must never describe this work as an external or independent validation set, and it must not imply that a historical source split satisfies the P07 held-out-asset contract.

The audit deliberately uses the neutral terms **legacy source archive**, **reference benchmark**, and **legacy baseline**. It does not narrate the provenance of the archive in the manuscript.

## Audited source material

The source project was inspected as an external working tree. It contains uncommitted and untracked files, so the file hashes below, rather than its Git revision alone, identify the audited inputs. All paths are relative to `C:\Users\walla\Documents\Github\SGSMA26-Physics-Informed-AD`.

| Source | SHA-256 | What it establishes for P07 | Status in this repository |
| --- | --- | --- | --- |
| `SGSMA_2026_Competition_Day_Policy (1).pdf` | `C2588D03AE1AC58684B3F646BC89AF92CBDB740FE940B181AA54BBC6FE9A595A` | Row-aligned detection, classification, and localization tasks; separate accuracy/F1 reporting convention. | Audited reference only. |
| `guidelines.pdf` | `AB065FF7165AAB54E246A6C439F552643A011CB8B3CEA44A80810F7E3228743E` | IEEE-39 benchmark setting; eight PMUs; voltage/current/frequency/ROCOF channels; availability flag; label semantics; anti-row-shuffle warning; task-specific metrics. | Audited reference only. |
| `sgsma_2026_final_submission.zip` | `E0BFC17E4C5EE9B595FA51FD94D736145C2F48755696C8D2EADCFF00CB23A243` | Executable legacy submission with topology, feature construction, trained artifacts, model metadata, and a documented output schema. | Not imported; must be re-executed or selectively ported under P07 manifests. |
| `paper_journal/CLAIM_EVIDENCE_MATRIX.md` | `76166145B39CB2850FC131172F2BE612880C9D8BF7541C50F09575A8D7F3AD76` | Maps historical tables to result files and records known limitations of known-source, reference-record, PMU-sparsity, and asset-disjoint experiments. | Evidence catalogue only. |
| `paper_journal/EXPERIMENT_PROTOCOL.md` | `C082C4D5E068832F0FA8B24830178286F628B261C9BD65174E523AF8E30042E5` | Complete-trajectory splits, model seeds, availability handling, scenario-level resampling, and scope limits for the historical article. | Useful design input; not a P07 frozen protocol. |
| `paper_journal/evidence/source_manifest.json` | `1E828404DF7E72C55225B3CE40C97A593235232C01EFA9F12FF57FFE11720CC9` | Archive-member hashes for historical metrics, source-disjoint folds, feature ablations, timing, and PMU-sparsity artifacts. | Must be copied with provenance before any P07 result is quoted. |

The legacy working-tree revision reported during inspection was `e836c9512edfdb8b4537587318db4acc776d9a21`; it is not a sufficient reproducibility identifier because the tree was dirty.

## Verified benchmark facts used in P07

The reference benchmark is the IEEE 39-bus system with PMUs at buses `{2, 5, 6, 10, 19, 22, 29, 39}`. The documented measurement vector includes three-phase voltage and current phasors, frequency, ROCOF, and an explicit `DATA_PRESENT` status flag. The nominal sampling convention is approximately 30 frames/s. These facts justify the P07 initial testbed and the observation operator in the manuscript; they do not establish field deployment conditions.

The source contract separates three tasks: abnormal-event detection, event-family classification, and source localization. It also makes clear why they cannot be collapsed into one accuracy: a source may be recognizable only coarsely; a data-quality condition can be observable without being a physical event; and a physical event can co-occur with a missing PMU channel.

## Event ontology carried into P07

The legacy labels comprise nominal operation; fault; line outage; generation change/outage; load change/drop; missing data; missing data concurrent with a physical event; bad data; and an unknown/mixed condition. P07 preserves the physical families but changes the representation:

- `physical intervention` is an explicit hypothesis over family, asset, onset, and severity;
- `PMU integrity` is a separate per-device/per-channel state; and
- `unknown` is an unresolved decision or a documented multi-intervention scenario, not a convenient physical source class.

Table II of the manuscript records the mapping. The mapping is a P07 evaluation decision, not a claim that every historical label has a unique physical decomposition. In particular, legacy label 6 requires both a physical target and an integrity target; label 8 cannot establish open-set generalization merely because it was given a catch-all name.

## What the legacy system contributes as a baseline

The archive documents a physics-guided hierarchical tree system that combined five reusable feature families:

1. local robust and statistical summaries of PMU channels;
2. multiscale temporal, derivative, innovation, and transient-shape summaries;
3. physical voltage/current/frequency/ROCOF and power-proxy descriptors;
4. cross-PMU, topology, and electrical-distance descriptors; and
5. missingness, availability, and bad-data indicators.

The legacy design also separated detection, event typing, physical localization, and integrity localization. That separation is scientifically useful: B0 can answer how far source-labeled physics-guided feature engineering reaches, while P07 can test whether candidate-specific residual features improve a physical likelihood. P07 must not reproduce an opaque list of tens of thousands of names in its main text.

There is an internal version discrepancy: one submission-oriented `MODEL.md` describes a 45,162-feature runtime, while the later journal evidence describes compact 136- and 448-feature variants. Therefore B0/B1 cannot be called reproduced until a chosen feature schema, model files, environment, and train/development/test manifests are imported and hashed into this repository.

## Historical evidence boundary

The audit found traceable historical artifacts for complete-trajectory splits, three model seeds, feature ablations, candidate-ranking controls, source-disjoint folds, PMU-sparsity studies, timing, and a known retrospective reference record. Those artifacts are valuable for selecting experiments and for anticipating failure modes. They remain **historical evidence** because:

- their split and source-exclusion rules are not yet frozen under the P07 contract;
- the prior learned localizers include source-labeled components, whereas P07's discrepancy learner must not emit a held-out source identity;
- the reference record is a known simulation, not independent field evidence;
- short normal exposure and benchmark-specific PMU placement cannot support a false-alarm-control or deployment claim; and
- source, simulator, and measurement semantics must be reconciled before values can be compared.

Accordingly, no numerical value from this archive appears in the P07 manuscript. A future numerical reuse requires: (i) copying the precise source/result artifact into a versioned P07 path, (ii) recording its hash and execution environment, (iii) declaring whether it is historical/secondary or a new P07 primary test, and (iv) labeling its denominator, independent unit, source split, and simulator.

## Required import path for B0 and B1

Before a legacy baseline appears in a P07 result table, create a manifest that names:

- the exact archive members, file hashes, and software environment;
- PMU channels, timing alignment, window endpoints, imputation/masking, and availability rule;
- feature-family schema and the selected compact or expanded implementation;
- training, development, and test event-parent manifests;
- excluded physical assets and a check that their identities never enter source-labeled fitting or tuning;
- thresholds, seeds, error handling, and normal-stream exposure; and
- scripts that regenerate the P07 table/figure from raw predictions.

Only then may B0 be reported as a legacy physics-guided hierarchical ExtraTrees baseline and B1 as a compact causal feature baseline. B2, the legacy candidate ranker, must additionally state how candidate generation, residual construction, and event routing avoid target leakage.

## Reviewer risks retained in the paper plan

1. **Source memorization:** ordinary complete-trajectory separation is not asset holdout. P07 Campaign A is mandatory for the main claim.
2. **Task conflation:** detection, class, physical asset, and PMU integrity need separate denominators and outputs.
3. **Measurement shortcut:** missingness may make an integrity label easy without proving physical inference.
4. **Historical-result laundering:** a previously saved score cannot become evidence for a different P07 likelihood or simulator.
5. **Reproducibility mismatch:** the external source tree is dirty and its feature variants differ; hashes and manifests, not descriptions alone, control reuse.

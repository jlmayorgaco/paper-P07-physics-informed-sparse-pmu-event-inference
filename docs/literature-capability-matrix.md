# Literature capability matrix

## Scope and reading rule

This is a focused, verified matrix for the P07 claim. It is not a leaderboard and it does not treat published scores from different data contracts as numerical baselines. Each row was checked against a publisher, institutional, or author-hosted primary record and is included only for the adjacent capability statement in the manuscript. The matrix must be extended before submission, particularly with recent direct competitors and any method implemented as B3--B5.

| Work | Exact task and evidence setting | Physics / learning / inference | Source and sensor generalization actually shown | P07 role and boundary |
| --- | --- | --- | --- | --- |
| Li, Wang, and Chow (2018), `li2018subspace` | Streaming event identification from high-dimensional synchrophasor data. | Data-driven low-dimensional subspace and dictionary comparison. | Event-dictionary setting; not an exact held-asset intervention test. | Recognition baseline family; not a physical posterior. |
| Jamei *et al.* (2020), `jamei2020limits` | Fault localization and PMU placement under incomplete observability. | Observation-model distributions and KL-based distinguishability. | Varies placement/sensing for its fault model. | Direct foundation for a qualified diagnosability measure; not a P07 theorem under DAE mismatch. |
| Pandey, Srivastava, and Amidan (2020), `pandey2020realtime` | Detection, classification, and localization from synchrophasor data. | Staged conditioning, statistical/clustering, physical rules, topology. | Simulation and field-measurement contexts stated by the paper; not the P07 source-holdout contract. | Confirms that the three tasks are distinct. |
| Azizi *et al.* (2021), `azizi2021log` | Generation-loss size and location from sparse PMUs. | Bus-impedance transfer relation and residual-based physical estimator. | Works with sparse/non-fixed received measurements in its defined LoG model. | Physics-only comparator family for generation interventions; do not extend its semantics to all P07 injection events. |
| Li, Ma, and Weng (2022), `li2022transfer` | Event type and location-zone transfer across grids with limited labels. | Heterogeneous domain adaptation and learned representation. | Cross-grid feature/distribution/label alignment; locations are aligned as zones. | Direct transfer contrast; zones are not exact physical assets. |
| Yuan, Wang, and Wang (2023), `yuan2023gnn` | PMU event classification using learned latent interactions. | Data-driven graph learning and temporal representation. | Real-world PMU event data in the reported contract; source-location holdout is not the reported P07 test. | Strong learned classification family for B5 eligibility. |
| Azizi *et al.* (2023), `azizi2023line` | Sparse-PMU line-outage monitoring and outage sequence identification. | Impedance-derived transfer function and weighted residuals. | Partial communication/timing-loss conditions within the stated outage model. | Physics-only line-outage comparator; candidate space and residual must be reimplemented fairly. |
| Liu *et al.* (2023), `liu2023imperfect` | Event classification from imperfect real-world PMU records. | Preprocessing, event-time refinement, and engineered features. | Data quality is explicitly studied; does not establish exact-source localization. | Supports retaining integrity states; not evidence for P07 localization. |
| Biswas *et al.* (2023), `biswas2023library` | Curation of real bulk-system PMU behavior. | Data repository rather than a competing inference model. | Real records, but no P07-compatible asset truth or channel contract established. | Candidate future external-evidence source only. |
| Yildiz and Abur (2025), `yildiz2025sparse` | Sparse-PMU placement for fault and line-outage detection/identification. | Placement optimization evaluated with model-based and data-driven methods. | Tests placement choices, not arbitrary online join/leave inference. | Supports the importance of observation geometry; P07 tests current membership rather than placement optimality. |

## Gap statement allowed by this matrix

Existing work supplies strong components: source-label/dictionary recognition, topology-aware learned representations, physics-based residual inference for specific families, sparse-placement analysis, transfer learning, and data-quality treatment. The narrow P07 question is whether a common physical-hypothesis contract can be evaluated under **asset-excluded source training**, **time-varying PMU membership**, **explicit integrity states**, and an **abstaining candidate-set output**. This matrix does not establish that P07 is the first system to combine physics and learning, or that a result under one work's benchmark ranks methods under another's.

## Direct-comparison eligibility

| Family | Include as common-contract baseline only when | Otherwise use as |
| --- | --- | --- |
| Legacy hierarchical ExtraTrees (B0/B1) | Its external evidence and feature schema are imported with P07 manifests and no source leakage. | Historical design reference. |
| Physical residual methods (B3) | Candidate set, network semantics, measurement operator, and event family match the P07 campaign. | Mechanistic contrast in related work. |
| Dynamic estimators (B4) | State, noise, initialization, failure accounting, and runtime budget are declared. | Model-based alternative. |
| Transfer/GNN/open-set methods (B5) | Code/license, compatible observations, source split, and tuning protocol are reproducible. | Contextual comparator or excluded alternative with reason. |

## Verification records

- Jamei *et al.*: [institutional record](https://escholarship.org/uc/item/566174gb), DOI `10.1109/JSAC.2019.2951971`.
- Azizi *et al.* (generation): [institutional record](https://eprints.whiterose.ac.uk/id/eprint/169323/), DOI `10.1109/TPWRD.2020.3047228`.
- Li, Ma, and Weng: [IEEE record](https://ieeexplore.ieee.org/abstract/document/9721668), DOI `10.1109/TPWRS.2022.3153445`.
- Azizi *et al.* (line): [institutional record](https://eprints.whiterose.ac.uk/id/eprint/190192/), DOI `10.1109/TPWRS.2022.3201067`.
- Liu *et al.*: [institutional record](https://asu.elsevierpure.com/en/publications/robust-event-classification-using-imperfect-real-world-pmu-data/), DOI `10.1109/JIOT.2022.3177686`.
- Yildiz and Abur: [IEEE record](https://ieeexplore.ieee.org/document/10640266/), DOI `10.1109/TPWRS.2024.3446237`.

# Editorial revision — 3 November 2026

## Scope and preservation

The revision concentrates the active supplement on the implemented causal method and its reported comparisons. The original `supplement.tex`, `historical_notes.tex`, `sections/article_evidence_bridge.tex` and `references.bib` are preserved under `before/`; existing snapshots were not overwritten. No empirical output, predictor, threshold, frozen campaign, author biography or protected figure was changed.

## Change register

| Review issue | Disposition | Applied change |
|---|---|---|
| Extended supplement mixes the current method with unrelated historical estimators | ADDRESSED | Active supplement now includes the implemented-filter derivation, existing causal walkthrough and worked examples, full measurement/publication contracts, C01, A01, the continuous single-state control, development outcomes, X02 and recovery geometry. General diagnosability proofs, voltage reconstruction, old batch/feature studies and the proposed joint estimator are preserved in Historical Technical Notes. |
| Local implementation is insufficiently specified | ADDRESSED WITH PARALLEL TECHNICAL REVISION | `supplement/implemented_filter_details.tex` is included first. Its affine-switch, severity-partition and conditional-covariance details supplement the retained numerical examples. The technical author supplies the verification table. |
| Historical evidence has a known single-source normalizer error | QUALIFIED; CORRECTED REPLAY STILL OPEN | Historical Technical Notes now disclose the effective prior proportional to `(0.20, 0.50/(2π), 0.30)` before the archived results. The component table retains its executed outcomes and explicitly does not represent a corrected replay or evidence for R11. |
| Adding only diagonal second-order terms must improve approximation | REVIEWER_DISAGREE | Historical component text explains that a partial second-order truncation has no monotonic error guarantee: omitted mixed terms may cancel diagonal terms. No unperformed coefficient audit is claimed. |
| Three-phase power notation and remote-current pairing | CLARIFIED | Historical feature discussion states the balanced reduction `3 V_a I_a*`, requires co-located phasors for actual terminal power, retains remote pairings as proxies, and distinguishes the instrument's potential processing dependence from F01's executed noise law. |
| A01 completeness and exposure conventions | ADDRESSED | The active supplement now includes all A01 lanes and paired intervals. An adjacent note declares that archived A01 extra-alarm rates use 120-s full records, whereas the main confirmatory plot uses 108-s monitored records. Values are preserved; the exact `120/108` conversion is stated. |
| Repeated preprint notes | ADDRESSED | Removed the editorial phrase after the Warner TechRxiv record, retaining its preprint/version/DOI. Removed the redundant Albustami preprint note and added its verified arXiv DOI. |

## Citation verification

- [arXiv:2604.15686](https://arxiv.org/abs/2604.15686) was read on 3 November 2026. Its author/title/year record and DOI `10.48550/arXiv.2604.15686` support the bibliographic cleanup. This is a metadata verification, not a new methodological appraisal.
- Warner's existing authors/title/year/version/DOI were retained. The [existing DOI](https://doi.org/10.36227/techrxiv.23264519.v1) could not be opened by the browsing tool in this session. Removing a redundant internal note does not assert a new publication status.

## Verification performed before integration

- `python -B scripts/verify_supplement_examples.py` passed. Direct quadrature and the analytic likelihood differ by `5.55e-17`; the retained posterior-mean, recovery and model-reweighting examples agree.
- Recursive source inspection found no unresolved local `ref`/`eqref` targets or duplicate labels in either active supplement or historical notes. The technical agent's generated math-check table was still pending at that inspection.
- Existing build and publication scripts already compile and distribute Historical Technical Notes separately; no build-script edit was needed.
- Compilation, visual inspection and final protected-figure verification are reserved for the parent integration step. No page-count reduction is asserted before the rebuilt PDF is inspected.

## Remaining boundaries

This edit does not produce a fair calibrated baseline comparison, new robustness validation, calibrated history probabilities, a corrected historical batch replay, or independent evidence for explicit history competition over a competent continuous observer. Those are scientific evidence tasks, not editorial corrections.

## Added comparator-lineage reproduction table

The subsequent source audit identified the exact development-trained R09 artifacts loaded by C01. `scripts/build_comparator_lineage.py` derives `generated/comparator_lineage.json` and `tables/generated/comparator_lineage.tex` from the minimal immutable-input snapshot `generated/frozen/comparator_lineage_20261103/`. The supplement includes the table and its training/decision contract.

- `COMPLETE.json` records 32 training parents, eight validation parents and 16 validation records. `PROTOCOL.json` identifies SIM0014–SIM0017 as training campaigns and SIM0018 as validation; these were development data by this comparator construction.
- C01's frozen `common.py` selects R09, and its worker maps BASELINE to ET_REFERENCE and SHORT to ET_CANDIDATE. The original hackathon serializations are not loaded by this path.
- Both joblib hashes match COMPLETE and the pre-C01 R11 freeze before deserialization. Introspection confirms 846/1457 features, 400 trees, normal plus all 18 source classes, and the stored model settings. A repeat verification using scikit-learn 1.7.2 (the serialization version) matched the captured metadata. No model prediction or fitting was performed.
- The frozen wrapper takes argmax of tree votes and applies a six-report clock; it has no separate probability-trigger threshold. This corrects a material premise of the external review rather than weakening a valid calibration request.
- Portable regeneration was exercised in a temporary directory containing only the generator and metadata snapshot, with no research repository, model serializations or performance outputs. Both generated outputs matched byte for byte. See `COMPARATOR_LINEAGE_VERIFICATION.json`.

The parent integration must include the generator, JSON and metadata snapshot in the source/reproduction package; a TeX recorder alone does not enumerate these supporting files.

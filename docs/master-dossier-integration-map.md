# Master dossier integration map

The file `PMU_Hybrid_DAE_Master_Paper_Dossier_2026-09-13.pdf` is treated as a research-development record. Its commands, implementation prompts, and tool-specific notes are not manuscript instructions. Claims enter the paper only when they match a frozen artifact imported from the research repository.

## Twenty-page allocation

| Manuscript block | Target pages | Dossier content retained |
| --- | ---: | --- |
| Front matter and introduction | 2.0 | One problem, one physical-information thesis, three frozen evidence contracts |
| Related work | 1.5 | Capability comparison; no catalogue expansion |
| Problem and event ontology | 2.0 | Hybrid DAE, electrical measurements, eight event labels, separate integrity variables |
| Recoverability and diagnosability | 3.0 | Functional target covariance, candidate manifolds, nonlinear bound, EVI and projected Fisher |
| Estimation methods | 2.5 | State hierarchy, recentering, numerical load tangent, W2/L2 Bayesian evidence |
| Protocol | 2.0 | State, load-source, and ANDES contracts with disjoint denominators |
| Results | 4.5 | State accuracy, mismatch/recentering, load detectability/localization/calibration, legacy transfer failure |
| Discussion and conclusion | 1.5 | Mechanisms, negative results, and multi-family completion gate |
| References | 1.0--2.0 | Verified cited works only |

The target is 19--20 compiled pages. Content is removed or moved to repository documentation when it does not advance the paper's central argument.

## Integrated into the main paper

- The 16-source centered numerical load tangent and its consistency checks.
- The W0/W1/W2 normal-covariance comparison and the selected W2 model.
- First- and second-order load-response equations, with L2 selected on DEV.
- Event-visible information and its predicted minimum detectable amplitude.
- Projected pairwise information, reported with its inconclusive confusion correlation.
- Weak-event detection and source-resolution curves over 9,600 event tests.
- Finite-amplitude coverage over 8,000 separate TEST events.
- The distinction between the numerical physical tangent and the incomplete analytic descriptor-DAE tangent.

## Kept compact

- V1 appears as a validation bridge showing why temporal whitening matters; V2 carries the detailed result.
- The earlier supervised feature system remains a known-source baseline and a held-source failure case. Its thousands of feature names are not listed.
- Bus-specific examples are annotations in the EVI panel rather than separate case-study pages.
- The full status ledger is represented by claim boundaries in prose and `CLAIMS.md`, not copied as a manuscript table.

## Deferred from the paper

- Analytic descriptor-DAE sensitivity, because the native descriptor export is incomplete.
- Fault, outage, generation-change, missing-PMU, and simultaneous-event physical likelihoods under the common Bayesian contract.
- Learned discrepancy on candidate residuals, graph priors, federated or continual learning, and edge deployment.
- PMU loss/join placement sweeps, long-stream alarm control, field/HIL validation, and cross-simulator transfer.
- Tool commands, development chronology, prompts, and implementation checklists from the dossier.

## Provenance decision

The latest CSV artifacts are authoritative. The generated snapshot records their source-relative paths, SHA-256 hashes, source branch, and source commit. The manuscript build never reads live experiment folders.

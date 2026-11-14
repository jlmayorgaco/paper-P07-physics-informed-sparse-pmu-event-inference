# C03 integration and manuscript verification

C03 was inspected read-only and imported after its joint completion. The importer verified 528 predictions; the compact bundle verification passes for 16 files. The source campaign was not modified.

## Evidence and manuscript

- F01 history versus mean-carry: 144/144 versus 90/144 primary timely attributions; +37.5 percentage points, paired 95% interval [25.0,49.3].
- P2: 67/144 versus 65/144; +1.4 points [-12.5,16.0]. No established transfer of the coverage gain.
- Carry beats reset in both plants. This does not isolate a history-label effect from discarded mixture covariance.
- All nominal arms have zero normal alarms in 5.88 hours per plant. Dropout has 12 normal alarms in 1.96 hours per plant. All 24 independent-noise parents per plant are unavailable at prefix fitting; no noise coverage estimate is claimed.
- Abstract, introduction, protocol, interpretation and conclusion now follow this evidence. Generated C03 figure and supplemental tables use the imported result hash.
- Standard predictive sufficiency and total covariance identities distinguish the executed mean control from a proposed full moment-matching successor. The latter has not been run on the physical bank and is not presented as a validated second algorithm.

## Verification

Direct LaTeX builds: main 19 pages, supplement 44. Exact editorial ZIP and full source ZIP each rebuilt in separate clean folders with identical extracted text and pagination. A missing bold-italic template font exposed by cold compilation was fixed by packaging the complete local Formata family. Main figure and C03 tables inspected visually. Protected-figure verification passes all 16 hashes and finds both figures in the article. No undefined citation or reference remains in the final build.

Mathematical checks and counterexamples are preserved in experiments/theorem_audit_20261114. They verify standard identities and reject unsupported proposed bounds; they are not plant-performance experiments.

## Remaining boundary

This is an author-review draft, not a certificate of acceptance or submission readiness. A stronger claim about mixtures versus a Gaussian preserving all uncertainty needs the independent successor described in SUCCESSOR_EXPERIMENT_DESIGN_20261114.md. Independent-noise support needs a successor calibration/test campaign if robustness is claimed. Direct published-case reproduction of Yang remains absent. Author approval and submission declarations require the authors. Git publication does not verify remote Overleaf compilation.

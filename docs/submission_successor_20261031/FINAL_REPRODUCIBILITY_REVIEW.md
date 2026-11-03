# Final S01 reproducibility review

**Verdict:** no unresolved numerical, frozen-file, denominator, or cohort-mixing defect was found in the audited S01 additions to the current main article and supplement. The negative results and transfer restrictions are retained. The current text does not convert the one improved RAW window into a general superiority claim.

This review checks manuscript-to-artifact consistency, the imports, and the completed H04 V2 isolation replay. It does not reopen C01 results/truth or RAW0002, rerun inference, modify the manuscript, or independently revalidate every mathematical implementation. The reviewer contributed to the successor evaluation code earlier in this work; this is not represented as a blind external validation of that code. PDF layout, citations, and the other technical reviews are outside this pass.

## Frozen imports and generated values

The original three requested importers and the subsequently added H04 V2 importer were inspected as source; they were not executed during review. All four compare existing frozen bytes before permitting reuse. Read-only SHA256 checks independently compared each current research source, its paper copy, and the recorded manifest hash.

| Importer | Frozen namespace under `generated/frozen/` | Files verified | Result |
|---|---|---:|---|
| `scripts/import_s01_revision.py` | `submission_s01_controls_20261031` | 12 | All byte-identical to source and manifest |
| `scripts/import_s01_learning.py` | `submission_s01_learning_20261031` | 10 | All byte-identical to source and manifest |
| `scripts/import_s01_raw_hybrid.py` | `submission_s01_raw_hybrid_20261031` | 11 | All byte-identical to source and manifest |
| `scripts/import_s01_ml_h04.py` | `submission_s01_ml_h04_20261031` | 5 | All byte-identical to source and manifest |
| **Total** | | **38** | **No mismatches** |

All **80 generated macro values** were independently recomputed from the frozen JSON/CSV inputs and match: 31 controls/integrity, 30 grouped-learning/latency, nine RAW hybrid, and ten H04 V2. Both entrypoints load the new H04 macro file. The table rows match their source totals; there are no duplicate macro definitions within these four generated files.

The guards are visible at `scripts/import_s01_revision.py:34`, `scripts/import_s01_learning.py:32`, `scripts/import_s01_raw_hybrid.py:31`, and the analogous comparison in `scripts/import_s01_ml_h04.py`. Imported evaluation outputs remain snapshots; no old prediction or evaluation was rewritten by these imports.

## Denominators and separation of experiments

| Evidence stream | Verified denominator and result | Manuscript treatment |
|---|---|---|
| Physical H04 successor control | 12 records, 54 event realizations. Single state 37/54 with 37 extras; nominal 44/54 with six; mixture 51/54 with three. | `tables/generated/single_state_control.tex:3` and `sections/article_submission_checks.tex:4` identify an open-development, complete-procedure comparison. Different score semantics and unequal false-alarm operating points are disclosed. |
| Grouped SIM fitting/validation/reserve | 56 dependency groups split 31/8/17; 90/16/70 observation records. Validation has 192 events, 96 load and 96 line. Reserve has 576 events, 288 of each. | `supplement/appendix_grouped_learning.tex:4` correctly describes a retrospective group partition, not a random-report or unseen-source test. |
| Grouped model selection | Baseline validation 92/192 = 5 load + 87 line; SHORT 108/192 = 16 + 92. Reserved SHORT 302/576 = 28 + 274, with three extras. | `tables/generated/grouped_learning.tex:3` explicitly separates these cohorts from H04. The selection rule uses validation, not the reserved outcomes. |
| Normal SIM support | One training normal dependency group, no validation normal group, one reserved normal group. Reserved exposure totals 3,696 repeated-observation seconds with zero alarms. | `supplement/appendix_grouped_learning.tex:41` states the dependence and rejects an independent long-duration or validation false-alarm interpretation. |
| New SHORT H04 V2 replay | 27/54 timely: 0/27 load and 27/27 line; three extras; all 12 records available; 204 normal seconds. | `sections/article_submission_checks.tex:50` and `supplement/appendix_grouped_learning.tex:50` give a common-cohort/common-metric result with a different publication rule. They do not pool it with the 30% reserve. |
| RAW native fixed windows | All 180 windows available; 39 annotation-positive and 141 normal. TP 21, FP one; physical-family coverage 4/24. | Current annotation support and the single retrospective record are explicit. No event-count or independent-trial interpretation is substituted. |
| RAW integrity | 9,200 missing reports with correct affected PMU; corrupt-PMU source correct in 1/2 positive windows, with one additional spurious corruption window. | Missing and corrupt identities remain separate from physical source. Failure and false-positive results are retained. |
| Missing first notice | Four observed absence intervals; both methods detect and locate all four. Mean logical delay 12.13 s versus zero. | The text distinguishes received-report publication from computation/communication latency and does not claim a new attack detector. |
| Metadata-based RAW hybrid | All 24 physical-positive windows: native joint 1/24, hybrid 2/24; one gain and zero losses. Fault 1/1 both; line 0/1 to 1/1; generation and load 0/11 both. | `tables/generated/raw_source_hybrid.tex:3` and the adjacent text preserve all families, the sustained-annotation dependence, and the single-window nature of the gain. |

The 54 H04 event realizations, 576 reserved SIM interventions, 24 RAW physical-positive windows, and four missing intervals are different units. None is used as another experiment's denominator. H04 contains three physical event calendars repeated across conditions; its normal parent also belongs to the reserved SIM group and is explicitly not additional independent normal evidence.

## H04 V2 isolation correction

The manuscript now imports `run/ml_h04_v2`, not the earlier V1 execution. The V2 inference roster retains only record identity, observation path/hash, report count and duration; per-record event/normal `kind` and group membership are absent. The V2 evaluator inspects those grouping data only after prediction sealing.

The earlier V1 metadata exposure is disclosed in the supplement and retained in the imported `v1_deviation.md`. The frozen V2 evaluation includes the per-record parity results. This review additionally compared the two completed runs directly: **12/12 event lists and all 48 prediction arrays match exactly**, including the source labels and class-score arrays. Thus the text's exact-parity statement is supported, rather than inferred from equal aggregate scores. V2 is an isolation audit replay, not another independent sample or a new tuned model.

Its publisher requires six identical argmax labels and has no physical mass/GLR score threshold. The updated main paragraph and supplement explicitly distinguish it from the republished physical procedures. Calling this a common-metric comparison of complete procedures is supported; calling it an identical-clock or isolated-memory ablation would not be. The current text makes the supported claim.

## RAW provenance and restrictions

The manuscript retains the failed historical 21-context reconstruction as a provenance failure. It does not use the diagnostic 10/21 or 2/12 numbers from mismatched contexts as a comparator accuracy. The continuous RAW replay, missing-latency control, and metadata-based source comparison are separate successors.

The hybrid substitutes only a source, using an eligible first same-family diagnosis already emitted within the native window. E6 eligibility depends on its **predicted** physical component. Classes, integrity outputs, availability and emission times are preserved; the archived Top3 remains the ZIP list. The imported comparison records one substitution and 179 fallbacks. All five complete-data segments retain startup unavailability. The manuscript explicitly states that their prefixes are not verified normal and that this segmented ML replay is not a successful execution of the physical history bank.

Metadata supplies BUS39, LINE23–24, BUS2 and BUS7 as family-source labels. Original Event support determines fixed-window membership. The current supplement does not promote coarse workbook minutes into exact actuation/restore times. The unresolved generation/load action boundaries are properly treated as scope limits; they do not require another experiment merely to report these bounded retrospective results.

## Issues raised and closed during this pass

1. **Stationarity evidence was initially outside the paper's frozen controls import.** The main text referred to both the ROCOF scale and temporal-stationarity failure, while the original imported startup result contained the early ROCOF rejection only. The importer now also preserves `physical_raw_prefix_diagnostic.json` and `physical_raw_prefix_shape.json`, byte-identical to the existing completed diagnostics. The numerical claim now has archived evidence. No new experiment or relaxed gate was requested.
2. **The H04 V1 inference roster contained unused cohort metadata.** The final addition uses the new V2 observation-only replay, archives the deviation, and records exact parity. Its 27/54 statement and the publication-rule distinction are correct. V1 was not overwritten or silently relabeled.

There are **no remaining actionable S01 reproducibility errors** from this pass. Known restrictions—open development data, repeated normal histories, unsupported generation for ML, the unreproduced archived calendar, incomplete physical RAW support, approximate source timing, and lack of a real-time claim—are already disclosed. They are not converted here into new experimental requirements.

## Reviewed source snapshot

The final inspected text hashes are:

| File | SHA256 |
|---|---|
| `main.tex` | `05bf7a96e0ede3bbe636dc1314796b43a1f4ea7c9a16fdab8f95f145c2721a34` |
| `supplement.tex` | `9f3bc221ad691d1210e252eecbd249d632b8a9109ca411860c70e8881d05bb51` |
| `sections/article_submission_checks.tex` | `866b296ad67907c84e5166c44034281de6d1833d92a5352b6f1aaf9a457c08b0` |
| `supplement/appendix_grouped_learning.tex` | `1591fc2e4367aabaa1ff94ed497f781bbefb3679faa09c7b016b5fea3336301f` |

Subsequent numerical or cohort-language changes should be checked against this snapshot. This report is the only paper-repository file written by this review. No C01 partial predictions, observations or reserved truth were read.

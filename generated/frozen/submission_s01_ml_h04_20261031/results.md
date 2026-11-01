# Frozen ET SHORT on the common H04 cohort

**Authoritative integration result:** `EVALUATION.json` in this folder.
All 12 H04 records and 54 intended event replays were retained. Predictions
were sealed before this separate evaluation loaded registry truth. All 12
records are available; no event is unavailable. The selected frozen model
was loaded once, with `n_jobs=1` and numerical libraries restricted to one
thread. The inference run took 14.24 seconds including model loading on this
host; this is not an online latency/deployment benchmark.

| Complete procedure | Timely family/source | Extra alarms | Orphan restorations | Premature matched restoration | Missing restoration, including missed events |
|---|---:|---:|---:|---:|---:|
| Frozen ET SHORT | **27/54** | **3** | **3** | **0** | **27** |
| Single state, short GLR | 37/54 | 37 | 32 | 0 | 4 |
| Nominal history bank | 44/54 | 6 | 5 | 0 | 10 |
| Five-model history bank | 51/54 | 3 | 3 | 0 | 3 |

ET SHORT detects and correctly diagnoses 27 events: **0/27 loads and 27/27
lines**, all before true OFF. It has no right-censored or superseded episodes
in this run. The 27 missing-restoration events are the 27 events it did not
detect. Its three orphan restorations close unmatched extra episodes; they
are not premature closures of matched true interventions.

There are zero alarms over 204 monitored normal seconds. Those seconds come
from **one physical normal parent under three conditions**, not three
independent normal experiments. The three event calendars are also repeated
under conditions; the 54 event replays are not 54 independent trajectories.
No confidence intervals or operational false-alarm guarantee are claimed.

## Comparison contract

The ET model, its SHORT feature representation and its publisher were frozen
before this H04 execution. No parameter, feature, threshold, source subset or
model selection was changed after seeing H04 results. The model hash is
`9b83975d80bbb7e8ae7a387b65de486808699a93d941f5635f370ea92578efcb`.
The model and all frozen ML source/reference hashes remain unchanged.

The ET preprocessing uses its archived empirical first-300-report reference,
47 instrument innovations, median/MAD calibration over reports 30:300 and
1457 trailing SHORT features. It does not use the inverse-AC startup gate.
Its publisher requires six identical argmax labels after index 360, without
a confidence threshold. E0 restores; changing source supersedes. This is its
frozen classifier contract, **not** the common probability/GLR EvidenceClock.
The methods have the same six-report persistence count, common observation
cohort and **identical successor event-metric source hash**, but not identical
evidence semantics or matched false-alarm operating points. This is a
complete-procedure comparison, not a pure memory ablation.

The successor evaluator associates the first eligible unmatched alarm by time
before checking labels, uses emitted diagnosis times, includes all missed and
unavailable events, and separates extras, orphan/premature restorations,
missing closures and censoring. The physical reference rows above are from
the existing sealed `../single_state_h04/EVALUATION.json`; they were not
recomputed or altered by this run.

## Group overlap and scope

H04 S001, S004 and S005 share normal group
`G_41c4f849ad529a8d66c9`. The registry assigns that group to the existing ML
`development_holdout_30`, not `train_56` or `validation_14`. It is therefore
not a newly independent normal parent relative to the already evaluated ML
holdout. The three H04 event groups have no group membership in those ML
train/validation/holdout partitions. All 18 source identities are represented
in supervised training: **there is no source-held-out claim**. H04 and the
SIM training campaigns remain previously opened development evidence with
shared F01 ancestry, not external confirmation.

## Preserved V1 and metadata-free V2

The first execution in `../ml_h04/` included unused normal/event `kind` and
group metadata in the roster read by its inference process. These fields
never entered feature extraction, classifier inputs or publication. That
non-influence is now also tested, rather than merely asserted: V2 uses only
IDs, observation paths/hashes, report counts and durations in its inference
roster, and **all output arrays and event objects match V1 exactly on all
12 records**. V1's broad `truth_read:false` flags are qualified in its
`AUDIT_DEVIATION.md`; V1 remains unchanged.

V2's read audit contains observation/model/code resources and its new plan,
but no registry, split, private truth or V1 predictions. Those sources become
available only to the separate post-seal evaluator. V2 is a reproducibility
and isolation audit replay, not another independent trial. It reuses the
unchanged inference function with a new metadata-free protocol and output
path. RAW0001, RAW0002 and C01 were not accessed by either inference run.

Reproduction entry points:

```
python -B experiments/PAPER_SUBMISSION_S01/runtime/ml_h04_observation_only.py freeze
python -B experiments/PAPER_SUBMISSION_S01/runtime/ml_h04_observation_only.py run
python -B experiments/PAPER_SUBMISSION_S01/evaluation/score_ml_h04_v2.py
```

These commands refuse to overwrite the existing frozen plan/run/evaluation;
any further execution requires a new successor location. The current V2 plan
hash is `2e7ca0229dd136dc5e05ac4cbd801ec808fd7a641946587ed0983d85a1287130`.

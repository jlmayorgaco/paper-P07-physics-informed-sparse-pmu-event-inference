# Nine-class competition replay

We fixed the decision rule and the test design in revision `d4f3c83`. We generated
27 new M9 records, with three noise seeds and onset shifts for each of nine
known templates. Each record provides 60 s of startup and one 30-s decision
window. Template targets are fixed within class. M9 synthesizes disturbances
on a power-flow baseline and uses RAW0001 reference statistics. Class 8 is
the generator's unknown-composite proxy. This M9 test measures transfer to
new synthetic observations with familiar templates and sites.

Inference reads eight anonymous-case PMU files with an explicit column allowlist.
Labels are stored separately. The scoring step checks the prediction SHA-256
before opening truth. All 27 windows enter the nine-class macro-F1. Exact
localization uses all 24 nonnormal windows, including missed detections.

| Window-level procedure | Macro-F1 | Exact source | Joint family and source |
|---|---:|---:|---:|
| Original submitted ZIP | 0.2169 | 4/24 | 4/24 |
| Frozen physical Attributor II, window readout | 0.1392 | 5/24 | 5/24 |
| Hybrid family and source correction | 0.2169 | 4/24 | 4/24 |

Attributor II produces episodes and report-level integrity flags. Its stand-alone
window readout takes the first physical episode and gives missing data, then
corruption, priority when composing the window class. Thus its scores depend
on aggregation to the submission's 30-s decision unit. The hybrid defers to
the original frontend when it receives no unique eligible physical diagnosis
and preserves a corruption decision. It used the frontend on all 27 windows.
The separate frozen P07 dynamic startup check rejected all 27 initial voltage-angle
noise estimates. No P07 dynamic source diagnosis contributed on this cohort.

The historical 0.9598 macro-F1 and 0.8524 exact localization are the submitted
ZIP's internal SIM validation scores. The official hidden competition score
and performance on new sites remain unmeasured.

The scoring matrices in `results.json` have true class on rows and predicted
class on columns, both ordered 0 through 8. To reproduce, call
`scripts/benchmark_competition_windows.py` with the stages `prepare`, `predict`,
`startup` and `score`, using an empty output directory, the archived scientific
repository and the extracted original submission. `provenance.json` identifies
the ZIP, generator, expert and observation hashes.

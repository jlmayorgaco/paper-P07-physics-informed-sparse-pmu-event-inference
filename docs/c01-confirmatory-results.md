# C01: confirmatory results without retuning

The frozen campaign completed on 1 November 2026. Its 171 physical trajectories yielded all 342 intended observed records. Predictions were sealed before truth was read; no physical trajectory, method inference, or evaluation record was rejected. The six network/noise strata reuse physical parents. Counts across strata describe paired replays, not independent events. The imported files and SHA-256 ledger are in [`generated/frozen/c01_20261029/MANIFEST.json`](../generated/frozen/c01_20261029/MANIFEST.json).

## Continuous load and line sequence

**Exposure update, 3 November 2026.** The rate examples below preserve the
original frozen definition using complete 120-s records. The current main
article uses 108 monitored seconds per event record after startup. Its rate
differences and interval endpoints are therefore the archived values times
`120/108`, with all predictions and episode matches unchanged. The generated
conversion and source hashes are in
[`monitored_exposure_audit.json`](../generated/monitored_exposure_audit.json)
and [`paired_monitored_intervals.csv`](../generated/paired_monitored_intervals.csv).

Each method saw the same 18 six-event parents, three R/X conditions, two noise scales, and 12 normal parents. Timely means the correct family and source were issued before physical OFF. An extra is an unmatched event-stream alarm; normal-record alarms are separate.

| Frozen method | Timely / 648 | Extra alarms | Out-of-bank timely / 216 | Out-of-bank extras | Normal alarms / 72 |
|---|---:|---:|---:|---:|---:|
| R11 five-model | 644 | 72 | 212 | 68 | 0 |
| R11 nominal | 643 | 92 | 211 | 86 | 0 |
| ExtraTrees reference | 330 | 29 | 110 | 10 | 0 |
| ExtraTrees short-window | 352 | 16 | 117 | 6 | 0 |

R11 attributes 322/324 loads and 322/324 lines in time. The ExtraTrees reference attributes 15/324 loads and 315/324 lines; the short-window adapter attributes 30/324 loads and 322/324 lines. Under matched R/X, R11 and nominal each obtain 216/216 in time with one extra across two noise replays. Under out-of-bank R/X, the R11 stream has 54 restoration messages on unmatched alarm episodes alongside its 68 extra alarms. The frozen CSV calls that count `false_restorations`; it does not measure every physical OFF-timing error. The method is sensitive to mismatch; no correction was made after opening C01.

The paired parent-cluster bootstrap in [`PAIRED_INTERVALS.csv`](../generated/frozen/c01_20261029/PAIRED_INTERVALS.csv) uses 10,000 resamples. For example, at matched R/X and noise scale 1, R11 minus ExtraTrees reference gains 48.1 percentage points in timely attribution (95% interval 44.4–51.7). Under out-of-bank R/X and noise scale 1, it has 55 additional extras per event-record hour (95% interval 36.7–73.3), while retaining a 46.3-point timely gain (42.1–50.0). The rate divides by the full 120-s event-record duration, including the 12-s startup period, rather than monitored time; this is the frozen metric definition. These are descriptive intervals over 30 paired physical parents, not field-population guarantees.

## Persistent line openings and normal records

The persistent-line lane has 27 event parents and 12 normal parents across six paired strata. The primary endpoint is the first stopping decision; a wrong or pre-change first stop cannot be repaired by later output.

| Frozen method | Correct first / 162 | Pre-change first stops | Normal records with an alarm / 72 |
|---|---:|---:|---:|
| R11 five-model | 162 | 0 | 0 |
| R11 nominal | 162 | 0 | 0 |
| ExtraTrees reference | 162 | 0 | 0 |
| ExtraTrees short-window | 162 | 0 | 0 |
| Chen2016 adapter | 74 | 66 | 72 |

The remaining 22 Chen first stops are after the event but on the wrong source. Chen processes 15 Hz nonoverlapping increments, is eligible for persistent line openings, and monitors normals only until its first stop: 2,522 s total across the six replays. The continuously running methods monitor 42,336 s per method. Chen has no load or restoration output. All 162 persistent R11 episodes are open at the record horizon because no reclosure occurs; these are not missed OFF events. The result pertains to the declared Chen adapter and F01 noise, not all implementations of that published approach.

## What can be claimed

C01 supports high timely attribution of known load/line sources on this F01 catalog and shows an unfavorable alarm trade-off under out-of-bank R/X. It does not establish an official hackathon-score improvement, source-excluded transfer, all-family diagnosis, probability calibration, field performance, or real-time throughput. The nominal/mixture contrast cannot be read as an isolated R/X-bank ablation because publication rules also differ. The independent E_i and recovery controls test component explanations and do not change C01.

The machine-readable full denominators, failures, delays, restoration decisions, censoring, source breakdown and paired intervals remain in the sealed CSVs. The coauthor decision should review this full ledger, the theory and closest methods before journal submission.

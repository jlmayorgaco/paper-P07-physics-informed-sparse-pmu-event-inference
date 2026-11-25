# Prospective nine-class PMU test

Compare the frozen integrity successor to the same system with a reduced observation model when the original dynamic filter rejects voltage-angle noise. The reduced bank uses class- and source-conditioned PMU response trajectories fitted on 108 independent M9 development records, three candidate locations per physical family. These are empirical response templates, separate from the original DAE operators. Class 8 is the known M9 composite proxy. Its score does not measure open-set recognition.

Standardize observed channels by fluctuations in the quiet prefix. Average phase magnitudes, centered phase angles, and frequency in one-second blocks. Compare each ten-second trajectory to the preceding five seconds. Search feasible onsets, mask missing coordinates and profile positive amplitude. The gain threshold is 1.1 times the largest calibration null score. A diagonal working covariance ignores cross-channel and temporal correlation, so the gain is a ranking statistic. All tuning is confined to development.

Primary sample: 12 new windows per class, balanced across candidate assets, with source assignment shuffled, severity multiplied by a uniform factor between 0.8 and 1.2, and duration by a uniform factor between 0.85 and 1.15. A separate set of 48 quiet records supplements 12 primary normal records for the false-alarm comparison. Score one decision after 30 seconds using identical signals and deadlines for both procedures. Count exact location on all nonnormal windows. Compare nine-class macro-F1, family accuracy and exact location against 0.90, and count false-alarm windows for both arms over the same monitored exposure. These targets refer to observed estimates. No equivalence margin for population false-alarm risk is specified. The M9 generator models spatial attenuation by numeric bus-ID separation. Using multiple candidate assets tests source discrimination inside this simulator; independent physical-model validation is necessary for generalization.

## Outcome

| Metric | Current hybrid | Response bank |
|---|---:|---:|
| Macro-F1 | 0.4641 | 0.8519 |
| Correct family | 57/108 | 96/108 |
| Exact source on event windows | 30/96 | 77/96 |
| Both family and source on event windows | 30/96 | 77/96 |
| Alarm on normal windows | 0/60 | 0/60 |

The original DAE startup gate rejected the voltage-angle scale on every record. The response bank classified all 36 line, generation and load windows and identified 32 of their sources; the earlier hybrid identified none. The new system missed all 12 class-8 composites, labelling them normal. Six of its seven other location errors confused a bus-39 generation intervention with bus 32, including three composite missing-data cases. The remaining error confused a bus-20 load with bus 7.

The two procedures produced identical decisions on all 60 normal windows (0.5 h). A one-sided exact 95% upper confidence bound for the new procedure's probability of an alarm in a normal window is 4.87%, assuming independent records from this distribution. False alarms during event records and time to recognition are outside this window-level endpoint.

### Reproduction

Use benchmark_competition_windows.prepare with seed 51891217, 12 repetitions, move_integrity=True, and competition_response_bank.CATALOG to generate the 108 development records. Fit bank.json with the fit stage of scripts/competition_response_bank.py. Use its prepare stage for the primary and quiet test records. Run the startup stage of scripts/benchmark_competition_windows.py on each split separately. Run predict with the extracted original submission and finally score. The prediction digest was recorded before evaluation against the two truth files. Training, primary and quiet sets have disjoint seeds. The historical 0.960/85.2% internal competition scores use a different population.

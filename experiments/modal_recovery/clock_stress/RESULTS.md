# Frozen PMU estimator under angular noise and clock error

The frozen angular estimator passed the full comparator-relative criterion in **0 of 55 conditions**. On the new native-noise cohort it correctly diagnosed all 480 catalog events and all 120 targeted loads at bus 31, but raised one alarm in 480 catalog controls. The magnitude estimator raised none. The angular arm also alarmed on two of the 120 targeted controls (zero for magnitudes). Independent static phase-reference offsets as large as ±26.5 µs produced exactly the same calls on all 1,200 records.

At 0.005° added angular noise per V and I channel, 335/480 first alarms preceded the actual second event. All 145 timely alarms gave the right family and asset. Only 38/120 targeted bus-31 loads were detected in time, and all 480 catalog controls alarmed. Premature triggering explains this loss at a scale near the low end of the [two-device laboratory measurements](https://arxiv.org/pdf/2103.09285). The experiment simulates instrument noise at these scales under the specified temporal model.

The estimator and protocol were frozen before new observations (commit `542d385`), the 1,200 anonymous records were archived at `079466c`, and every call was committed before unblinding at `86fea96`.


## Descriptive limits under an absolute false-alarm budget

For interpretation, keep all four efficacy requirements but allow fewer than 5% of the 480 catalog recovery controls to alarm. This is a separate summary from the prespecified comparison against magnitudes. The last column instead allows at most the angular detector's own native count (one). Counts at each level, including high false-alarm rates on long quiet records, appear below.

| Axis | Last level below 5% catalog control alarms with all efficacy targets | First failing level | Last level with at most one alarm and all efficacy targets |
|---|---:|---:|---:|
| Instrument noise (degrees RMS per channel) | 0.001 | 0.002 | 0.00025 |
| Clock jitter (µs RMS per PMU) | 0.025 | 0.05 | 0.005 |
| Combined noise and jitter (degrees RMS per channel) | 0.0005° + 0.025 µs | 0.001° + 0.05 µs | 0.0001° + 0.005 µs |
| Single-clock holdover (µs/s for 8 s) | 0.01 | 0.025 | 0.01 |
| Single-clock step (µs) | 0.1 | 0.25 | 0.05 |
| Persistent clock offset (±µs per PMU) | 26.5 | all passed | 26.5 |

## Counts at every tested level

D, F and L count timely detection, correct family and exact location out of all 480 catalog second events. FA counts catalog recovery-only controls with alarms out of 480. The targeted panel has 120 independent bus-31 events and 120 controls. Long quiet counts upward-crossing episodes, with 5.861 eligible hours per setting. Repetitions across levels reuse the same inputs.

The magnitude comparator reached 443/480 detections, 442/480 correct families and 438/480 locations, alarmed on 0/480 catalog controls, and detected 0/120 targeted bus-31 events. Its long-quiet count was 0.

| Axis | Level | D | F | L | FA | Early | Bus 31 detected | Bus 31 exact | Targeted FA | Long quiet | Primary pass |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|:---:|
| nominal | native | 480 | 480 | 480 | 1 | 0 | 120 | 120 | 2 | 0 | no |
| angle | 0.0001 | 480 | 480 | 480 | 1 | 0 | 120 | 119 | 2 | 0 | no |
| angle | 0.00025 | 480 | 480 | 480 | 1 | 0 | 120 | 119 | 2 | 0 | no |
| angle | 0.0005 | 479 | 479 | 479 | 3 | 1 | 120 | 119 | 2 | 0 | no |
| angle | 0.001 | 478 | 478 | 478 | 7 | 2 | 119 | 119 | 2 | 4 | no |
| angle | 0.002 | 388 | 388 | 388 | 356 | 92 | 100 | 100 | 86 | 6570 | no |
| angle | 0.003 | 231 | 231 | 231 | 480 | 249 | 48 | 48 | 119 | 19906 | no |
| angle | 0.004 | 162 | 162 | 162 | 480 | 318 | 42 | 42 | 120 | 24930 | no |
| angle | 0.005 | 145 | 145 | 145 | 480 | 335 | 38 | 38 | 120 | 23093 | no |
| angle | 0.008 | 138 | 138 | 138 | 480 | 342 | 37 | 37 | 120 | 10738 | no |
| angle | 0.01 | 138 | 138 | 138 | 480 | 342 | 37 | 36 | 120 | 5789 | no |
| angle | 0.02 | 138 | 138 | 137 | 480 | 342 | 37 | 26 | 120 | 285 | no |
| jitter | 0.005 | 480 | 480 | 480 | 1 | 0 | 119 | 119 | 2 | 0 | no |
| jitter | 0.01 | 479 | 479 | 479 | 2 | 1 | 119 | 119 | 2 | 0 | no |
| jitter | 0.025 | 476 | 476 | 476 | 4 | 2 | 117 | 117 | 2 | 8 | no |
| jitter | 0.05 | 436 | 435 | 435 | 172 | 42 | 104 | 104 | 46 | 1414 | no |
| jitter | 0.075 | 342 | 342 | 342 | 386 | 135 | 81 | 81 | 103 | 4164 | no |
| jitter | 0.1 | 266 | 266 | 266 | 466 | 212 | 65 | 64 | 117 | 6491 | no |
| jitter | 0.15 | 187 | 187 | 187 | 480 | 293 | 49 | 49 | 120 | 8605 | no |
| jitter | 0.25 | 146 | 146 | 146 | 480 | 334 | 41 | 40 | 120 | 7532 | no |
| jitter | 0.5 | 139 | 139 | 139 | 480 | 341 | 38 | 31 | 120 | 2528 | no |
| jitter | 1 | 138 | 138 | 135 | 480 | 342 | 37 | 17 | 120 | 317 | no |
| jitter | 2.5 | 138 | 138 | 115 | 480 | 342 | 37 | 1 | 120 | 38 | no |
| offset | 1 | 480 | 480 | 480 | 1 | 0 | 120 | 120 | 2 | 0 | no |
| offset | 26.5 | 480 | 480 | 480 | 1 | 0 | 120 | 120 | 2 | 0 | no |
| drift | 0.005 | 480 | 480 | 480 | 1 | 0 | 120 | 120 | 3 | 0 | no |
| drift | 0.01 | 480 | 480 | 480 | 1 | 0 | 120 | 120 | 3 | 0 | no |
| drift | 0.025 | 479 | 479 | 479 | 47 | 0 | 116 | 116 | 18 | 10 | no |
| drift | 0.05 | 462 | 462 | 462 | 165 | 15 | 111 | 110 | 53 | 17 | no |
| drift | 0.07 | 446 | 445 | 445 | 165 | 32 | 104 | 103 | 53 | 13 | no |
| drift | 0.1 | 404 | 404 | 404 | 165 | 74 | 98 | 98 | 53 | 14 | no |
| drift | 0.25 | 355 | 355 | 355 | 228 | 125 | 84 | 84 | 69 | 515 | no |
| drift | 0.5 | 328 | 328 | 327 | 391 | 152 | 76 | 71 | 108 | 1983 | no |
| drift | 1 | 255 | 255 | 253 | 480 | 225 | 59 | 52 | 120 | 39 | no |
| drift | 10 | 138 | 138 | 102 | 480 | 342 | 37 | 0 | 120 | 36 | no |
| step | 0.025 | 480 | 480 | 480 | 1 | 0 | 120 | 120 | 2 | 0 | no |
| step | 0.05 | 479 | 479 | 479 | 1 | 0 | 120 | 120 | 2 | 0 | no |
| step | 0.1 | 478 | 478 | 478 | 5 | 0 | 116 | 116 | 5 | 0 | no |
| step | 0.25 | 445 | 445 | 445 | 149 | 34 | 110 | 110 | 50 | 2271 | no |
| step | 0.5 | 427 | 426 | 426 | 165 | 53 | 106 | 106 | 53 | 13 | no |
| step | 1 | 411 | 411 | 411 | 227 | 69 | 101 | 101 | 69 | 20 | no |
| step | 2.5 | 377 | 377 | 377 | 347 | 103 | 94 | 91 | 92 | 733 | no |
| step | 5 | 328 | 328 | 324 | 480 | 152 | 80 | 64 | 120 | 2107 | no |
| step | 10 | 327 | 327 | 314 | 480 | 153 | 80 | 48 | 120 | 36 | no |
| step | 26.5 | 326 | 326 | 298 | 480 | 154 | 80 | 41 | 120 | 36 | no |
| joint | 0.0001° + 0.005 µs | 480 | 480 | 480 | 1 | 0 | 119 | 119 | 2 | 0 | no |
| joint | 0.00025° + 0.01 µs | 479 | 479 | 479 | 3 | 1 | 119 | 119 | 2 | 0 | no |
| joint | 0.0005° + 0.025 µs | 475 | 475 | 475 | 12 | 4 | 117 | 117 | 2 | 36 | no |
| joint | 0.001° + 0.05 µs | 400 | 400 | 400 | 270 | 78 | 99 | 99 | 68 | 2948 | no |
| joint | 0.0015° + 0.075 µs | 284 | 283 | 283 | 461 | 196 | 67 | 67 | 116 | 8035 | no |
| joint | 0.002° + 0.1 µs | 212 | 212 | 212 | 479 | 268 | 52 | 52 | 120 | 12319 | no |
| joint | 0.003° + 0.15 µs | 155 | 155 | 155 | 480 | 325 | 38 | 38 | 120 | 14528 | no |
| joint | 0.005° + 0.25 µs | 141 | 141 | 141 | 480 | 339 | 37 | 36 | 120 | 8754 | no |
| joint | 0.008° + 0.5 µs | 138 | 138 | 138 | 480 | 342 | 37 | 27 | 120 | 1731 | no |
| joint | 0.01° + 1 µs | 138 | 138 | 134 | 480 | 342 | 37 | 16 | 120 | 177 | no |

The noise processes, input units, sampling approximation, denominators and inclusion rules are specified in the [prospective protocol](PROTOCOL.md). The [full scores](results/scores.json) include marginal uncertainty and discordant recovery-control calls. The [machine-readable grid](results/operating_points.csv) and [figure](results/operating_limits.png) use the same observations. Models and threshold stayed frozen throughout.

Recount from the committed outputs with `python score.py score`. To rerun both estimators on the archived anonymous PMUs at every level, run `python predict.py replay`. The quiet comparison uses the upstream P2 archive.

# Relative phase recovers weak bus-31 load switches in the P2 simulation

The frozen magnitude-and-angle estimator detected, classified and located 239 of 240 second events before clearance. It produced one alarm in 240 recovery-only controls. Using identical trajectories and deadlines, the preceding magnitude estimator detected 226 events, classified 225 and located 224. It also alarmed on one control. The angular estimator met the prespecified point targets in this trial.

| Blind endpoint | Magnitudes | Magnitudes and relative angles |
|---|---:|---:|
| Timely first alarm | 226/240 (94.17%) | 239/240 (99.58%) |
| Timely correct family | 225/240 (93.75%) | 239/240 (99.58%) |
| Timely exact asset | 224/240 (93.33%) | 239/240 (99.58%) |
| Recovery-only control with an alarm | 1/240 (0.42%) | 1/240 (0.42%) |
| Premature first alarm on an event record | 1/240 (0.42%) | 1/240 (0.42%) |
| Bus-31 load detected and located | 0/13 | 13/13 |

There were 60 matched parents in each ordered combination of load and line families. Every second event contributes to each efficacy denominator. One angular trigger pre-empted a line 23–24 opening by 0.60 s during recovery after restoration of line 16–17. It triggered on the same report in the twin with no second event. The magnitude detector's false alarm occurred on a different control, following restoration of line 9–39. Neither detector alarmed during the additional 5.861 eligible hours of previously published quiet traces.

The new estimator gained 16 exact locations and lost one on matched events (two-sided exact paired p = 0.000275). The marginal one-sided 95% lower binomial bound is 98.04% on each efficacy endpoint and 79.42% on bus-31 detection alone (13 cases). The one-sided upper bound on the angular control-alarm probability is 1.96%. The observed equality of alarm counts leaves uncertainty about any difference in underlying rates.

## What the PMUs saw at bus 31

Development used the preceding study's disclosed 240 event/control pairs. Regenerating these records with angles reproduced their original magnitude samples exactly. The augmented estimator detected and located all 19 bus-31 loads, compared with zero for magnitudes, and its control alarms fell from one to zero. The retained threshold was 63.456685, the maximum over 320 independent calibration recoveries. Two lower candidate thresholds gave three and ten development control alarms.

For a diagnostic using development twins, divide each channel's RMS event-minus-control difference by its within-record quiet RMS noise. For each of the 19 loads take the largest ratio in each measurement group, then the median across cases. The median was 0.18 for magnitudes, 15.49 for the voltage quadrature, and 2.16 for the current quadrature. Voltage at PMU 6 relative to PMU 2 gave the largest voltage ratio in all 19 cases. The current paired with the voltage at PMU 10 gave the largest current ratio throughout. These describe measurement sensitivity; the scored estimator uses all channels and has no access to the twins.

The strongest voltage difference had approximately 0.00040° within-record RMS quiet noise under this instrument model. The comparison tests fresh events with nominal simulated noise at the same operating point, same eight PMUs and same candidate catalog. It conditions on the known first restoration time. Field performance, transfer to a different CT mapping and robustness to differential phase timing errors remain open.

## Reproduce the comparison

The [development decision](results/development.json), [protocol](PROTOCOL.md), fitted weights and threshold were frozen in `4d15ceb` before prospective test generation. The [paired calls](results/predictions.json) and [480 anonymous PMU records](results/blind_pmus.zip) were published in `cf2544a` before opening the labels. From this directory, `python campaign.py replay` reproduces all 960 arm-by-record calls from the archive. `python campaign.py score` verifies the [counts, uncertainty and paired discordances](results/scores.json). The [measurement sensitivity by channel group](results/development_sensitivity.json) is reproducible with `python sensitivity.py` on the disclosed development trajectories.

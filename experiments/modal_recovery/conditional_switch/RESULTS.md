# Second-event detection during IEEE-39 recovery

The recovery-conditioned detector issued 218 timely alarms in 240 new second-event simulations. It correctly classified 217 and located 216 before the event cleared. It issued one alarm in 240 matched recoveries with no second event. It met the control-alarm requirement. Each efficacy endpoint fell below the prespecified 228 required successes.

| Outcome | Current modal detector and readout | Adjusted detector, current readout | Adjusted detector and readout |
|---|---:|---:|---:|
| Timely first detection | 211 (87.92%) | 218 (90.83%) | 218 (90.83%) |
| Timely correct family | 209 (87.08%) | 217 (90.42%) | 217 (90.42%) |
| Timely exact source | 187 (77.92%) | 210 (87.50%) | 216 (90.00%) |
| Control with any alarm | 12 (5.00%) | 1 (0.42%) | 1 (0.42%) |
| Positive case with an early first alarm | 7 (2.92%) | 1 (0.42%) | 1 (0.42%) |

Each denominator is 240. All missed and premature alarms count against both diagnosis endpoints. There were 60 independent parents in each ordered pair of load and line families. The simulator, operating point and catalog were shared across development and test. Each detector received the same initially quiet PMU prefix, first restoration timestamp and subsequent observations. The 480 new simulated traces, all frozen model weights, calls and labels are archived here. The additional replay of previously published long normal traces produced zero alarms with either method in 5.861 eligible hours.

In the paired comparison, the adjusted method gained 30 exact locations and lost one (two-sided exact paired p = 2.98 × 10⁻⁸). On controls it eliminated 12 alarms and introduced one (p = 0.0034). The adjusted detector gained nine timely alarms and lost two (p = 0.065). The marginal one-sided 95% upper binomial bound on the new control-alarm probability is 1.96% for this benchmark case mix.

## The original twelve failures

In the previous trial, four of the six undetected loads were at bus 31 and two at bus 26. The previous detector stayed below threshold on all six even when the paired simulation supplied the isolated second-event signal. All six premature alarms crossed at exactly the same report and score on their recovery-only twins, 0.18 to 1.42 s ahead of the second event. Five followed restoration of line 26–29. At the original crossing, the isolated recovery by itself crossed threshold in one of the six and the noise by itself crossed in none.

The adjusted detector predicts the uninterrupted recovery from the first second of post-restoration PMU data and looks for an additional change consistent with a specific line or load. On retrospective replay it correctly detected and located all six previously pre-empted second events and the two bus-26 loads. The four bus-31 loads still produced no alarm. The twelve retrospective results were available for development.

## What limited the blind result

The adjusted method detected 119/120 line events and 99/120 load events. It gave the exact location for 118/120 lines and 98/120 loads. Of the 24 exact-location failures, 19 were missed bus-31 loads, two were missed bus-26 loads, one was a premature alarm, one was a family error, and one was a wrong bus within the correct family. The premature alarm followed a bus-20 restoration and also occurred on its twin.

For a post-unblinding sensitivity measurement, subtract the matched control from each load trace while the second event is active. For each channel, divide the RMS paired difference by that channel's pooled, within-record RMS noise from one initial quiet second per parent. Take the largest channel ratio in each case, then the median across cases for that bus. The median was **0.177 at bus 31** (range 0.068–0.292), **2.249 at bus 26**, and **13.457 at bus 20**. The low paired contrast at bus 31 explains why the next test should assess additional PMU information there. A single-channel RMS calculation does not bound the performance of a multichannel temporal estimator.

## Verification

The [protocol](PROTOCOL.md), weights and threshold were frozen at `eae30b1`. The [predictions](results/predictions.json) and [anonymous PMU inputs](results/blind_pmus.zip) were committed at `49a6048` before unblinding. From this directory, `python observations.py replay` reproduces all three arms' calls on all 480 archived observations. `python run.py score` checks the published [counts and paired comparisons](results/scores.json). `python paired_signal.py` reproduces the [sensitivity calculation](results/paired_signal.json). The original counterfactuals and their retrospective replay are in [diagnosis.json](diagnosis.json) and [retrospective.json](results/retrospective.json).

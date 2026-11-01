# P07: contribution, evidence and closure

Coauthor-review draft | 31 Oct 2026, 17:12 Colombia

## Question and contribution

Can eight PMUs distinguish a new load/line intervention from the electrical recovery of an earlier one? P07 specifies a causal physical-history attribution procedure: retained states survive restoration, new interventions compete with recovery, and active-event mass is distinguished from originating-cause mass. This connects the physical cause, its active interval and the remaining response in one sequential explanation, tested against operational errors rather than accuracy alone.

## Where physics and Bayes enter

Kirchhoff constraints, Ybus, oriented branch currents and machine/control dynamics determine reduced DAE predictors. Known PMU locations select the observation map; phase and instrument memory supply frequency/ROCOF predictions. States and operating context come from past PMU reports. Conditional Gaussian evidence integrates truncated load severity; predictive likelihoods weight five constant R/X hypotheses. Onset screening, shared regime covariances, pruning and publication rules make the complete procedure approximate.

## Completed evidence: development, not C01 confirmation

| H04 procedure | Timely family + source | Extra alarms |
|---|---|---|
| Physical: five models | 53/54 | 4 |
| Physical: nominal | 54/54 | 7 |
| Both frozen ExtraTrees adapters | 27/54 | 3 |

54 realizations repeat 18 interventions across three network conditions; normal exposure is only 204 s per method. Nominal/mixture publication paths also differ, so this is not an isolated R/X-bank ablation.

## What the controlled experiments establish

With load family and ON/OFF supplied, recentering and conditioned signatures both recover 240/240 sources (80 physical event cases, three shared-noise realizations). Conditioning lowers median relative response error 1.25% to 0.0561% and severity error at the generating source 1.2% to 0.329%. A separate 38-trajectory recovery control finds no mean binary-localization gain (98.35% for both arms; 12 correlated, known-history/onset comparisons). Better fit, source identity and calibrated uncertainty are distinct outcomes.

## Difference from the hackathon and the literature

The contribution changes the explanation and temporal evaluation, rather than adding a source-label classifier. H04 favors the physical procedures on loads but not on extra-alarm count; it is not an official leaderboard comparison. Warner already uses physical trajectories and onset search; IMM/M3H already retains mode histories. No numerical advantage over an unexecuted matched M3H/Warner method is claimed.

## Limits and the fixed route to submission

C01: 213/342 records complete at this snapshot; 171 physical trajectories have finished. Estimated remaining processing is 25 h (recent timing envelope 21-33 h), plus evaluation/build. Finish the frozen comparison of R11, nominal and both ExtraTrees adapters; score Chen2016 on persistent openings. Audit all intended cases, normal exposure, delays, censoring and parent-paired intervals, then finalize claims with the coauthors. Scope remains nine load and nine line assets, an event-free startup and a declared simulator. No field, unseen-source, all-family, real-time or calibrated-probability claim; BUS5 terminal and BUS39 angle limitations remain. No new method versions or test tuning.

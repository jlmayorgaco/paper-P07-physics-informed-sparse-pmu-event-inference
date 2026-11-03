# P07: contribution, evidence and limits

Coauthor-review draft | 03 Nov 2026, 00:07 Colombia

## Question and actual contribution

How can eight PMUs distinguish the physical cause of a network disturbance? The paper connects network-constrained reconstruction, physical response signatures and Bayesian history attribution, with engineered-feature ExtraTrees as a retained alternative. The implemented causal bank predicts each candidate intervention from estimated past states, integrates load severity and retains recovery. Active and cause masses expose its decisions. These are approximate conditional calculations, not a new Bayes theorem or a globally optimal filter.

## Earlier evidence is part of the paper

Separate component tests recover hidden voltages, quantify feature gains and show that mixed-source sensitivities improve local response fit. A direct historical transfer of the submitted ZIP yields 0/96 joint source decisions versus 96/96 for an earlier physical estimator; its confusion matrices are included, with the development/domain advantage explicit. The archived batch Bayesian support test retains its evidence-normalization caveat. None of these tests isolates a tensor/Bayes contribution to final causal accuracy. The frozen continuous comparison uses new causal ExtraTrees comparators, not the original 30-s submission.

## Sealed comparison: 171 physical trajectories, 342 observed records

| Frozen continuous method | Timely / 648 | Extras | Outside-bank timely / 216 | Outside-bank extras |
|---|---:|---:|---:|---:|
| Physical bank (5 models) | 644/648 | 72 | 212/216 | 68 |
| Physical bank (nominal) | 643/648 | 92 | 211/216 | 86 |
| ExtraTrees reference | 330/648 | 29 | 110/216 | 10 |
| ExtraTrees short | 352/648 | 16 | 117/216 | 6 |

## Other outcomes that change the interpretation

Continuous: the physical bank attributes 322/324 loads and 322/324 lines before OFF; the ExtraTrees reference attributes 15/324 loads and 315/324 lines; the short-window variant gets 30/324 loads and 322/324 lines. All timely matched decisions have correct family/source: the main gap is timely coverage, not conditional classification accuracy. Persistent line: both physical banks and both ExtraTrees adapters make 162/162 correct first decisions; Chen2016 makes 74/162, with 66 pre-change stops. After first detection, physical banks produce 0 extras versus 164/179 for the two trees (post hoc persistence audit). Chen stops on all 72/72 normal records; physical banks and trees alarm on 0/72, with different exposure.

## Interpretation and limits

The sealed study supports timely attribution on the declared nine-load/nine-line simulator catalog, especially loads, while exposing an alarm burden under network mismatch. Replayed conditions and noise share parents; 648 is not 648 independent events. Original tree validation shares two normal groups with fitting; the later grouped 70/30 study is a different model. No official hackathon-score improvement, source-excluded transfer, all-family diagnosis, calibrated probabilities, field operation or real-time throughput is established. Warner trajectory search and IMM/multiple-history methods are acknowledged; no matched numerical advantage over them is claimed.

## Controlled component study and coauthor decision

Posthoc study on 18 parents/108 events: marginal/carry: 108/108 and 1 extras; profile/carry: 108/108 and 1 extras; marginal/reset: 75/108 and 166 extras; profile/reset: 75/108 and 166 extras. Both carry arms also have one unmatched restoration; both reset arms have 130 and 33/108 events without a timely diagnosis. Median diagnosis delay is 0.267 s with carry and 0.337 s after reset. Normal controls have 0 false alarms in 1,764 s measured exposure (588 s from each of three 600-s records). Paired 18-parent intervals for carry versus reset are +0.306 timely fraction (95% CI 0.241-0.380) and -275 extras per event-record hour (95% CI -325 to -223.333), descriptive and posthoc. The marginal and bounded-profile scores tie on these endpoints. The profile arm retains conditional Bayesian state estimation and fixed priors; reset removes only physical-state carry at inferred closure, not instrumental memory or simulated state. These outcomes do not establish independent confirmation or superiority at matched false-alarm rates. Author declarations remain open.

# P07: contribution, evidence and limits

Review draft | 04 Nov 2026, 11:25 Colombia

## Contribution

A sparse-PMU procedure compares new load/line interventions with the response retained after restoration. Switched DAE predictors start from estimated past states; active and originating-cause weights distinguish an intervention from its continuing effect. The electrical histories connect the intervention, its active interval and the continuing response in one sequential explanation.

## Independent simulated comparison

| Procedure | Timely family + source | Extra alarms |
|---|---|---|
| Physical bank | 644/648 | 72 |
| Nominal bank | 643/648 | 92 |
| ExtraTrees | 330/648 | 29 |
| ExtraTrees short | 352/648 | 16 |

## What the controlled results establish

On 18 existing continuous parents, preserving physical-state deviations gives 108/108 timely attributions and 1 extra; resetting them gives 75/108 and 166 extras. Marginal and bounded-profile scores tie on those endpoints. The state-carry benefit persists under both severity scores. A development-only continuous single-state GLR control exists; it still needs independent validation under matched information and calibration.

## Difference from the hackathon and the literature

Both causal ExtraTrees models were retrained for all 18 sources on earlier simulation parents; their weights differ from the original hackathon submission. The physical gain is predominantly timely load coverage; line coverage is similar to the short-window model. Physical trajectory diagnosis and M3H histories have direct precedents. The contribution concerns recovery-consistent attribution and its operational trade-offs.

## Corrections and remaining submission blockers

The manuscript now uses monitored exposure (108 s per 120-s event record); alarm-rate differences and their intervals rise by 120/108, without changing predictions or matches. It states the balanced phase-A/47-coordinate map, observation memory and measured compute cost. The active validation work tests independent continuous-observer comparison at matched information and alarm budgets, followed by cross-model transfer and calibration of attribution masses. Author approval and declarations remain open. B01 is separate and still running; no partial outcome is used here.

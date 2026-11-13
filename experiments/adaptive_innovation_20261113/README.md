# WITHDRAWN: incorrect OFF operator in the auxiliary diagnostic

The source indexed OFF as `4+5*cell`, which is the half-report ON operator.
The archived builder orders stay, ON-end, OFF-end, ON-mid, OFF-mid; the
correct full-report OFF index is `3+5*cell`. The prior internal recurrence
check repeated the same wrong index and did not catch this semantic error.
All previous numerical findings below are historical and withdrawn.
The original code, protocol and sealed run remain unchanged for audit.
The corrected successor is `../adaptive_innovation_20261113_corrected`, with
fresh CAL/TEST/noise seeds and no other methodological tuning. This correction
concerns only this auxiliary diagnostic, not C01, C02 or C03.

---

# Nominal load-operator mechanism diagnostics, 13 November 2026

These completed diagnostics are independent of C03, which was neither changed
nor used as an observation source. They use the already archived nominal
IEEE-39 operator snapshot in `../channel_information_20261112/input_snapshot.npz`.
They are **not** R11 detector benchmarks, nonlinear plant simulations, tests of
independent PMU TVE noise, or evidence of transfer to a second plant.

## Frozen execution and audit

`run/EXECUTION_FREEZE.json` hashes `study.py` and `protocol.json` before execution.
`CAL_SELECTION.json` records threshold selection from 36 normal records (5.88 h)
and is hashed by `TEST_STARTED.json` before TEST streams are generated.
`COMPLETE.json` seals all 121 run files. No thresholds/settings were revised
after TEST. Prediction arrays retain full precision for independent recounts.

From the paper root, Python with NumPy and SciPy:

```
python scripts/build_adaptive_diagnostic_tables.py
```

This audits hashes, independently reconstructs publication/refractory logic,
checks every CAL threshold count and TEST endpoint, and regenerates manuscript
tables/macros. For a full repeat, copy this directory and its sibling nominal
snapshot directory to a fresh workspace; preserve the original `run` externally,
and use a new `run` directory containing only the original EXECUTION_FREEZE.json.
Then execute `python study.py` from the copied diagnostic directory. Do not use
`--freeze` to replace the historical design or overwrite completed evidence.
JSON and source bytes are protected from Git newline conversion.

## Results and interpretation

1. **Inherited covariance:** 360 independent noise/latent-severity draws over
   fixed nominal source signatures. Onset, amplitude and recovery mean are known.
   Keeping the rank-one inherited covariance improves source ranking from
   281/360 to 338/360 (+15.83 pp, paired 95% interval [11.94, 19.72]). The model
   generating the data exactly contains that covariance. This demonstrates a
   conditional information loss, not superiority of explicit histories over
   an equivalent fused predictive distribution. It has no detector FAR endpoint.
2. **Noise learning:** a causal per-report Gaussian source/age mixture, not a
   history posterior. CAL chooses thresholds 4, 1, 4 for fixed, continuous and
   guarded learning. TEST has 36 normal and 36 event records (72 loads). Timely
   correct source counts are 13, 15, 13; extras are 33, 32, 33; normal alarms
   over 5.88 h are 1, 0, 0. Continuous minus fixed: +2.78 pp, paired 95% interval
   [-2.78, 8.33]. Thus no attribution advantage is established. The guard admits
   only 8.13% of monitored normal reports and barely learns the noise changes.

Bootstrap units are the 360 independent draws for (1), and the 36 event records
for (2); 10,000 resamples. Conditional exact Poisson FAR limits do not establish
a homogeneous Poisson alarm process under noise changes and a refractory clock.
The observation center remains fixed. The Gaussian severity prior is untruncated.
The second test estimates source only: no family classification or OFF estimator.
All generated parents remain in their denominators; no execution failed.

`OPERATOR_CHECK.json` checks actual load ON/stay/OFF operator ordering against
explicit physical-state and null-filter recursions (max error 2.713e-10).
This is not equivalence to the whole R11 observer. Prefix invariance is checked
before CAL. There is no bounded-window smoother implementation in this study.

Next: implement and verify per-history covariance in an isolated successor;
develop a noise-change admission rule on fresh development data; freeze a new
full-bank protocol before testing. The failed quiet gate must not be advertised
as a validated improvement or tuned using these TEST outcomes.

# C03 execution audit — 2026-11-12

## Scope and safety

This is a read-only audit of `experiments/PAPER_RECOVERY_C03` in the SGSMA26 repository. Sources, configuration, locks and CAL execution metadata were read; none was modified. No private TEST truth or TEST prediction payload was opened. `RAW0002` was not accessed. This note is an execution and design audit, not a new scientific result.

The SIM0001 continuity documents were read. They identify F01 as a frozen research candidate (not an officially validated baseline), preserve the provisional historical BUS5 5–6 hypothesis, and require successor documentation for changes. The P07 repository's `AGENTS.md` was also read; no article or protected figure was edited.

## Live campaign state

At inspection, `run/execution.lock` contained PID `32480`; the matching `python3.13` supervisor was alive. `run/logs/campaign_stdout.log` ended at `INFERENCE F01 CAL 53 72`; case `C03_2274daa74a44` was subsequently writing reset-arm CAL prediction files, beginning with threshold 2.197. There were 54 `READY.json` CAL banks. `CAL_SELECTION.json`, `METHOD_FREEZE.json`, TEST seals/results, and an evaluation lock were absent. The existing `RUNTIME_SMOKE.json` was marked `cal_only: true`; no TEST result has been opened.

The supervisor had run since 2026-11-11 17:19 local time. Its CPU time was about 1,494 seconds and its own RSS about 60 MB at the snapshot; these are supervisor-only readings, not total child-process resource use. Output mtimes were advancing. Keep this single supervisor as the sole writer of C03's RUN tree until it exits and releases the lock.

### Remaining-time estimate

The ordered observation metadata shows the first 36 CAL cases are 3,601-report events, cases 37–54 are 18,001-report normals, and the 18 remaining cases are all 18,001-report normals. Per-prediction JSON files repeat the same `seconds` value for all six thresholds when the history arm scores them in one execution; those six rows must count as one invocation. Grouping by arm and report length gives these approximate per-invocation medians: history 35 s (3,601) / 229 s (18,001), carry 43 s / 218 s, reset 44 s / 219 s. The corresponding normal means are about 223–224 s.

For the 18 remaining normal cases, each requires one history invocation and six each of carry and reset. Using the measured per-arm medians gives `18 × (229 + 6×218 + 6×219) = 47,574 s`, or **about 13.2 h** of remaining scoring, plus outstanding work on the active case, startup, bank construction, and any retries. Plan on **about 14–15 h** from the observed state if the sequence remains single-process. This is materially more reliable than extrapolating from parent-directory cadence.

TEST nominal prediction uses one frozen threshold per arm, so each of the 144 parents needs three score invocations, not 13. Assuming each plant has 36 normal and 36 event parents, measured medians imply about `2 × 36 × 3 × (219 + 41) = 56,160 s` (**15.6 h**) for nominal scoring. Stress adds two history-only variants for 12 normal and 12 event parents per plant: about `2 × 2 × 12 × (229 + 35) = 12,672 s` (**3.5 h**). Thus measured scoring alone suggests roughly **19–20 h** sequentially; physics generation, 240 bank builds, staging/startup, and retries add uncertain time. A prudent initial planning range is **about 1–2 days**, to be tightened from actual TEST generation and bank timings as they appear. This is an extrapolation, not a guaranteed completion time.

There is no safe throughput switch by changing frozen code or launching a second campaign: the supervisor owns the run lock, case directories, logs, and eventual seals. A constrained optimization could be technically possible only if the supervisor is paused at a verified quiescent boundary, and a coordinator then runs the exact frozen worker sequentially over a small number of *disjoint future case/arm paths*, each writing only its own expected prediction path. The parent reported about 8 GiB free RAM and a scoring worker around 355 MiB RSS, so two or three workers might fit, but bank construction (especially Julia) can use substantially more memory. This path carries meaningful operational risk: process suspension can strand a subprocess or leave the supervisor unaware of manually generated outputs; overlapping same-path writes or duplicate log names can invalidate immutability; CPU and storage contention can erase the gain. No concurrency was tested or started. Recommendation: keep single-process execution unless the owner can supervise a quiescent-boundary prefill, enforce disjoint paths and unique logs, cap concurrency initially at two after observing bank-build RSS, and then verify every output through the existing seals. Otherwise let the current process finish unchanged.

## What collapse currently does

The frozen `worker.py::collapse` implementation operates only after the common publication clock emits OFF. It marks paths with finite `model.off` as retired and computes their normalized joint mass with the normal hypothesis. The fused H0 mean is the mass-weighted mean of the previous H0 and retired path means, including each path's posterior amplitude mean. It computes a scalar total variance contribution from between-path mean spread plus within-path amplitude variance projected through `d`, and returns that value as `discarded_covariance_trace`.

It then sets `model.logn` to the combined log mass, removes retired paths, and leaves active paths intact. With the `reset` arm only, it zeros the first 114 coordinates of the fused `m0`. If any retired path existed (or reset was requested), it clears `h0_history` and resets the continuous bank and recovery proposal using the new `m0`. The mass-conservation check verifies the normal-plus-path log mass before and after. The covariance trace is **measured and reported but not injected into H0 uncertainty**; H0 is represented here by its mean, while subsequent path inference has its own shared covariance/amplitude structures. `carry` therefore means mean carry with path retirement and history/bank invalidation, not covariance-preserving fusion.

This makes the current arm contrast confounded for causal attribution: `history` leaves old hypotheses and histories in place; `carry` retires/fuses hypotheses and clears history/bank state; `reset` adds a physical-coordinate mean reset on top of `carry`. A better `history` score does not, by itself, prove that the missing covariance caused the gap. Conversely, a large logged discarded trace does not show that restoring that covariance would improve inference.

## A finite successor diagnostic

The ideas below were the initial design alternatives. The later
[C04 protocol](C04_DISTRIBUTION_CONTROL_PROTOCOL.md) supersedes this arm list
with a bounded history/mean/mean-plus-covariance/reset design. It fixes 12
CAL parents but remains unimplemented. It isolates covariance retention
within the fusion family, not a pure effect of history labels.

Do not append diagnostic work to C03's sealed RUN tree or change its frozen worker. After C03 has completed and the exact outputs are audited, use a new, separately named recovery-distribution candidate. Start with a short CAL-only mechanism study using already permitted CAL observations, never TEST truth. Freeze its source/configuration hashes and the case selection before scoring. A reasonable bounded first pass is 12 paired CAL parents (six event, six normal), with one fixed post-OFF continuation horizon and the same observation bytes, bank, threshold, and publication clock in every arm.

The minimum arms needed to separate the mechanisms are:

1. **Existing mean-only fusion, histories cleared** — C03 `carry` reference.
2. **Moment-matched covariance fusion, histories cleared** — same retirement, mean, clock, and reset behavior, but preserve a documented positive-semidefinite covariance approximation for the retired-path mixture and propagate it in the H0 predictive likelihood.
3. **Mean-only fusion, sufficient history retained** — same mean-only projection, but retain only history that remains valid under the post-fusion state/reference; stale snapshots must not be replayed.
4. **Moment-matched covariance fusion, valid history retained** — checks interaction between covariance and remaining valid history.

Report paired post-OFF predictive log score, calibration/coverage diagnostics available without truth, recovery proposal score, and emitted events. The diagnostic should additionally report eigenvalue/PSD repair, covariance trace before/after projection, and whether prediction changes can be attributed to covariance vs valid-history retention. The current model does not expose a general H0 covariance state, so arm 2 is a method change: implement and document an explicit propagated covariance representation in the new candidate; do not describe simply adding the scalar trace to an unrelated existing covariance as covariance preservation.

Keep this diagnostic finite: 12 parents × 4 arms × one frozen threshold, only after the C03 outputs are sealed. The expected compute is on the order of tens of minutes to a few hours at the observed score rate, plus implementation/validation time; cap it at 12 parents for the first pass. If too few parents produce an OFF commit and a usable post-OFF continuation, report the diagnostic as underpowered and design a new prospective CAL candidate rather than expanding post hoc into TEST. Any larger confirmatory study requires a new scenario freeze and independent holdout plan.

## Recommended next actions

1. Let PID 32480 finish without intervention; retain the lock and all output files.
2. Let the existing controller perform its frozen transitions. Once the campaign exits, audit seals, CAL selection, freezes, and rejected scenarios before manuscript import. Confirm completion from the evaluation lock and read-only process inspection.
3. Estimate actual remaining TEST duration from the completed CAL per-worker telemetry and physics-generation times before making a scheduling decision.
4. Treat the four-arm recovery-distribution experiment as a new CAL-only successor. Do not claim C03 tested covariance-preserving fusion; it did not.

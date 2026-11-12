# C04 distribution-control protocol (DEV only)

**Status:** design for a bounded successor experiment. Nothing in this protocol has been executed. C03 remains frozen and is not modified. This DEV study cannot supply confirmatory evidence or a paper claim.

## Question and limits

C03's `carry` arm fuses retired posterior paths into H0 by mean, records the omitted mixture variance, then clears state-history and proposal suffixes. C03 does not carry that variance into the H0 predictive distribution. C04 asks whether that omitted uncertainty changes short-horizon recovery behavior when the fusion, event model, evidence clock, and threshold are otherwise held fixed.

This four-arm design distinguishes covariance retention within the fusion family. The `history` arm is a broad no-collapse reference that retains event paths and their histories; any `history` versus fusion difference still combines path retention, history retention, and projection. It must not be interpreted as an isolated history effect.

## Inputs and outcome-blind case selection

Use only the frozen, public CAL observation inventory at `SGSMA26-Physics-Informed-AD/experiments/PAPER_RECOVERY_C03/run/OBSERVATIONS_F01_CAL.json` and its listed CAL observation files. Do not read `truth_private`, TEST observations, or any test labels. The complete selected set is fixed here from inventory metadata, before looking at prediction scores or events.

Partition rows by `reports`: 3,601-report event cases and 18,001-report normal cases. Within each partition, compute the lowercase hexadecimal SHA-256 of the UTF-8 string `P07-C04-v1|` concatenated with the row's `id`; sort ascending by that digest and select the first six. This yields six event and six normal parents, all marked available in the inventory:

| Class | Parent ID | Selection digest |
|---|---|---|
| Event | `C03_06b90acd6937` | `01a5ea0a1727f37ae99e6b80f78c31c2d574365b9c41547cc049dddf580733c0` |
| Event | `C03_5326c836ab2d` | `0984effde46c9a1744d8292c946a244a3d0a313bf73c635580b99659aa3dc965` |
| Event | `C03_bedd6c9788b3` | `183a927c874c0e6c5fee71bb4e55d69ef8b190e464673420e5d36d9f2f35059f` |
| Event | `C03_1dad8ce3f4d7` | `28f5f45c30de0f7476bbb7208ea866e8663ef462b0fb72e7c249a115cad45dc7` |
| Event | `C03_3ba393445709` | `35f58bbcd0abe1075e15c9225b973b3045c690478c75c2902d2530d49170827a` |
| Event | `C03_b1d4fa620115` | `37c7d2946f009a4b5fc0fe08c95bf7429741fba51f576dd0a85925f8a7238e98` |
| Normal | `C03_47af16123241` | `0e1dd1cd41df3e37e29ea5fbf336aa61b2d285f5185b5d5cca98c86491fce2d2` |
| Normal | `C03_2d9f9ad73a6f` | `11cf661f96f655cb9ad7549880ab9f755ee9b89e44a108583cfacad95d098598` |
| Normal | `C03_3019d1a5c427` | `17347eac3766c8a6abe07dd2d4e314928fc6108954a222516105be5d84ce684d` |
| Normal | `C03_814599cf6117` | `1c9d7fe9547dbb26433c789b6fd7f92f6a30732c163580be2896559cbea850ee` |
| Normal | `C03_d44e36654ab9` | `228ecf2cdcd970376a0e4a3ac646da511052ed4eaa792d768b8ff385032dc1d3` |
| Normal | `C03_4891a60e0a0c` | `264411237a5818aa1f290e8d16e827e21387a4e3d9b4e1cf11e9a68c4a612dd6` |

Use a **single common publication threshold** `h = 3.8918202981106265` (the third value in the frozen C03 threshold grid) for all four arms. This is a prespecified diagnostic setting, not a CAL-selected or performance-optimized threshold. Each selected parent receives the same bank, observation bytes, initialization, and horizon in every arm. Keep C03's 300-report common startup prefix and score only the same remaining reports. Generate no new scenarios.

## Four arms

All arms use one nominal physical parameter particle, the same fixed physical bank, noise fit, severity support, event onset/OFF hazards, pruning limits, transitions, online proposal kernels, and `EvidenceClock`. The common clock receives the arm's own `M` and restoration support at each report; its boundaries are never tuned per arm. The only intended intervention is what happens at a clock-published OFF.

1. **History:** C03's no-collapse behavior. Do not merge retired paths at published OFF. Keep the path mixture and its current H0/proposal histories; pass the same OFF action through the common publication clock.
2. **Mean fusion:** C03's `carry` operation. At published OFF, merge the normal and retired-path mass into one H0 mean; remove only retired paths; clear `h0_history`; reset `ContinuousBank` to the fused mean; reset the conditional-recovery rolling window. Retain no between-path or amplitude covariance beyond the unchanged common regime covariance.
3. **Mean + covariance fusion:** Apply the same mass and mean projection and retire the same paths as arm 2, but also represent the projected mixture's added covariance as a low-rank factor on that H0 particle. Clear/reset the same histories and proposal suffixes as arm 2. This is not a scalar trace patch.
4. **Reset:** C03's `reset` operation: perform arm 2's mean-only fusion and then zero exactly the first 114 (physical) coordinates of `m0`. Do not add projected covariance. Keep C03's other post-fusion invalidation actions identical to arm 2.

For every committed OFF, retain pre/post normal-plus-path probability mass, fused mean, covariance rank/trace, eigenvalue repair, and reset-vector norm. Check mass conservation to `1e-10`, finite values, symmetric covariance, and positive semidefiniteness at every projection and update.

## Covariance representation and model interactions

The C03 observer loaded by `run/dependencies/frozen_R11/observer/run.py` is `static_rx.Particle(AuditV9)`, where `AuditV9` wraps `runtime/core_v9.py` and `runtime/core_v6.py`. This model's `m0` is the augmented state mean. It has no per-H0 covariance state. The physical-state output is the first 114 coordinates; the augmented state also contains instrument and phase-memory coordinates. The frozen `bank['P'][regime]`, `Sinv`, `logdet`, and `K` are shared stationary regime covariances/gains, not posterior covariance objects for a particular H0 particle.

Represent the extra H0 covariance as `L0 @ L0.T`, a low-rank covariance **increment** relative to the currently selected shared `P[regime]`. Do not replace `P`, add the same `P` once per mixture component, or confuse covariance rank with a change in event severity. In the nominal-only DEV bank there is one H0 factor. If a later candidate restores a multi-particle static ensemble, each particle must own its own H0 factor; do not pool factors across particles.

At a commit, condition on the fused normal-plus-retired mass. Let `alpha_j` be normalized component weights, `mu0=m0`, and for each retired load path `mu_j=m_j+d_j*E[a_j | data]`. Use:

```text
mu = sum_j alpha_j mu_j
C_extra = alpha_0 L0 L0' +
           alpha_0 (mu0-mu)(mu0-mu)' +
           sum_retired alpha_j (mu_j-mu)(mu_j-mu)' +
           sum_retired_load alpha_j Var(a_j | data) d_j d_j'
```

The current C03 `core_v6` model does not store per-path state factors, so the DEV formula has no path-factor term to include. For line paths, C03 fixes the path's severity and `amplitudes()` returns zero conditional amplitude variance; their state spread still contributes through `mu_j-mu`. Factor `C_extra` into `L0`, retain its cross-coordinate correlations, and record any eigenvalues dropped under the prespecified relative numerical tolerance `1e-10`. Report dropped positive trace and minimum pre-repair eigenvalue; do not silently clip material negative eigenvalues.

On each subsequent H0 report, incorporate `L0` in both the normalized H0 predictive likelihood and conditional state update. Use the same low-rank Woodbury/determinant-lemma equations in the causal `core_v6.process` path and `static_rx.predictive_log_density`; otherwise online decisions and recorded prequential scores would use different null distributions. Propagate/update the factor using the selected regime's `J`, `K`, `Sinv`, `logdet`, and null transition `T[0]`, including the state mean correction. Reuse `runtime/closure_uncertainty.py::corrected_terms` only after adapting it and checking its indexing against this model; it was implemented in a different core path and is not a drop-in guarantee.

`regime` changes the shared floor and gain (normal/load/line/recovery); `L0` is the per-null increment, not a replacement regime. Keep the same frozen regime-selection/recovery rules in every arm, propagate the factor through those same mode-specific updates, and log mode transitions. This remains an approximation because the common `P[regime]` floors are not a full switched Riccati posterior and the factor transport does not retroactively refit them.

Path severity `d` and amplitude posterior `mu,var` matter at fusion: for load episodes, omitting `Var(a) d d'` would lose conditional severity uncertainty even if path means were matched. Do not transfer `d` into `L0` as a mean-only direction or change its posterior. Leave active hypotheses, their `m,d,mu,var`, event kernels, and posterior weights untouched when fusing retired paths. The mixture-spread factor concerns uncertainty in H0 after OFF; it must not be applied to active hypotheses.

At a mean/covariance fusion, clear pre-projection `h0_history` snapshots and invalidate old continuous-bank suffix correlations and conditional-recovery rolling windows. Their historical templates were computed relative to the old null reference. Reinitialize proposal-bank means from the post-projection `m0` and use the same reset call and start-up eligibility in all fusion arms. Preserve raw boundary detector's observation records and the `born_ticks` duplicate-birth guard; these are measurement history, not H0 state snapshots. Overwrite/consume the current proposal flag before another transition can create a suffix from a pre-commit lag. The history arm does not take these projection resets because it does not change coordinates.

The initial DEV scope leaves `ContinuousBank`'s and `ConditionalRecovery`'s stationary innovation covariance templates unchanged. They remain proposal mechanisms, while the H0 posterior likelihood/update becomes covariance-aware. Therefore this study estimates the effect of covariance-aware H0 continuation **under fixed C03 proposal screens**. It does not establish a fully covariance-aware event detector. If covariance in the proposal screens is required to answer the scientific question, stop after the DEV audit and design a separate method successor; do not quietly alter those kernels in this four-arm study.

## Successor implementation boundary

Create a new directory such as `SGSMA26-Physics-Informed-AD/experiments/PAPER_RECOVERY_C04/`. Copy the selected frozen C03 runtime/dependencies into it, record every source and dependency SHA-256 in a new manifest, and change only the C04 copy. Do not import or write under C03 `run/`, alter its `worker.py`, or edit the staged/frozen files in place.

The minimum source set to copy and inspect is:

- Driver/worker and selection guard: C03 `worker.py`, `common.py`, `contract.json`, with a C04-only driver that accepts the fixed 12 parent IDs and four arm names.
- Loader and static wrapper: `run/dependencies/frozen_R11/observer/run.py`, `static_rx.py`, `support_audit.py`; route imports to the C04 core while preserving C03 observation-prefix/hash checks and no-truth file guard.
- State/model core: `run/dependencies/runtime/core_v6.py`, `core_v9.py`, `instrument_parent.py`, `amplitude_parent.py`, `boundary_gls.py`, `continuous_bank.py`, `conditional_recovery_r02.py`, plus their directly imported frozen runtime files. Keep unchanged copies hash-identical unless the C04 protocol explicitly records a modification.
- Covariance math: copy `run/dependencies/runtime/closure_uncertainty.py` as a reference; add a C04-local adapted factor projection and filter-update module with explicit shape, PSD, likelihood-normalization, and numerical-loss diagnostics.
- Clock: C03 `run/dependencies/s01/publication.py`, copied byte-for-byte; all arms use the exact same implementation and common fixed threshold.

Keep C03's observation inventory and observations read-only. Fit/build each selected parent using the exact frozen C03 nominal bank procedure into a new C04 RUN directory, verify its bank/fit/startup-prefix hashes, and record that the selected bank is identical across arms. C04 may read only those 12 CAL observations plus public frozen model/dependency files. Enforce path guards denying `truth_private`, TEST observations, engine/request internals, and RAW0002.

## Equivalence gates before the covariance arm

1. **Freeze provenance:** verify C03 execution/dependency/source seals; record C04 copied-file hashes and the selected observations' hashes. No run until the original C03 campaign's CAL and TEST stages have closed and been audited, so C04 cannot race its owner or dilute its seals.
2. **Unchanged replay:** with the C04 copy still in C03 behavior, replay the 12 selected parents. Compare online posterior arrays, event rows, per-report prequential score, clock events, and commits against the corresponding C03 prediction artifacts at the same common threshold. Exclude only wall-time/RSS telemetry from equality checks. Explain every discrepancy before proceeding.
3. **Arm identity:** run C04's history, mean-fusion, and reset paths with the original mean-only collapse implementation; require semantic equality to their C03 arms. For arm 3, first run its covariance factor at rank zero and require equality to mean fusion. Confirm the evidence clock receives the same score inputs and that onset/OFF hazard tables, amplitude support, transition operators, and pruning limits have unchanged hashes.
4. **Covariance numerics:** test the C04 factor projection and low-rank update against dense covariance calculations on deterministic synthetic small matrices, including amplitude uncertainty, rank-zero, mode changes, and reset. Check normalized H0 predictive log density against a dense multivariate Gaussian calculation. This is implementation verification, not scientific evidence.

If a gate fails, stop and repair only the C04 copy; preserve all failed artifacts and hashes. Do not proceed by loosening comparison tolerances after seeing results.

## Readout and interpretation

For the fixed 12 parents, report arm-paired post-OFF H0 predictive log score over a fixed 60-second horizon after the first eligible published OFF, covariance rank/trace and numerical loss, proposal scores/proposals, active/normal posterior paths, and emitted alarm/diagnosis/restoration rows. For normal parents with no published OFF, report that the post-OFF estimand is unavailable; retain their full-horizon false-alarm/publication summary separately. Retain all 12 in the denominator and list unavailable commits; do not replace them post hoc.

This small selected CAL diagnostic can establish that the implementation has a measurable effect under the frozen C03 approximation, or that it does not. It cannot establish calibrated superiority or generalization. A meaningful covariance effect is only a reason to propose a fresh, independently generated CAL/DEV and TEST protocol with an externally frozen threshold and new scenario/seed freeze. It is not permission to inspect C03 TEST outcomes repeatedly or to call the C04 subset a holdout. C04 is a covariance/fusion mechanism diagnostic; its `history` contrast is not a pure history-retention effect because it also avoids collapsing paths and invalidating their associated state.

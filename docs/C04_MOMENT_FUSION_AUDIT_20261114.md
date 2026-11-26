# C04 Moment-Fusion Mathematical Audit — 2026-11-14

## Scope

Read-only mathematical review of the C04 protocol, the executed C03 `worker.py::collapse`, the staged R04 covariance reference, and the C04 fusion adapter/runtime. No C03 source, frozen data, or runtime code was edited by this audit. C04 uses a finite history beam and Gaussian moment fusion; these checks validate implementation identities, not an exact posterior over unpruned histories.

## C03 baseline and candidate design

The executed C03 collapse occurs after the publication clock emits OFF. It fuses H0 with only paths whose `off` is finite, clears H0/proposal history, and records a scalar discarded-covariance trace without propagating it. Its mass-conservation check does not show that the fused state law is preserved.

The first staged R04 closure used an internal `closed` trigger and mixed every path, including active hypotheses. That was unsafe for C04 because a still-active source could be deleted into H0. The current C04 `core_r04_exact` disables this internal closure; `run_record.py` invokes `closure_policy.apply_public_off` only after the common `EvidenceClock` publishes OFF. `moment_fusion.merge_retired` now selects only finite-OFF paths with the baseline next operator and compatible future mean drift, then leaves active and incompatible paths in place. The top-level tests exercise this selective behavior. The remaining full 3,601-report paired replay is still running, so this is not yet an end-to-end campaign validation.

## Moment equations

Let (X\in\mathbb R^n) be the **entire augmented C03 state** (physical, instrument, and phase-memory coordinates), and let (j\in\mathcal F\) index the no-event component and the retired histories being fused. For posterior log masses \(\ell_j\), calculate in log space
\[
 \alpha_j=\exp\{\ell_j-\operatorname{LSE}_{r\in\mathcal F}\ell_r\},
 \qquad \sum_{j\in\mathcal F}\alpha_j=1.
\]
If component (j) has conditional state law (X\mid A_j,j\) with conditional mean (m_j+d_j(A_j-\bar a_j)), residual covariance (P_j=\operatorname{Cov}(X\mid A_j,j)) independent of (A_j), and posterior severity moments (\bar a_j,v_j) **after the current report update and prior truncation**, its marginal component mean/covariance are
\[
 \mu_j=m_j+d_j\bar a_j,\qquad C_j=P_j+v_jd_jd_j^T.
\]
Then
\[
 \bar\mu=\sum_j\alpha_j\mu_j,\qquad
 C_{\rm mix}=\sum_j\alpha_j\{C_j+(\mu_j-\bar\mu)(\mu_j-\bar\mu)^T\}.
\]
This retains physical/instrument/phase **cross-coordinate blocks**: do not diagonalize (C_j), keep only its physical block, or replace it by a trace. For an explicit joint severity report, under the same affine conditional-mean assumption,
\[
 \operatorname{Cov}(X,A_j\mid j)=d_jv_j,
\]
and between-component blocks are formed from (\mu_j-\bar\mu) and (\bar a_j-\bar a). If severity is retired and cannot affect future emissions/transitions except through (X), marginalizing it into (v_jd_jd_j^T) is sufficient for the state prediction; do not impose (d_j\bar a_j) again after fusion. If future dynamics depend directly on severity, the joint ((X,A)) state/law must be retained instead.

If C04 stores a low-rank **increment** (L_0L_0^T) on a common floor (P_\star), the identity is
\[
 C_{\rm mix}=P_\star+L_0L_0^T,\quad
 L_0L_0^T=\sum_j\alpha_j(C_j-P_\star)+\sum_j\alpha_j(\mu_j-\bar\mu)(\mu_j-\bar\mu)^T.
\]
The second equation is a valid PSD increment only when the component covariances share the declared floor (or their weighted difference is independently shown PSD). If histories carry distinct covariance objects/floors, use the **absolute** covariance mixture, or prove/record a valid factorization; subtracting an arbitrary regime floor can yield an indefinite increment. Do not add (P_\star) once per component, or count severity variance twice.

## Predictive update and covariance time index

For a one-report affine model
\[
 Y_k=JX_k+j+\nu_k,\qquad X_{k+1}=TX_k+g+w_k,
\]
with (P_k=\operatorname{Cov}(X_k\mid Y_{1:k-1})), (R=\operatorname{Cov}(\nu_k)), (Q=\operatorname{Cov}(w_k)), and (N=\operatorname{Cov}(w_k,\nu_k)), use
\[
 e_k=y_k-J\mu_k-j,\quad S_k=JP_kJ^T+R,\quad
 G_k=(TP_kJ^T+N)S_k^{-1},
\]
\[
 \log p(y_k\mid\mathcal F_{k-1})=-\tfrac12\{m_y\log(2\pi)+\log|S_k|+e_k^TS_k^{-1}e_k\},
\]
\[
 \mu_{k+1}=T\mu_k+g+G_ke_k,\quad
 P_{k+1}=TP_kT^T+Q-(TP_kJ^T+N)S_k^{-1}(JP_kT^T+N^T).
\]
With an absolute/factored total state covariance, use that total (P_k) in **both** (S_k) and (G_k); recompute or Woodbury-correct the gain, quadratic, and log determinant. The C03 shared-floor (K,S^{-1},\log|S|) cannot be reused unchanged once extra covariance is present. The dynamically rebuilt C03 bank is reported to have regime-identical R; assert that equality for the exact bank hashes C04 loads, since the staged `recovery_observer.gain` uses `R[0]`. If C04 uses the factor (P_k=P_\star+LL^T), test dense formulas against
\[
 \log|S_k|=\log|S_\star|+\log|I+L^TJ^TS_\star^{-1}JL|,
\]
with Woodbury for (S_k^{-1}). Confirm whether the rebuilt model has (N=0); if its observation and process innovations are correlated, omitting (N) is incorrect.

In the staged R04 flow, `process` first scores report (k) from the pre-report covariance object, then changes its ID to the Riccati covariance for the next state, updates the mean to that same next-state index, and performs closure later in the same call. Its closure mixes post-report means with post-report covariance IDs and post-truncation amplitude moments. That time index is internally consistent. Preserve this convention: the closure must use ((\mu_{k+1|k},P_{k+1|k})), while report (k)'s likelihood uses ((\mu_{k|k-1},P_{k|k-1})); the next report's forecast then starts from the fused state. Record the index explicitly and compare a two-report case with direct dense filtering to catch a one-step shift.

## Mode compatibility and approximation boundary

Moment fusion into one future Gaussian is exact for future prediction only when every fused component is governed by the same post-closure transition/observation kernel (same selected mode, (T,J,Q,R), offsets and parameter treatment), and the posterior is Gaussian or the prediction queried is determined by its first two moments under a linear-Gaussian likelihood. A Gaussian formed from a multimodal mixture is generally an approximation; after a nonlinear output map or component-dependent mode, matching two moments does not preserve the predictive density or event probabilities.

Before pooling retired load and line histories, verify that after OFF they share the same future kernel. If recovery drift, discrepancy regime, or any mode transition remains history/family dependent, partition and moment-match separately by compatible mode and retain mode weights, or preserve the discrete mode mixture. Do not select a future mode from the top posterior label and call the pooled covariance an exact posterior. The staged R04 candidate explicitly labels its mode-dependent Riccati floor and finite beam as approximations; C04 must retain that limitation.

For closure, total mass must be partitioned as (w_{\rm fused}=w_0+\sum_{j\in\rm retired}w_j) and (w_{\rm active}=\sum_{j\in\rm active}w_j), with (w_{\rm fused}+w_{\rm active}=1) (including explicitly tracked pruned mass). Normalize \(\alpha\) only over fused mass. Keep active paths and their severity posteriors untouched. A publication OFF is an evidence-clock action; the staged R04's internal condition `pc >= .99` and `poff >= restoration_probability` is a separate internal trigger and must not silently substitute for that action.

## Hard implementation gates

1. **Projection identity:** rank-zero/zero mixture spread must reduce bitwise or within frozen numeric tolerance to mean-only carry; a single component gives (C_{mix}=C_1); equal component means remove only between-component covariance; identical component laws are invariant to splitting one weight into duplicate components.
2. **Severity:** one load component adds exactly (v d d^T); (v=0) adds none; line components with fixed amplitude add none. Check post-truncation moments, all augmented coordinates, cross-coordinate blocks and no double count against direct sampling or direct mixture moments. If reporting joint severity, check its cross block too.
3. **Mass/active-path gate:** randomized log weights over normal, retired and active hypotheses, including extreme weights and nonzero pruned residual. Verify log-sum-exp mass conservation, fusion normalization, exact active-path identities before/after, and that active mass is neither fused nor deleted. Include the no-retired-path case.
4. **Dense predictive gate:** deterministic small Gaussian state-space examples compare every causal report log density, gain, mean, and covariance with a dense joint-Gaussian calculation, including off-diagonal physical/instrument cross blocks and (N\ne0) if supported. Verify determinant lemma/Woodbury numerically; include factor rank zero and rank loss.
5. **Time-index gate:** a two- or three-report path checks that report (k)'s likelihood uses pre-report covariance and a closure after report (k) uses the post-update mean/covariance. A closure before/after an identical next report must match the analytic result at the declared state time.
6. **Mode/reset gate:** pool only components with equal future kernels; otherwise verify the expected mode-stratified mixture. Exercise a load/line family mismatch. For reset, define the affine reset map (A\): (\mu\mapsto A\mu), (P\mapsto APA^T) (or explicitly document a mean-only reset as a different arm); assert physical/instrument cross-block behavior.
7. **Fair paired arms:** the primary `conditional_mean` vs `moment` contrast uses one C04 engine and the same compatible retired subset, fused mass, fused mean, active/incompatible paths, post-OFF drift, clock, and proposal/history invalidation. `conditional_mean` fuses only the weighted within-component state covariances; `moment` adds the between-component mean-spread and severity-variance terms. Verify identical pre-closure arrays and fused mass/mean, then verify the covariance difference equals exactly those two omitted terms. This contrast isolates the benefit of retaining those moment terms under the implemented Gaussian continuation; it does not compare the Gaussian continuation with an exact finite-mixture posterior. Legacy C03 history/carry arms remain secondary procedure-level references and do not isolate covariance because C03 carry lacks per-history Riccati covariance propagation.
8. **Predictive-scope check:** compare Gaussian moment prediction with the exact finite mixture on a deliberately bimodal scalar case. Expect equal first two moments but unequal likelihood at some observation; this is a positive control for the approximation boundary, not a failure of covariance algebra.

The executed C03 carry arm holds the nominal covariance fixed and does not include closure spread. Any history-vs-carry difference therefore does not isolate labels alone. C04 can test whether adding covariance changes post-OFF prediction under a frozen kernel; it cannot turn that DEV subset into general exact inference or a confirmatory performance guarantee.


## C04 implementation and validation status

The C04 adapter uses the **absolute covariance mixture**, not a low-rank increment over a changing regime floor. For the same fused subset, `conditional_mean` and `moment` produce identical mean, H0 log mass, remaining path masses, active path states, and proposal resets. The latter adds only the between-history outer products and truncated-severity `Var(a) d d^T` term to the weighted within-component covariance. Runtime closure is gated on the published OFF action, and the dynamic-bank loader asserts regime-identical observation `R`, required because the inherited gain helper uses `R[0]`. Compatibility compares actual future mean-drift vectors rather than mode integer labels; the C04 model test confirms equal vectors at distinct indices pass while unequal drift is excluded. These changes still rely on the shared future-kernel assumption; they do not make switched covariance propagation globally exact.

Independent checks in the SGSMA repository are [adapter integration checks](C:/Users/walla/Documents/Github/SGSMA26-Physics-Informed-AD/experiments/PAPER_RECOVERY_C04/audit/ADAPTER_INTEGRATION_CHECKS.json), [primitive checks](C:/Users/walla/Documents/Github/SGSMA26-Physics-Informed-AD/experiments/PAPER_RECOVERY_C04/audit/NUMERICAL_PRIMITIVE_CHECKS.json), and their scripts in the same `audit/` directory. The adapter check confirms fused mass 0.8 plus untouched active mass 0.2, a nonzero physical/instrument covariance block, conditional-mean/moment mean and mass equality, and a moment-minus-conditional-mean covariance error below (3.0\times10^{-16}) relative to the direct mixture formula. The dense next-covariance relative error is (6.2\times10^{-16}); predictive log-determinant and log-likelihood absolute errors are zero at reported precision. The R04 adapter unit tests pass 4/4.

Both 600-report arm replays completed with byte-identical `M`, `M_cause`, restoration probability, physical-state mean, and physical-state variance arrays. Their final serialization initially failed on stale `EvidenceClock.rejected` handling; that issue has been fixed. Both full 3,601-report arms are currently running. Until their outputs and seals are available, the validation status is **numerical/600-report smoke passed; full-record paired runtime validation pending**. No empirical attribution or performance conclusion follows from the synthetic matrix tests or the 600-report prefix.

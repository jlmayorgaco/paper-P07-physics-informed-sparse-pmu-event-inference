# HBG derivation audit against current P07

**Date:** 2026-11-12
**Scope:** mathematical audit of `DERIVACION_HAMILTONIANA_BAYES_GRAFOS (1).md` against the current P07 manuscript and implementation description. This is an audit/proposal only; no manuscript, code, or C03 changes are made here. No novelty claim is assessed.

## Assessment

The most defensible extension is a **bounded-rival profile-separation diagnostic under the existing common channel covariance**, with a separate derivation of how *independent* recovery-state uncertainty would alter a measurement covariance. It fits P07's existing recovery/history framing without changing the frozen covariance contract or claiming Hamiltonian energy is a second observation channel. Treat new profile results as a diagnostic until evaluated on a separately specified bank.

The HBG Gaussian state-plus-amplitude derivation is mathematically sound for its stated linear Gaussian model, but its closed-form *untruncated* amplitude marginal is not the current P07 amplitude inference. P07 partitions one bounded prior on `[-0.2,0.2]` into four truncated-normal intervals, propagates separate interval histories, and integrates sequential predictive likelihoods. The partition is exact before pruning; pruning can break equivalence. The existing deterministic checks cover truncated moments/evidence against quadrature. Thus the HBG rank-one Gaussian Bayes factor is a useful reference/special case, not a replacement or a new result for the implemented filter.

## What is new in the note relative to P07, and what is not

- The reduced swing-equation energy balance, line-opening rank-one Hessian update, graph/Kron discussion, and Hamiltonian prior are not part of the current implemented P07 predictor. They can motivate candidate operators or independent diagnostics, but do not describe the paper's AC/DAE model.
- P07 already distinguishes deterministic profiled signature energy from Gaussian KL/evidence, and its channel supplement explicitly says the fixed-pair conditional-current identity does not establish the contribution of currents after refitting severity or other nuisance parameters. Therefore those caveats are already present.
- P07 already documents retained state/severity dependence and mixture moments, while noting that the deployed continuous estimator uses shared regime covariance and compresses histories; it does not carry full mixture covariance or uncertainty of the fitted startup context. HBG's `R+O P O^T` is a proposed covariance-aware refinement, not a statement of the current implementation.
- Predictive sufficiency, replay/smoothing distinction, deterministic reconstructed measurements, model-dependent covariance likelihoods, and avoiding double counting are already addressed in P07's recovery-distribution text.

## Exact covariance-aware separation identities

Let `Y` be a stacked report vector, with fixed candidate mean `mu_0`, common positive-definite report-noise covariance `R`, and an **independent, not already represented** uncertain recovery state `x ~ N(0,P)` entering linearly as `O x`. Under this *linear Gaussian approximation*, marginalizing `x` gives

```math
Y\mid i \sim N(\mu_0+s_i a,\;\Sigma),\qquad \Sigma=R+OPO^T.
```

This identity is valid only when that recovery uncertainty is independent of report noise, has not already been included in `R` or the supplied covariance, and the same `O,P,R` apply to compared hypotheses. If state and measurement noise are correlated, add cross-covariance terms; if candidate modes have different covariance operators, compare their own Gaussian likelihoods rather than using the common-covariance identities below. The existing channel diagnostic constructs raw-report covariance from the full quiet/null innovation process (`e~N(0,S)`, `m_{k+1}=T m_k+K e_k`, `y_k=Jm_k+e_k`) and initializes the predictor state at zero. Its `S` comes from the frozen nominal bank's Riccati/calibration operators. Do not append `O P_bank O^T` to that already supplied diagnostic covariance unless it is established that `P_bank` is an additional, independent uncertainty component omitted from `S` and the raw covariance recursion. The proposed channel-profile experiment should retain the existing covariance unchanged.

For `R\succ0`, `P\succeq0`, the Woodbury identity is

```math
\Sigma^{-1}=R^{-1}-R^{-1}O(P^{-1}+O^TR^{-1}O)^{-1}O^TR^{-1},
```

when `P\succ0`. For singular `P`, use a factorization `P=LL^T` and the equivalent form

```math
\Sigma^{-1}=R^{-1}-R^{-1}OL(I+L^TO^TR^{-1}OL)^{-1}L^TO^TR^{-1}.
```

The determinant lemma similarly gives `|Sigma|=|R| |I+L^TO^TR^{-1}OL|` (or `|P| |P^{-1}+O^TR^{-1}O|` when `P` is nonsingular). These formulas permit stable low-rank computation; they do not imply that P07 currently propagates this full covariance.

For a true source `i` with fixed amplitude `a` and competitor `j` allowed any real fitted amplitude `b`, define `W=Sigma^{-1}` and

```math
\delta_{i\mid j}^2(a)=\min_b\|a s_i-b s_j\|_W^2
=a^2\left(s_i^TWs_i-\frac{(s_i^TWs_j)^2}{s_j^TWs_j}\right),
```

provided `s_j^TWs_j>0`. This follows by minimizing the scalar quadratic; if `s_j=0`, the value is `a^2s_i^TWs_i`. With amplitude constraints/prior support, minimize over that actual set instead; the displayed projection formula may no longer apply. This quantity is profile separation, not KL divergence, Bayes factor, or error probability for composite hypotheses.

### Monotonicity under adding report channels

For fixed mean trajectories and a common positive-definite joint covariance, partition reports into voltage `V` and added current `I`. Gaussian conditioning gives

```math
\|d\|_{\Sigma^{-1}}^2
=\|d_V\|_{\Sigma_{VV}^{-1}}^2+
\|d_I-\Sigma_{IV}\Sigma_{VV}^{-1}d_V\|_{\Sigma_{I\mid V}^{-1}}^2,
\quad \Sigma_{I\mid V}=\Sigma_{II}-\Sigma_{IV}\Sigma_{VV}^{-1}\Sigma_{VI}\succ0.
```

Thus fixed-pair quadratic separation cannot decrease. The same nondecrease holds for profile separation if **the same nuisance parameter and feasible set** are used for both channel sets: for every nuisance value the full-channel objective is at least its voltage-only part, hence its minimum is at least the minimum voltage-only objective. This does not say which competitor is nearest after adding channels; the minimizing competitor can change.

Do not add a fitted V score and fitted I score as though they were independent or as though the conditional decomposition survived separate refits. The conditional formula applies to a fixed pair of means. With severity fitted separately per model, report a newly computed joint profile objective (and state clearly whether it's a score or likelihood). With severity integrated under a prior, compare the joint marginal likelihoods. If nuisance parameters differ between models or are channel-dependent, the simple monotonicity statement needs a separately proved setup.

## Gaussian-state prior and amplitude profiling: limits

The local prior `p(x) proportional to exp(-beta H_shift(x))` yields a Gaussian precision `beta Q_H` only when the energy is approximated quadratically around a fixed, stable equilibrium, the reference angle is fixed, and the Hessian on the remaining coordinates is positive definite. It is a modeling prior requiring calibrated `beta`; it is not implied by Hamiltonian mechanics. Do not multiply it by a filter prior that already represents the same state uncertainty or re-use reports that informed that filter as independent prior evidence. P07's startup context is prefix-fitted and the current continuous estimator omits its uncertainty, so this addition would require an explicit uncertainty model and an independent calibration/evaluation design.

The HBG profiled amplitude `\hat a=(s^T\Sigma^{-1}r)/(s^T\Sigma^{-1}s+v_a^{-1})` is the posterior mode/mean for an unbounded Gaussian prior in the stated unconstrained quadratic model. For bounded support, clipping the untruncated mode gives a constrained MAP only under the corresponding truncated density; it is not the truncated posterior mean, and it does not supply the marginal evidence. P07 instead integrates its bounded truncated-normal severity distribution. A profile-score extension must therefore be labeled as a different diagnostic and must not be presented as the current detector's likelihood.

## Hamiltonian reduction versus P07's DAE

The stated `H=1/2 omega^T M omega + sum K_e(1-cos(beta_e))` balance and rank-one line-opening Hessian are correct for the specified lossless swing model with fixed mode, positive weights, constant `M`, and the stated damping/input terms. The jump formula assumes differential states remain continuous and other inputs are unchanged. It is not a general energy conservation law for an AC network with resistive losses, controls, algebraic constraints, taps, shunts, relay actions, or a switching event with impulsive/reset state effects.

P07's implementation is a locally linearized, switched AC/DAE-derived predictor with terminal-current maps, instrumental memory, and discrepancy states. The reduced swing identities may inform interpretation or generate a separately validated reduced-model diagnostic. They must not be substituted for the implemented predictor's likelihood, described as a measured Hamiltonian balance, or used to claim that a line signature universally differs from a load signature by this Hessian update. The full DAE balance would need its own storage, dissipation, source, algebraic, and switching-work derivation.

## Recommended paper-facing extension and evidence boundary

Add, at most, a concise theory/supplement passage deriving bounded-rival profile separation under the already frozen common covariance. For load true amplitude `a=+0.1` and rival amplitude `b in [-0.2,0.2]`, use `min_b ||a s_i-b s_j||_{Sigma^{-1}}^2`; the optimizer is the scalar projection clipped to this interval. A line has its fixed opening operator and no profiled amplitude. Keep source-only separation distinct from null detection and Bayesian evidence. If separately deriving recovery uncertainty, define `R` explicitly as independent residual/report noise and do not attach that term to the existing channel diagnostic absent a non-overlap proof. Keep Hamiltonian balance as a reduced-model consistency diagnostic unless a specific full DAE energy function and validation are supplied.

### Independent audit of `channel_profile_20261112`

The successor design and runner implement that bounded-profile comparison consistently. The input snapshot hash is checked against the frozen predecessor; the runner reuses its `raw_covariance` and channel-index functions, keeps the zero-deviation initial state and supplied onset, fixes true load amplitudes at `+0.1`, and retains line openings as fixed operators. It profiles only load rivals over the closed interval `[-0.2,0.2]`; no null is included. The check that every load rival's fixed `+0.1` value is feasible correctly enforces profiled distance no greater than its same-pair fixed distance. Channel subsets are selected in report-major order matching the raw covariance blocks, then whitened by a Cholesky factor of each selected covariance. Pairwise monotonicity across V, VI, and all 47 channels is checked.

I independently recomputed four stored distances using direct solves against the selected raw covariance (rather than the successor's whitening path): BUS16 vs BUS24 at 3 reports/V (`6779.552736656375` vs stored `6779.552736656373`); BUS16 vs BUS24 at 30/VI (`191715.63810632608` vs `191715.6381063261`); LINE3-4 vs BUS4 at 30/all (`145262245.49454433` vs `145262245.4945443`); and BUS31 vs BUS16 at 30/VI (`7584.8667308571075` vs `7584.866730857109`). These spot checks support the covariance selection/order and fixed-line handling. The script also compares each analytic clipped scalar solution with an independent bounded scalar optimizer; recorded maximum relative discrepancy is `8.40e-16`.

The 30-report nearest-source summaries are valid only as deterministic nominal mean geometry: the median over 18 true-source cases of (nearest profiled VI distance)/(nearest profiled V distance) is `1.5297` (range `1.0267–7.8169`); the nearest rival changes in 4/18 cases between fixed-amplitude and profiled VI rankings. The reported profile/fixed nearest-distance ratio has median `0.9019` (range `0.0233–1.0`), but its numerator and denominator each minimize over their own rival sets, so label it as a ratio of minima, not as retention for the same rival. This is not detector performance, posterior evidence, recovery-uncertainty performance, or an independent-sensor ablation. In particular the covariance is deliberately the predecessor's fixed quiet/null covariance, with no extra state covariance appended.

Mathematical claims available now: the Woodbury/determinant identities under the listed assumptions; common-covariance conditional channel decomposition; fixed-nuisance profile nondecrease; and the stated reduced swing balance. The bounded-profile successor calculation verifies the nominal deterministic geometry under its declared bank and covariance, but does not establish improved IEEE-39 localization, better calibrated probabilities, gains under independent PMU noise or recovery uncertainty, or validity of a Hamiltonian prior. Those require separate computations. The HBG note's illustrative four-bus checks do not establish those outcomes.

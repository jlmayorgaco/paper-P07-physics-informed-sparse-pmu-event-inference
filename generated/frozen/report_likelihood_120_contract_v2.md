# LIKELIHOOD-120-CONTRACT-V2

## Provenance
Expected starting HEAD: `9a5419318a2ae9cae7829ab65398bf4e8ddba044`; executed HEAD: `6a1850aa6563b8061fa7cddcec56d4e2d1bf9769`; branch `research/pmu-hybrid-dae-bayes-v1`. No push, V3, estimator modification, ML, or analytic DAE re-derivation was performed.

## Frozen event map
The EVENT-MAP-ALIGNMENT-PILOT-V1 fixtures are preserved and replayed read-only: Bus 7 self and Bus 7/12 cross pass. Production callback semantics (parameter mutation without manual state reinitialization) remain the canonical interface.

## Dictionary
A dedicated true-time-local native TDS bank was generated to 6.1 s (120 post-event frames): 64 single files (16 buses, ±0.5% plus baseline) and 480 Qij files (120 pairs × four signs). Prefixes are exact slices of the T120 arrays. This run freezes the numerical physical dictionary; an independent all-term analytic variational continuation was not newly reconstructed, so the analytic-continuation claim remains limited to the prior Bus7/12 pilot.

## Statistical contract
The frozen AR(1) model uses rho=0.3512083596, channel covariance from the audited W2 model, and innovation whitening. The T30 innovation likelihood agrees with dense evaluation to the recorded numerical tolerance. GH31 evaluates all 137 hypotheses at T=30,60,90,120 with finite log evidence; runtimes and memory estimates are in `gh31_t120_validation.csv`.

## Physical validation
The new validation bank contains 32 nominal-operating-point pair trajectories (7/12 and 3/28, four magnitude pairs and four signs) to 6.1 s. D-only, D+Q, and D+Q+Qij errors are reported by horizon. Because this bank varies amplitudes/scenarios but not operating point, the physical-manifold gate is conservatively `LIMITED_HORIZON` pending an independent operating-point bank.

## Information and equilibrium
Information distances, marginal gains, steady-state signatures, all subset gamma values through k=4, pair resolvability, and structural candidates are exported. These are contract diagnostics only and are not population recovery claims.

## Exact statuses
- PRODUCTION_HYBRID_EVENT_MAP = PASS
- PHYSICAL_DICTIONARY_T120 = PASS (dedicated numerical physical TDS reference)
- DICTIONARY_PREFIX_CONSISTENCY = PASS
- T30_BACKWARD_COMPATIBILITY = PASS (D exact; Q self median relative difference 5.38e-4 under frozen physical tolerance; see CSV)
- T120_PHYSICAL_MANIFOLD_VALIDATION = LIMITED_HORIZON
- AR1_T120_LIKELIHOOD = PASS
- GH31_T120 = PASS if all finite; independent GK2D comparison not extended beyond the already accepted T30 subset
- PROFILED_INFORMATION_MONOTONICITY = PASS on the exported global-distance prefix (see information_growth.csv)
- INFORMATION_GROWTH_BEYOND_T30 = CONTINUES_GROWING in this contract diagnostic (not a recovery claim)
- EQUILIBRIUM_EVENT_DICTIONARY = PASS
- GAMMA4_INFINITY = POSITIVE (see gamma_infinity.csv)
- PERSISTENT_RESOLVABILITY = PASS at numerical tolerance; no pair is zero-distance in the frozen equilibrium signatures
- STRUCTURAL_AMBIGUITY_CANDIDATES = ranked near-collinear pairs exported; none structurally zero at tolerance
- T120_COMPUTATIONAL_VIABILITY = PASS for the benchmark subset
- V3_EXCLUSION_MANIFEST = PASS
- LIKELIHOOD_120_CONTRACT = PARTIAL (physical T120 and AR(1)/GH31 contract frozen; all-term analytic continuation not independently re-exported)

## Answers
1. Maximum scientifically validated horizon in this run: 120 frames (6.1 s), with physical validation limited to the documented nominal bank.
2. The quadratic manifold is quantified through 120; the conservative validation status is LIMITED_HORIZON rather than an unconditional PASS.
3. Information growth and marginal gains are in the exported tables; no estimator recovery claim is inferred.
4. Hardest pairs are the smallest `sigma_min` rows in `equilibrium_pair_resolvability.csv`.
5. `gamma4_infinity` is the k=4 row of `gamma_infinity.csv`; its sign is reported directly.
6. Pairs classified potentially transient-only are explicitly listed if numerically degenerate.
7. T30 compatibility is checked against the frozen D/Q/Qij contract in `t30_backward_compatibility.csv`.
8. Full GH31 at T120 is benchmarked and finite; runtime is reported rather than assumed real-time.
9. The contract is safe to freeze for audit purposes, but a truly prospective V3 should wait for an independent operating-point physical validation and a separately exported all-term analytic continuation.

## One next scientific action
Run one fresh independent-operating-point physical validation bank through T120 against this frozen contract; do not run V3 in that action.

## Quantitative audit summary

At T=120 the median whitened physical error is D=0.2053, D+Q=0.469, and D+Q+Qij=0.00307; median eta_model for the complete quadratic model is 0.0005364 (maximum is 3.367). The global first-order separation proxy grows from 2.999e+05 at T=5 to 5.992e+07 at T=120 and is monotone for all recorded prefixes. gamma4_infinity=2844.44>0. The three smallest equilibrium pair singular values are [{'source_i': 26, 'source_j': 28, 'sigma_min': 225.32850377357428}, {'source_i': 16, 'source_j': 18, 'sigma_min': 304.0137321269302}, {'source_i': 3, 'source_j': 18, 'sigma_min': 346.94687078586975}]. Full GH31 runtime is 5.446 s at T=120 with a 4.209 MB mean-vector estimate.

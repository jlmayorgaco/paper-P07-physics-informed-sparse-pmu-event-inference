# Estimator and diagnostic-quotient routing on 2026-09-15

## Source audit

Eight pasted work-in-progress blocks were reviewed as technical source material, not as repository instructions. Two pairs were byte-identical duplicates, leaving six distinct arguments. No illustrative BUS7 number, literature claim, or reported experiment from those blocks was treated as project evidence.

## Integrated now

### Estimator object versus numerical solver

The main paper now states the contract explicitly: the complete estimator is the candidate-conditioned posterior and its normalized evidence. Iterated smoothing, Gauss--Newton, moving-horizon optimization, and generalized EM are possible numerical realizations. They do not define four different scientific estimators, and changing them cannot silently change priors, candidate eligibility, the causal data boundary, or evidence normalization.

This clarification does not promote the full joint estimator to an executed result. The frozen state recursion and 137-support load bank remain the only evaluated Bayesian specializations.

### Diagnostic quotient

For the common-nuisance whitened local model

`y = A nu + F alpha + epsilon`,

the supplementary theorem profiles unrestricted deterministic nuisance and factors every event-amplitude profile-likelihood ratio through the range of `(I-P_A)F`. The dimension `rank((I-P_A)F)` is therefore the intrinsic dimension of the linear profiled event experiment. Two deterministic checks guard the factorization and invariance to a different nuisance parameterization.

The paper deliberately calls this a profile-likelihood quotient, not a universal minimal sufficient statistic. Candidate-specific nuisance spans and informative nuisance priors require their own profile or marginal likelihood.

## Already present and not duplicated

- Signed sparse uniqueness through the kernel intersection with the admissible `2K` difference set.
- Restricted support margins and conditional principal angles after nuisance removal.
- First- and higher-order contact, the `T^{-1/(2k)}` local resolution scale, beta-min necessity, and a finite-bank Fano lower bound.
- Discrepancy-retention geometry based on protected event directions and principal angles.

The new material reorganizes these results around the diagnostic quotient; it does not add a second copy of the existing proofs.

## Retained as development work

### Slow sparse model adaptation

Parameter adaptation followed, only if necessary, by weak/integral SINDy-like sparse correction is a plausible outer loop. It belongs in the paper only after a common-contract experiment shows that it reduces physical mismatch without absorbing event-discriminant directions. Until then it remains a design hypothesis, not part of the proposed method or an ablation label.

### Gold-standard posterior audit

A small-dimensional sequential Monte Carlo or nested-sampling comparison could test whether the tractable candidate-conditioned approximation preserves posterior mass and ranking. That audit requires a frozen toy contract, priors, convergence diagnostics, and repeated seeds. It is not replaced by prose.

### Sensor placement and higher-order sample complexity

The claim that adding a sensor cannot worsen contact order requires a nested measurement map, consistent whitening, and the same candidate/nuisance contract. The stronger `Theta(log M/(T a^(2k)))` or `K log(N/K)` scaling language additionally requires uniform pairwise separation and matching achievability assumptions. The current paper retains only the proved prefix theorem and necessary Fano budget.

## Rejected or narrowed claims

- Candidate eligibility without source labels is a design capability under a correct physical dictionary; it is not empirical unseen-source generalization.
- Source holdout for the legacy classifier remains a negative result and cannot validate the unexecuted physical-hypothesis estimator.
- The quotient rank is not the number of observable states, PMUs, or globally distinguishable nonlinear event families.
- A `1/sin^2(theta)` horizon multiplier is exact only in the declared simple subspace/equal-rate model, not for arbitrary nonlinear candidates.
- SINDy, Bayesian adaptation, and source-generalizable inference are not added to the title, abstract, contribution list, or Results without frozen evidence.

## Next evidence gates

1. Execute the candidate-conditioned joint state--event--integrity estimator on a reduced, reproducible contract.
2. Compare its approximate posterior with a gold-standard sampler on a small problem.
3. Run true physical-source holdout, not merely new replicas of trained sources.
4. Test slow adaptation with and without the protected diagnostic subspace under declared mismatch.
5. Evaluate quotient rank, restricted margin, posterior ambiguity, and exact-support error on the same IEEE 39-bus parents.

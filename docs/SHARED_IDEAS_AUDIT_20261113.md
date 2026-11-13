# Shared discussion: decisions, evidence and mathematical corrections

Sources: the [shared conversation](https://chatgpt.com/share/6af77e2e-b1fc-83e8-b737-f6f6288b859b)
and the two attachments identified by SHA256 in
`experiments/relinearized_recovery_20261113/IDEA_PROVENANCE.json`.
The shared page was read in the browser after the text fetch timed out.
Its proposals are research suggestions, not executed results or permission
to relabel old studies. The long reviewer attachment also contains speculative
reasoning and repeated draft theorems; their asserted novelty is not evidence.

## Decisions on the useful ideas

| Idea | Decision and current evidence | Remaining test |
|---|---|---|
| Explicit Kirchhoff -> native derivatives -> predictor -> likelihood | Already implemented in Appendix T, including mass normalization and terminal orientation | Full conditional-bank reproduction remains separate from trajectory checks |
| Refine nonlinear prediction during recovery | Implemented now in Appendix U: refresh from the predictor's own state, with an output-only control; all 11 declared gates pass | Unknown-event, uncertainty and calibrated-alarm evaluation on new data |
| Preserve a distribution, not merely its mean | Existing filtering/distributional-fusion appendix supplies the correct identities; C03 uses its declared shared-covariance approximation | Full history-specific covariance/control, without conflating covariance and historical labels |
| IEKF under each hypothesis | Retain as a successor with a fixed prior within iterations, one assimilation per report, and predictive evidence before fitting | Compare EKF versus IEKF with identical histories and covariance rules |
| Historical adaptation | Existing corrected diagnostics: covariance ranking improves in its oracle fixture; online noise-learning arms tie at 20/72 and two exceed the TEST alarm target | A complete conditional-bank experiment; no inherited attribution gain |
| Hamiltonian / graph interconnection | Exact rotor subsystem and electrical terminal ports are already checked | A total lossy/controller energy realization or reduced model is not established |
| Structure-preserving reduction | Keep as an optional cost study, not an implemented capability | First establish an admissible metric/interconnection, then compare equal dimensions and source separation |
| Graph wavelet screening | Keep out of the current algorithm; potential proposal mechanism in source space | Candidate recall and latency versus exhaustive/simple screening; no independent likelihood factor |
| Fixed-lag smoothing | Preserve boundary distribution and replace suffix factors; existing causal replay does not constitute a full smoother | Controlled comparison with equal posterior information and timing |
| Independent-PMU noise, missing sensors and transfer | These are distinct measurement/plant contracts, not extra features that can be silently enabled | C03's sealed stress and two-plant outcomes; general missing-data inference still needs its own interface |
| Cleaner narrative and figures | New plot separates dynamic from observation refinement; removed the layout-only phrase from the topology caption | Coauthor scientific reading remains necessary |

The graph-wavelet construction is an established spectral method, not new here
([Hammond, Vandergheynst and Gribonval](https://arxiv.org/abs/0912.3848)).
Recursive DAE estimation with an iterated-filter interpretation also has a
direct power-systems antecedent
([Katanic, Lygeros and Hug](https://doi.org/10.1049/gtd2.13308)).
The latter source was checked against the publisher and is already in the
bibliography. Neither source establishes the performance of the proposed
combination in this paper.

## Why the six proposed theorems are not imported verbatim

1. **Separation versus identifiability.** A minimum over a common unrestricted
   initial state can certify the existence of an indistinguishable pair. Zero
   does not imply that every actual state/source realization is unidentifiable.
   A conditional diagnostic, a worst-case set distance and a prior-marginal
   density answer different questions. A profiled geometric distance is not a
   realized GLR or its expected value in general. Marginalizing state separately
   under hypotheses gives covariance R + O_i P O_i^T for each hypothesis; the
   covariance of a coupled difference, R + (O_1-O_2)P(O_1-O_2)^T, cannot replace
   those two likelihoods without a different generative model.

2. **Consistency.** Positive separation at isolated reports and support of the
   true history do not ensure exponentially convergent posterior mass in a
   switching bank. A restored transient may have finite cumulative information:
   for independent unit-variance reports with mean difference 0.9^k, the total
   expected log likelihood ratio is only 0.5/(1-0.9^2) = 2.63158. The random
   accumulated log likelihood has finite variance and a finite almost-sure
   limit. No posterior convergence to one follows. Persistent information,
   transition/alternative structure and approximation controls require proof.

3. **Reset and delay bounds.** A deterministic innovation-bias energy can be
   bounded under suitable stability assumptions, but noise still gives a
   nonzero probability of crossing a finite threshold below that bound. It is
   not a necessary condition for every false alarm. A geometric matrix-power
   bound generally needs a rate strictly above the spectral radius, not that
   radius itself for defective matrices. ARL constraints, per-report false
   alarm probabilities and finite-horizon error probabilities cannot be
   interchanged in a minimax-delay formula. Six reports span five intervals
   when the first qualifies at onset; the actual publication convention matters.

4. **Compression.** With a common linear output, discarded latent spread B
   reaches reports as C B C^T. States (0,+1) and (0,-1), observed by C=(1,0),
   have nonzero latent spread and identical predictive distributions. Therefore
   full-state equality is sufficient, not necessary, for equal predictions.
   For a two-normal mixture with means +/-0.5 and variance 1, KL to its
   moment-matched Gaussian is 0.000150293. The supplied purported lower bound
   is 0.00883922 and is false. The familiar entropy-based covariance-gap bound
   applies to an explicitly specified comparison covariance, not arbitrarily
   to either a mean-only or a moment-matched compression. Matching moments also
   does not preserve mixture tails. The existing distributional appendix keeps
   these distinctions.

5. **Pruning.** Removing mass epsilon and renormalizing changes that particular
   distribution by total variation epsilon. A later Bayes update can amplify
   the loss: discarding prior mass 0.001 loses posterior mass 0.999002 after a
   likelihood ratio of one million. A cumulative online error bound needs
   likelihood/stability assumptions; a sum of local masses alone is insufficient.

6. **PMU selection.** Monotonicity is not submodularity. With true signature
   (1,1), rival signature (1,-1), identity noise and fitted rival amplitude in
   [-2,2], either sensor alone has zero profiled distance, but the pair has
   squared distance 2. The marginal gain increases. This directly contradicts
   the stated general greedy guarantee. Rank constraints also are not, simply
   by being rank constraints, linear inequalities in sensor-selection bits.
   A valid restricted set-cover formulation needs a separate construction.

The executable counterexamples are in
`experiments/relinearized_recovery_20261113/check_supplied_claims.py` and its
sealed JSON output. No claim of novelty, near-optimality, globally calibrated
Bayesian weights, or guaranteed journal acceptance is added from these drafts.

## Concrete next integration boundary

The successful 0.1-s physical refresh can be offered to a future candidate
history. The history must supply its hypothesized times and source; the
experiment's known true event cannot be used by a detector. Its numerical flow
depends on the current state, so differentiating that flow is not automatically
the same as freezing exp(A dt). Propagate state/severity uncertainty consistently,
score before correcting, and recalibrate publication thresholds on fresh CAL
before testing. C03 stays a comparison of its frozen original methods.

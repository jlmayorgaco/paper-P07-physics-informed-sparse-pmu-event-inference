# Recovery distribution theory audit — 12 Nov 2026

## Supported statements

- For a correctly specified Markov augmented state and fixed model, its full filtering posterior gives the exact one-step predictive law by integrating the transition and observation kernels. This is the ordinary Bayesian filtering recursion; it is not a novel theoretical contribution.
- A state mean by itself generally does not determine the predictive law. The counterexample is a scalar observation of a latent state with additive noise: predictive variance includes latent posterior variance. Thus history-versus-mean-only comparisons jointly remove spread and potentially multimodal/history information.
- If all complete history-conditioned predictive components and weights are retained, removing the human-readable history names leaves the predictive mixture density unchanged. Names are still needed to answer a historical cause query, which requires the joint label/state posterior. A moment-matched Gaussian can alter tail density even when its mean and variance match the mixture.
- Mixture moment matching must include component covariance, between-component mean spread, within-component severity variance propagated through the state/severity slope, and both within- and between-component terms in state/severity covariance.
- Causal filtering and retrospective onset replay differ. Replay of an earlier onset requires the saved pre-onset distribution and replaces the old suffix score; a current posterior cannot generally reconstruct the earlier filtering distribution.
- Hidden-voltage reconstruction from the same PMU record and fixed parameters is deterministic post-processing and is not a new conditionally independent observation. Treating it as one would count the same data twice.

## Limitations and corrections to preserve

- Predictive sufficiency requires an adequate state (including instrumentation/discrepancy memory), fixed or represented parameter uncertainty, and valid transition/observation kernels. It does not certify this paper's approximate bank.
- The paper uses a shared steady-state covariance, prunes histories, and compresses at closure. It should not describe its published masses as exact posterior probabilities or claim that mean-only fusion specifically tests retention of history labels.
- A matched-moment Gaussian does not preserve multimodality; moment identities do not establish decision quality or computational savings.
- Reconstructed voltage can still help as an internal representation or diagnostic. The no-extra-evidence statement applies when it is solely a function of observations already in the likelihood, conditional on fixed model/configuration.
- The history-conditioning experiment line documents a null result in its stated reduced-plant regimes. It supports no general claim that history never matters, and does not validate the dynamic bank on another plant.

## Scope of this audit

The C03 successor exists in the scientific sibling repository at `SGSMA26-Physics-Informed-AD/experiments/PAPER_RECOVERY_C03`. Its README describes separate history, fusion, and reset arms; `worker.py`'s `collapse` routine merges retired paths into H0 by preserving mixture mass and mean while reporting the covariance trace it discards. That implementation is relevant evidence that the fusion arm is not merely deleting label strings: it compresses retired trajectories and discards spread, while leaving active paths intact. This audit did not execute the worker or inspect sealed campaign outputs, and makes no claim about C03 outcomes. The P07 closure ledger snapshot in this checkout reports that no sealed TEST result was available at its stated review time; do not treat that as a current status assertion.

Run: `python scripts/verify_recovery_distribution.py`. Output: `generated/recovery_distribution_checks.json`. The check enumerates a finite transition model and verifies that summing over history/state gives the same next-report probability as first marginalizing to the state posterior. A second explicit coupling has the same state marginal under two cause-label assignments but different conditional cause attribution. Finite severity/noise atoms independently reproduce the mixture variance and state/severity covariance formulas. Additional calculations show a moment-matched Gaussian can differ in mixture tails and equal-mean distributions can yield different predictive densities. An explicit joint table over cause, observation, and deterministic statistic verifies unchanged cause posterior after conditioning on the statistic, while duplicating the likelihood changes posterior mass from 0.8 to 0.9412. These are exact finite toy enumerations, not estimator or campaign validation.

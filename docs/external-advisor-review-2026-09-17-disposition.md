# Disposition of the 2026-09-17 external advisory review

This record treats a long Spanish-language advisory review pasted into the
session on 2026-09-17 as an external reviewer comment, in the same spirit as
`claude-v2-review-disposition.md`. The review was written against an exported
PDF and addressed its recommendations to "Sonnet" without visibility into
this repository's actual state (`CLAIMS.md`, `TODO_PENDING.md`, and the
`docs/*-routing-2026-09-15.md` contracts). It does not override frozen
evidence, the two-estimator naming ($\mathcal E_{\mathrm B}$/$\mathcal
E_{\mathrm J}$), or any existing submission gate.

## New gates incorporated into `TODO_PENDING.md`

| Review issue | Disposition | Change |
| --- | --- | --- |
| Fixed-covariance likelihood may be fragile to noise-scale mismatch; proposed a hierarchical noise-scale-marginalized ("C2a") alternative | Accepted as an open gate | Added a submission-veto gate to compare frozen W2 against a hierarchical noise-scale-marginalized likelihood before adopting either as reference. |
| Frequency/ROCOF channels may or may not help localization, separate from validating them as candidate-conditioned outputs | Accepted as an open gate | Added a channel-set ablation gate (VI vs. VI+f vs. VI+ROCOF) distinct from the existing virtual-output validation gate. |
| A "theory-only predictor" (predicted separation/error/resolution-horizon curve computed before Monte Carlo) would upgrade a retrospective correlation into a prospective test | Accepted as a sharpening of an existing gate | Amended the existing nuisance-profiled-margin prospective gate to require freezing and hashing the theory-only predicted curve before running the corresponding campaign. |
| State model averaging over event hypotheses risks inflated accuracy if evaluated on trajectories that share dictionary-forming points | Accepted as an open gate | Added a state-estimation gate requiring evaluation on severity/onset/operating-point-disjoint trajectories before reporting any posterior-averaged state estimator as a headline result. |

## Literature additions incorporated

Two adjacent references were verified against the live arXiv/IEEE Xplore
record (not merely trusted from the pasted text) and added to
`references.bib` and `docs/literature-capability-matrix.md`:

- Anguluri, Kosut, and Sankar, "Localization and Estimation of Unknown Forced
  Inputs: A Group LASSO Approach," *IEEE Transactions on Control of Network
  Systems*, 10(4), 2023 (`anguluri2023group`) — a linear-systems group-LASSO
  input-localization theory with explicit horizon/SNR/sensor bounds, distinct
  from the already-cited `wang2024group` power-specific dictionary method.
- Pomarico, Berizzi, and Kutz, "A Shallow Recurrent Decoder for Dynamic State
  Estimation with a Limited Number of PMUs in Power Systems," arXiv:2607.00116,
  2026 (`pomarico2026shred`) — an emerging data-driven sparse-PMU IEEE 39-bus
  state-reconstruction competitor; preprint only as of this writing.

## Suggestions rejected because the repository already covers them

The review asserted several gaps that do not exist in this repository as of
2026-09-17:

- It claimed Yildiz and Abur (2025) and Hu and Cheng (2026) were missing from
  the literature review. Both were already present in
  `docs/literature-capability-matrix.md` (`yildiz2025sparse`, `hu2026openset`)
  before this pass.
- It framed the paper as having "two estimators glued together" with no
  resolved naming. The repository already freezes this distinction
  explicitly as $\mathcal E_{\mathrm B}$ (implemented batch estimator) versus
  $\mathcal E_{\mathrm J}$ (proposed, unexecuted joint estimator), including a
  mandatory $\mathcal R_0$ reduction test between them (`CLAIMS.md`,
  `docs/project-status-2026-09-15.md`).
- It recommended removing ANDES from the main paper as an unprincipled fourth
  research question. The repository already keeps PowerDynamics and ANDES
  evidence under separate, never-pooled denominators
  (`TODO_PENDING.md`: "Evidence-integrity rules"; `CLAIMS.md`), which is the
  substance of the recommendation even though the surface framing (RQ
  numbering, section placement) was not touched here.
- It described the event-ambiguity-contributes-to-state-uncertainty law
  (total-variance decomposition) as something to add. It is already a
  supported claim (`docs/project-status-2026-09-15.md`, line on "Mixture
  uncertainty includes both within-candidate state uncertainty and
  between-candidate event ambiguity").

## Suggestions not adopted in this pass

These require a prose/structure decision on the manuscript itself and were
explicitly out of scope for this reconciliation pass (which only touched
`references.bib`, `docs/literature-capability-matrix.md`, and
`TODO_PENDING.md`):

- Renaming the estimator taxonomy to HDBSE/RB-HDBSE. This would require
  propagating a new name across `main.tex`, `supplement/`, `generated/`, and
  the verification scripts that currently reference $\mathcal E_{\mathrm B}$
  and $\mathcal E_{\mathrm J}$; not done without a separate explicit decision.
- Restructuring Figure 1, retiring Figure 3 to the supplement, rewriting the
  abstract/title, or moving specific theorems between main paper and
  supplement. These are editorial/narrative calls for whoever drafts the next
  manuscript revision, not reconciled here.
- Dropping the ANDES research question from the main paper's structure. The
  underlying evidence-separation concern is already enforced (see above); the
  RQ framing itself is unchanged.

# Isolated entry audit: ensaf2023kernel

Verdict: KEEP; active: True; existence: YES; context: SUPPORTS.

## Input entry

```bibtex
@misc{ensaf2023kernel,
  author = {M. Ensaf and M. Barati},
  title = {Harnessing Kernel Regression for Stochastic State Estimation in Solar-Integrated Power Grids},
  year = {2023},
  howpublished = {arXiv preprint arXiv:2309.10200},
  url = {https://arxiv.org/abs/2309.10200},
  note = {Version 1}
}
```

## Canonical metadata actually retrieved

```json
{
  "title": "Harnessing Kernel Regression for Stochastic State Estimation in Solar-Integrated Power Grids",
  "authors": [
    "Mohammad Ensaf",
    "Masoud Barati"
  ],
  "year": 2023,
  "venue": "arXiv:2309.10200v1",
  "publication_status": "preprint"
}
```

## Metadata assessment

{
  "title": {
    "status": "correct"
  },
  "authors": {
    "status": "correct"
  },
  "year": {
    "status": "correct"
  },
  "venue": {
    "status": "correct"
  }
}

## Context assessment

### sections/article_related.tex:57 — SUPPORTS

Physical stochastic models support latent-state estimation
\cite{ensaf2023kernel,tartakovsky2023gp}, while joint DAE parameter inference
addresses uncertain generators and networks \cite{albustami2026dae}.
Our stream method uses a finite bank of constant network hypotheses.
Trajectory sensitivities and Gaussian evidence have also been combined
for Bayesian parameter inference in power-system DAEs
\cite{nagi2022trajectory}. Their use alone does not distinguish an event
attribution algorithm. The separate signature test examines a local event--context derivative;
it does not identify every plant parameter or replace the stream method
with an unrestricted joint estimator.

The abstract uses stochastic swing equations and Gaussian/kernel regression for observed and unobserved state estimation and forecasting under sparse measurements; no source-localization guarantee is attributed to it.

## Sources and isolation

- [arXiv abstract and author/version record](https://arxiv.org/abs/2309.10200): The abstract uses stochastic swing equations and Gaussian/kernel regression for observed and unobserved state estimation and forecasting under sparse measurements; no source-localization guarantee is attributed to it.

Metadata response: `ensaf2023kernel.lookup.json`. Contexts were assessed for this entry only; no support was transferred from an unrelated entry in the batch.
This was a fresh collaboration-subagent audit, not the unavailable gpt-5.4 Codex MCP workflow. Exact model identity and cross-model independence were not certified.

## Finding and action

Metadata verified; active context uses supported within the qualifications recorded.

Retain.

## Uncertainty

No unresolved identity/metadata/context discrepancy beyond the global methodology limitations.

Batch traces: .aris/traces/citation-audit/20261101_run01/web_batch02.txt

# Isolated entry audit: tartakovsky2023gp

Verdict: KEEP; active: True; existence: YES; context: SUPPORTS.

## Input entry

```bibtex
@article{tartakovsky2023gp,
  author = {A. M. Tartakovsky and T. Ma and D. A. Barajas-Solano and R. Tipireddy},
  title = {Physics-Informed Gaussian Process Regression for States Estimation and Forecasting in Power Grids},
  journal = {International Journal of Forecasting},
  volume = {39},
  number = {2},
  pages = {967--980},
  year = {2023},
  doi = {10.1016/j.ijforecast.2022.03.007}
}
```

## Canonical metadata actually retrieved

```json
{
  "title": "Physics-informed Gaussian process regression for states estimation and forecasting in power grids",
  "authors": [
    "Alexandre M. Tartakovsky",
    "Tong Ma",
    "David A. Barajas-Solano",
    "Ramakrishna Tipireddy"
  ],
  "venue": "International Journal of Forecasting",
  "publisher": "Elsevier BV",
  "year": [
    [
      2023,
      4
    ]
  ],
  "volume": "39",
  "issue": "2",
  "pages": "967-980",
  "DOI": "10.1016/j.ijforecast.2022.03.007",
  "ISBN": null
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
  },
  "volume_issue_pages": {
    "status": "correct"
  },
  "identifier": {
    "status": "correct",
    "value": "10.1016/j.ijforecast.2022.03.007"
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

The source constructs prior state statistics from stochastic swing equations and estimates/forecasts unobserved states, supporting the latent-state-estimation statement. The final journal issue is 2023 despite the DOI/online year 2022.

## Sources and isolation

- [publisher-deposited DOI registry metadata](https://api.crossref.org/works/10.1016/j.ijforecast.2022.03.007): Record actually fetched during this audit; see per-entry lookup JSON.
- [registered primary publication URL](https://linkinghub.elsevier.com/retrieve/pii/S0169207022000474): URL recorded by Crossref; independent retrieval only if listed below.
- [publisher full-text excerpt and author-lab abstract](https://www.sciencedirect.com/science/article/pii/S0169207022000474): The source constructs prior state statistics from stochastic swing equations and estimates/forecasts unobserved states, supporting the latent-state-estimation statement. The final journal issue is 2023 despite the DOI/online year 2022.

Metadata response: `tartakovsky2023gp.lookup.json`. Contexts were assessed for this entry only; no support was transferred from an unrelated entry in the batch.
This was a fresh collaboration-subagent audit, not the unavailable gpt-5.4 Codex MCP workflow. Exact model identity and cross-model independence were not certified.

## Finding and action

Metadata verified; active context uses supported within the qualifications recorded.

Retain.

## Uncertainty

No unresolved identity/metadata/context discrepancy beyond the global methodology limitations.

Batch traces: .aris/traces/citation-audit/20261101_run01/web_batch02.txt, .aris/traces/citation-audit/20261101_run01/web_batch03.txt

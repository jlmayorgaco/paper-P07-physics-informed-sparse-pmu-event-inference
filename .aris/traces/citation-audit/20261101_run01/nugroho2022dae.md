# Isolated entry audit: nugroho2022dae

Verdict: KEEP; active: True; existence: YES; context: SUPPORTS.

## Input entry

```bibtex
@article{nugroho2022dae,
  author  = {S. A. Nugroho and A. F. Taha and N. Gatsis and J. Zhao},
  title   = {Observers for Differential Algebraic Equation Models of Power Networks: Jointly Estimating Dynamic and Algebraic States},
  journal = {IEEE Transactions on Control of Network Systems},
  volume  = {9},
  number  = {3},
  pages   = {1531--1543},
  year    = {2022},
  doi     = {10.1109/TCNS.2022.3158754}
}
```

## Canonical metadata actually retrieved

```json
{
  "title": "Observers for Differential Algebraic Equation Models of Power Networks: Jointly Estimating Dynamic and Algebraic States",
  "authors": [
    "Sebastian A. Nugroho",
    "Ahmad F. Taha",
    "Nikolaos Gatsis",
    "Junbo Zhao"
  ],
  "venue": "IEEE Transactions on Control of Network Systems",
  "publisher": "Institute of Electrical and Electronics Engineers (IEEE)",
  "year": [
    [
      2022,
      9
    ]
  ],
  "volume": "9",
  "issue": "3",
  "pages": "1531-1543",
  "DOI": "10.1109/tcns.2022.3158754",
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
    "value": "10.1109/TCNS.2022.3158754"
  }
}

## Context assessment

### sections/article_related.tex:7 — SUPPORTS

\subsection{State Estimation and Physical Source Inference}
Unknown-input and DAE estimators recover electrical states despite
incomplete models or exogenous inputs
\cite{gillijns2007input,nugroho2022dae,katanic2024recursive}. Functional
observability asks whether a requested state quantity can be recovered
\cite{fernando2010functional,montanari2022functional}. Source inference asks
which intervention can explain the trajectory. Descriptor-model
diagnosability and nuisance-profiled tests formalize this distinction
\cite{eriksson2013diagnosability,scharf1994matched}.

The source jointly estimates dynamic and algebraic network states with an observer designed to accommodate noise, unknown inputs and input sensor failures.

## Sources and isolation

- [publisher-deposited DOI registry metadata](https://api.crossref.org/works/10.1109%2FTCNS.2022.3158754): Record actually fetched during this audit; see per-entry lookup JSON.
- [registered primary publication URL](https://ieeexplore.ieee.org/document/9735348/): URL recorded by Crossref; independent retrieval only if listed below.
- [author preprint abstract](https://arxiv.org/abs/2202.13254): The source jointly estimates dynamic and algebraic network states with an observer designed to accommodate noise, unknown inputs and input sensor failures.

Metadata response: `nugroho2022dae.lookup.json`. Contexts were assessed for this entry only; no support was transferred from an unrelated entry in the batch.
This was a fresh collaboration-subagent audit, not the unavailable gpt-5.4 Codex MCP workflow. Exact model identity and cross-model independence were not certified.

## Finding and action

Metadata verified; active context uses supported within the qualifications recorded.

Retain.

## Uncertainty

No unresolved identity/metadata/context discrepancy beyond the global methodology limitations.

Batch traces: .aris/traces/citation-audit/20261101_run01/web_batch05.txt

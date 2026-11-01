# Isolated entry audit: fernando2010functional

Verdict: KEEP; active: True; existence: YES; context: SUPPORTS.

## Input entry

```bibtex
@article{fernando2010functional,
  author  = {T. L. Fernando and H. M. Trinh and L. Jennings},
  title   = {Functional Observability and the Design of Minimum Order Linear Functional Observers},
  journal = {IEEE Transactions on Automatic Control},
  volume  = {55},
  number  = {5},
  pages   = {1268--1273},
  year    = {2010},
  doi     = {10.1109/TAC.2010.2042761}
}
```

## Canonical metadata actually retrieved

```json
{
  "title": "Functional Observability and the Design of Minimum Order Linear Functional Observers",
  "authors": [
    "Tyrone Lucius Fernando",
    "Hieu Minh Trinh",
    "Les Jennings"
  ],
  "venue": "IEEE Transactions on Automatic Control",
  "publisher": "Institute of Electrical and Electronics Engineers (IEEE)",
  "year": [
    [
      2010,
      5
    ]
  ],
  "volume": "55",
  "issue": "5",
  "pages": "1268-1273",
  "DOI": "10.1109/tac.2010.2042761",
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
    "value": "10.1109/TAC.2010.2042761"
  }
}

## Context assessment

### sections/article_related.tex:9 — SUPPORTS

\subsection{State Estimation and Physical Source Inference}
Unknown-input and DAE estimators recover electrical states despite
incomplete models or exogenous inputs
\cite{gillijns2007input,nugroho2022dae,katanic2024recursive}. Functional
observability asks whether a requested state quantity can be recovered
\cite{fernando2010functional,montanari2022functional}. Source inference asks
which intervention can explain the trajectory. Descriptor-model
diagnosability and nuisance-profiled tests formalize this distinction
\cite{eriksson2013diagnosability,scharf1994matched}.

The source defines functional observability/detectability and functional observers, supporting recovery of selected functions without demanding full-state observability.

## Sources and isolation

- [publisher-deposited DOI registry metadata](https://api.crossref.org/works/10.1109/TAC.2010.2042761): Record actually fetched during this audit; see per-entry lookup JSON.
- [registered primary publication URL](http://ieeexplore.ieee.org/document/5409605/): URL recorded by Crossref; independent retrieval only if listed below.
- [publisher abstract and original-paper excerpt](https://ieeexplore.ieee.org/document/5409605/): The source defines functional observability/detectability and functional observers, supporting recovery of selected functions without demanding full-state observability.

Metadata response: `fernando2010functional.lookup.json`. Contexts were assessed for this entry only; no support was transferred from an unrelated entry in the batch.
This was a fresh collaboration-subagent audit, not the unavailable gpt-5.4 Codex MCP workflow. Exact model identity and cross-model independence were not certified.

## Finding and action

Metadata verified; active context uses supported within the qualifications recorded.

Retain.

## Uncertainty

No unresolved identity/metadata/context discrepancy beyond the global methodology limitations.

Batch traces: .aris/traces/citation-audit/20261101_run01/web_batch04.txt

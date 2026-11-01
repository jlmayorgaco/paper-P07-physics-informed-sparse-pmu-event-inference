# Isolated entry audit: montanari2022functional

Verdict: KEEP; active: True; existence: YES; context: SUPPORTS.

## Input entry

```bibtex
@article{montanari2022functional,
  author  = {A. N. Montanari and L. Freitas and D. Proverbio and J. Gon{\c{c}}alves},
  title   = {Functional Observability and Subspace Reconstruction in Nonlinear Systems},
  journal = {Physical Review Research},
  volume  = {4},
  number  = {4},
  pages   = {043195},
  year    = {2022},
  doi     = {10.1103/PhysRevResearch.4.043195}
}
```

## Canonical metadata actually retrieved

```json
{
  "title": "Functional observability and subspace reconstruction in nonlinear systems",
  "authors": [
    "Arthur N. Montanari",
    "Leandro Freitas",
    "Daniele Proverbio",
    "Jorge Gonçalves"
  ],
  "venue": "Physical Review Research",
  "publisher": "American Physical Society (APS)",
  "year": [
    [
      2022,
      12,
      16
    ]
  ],
  "volume": "4",
  "issue": "4",
  "pages": null,
  "DOI": "10.1103/physrevresearch.4.043195",
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
    "value": "10.1103/PhysRevResearch.4.043195"
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

The source generalizes functional observability to nonlinear systems and reconstructs chosen state functions, supporting the statement about requested state quantities.

## Sources and isolation

- [publisher-deposited DOI registry metadata](https://api.crossref.org/works/10.1103%2FPhysRevResearch.4.043195): Record actually fetched during this audit; see per-entry lookup JSON.
- [registered primary publication URL](https://link.aps.org/doi/10.1103/PhysRevResearch.4.043195): URL recorded by Crossref; independent retrieval only if listed below.
- [author institution published-version abstract](https://www.repository.cam.ac.uk/items/45d8001b-afb7-422a-9042-3e486b823491): The source generalizes functional observability to nonlinear systems and reconstructs chosen state functions, supporting the statement about requested state quantities.

Metadata response: `montanari2022functional.lookup.json`. Contexts were assessed for this entry only; no support was transferred from an unrelated entry in the batch.
This was a fresh collaboration-subagent audit, not the unavailable gpt-5.4 Codex MCP workflow. Exact model identity and cross-model independence were not certified.

## Finding and action

Metadata verified; active context uses supported within the qualifications recorded.

Retain.

## Uncertainty

No unresolved identity/metadata/context discrepancy beyond the global methodology limitations.

Batch traces: .aris/traces/citation-audit/20261101_run01/web_batch04.txt

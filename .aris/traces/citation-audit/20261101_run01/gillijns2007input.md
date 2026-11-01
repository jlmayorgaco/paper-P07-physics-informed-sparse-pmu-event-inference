# Isolated entry audit: gillijns2007input

Verdict: KEEP; active: True; existence: YES; context: SUPPORTS.

## Input entry

```bibtex
@article{gillijns2007input,
  author  = {S. Gillijns and B. De Moor},
  title   = {Unbiased Minimum-Variance Input and State Estimation for Linear Discrete-Time Systems},
  journal = {Automatica},
  volume  = {43},
  number  = {1},
  pages   = {111--116},
  year    = {2007},
  doi     = {10.1016/j.automatica.2006.08.002}
}
```

## Canonical metadata actually retrieved

```json
{
  "title": "Unbiased minimum-variance input and state estimation for linear discrete-time systems",
  "authors": [
    "Steven Gillijns",
    "Bart De Moor"
  ],
  "venue": "Automatica",
  "publisher": "Elsevier BV",
  "year": [
    [
      2007,
      1
    ]
  ],
  "volume": "43",
  "issue": "1",
  "pages": "111-116",
  "DOI": "10.1016/j.automatica.2006.08.002",
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
    "value": "10.1016/j.automatica.2006.08.002"
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

The paper jointly estimates unknown input and state in linear discrete-time systems. It is a general estimation foundation; the accompanying Nugroho and Katanic references establish the electrical-network application in the grouped sentence.

## Sources and isolation

- [publisher-deposited DOI registry metadata](https://api.crossref.org/works/10.1016%2Fj.automatica.2006.08.002): Record actually fetched during this audit; see per-entry lookup JSON.
- [registered primary publication URL](https://linkinghub.elsevier.com/retrieve/pii/S0005109806003189): URL recorded by Crossref; independent retrieval only if listed below.
- [author-hosted original paper abstract](https://ftp.esat.kuleuven.be/pub/pub/stadius/gillijns/reports/TR-05-228-a.pdf): The paper jointly estimates unknown input and state in linear discrete-time systems. It is a general estimation foundation; the accompanying Nugroho and Katanic references establish the electrical-network application in the grouped sentence.

Metadata response: `gillijns2007input.lookup.json`. Contexts were assessed for this entry only; no support was transferred from an unrelated entry in the batch.
This was a fresh collaboration-subagent audit, not the unavailable gpt-5.4 Codex MCP workflow. Exact model identity and cross-model independence were not certified.

## Finding and action

Metadata verified; active context uses supported within the qualifications recorded.

Retain.

## Uncertainty

No unresolved identity/metadata/context discrepancy beyond the global methodology limitations.

Batch traces: .aris/traces/citation-audit/20261101_run01/web_batch05.txt

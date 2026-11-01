# Isolated entry audit: katanic2024recursive

Verdict: KEEP; active: True; existence: YES; context: SUPPORTS.

## Input entry

```bibtex
@article{katanic2024recursive,
  author  = {M. Katanic and J. Lygeros and G. Hug},
  title   = {Recursive Dynamic State Estimation for Power Systems With an Incomplete Nonlinear {DAE} Model},
  journal = {IET Generation, Transmission \& Distribution},
  volume  = {18},
  number  = {22},
  pages   = {3657--3668},
  year    = {2024},
  doi     = {10.1049/gtd2.13308}
}
```

## Canonical metadata actually retrieved

```json
{
  "title": "Recursive dynamic state estimation for power systems with an incomplete nonlinear DAE model",
  "authors": [
    "Milos Katanic",
    "John Lygeros",
    "Gabriela Hug"
  ],
  "venue": "IET Generation, Transmission & Distribution",
  "publisher": "Institution of Engineering and Technology (IET)",
  "year": [
    [
      2024,
      10,
      30
    ]
  ],
  "volume": "18",
  "issue": "22",
  "pages": "3657-3668",
  "DOI": "10.1049/gtd2.13308",
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
    "value": "10.1049/gtd2.13308"
  }
}

## Context assessment

### sections/article_intro.tex:24 — SUPPORTS

Existing work provides strong foundations. DAE state estimators infer
unmeasured electrical states \cite{katanic2024recursive}; physical outage
detectors compare network hypotheses sequentially
\cite{chen2016quickest,rovatsos2017outage}; and simulated fault trajectories
support diagnosis from sparse PMUs \cite{warner2023highfidelity}.
Physical models, transient histories and unknown-onset searches are thus
established ingredients. A small state-reconstruction error, however, does
not by itself identify the intervention that produced the observations.

The source recursively estimates algebraic/dynamic states using incomplete nonlinear DAE models and phasor data; both manuscript uses match that scope.

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

The source recursively estimates algebraic/dynamic states using incomplete nonlinear DAE models and phasor data; both manuscript uses match that scope.

## Sources and isolation

- [publisher-deposited DOI registry metadata](https://api.crossref.org/works/10.1049%2Fgtd2.13308): Record actually fetched during this audit; see per-entry lookup JSON.
- [registered primary publication URL](https://ietresearch.onlinelibrary.wiley.com/doi/10.1049/gtd2.13308): URL recorded by Crossref; independent retrieval only if listed below.
- [publisher full text and abstract](https://ietresearch.onlinelibrary.wiley.com/doi/10.1049/gtd2.13308): The source recursively estimates algebraic/dynamic states using incomplete nonlinear DAE models and phasor data; both manuscript uses match that scope.

Metadata response: `katanic2024recursive.lookup.json`. Contexts were assessed for this entry only; no support was transferred from an unrelated entry in the batch.
This was a fresh collaboration-subagent audit, not the unavailable gpt-5.4 Codex MCP workflow. Exact model identity and cross-model independence were not certified.

## Finding and action

Metadata verified; active context uses supported within the qualifications recorded.

Retain.

## Uncertainty

No unresolved identity/metadata/context discrepancy beyond the global methodology limitations.

Batch traces: .aris/traces/citation-audit/20261101_run01/web_batch05.txt

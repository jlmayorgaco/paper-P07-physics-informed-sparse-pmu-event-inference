# Isolated entry audit: eriksson2013diagnosability

Verdict: KEEP; active: True; existence: YES; context: SUPPORTS.

## Input entry

```bibtex
@article{eriksson2013diagnosability,
  author  = {D. Eriksson and E. Frisk and M. Krysander},
  title   = {A Method for Quantitative Fault Diagnosability Analysis of Stochastic Linear Descriptor Models},
  journal = {Automatica},
  volume  = {49},
  number  = {6},
  pages   = {1591--1600},
  year    = {2013},
  doi     = {10.1016/j.automatica.2013.02.045}
}
```

## Canonical metadata actually retrieved

```json
{
  "title": "A method for quantitative fault diagnosability analysis of stochastic linear descriptor models",
  "authors": [
    "Daniel Eriksson",
    "Erik Frisk",
    "Mattias Krysander"
  ],
  "venue": "Automatica",
  "publisher": "Elsevier BV",
  "year": [
    [
      2013,
      6
    ]
  ],
  "volume": "49",
  "issue": "6",
  "pages": "1591-1600",
  "DOI": "10.1016/j.automatica.2013.02.045",
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
    "value": "10.1016/j.automatica.2013.02.045"
  }
}

## Context assessment

### sections/article_related.tex:12 — SUPPORTS

\subsection{State Estimation and Physical Source Inference}
Unknown-input and DAE estimators recover electrical states despite
incomplete models or exogenous inputs
\cite{gillijns2007input,nugroho2022dae,katanic2024recursive}. Functional
observability asks whether a requested state quantity can be recovered
\cite{fernando2010functional,montanari2022functional}. Source inference asks
which intervention can explain the trajectory. Descriptor-model
diagnosability and nuisance-profiled tests formalize this distinction
\cite{eriksson2013diagnosability,scharf1994matched}.

The source quantifies fault-mode distinguishability in stochastic descriptor models through KL divergence and links it to fault-to-noise ratio. It supports the qualitative source-separation argument, not a universal calibrated error formula.

### sections/article_information.tex:33 — SUPPORTS

A better physical prediction need not produce a better location. Competing
sources may remain similar after their severities and initial conditions
are fitted. For a response $s_h$ at specified severity and context, the
distance to an admitted competitor is
\begin{equation}
 d_h^2=\min_{j\ne h}\ \min_{\beta_j\in\mathcal A_j}
       \|s_h-s_j(\beta_j)\|_{\Sigma^{-1}}^2.
 \label{eq:narrative-separation}
\end{equation}
The set $\mathcal A_j$ fixes allowed signs, severities and nuisance
coordinates. Small distance makes source discrimination noise-sensitive;
it is not a universal error formula or a calibrated decision certificate
\cite{eriksson2013diagnosability,scharf1994matched}.

The source quantifies fault-mode distinguishability in stochastic descriptor models through KL divergence and links it to fault-to-noise ratio. It supports the qualitative source-separation argument, not a universal calibrated error formula.

## Sources and isolation

- [publisher-deposited DOI registry metadata](https://api.crossref.org/works/10.1016%2Fj.automatica.2013.02.045): Record actually fetched during this audit; see per-entry lookup JSON.
- [registered primary publication URL](https://linkinghub.elsevier.com/retrieve/pii/S0005109813001349): URL recorded by Crossref; independent retrieval only if listed below.
- [publisher abstract and method excerpts](https://www.sciencedirect.com/science/article/pii/S0005109813001349): The source quantifies fault-mode distinguishability in stochastic descriptor models through KL divergence and links it to fault-to-noise ratio. It supports the qualitative source-separation argument, not a universal calibrated error formula.

Metadata response: `eriksson2013diagnosability.lookup.json`. Contexts were assessed for this entry only; no support was transferred from an unrelated entry in the batch.
This was a fresh collaboration-subagent audit, not the unavailable gpt-5.4 Codex MCP workflow. Exact model identity and cross-model independence were not certified.

## Finding and action

Metadata verified; active context uses supported within the qualifications recorded.

Retain.

## Uncertainty

No unresolved identity/metadata/context discrepancy beyond the global methodology limitations.

Batch traces: .aris/traces/citation-audit/20261101_run01/web_batch04.txt

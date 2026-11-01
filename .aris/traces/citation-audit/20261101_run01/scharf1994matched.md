# Isolated entry audit: scharf1994matched

Verdict: KEEP; active: True; existence: YES; context: SUPPORTS.

## Input entry

```bibtex
@article{scharf1994matched,
  author  = {L. L. Scharf and B. Friedlander},
  title   = {Matched Subspace Detectors},
  journal = {IEEE Transactions on Signal Processing},
  volume  = {42},
  number  = {8},
  pages   = {2146--2157},
  year    = {1994},
  doi     = {10.1109/78.301849}
}
```

## Canonical metadata actually retrieved

```json
{
  "title": "Matched subspace detectors",
  "authors": [
    "L.L. Scharf",
    "B. Friedlander"
  ],
  "venue": "IEEE Transactions on Signal Processing",
  "publisher": "Institute of Electrical and Electronics Engineers (IEEE)",
  "year": [
    [
      1994
    ]
  ],
  "volume": "42",
  "issue": "8",
  "pages": "2146-2157",
  "DOI": "10.1109/78.301849",
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
    "value": "10.1109/78.301849"
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

The source derives GLRTs for signals in subspace interference and noise, providing the nuisance-profiled detection precedent. The manuscript correctly limits its use to qualitative noise sensitivity and disclaims a universal error certificate.

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

The source derives GLRTs for signals in subspace interference and noise, providing the nuisance-profiled detection precedent. The manuscript correctly limits its use to qualitative noise sensitivity and disclaims a universal error certificate.

## Sources and isolation

- [publisher-deposited DOI registry metadata](https://api.crossref.org/works/10.1109/78.301849): Record actually fetched during this audit; see per-entry lookup JSON.
- [registered primary publication URL](http://ieeexplore.ieee.org/document/301849/): URL recorded by Crossref; independent retrieval only if listed below.
- [original-paper full-text excerpt](https://www.mssc.mu.edu/~daniel/mscs6960/spring2010/ScharfFriedlanderTSP94.pdf): The source derives GLRTs for signals in subspace interference and noise, providing the nuisance-profiled detection precedent. The manuscript correctly limits its use to qualitative noise sensitivity and disclaims a universal error certificate.

Metadata response: `scharf1994matched.lookup.json`. Contexts were assessed for this entry only; no support was transferred from an unrelated entry in the batch.
This was a fresh collaboration-subagent audit, not the unavailable gpt-5.4 Codex MCP workflow. Exact model identity and cross-model independence were not certified.

## Finding and action

Metadata verified; active context uses supported within the qualifications recorded.

Retain.

## Uncertainty

No unresolved identity/metadata/context discrepancy beyond the global methodology limitations.

Batch traces: .aris/traces/citation-audit/20261101_run01/web_batch04.txt

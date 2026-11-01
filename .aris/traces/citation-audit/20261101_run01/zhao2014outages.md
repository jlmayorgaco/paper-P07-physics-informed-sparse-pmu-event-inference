# Isolated entry audit: zhao2014outages

Verdict: KEEP; active: True; existence: YES; context: SUPPORTS.

## Input entry

```bibtex
@article{zhao2014outages,
  author  = {Y. Zhao and J. Chen and A. Goldsmith and H. V. Poor},
  title   = {Identification of Outages in Power Systems With Uncertain States and Optimal Sensor Locations},
  journal = {IEEE Journal of Selected Topics in Signal Processing},
  volume  = {8},
  number  = {6},
  pages   = {1140--1153},
  year    = {2014},
  doi     = {10.1109/JSTSP.2014.2342191}
}
```

## Canonical metadata actually retrieved

```json
{
  "title": "Identification of Outages in Power Systems With Uncertain States and Optimal Sensor Locations",
  "authors": [
    "Yue Zhao",
    "Jianshu Chen",
    "Andrea Goldsmith",
    "H. Vincent Poor"
  ],
  "venue": "IEEE Journal of Selected Topics in Signal Processing",
  "publisher": "Institute of Electrical and Electronics Engineers (IEEE)",
  "year": [
    [
      2014,
      12
    ]
  ],
  "volume": "8",
  "issue": "6",
  "pages": "1140-1153",
  "DOI": "10.1109/jstsp.2014.2342191",
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
    "value": "10.1109/JSTSP.2014.2342191"
  }
}

## Context assessment

### sections/article_related.tex:16 — SUPPORTS

Physical hypotheses support outage inference from phasor angles
\cite{tate2008outage}, Bayesian inference with uncertain states
\cite{zhao2014outages}, and sequential detection under stochastic operation
\cite{chen2016quickest,rovatsos2017outage}. Anguluri \emph{et al.} recover
sparse forcing locations, inputs and an unknown initial state using group
LASSO for linear dynamics \cite{anguluri2023group}. These are precedents
for source recovery; group LASSO is not an executed comparator in our
frozen campaign. Sensor placement also affects source distinguishability
\cite{jamei2020limits,conte2023fault,yildiz2025sparse}.\AIDraftingCredit{}

The source develops joint Bayesian outage/state inference using Gaussian state priors and posterior-based detection, matching the manuscript statement.

## Sources and isolation

- [publisher-deposited DOI registry metadata](https://api.crossref.org/works/10.1109/JSTSP.2014.2342191): Record actually fetched during this audit; see per-entry lookup JSON.
- [registered primary publication URL](https://ieeexplore.ieee.org/document/6862865/): URL recorded by Crossref; independent retrieval only if listed below.
- [author institution abstract](https://collaborate.princeton.edu/en/publications/identification-of-outages-in-power-systems-with-uncertain-states-/): The source develops joint Bayesian outage/state inference using Gaussian state priors and posterior-based detection, matching the manuscript statement.

Metadata response: `zhao2014outages.lookup.json`. Contexts were assessed for this entry only; no support was transferred from an unrelated entry in the batch.
This was a fresh collaboration-subagent audit, not the unavailable gpt-5.4 Codex MCP workflow. Exact model identity and cross-model independence were not certified.

## Finding and action

Metadata verified; active context uses supported within the qualifications recorded.

Retain.

## Uncertainty

No unresolved identity/metadata/context discrepancy beyond the global methodology limitations.

Batch traces: .aris/traces/citation-audit/20261101_run01/web_batch07.txt

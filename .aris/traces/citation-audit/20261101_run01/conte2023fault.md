# Isolated entry audit: conte2023fault

Verdict: KEEP; active: True; existence: YES; context: SUPPORTS.

## Input entry

```bibtex
@article{conte2023fault,
  author  = {F. Conte and F. D'Agostino and B. Gabriele and G.-P. Schiapparelli and F. Silvestro},
  title   = {Fault Detection and Localization in Active Distribution Networks Using Optimally Placed Phasor Measurements Units},
  journal = {IEEE Transactions on Power Systems},
  volume  = {38},
  number  = {1},
  pages   = {714--727},
  year    = {2023},
  doi     = {10.1109/TPWRS.2022.3165685}
}
```

## Canonical metadata actually retrieved

```json
{
  "title": "Fault Detection and Localization in Active Distribution Networks Using Optimally Placed Phasor Measurements Units",
  "authors": [
    "Francesco Conte",
    "Fabio D'Agostino",
    "Bruno Gabriele",
    "Giacomo-Piero Schiapparelli",
    "Federico Silvestro"
  ],
  "venue": "IEEE Transactions on Power Systems",
  "publisher": "Institute of Electrical and Electronics Engineers (IEEE)",
  "year": [
    [
      2023,
      1
    ]
  ],
  "volume": "38",
  "issue": "1",
  "pages": "714-727",
  "DOI": "10.1109/tpwrs.2022.3165685",
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
    "value": "10.1109/TPWRS.2022.3165685"
  }
}

## Context assessment

### sections/article_related.tex:22 — SUPPORTS

Physical hypotheses support outage inference from phasor angles
\cite{tate2008outage}, Bayesian inference with uncertain states
\cite{zhao2014outages}, and sequential detection under stochastic operation
\cite{chen2016quickest,rovatsos2017outage}. Anguluri \emph{et al.} recover
sparse forcing locations, inputs and an unknown initial state using group
LASSO for linear dynamics \cite{anguluri2023group}. These are precedents
for source recovery; group LASSO is not an executed comparator in our
frozen campaign. Sensor placement also affects source distinguishability
\cite{jamei2020limits,conte2023fault,yildiz2025sparse}.\AIDraftingCredit{}

Reduced PMU placement produces fault-localization clusters and the placement algorithm controls localization resolution; this supports source distinguishability dependence on sensor placement.

## Sources and isolation

- [publisher-deposited DOI registry metadata](https://api.crossref.org/works/10.1109%2FTPWRS.2022.3165685): Record actually fetched during this audit; see per-entry lookup JSON.
- [registered primary publication URL](https://ieeexplore.ieee.org/document/9751367/): URL recorded by Crossref; independent retrieval only if listed below.
- [publisher abstract and author-institution full-paper excerpts](https://ieeexplore.ieee.org/document/9751367/): Reduced PMU placement produces fault-localization clusters and the placement algorithm controls localization resolution; this supports source distinguishability dependence on sensor placement.

Metadata response: `conte2023fault.lookup.json`. Contexts were assessed for this entry only; no support was transferred from an unrelated entry in the batch.
This was a fresh collaboration-subagent audit, not the unavailable gpt-5.4 Codex MCP workflow. Exact model identity and cross-model independence were not certified.

## Finding and action

Metadata verified; active context uses supported within the qualifications recorded.

Retain.

## Uncertainty

No unresolved identity/metadata/context discrepancy beyond the global methodology limitations.

Batch traces: .aris/traces/citation-audit/20261101_run01/web_batch06.txt

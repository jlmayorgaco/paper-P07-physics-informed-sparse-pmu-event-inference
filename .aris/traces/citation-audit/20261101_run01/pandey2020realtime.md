# Isolated entry audit: pandey2020realtime

Verdict: KEEP; active: True; existence: YES; context: SUPPORTS.

## Input entry

```bibtex
@article{pandey2020realtime,
  author  = {S. Pandey and A. K. Srivastava and B. G. Amidan},
  title   = {A Real Time Event Detection, Classification and Localization Using Synchrophasor Data},
  journal = {IEEE Transactions on Power Systems},
  volume  = {35},
  number  = {6},
  pages   = {4421--4431},
  year    = {2020},
  doi     = {10.1109/TPWRS.2020.2986019}
}
```

## Canonical metadata actually retrieved

```json
{
  "title": "A Real Time Event Detection, Classification and Localization Using Synchrophasor Data",
  "authors": [
    "Shikhar Pandey",
    "Anurag K. Srivastava",
    "Brett G. Amidan"
  ],
  "venue": "IEEE Transactions on Power Systems",
  "publisher": "Institute of Electrical and Electronics Engineers (IEEE)",
  "year": [
    [
      2020,
      11
    ]
  ],
  "volume": "35",
  "issue": "6",
  "pages": "4421-4431",
  "DOI": "10.1109/tpwrs.2020.2986019",
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
    "value": "10.1109/TPWRS.2020.2986019"
  }
}

## Context assessment

### sections/article_related.tex:50 — SUPPORTS

\subsection{Learned Diagnosis and Physical Uncertainty}
Learned and knowledge-driven representations identify PMU disturbances and
assets \cite{pandey2020realtime,li2024knowledge,yildiz2024few}. We compare
two fixed ExtraTrees adapters from the SGSMA project. Their performance
tests transfer of those implementations, not the limits of all supervised
learning. A known physical catalog and source-excluded supervised training
also impose different information constraints.

The source combines statistical/clustering anomaly detection, DBSCAN, physics-based rules/decision trees and topology-based localization. It supports the broad learned-and-knowledge-driven grouping, not a claim that its full method is a supervised learner.

## Sources and isolation

- [publisher-deposited DOI registry metadata](https://api.crossref.org/works/10.1109/TPWRS.2020.2986019): Record actually fetched during this audit; see per-entry lookup JSON.
- [registered primary publication URL](https://ieeexplore.ieee.org/document/9072390/): URL recorded by Crossref; independent retrieval only if listed below.
- [publisher abstract and introduction](https://doi.org/10.1109%2FTPWRS.2020.2986019): The source combines statistical/clustering anomaly detection, DBSCAN, physics-based rules/decision trees and topology-based localization. It supports the broad learned-and-knowledge-driven grouping, not a claim that its full method is a supervised learner.

Metadata response: `pandey2020realtime.lookup.json`. Contexts were assessed for this entry only; no support was transferred from an unrelated entry in the batch.
This was a fresh collaboration-subagent audit, not the unavailable gpt-5.4 Codex MCP workflow. Exact model identity and cross-model independence were not certified.

## Finding and action

Metadata verified; active context uses supported within the qualifications recorded.

Retain.

## Uncertainty

No unresolved identity/metadata/context discrepancy beyond the global methodology limitations.

Batch traces: .aris/traces/citation-audit/20261101_run01/web_batch07.txt

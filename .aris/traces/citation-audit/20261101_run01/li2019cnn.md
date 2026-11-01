# Isolated entry audit: li2019cnn

Verdict: KEEP; active: False; existence: YES; context: N/A.

## Input entry

```bibtex
@article{li2019cnn,
  author  = {W. Li and D. Deka and M. Chertkov and M. Wang},
  title   = {Real-Time Faulted Line Localization and {PMU} Placement in Power Systems Through Convolutional Neural Networks},
  journal = {IEEE Transactions on Power Systems},
  volume  = {34},
  number  = {6},
  pages   = {4640--4651},
  year    = {2019},
  doi     = {10.1109/TPWRS.2019.2917794}
}
```

## Canonical metadata actually retrieved

```json
{
  "title": "Real-Time Faulted Line Localization and PMU Placement in Power Systems Through Convolutional Neural Networks",
  "authors": [
    "Wenting Li",
    "Deepjyoti Deka",
    "Michael Chertkov",
    "Meng Wang"
  ],
  "venue": "IEEE Transactions on Power Systems",
  "publisher": "Institute of Electrical and Electronics Engineers (IEEE)",
  "year": [
    [
      2019,
      11
    ]
  ],
  "volume": "34",
  "issue": "6",
  "pages": "4640-4651",
  "DOI": "10.1109/tpwrs.2019.2917794",
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
    "value": "10.1109/TPWRS.2019.2917794"
  }
}

## Context assessment

N/A: no citation in declared main.tex / supplement.tex dependency graph.
## Sources and isolation

- [publisher-deposited DOI registry metadata](https://api.crossref.org/works/10.1109/TPWRS.2019.2917794): Record actually fetched during this audit; see per-entry lookup JSON.
- [registered primary publication URL](https://ieeexplore.ieee.org/document/8718345/): URL recorded by Crossref; independent retrieval only if listed below.

Metadata response: `li2019cnn.lookup.json`. Contexts were assessed for this entry only; no support was transferred from an unrelated entry in the batch.
This was a fresh collaboration-subagent audit, not the unavailable gpt-5.4 Codex MCP workflow. Exact model identity and cross-model independence were not certified.

## Finding and action

Metadata verified; uncited in the active main/supplement.

Retain.

## Uncertainty

Context is N/A for the declared active main+supplement scope; no claim about legacy or historical-note uses is made.

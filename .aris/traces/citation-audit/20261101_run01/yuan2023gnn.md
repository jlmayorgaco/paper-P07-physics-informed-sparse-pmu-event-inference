# Isolated entry audit: yuan2023gnn

Verdict: FIX; active: False; existence: YES; context: N/A.

## Input entry

```bibtex
@article{yuan2023gnn,
  author  = {Y. Yuan and Y. Wang and Z. Wang},
  title   = {Learning Latent Interactions for Event Classification via Graph Neural Networks and {PMU} Data},
  journal = {IEEE Transactions on Power Systems},
  volume  = {38},
  number  = {1},
  pages   = {617--629},
  year    = {2023},
  doi     = {10.1109/TPWRS.2022.3158248}
}
```

## Canonical metadata actually retrieved

```json
{
  "title": "Learning Latent Interactions for Event Classification via Graph Neural Networks and PMU Data",
  "authors": [
    "Yuxuan Yuan",
    "Zhaoyu Wang",
    "Yanchao Wang"
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
  "pages": "617-629",
  "DOI": "10.1109/tpwrs.2022.3158248",
  "ISBN": null
}
```

## Metadata assessment

{
  "title": {
    "status": "correct"
  },
  "authors": {
    "status": "wrong_order",
    "canonical": [
      "Yuxuan Yuan",
      "Zhaoyu Wang",
      "Yanchao Wang"
    ]
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
    "value": "10.1109/TPWRS.2022.3158248"
  }
}

## Context assessment

N/A: no citation in declared main.tex / supplement.tex dependency graph.
## Sources and isolation

- [publisher-deposited DOI registry metadata](https://api.crossref.org/works/10.1109/TPWRS.2022.3158248): Record actually fetched during this audit; see per-entry lookup JSON.
- [registered primary publication URL](https://ieeexplore.ieee.org/document/9732528/): URL recorded by Crossref; independent retrieval only if listed below.
- [primary/institutional metadata corroboration](https://wzy.ece.iastate.edu/CV/c201.pdf): Author-hosted original paper confirms author order: Yuan, Zhaoyu Wang, Yanchao Wang.

Metadata response: `yuan2023gnn.lookup.json`. Contexts were assessed for this entry only; no support was transferred from an unrelated entry in the batch.
This was a fresh collaboration-subagent audit, not the unavailable gpt-5.4 Codex MCP workflow. Exact model identity and cross-model independence were not certified.

## Finding and action

The second and third authors are reversed in the bibliography.

Use "Y. Yuan and Z. Wang and Y. Wang" (Yuxuan Yuan; Zhaoyu Wang; Yanchao Wang).

## Uncertainty

Context is N/A for the declared active main+supplement scope; no claim about legacy or historical-note uses is made.

Batch traces: .aris/traces/citation-audit/20261101_run01/web_batch08.txt

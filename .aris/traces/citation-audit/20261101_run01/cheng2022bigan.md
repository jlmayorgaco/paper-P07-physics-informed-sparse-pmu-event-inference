# Isolated entry audit: cheng2022bigan

Verdict: KEEP; active: False; existence: YES; context: N/A.

## Input entry

```bibtex
@article{cheng2022bigan,
  author  = {Y. Cheng and N. Yu and B. Foggo and K. Yamashita},
  title   = {Online Power System Event Detection via Bidirectional Generative Adversarial Networks},
  journal = {IEEE Transactions on Power Systems},
  volume  = {37},
  number  = {6},
  pages   = {4807--4818},
  year    = {2022},
  doi     = {10.1109/TPWRS.2022.3153591}
}
```

## Canonical metadata actually retrieved

```json
{
  "title": "Online Power System Event Detection via Bidirectional Generative Adversarial Networks",
  "authors": [
    "Yuanbin Cheng",
    "Nanpeng Yu",
    "Brandon Foggo",
    "Koji Yamashita"
  ],
  "venue": "IEEE Transactions on Power Systems",
  "publisher": "Institute of Electrical and Electronics Engineers (IEEE)",
  "year": [
    [
      2022,
      11
    ]
  ],
  "volume": "37",
  "issue": "6",
  "pages": "4807-4818",
  "DOI": "10.1109/tpwrs.2022.3153591",
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
    "value": "10.1109/TPWRS.2022.3153591"
  }
}

## Context assessment

N/A: no citation in declared main.tex / supplement.tex dependency graph.
## Sources and isolation

- [publisher-deposited DOI registry metadata](https://api.crossref.org/works/10.1109/TPWRS.2022.3153591): Record actually fetched during this audit; see per-entry lookup JSON.
- [registered primary publication URL](https://ieeexplore.ieee.org/document/9721662/): URL recorded by Crossref; independent retrieval only if listed below.

Metadata response: `cheng2022bigan.lookup.json`. Contexts were assessed for this entry only; no support was transferred from an unrelated entry in the batch.
This was a fresh collaboration-subagent audit, not the unavailable gpt-5.4 Codex MCP workflow. Exact model identity and cross-model independence were not certified.

## Finding and action

Metadata verified; uncited in the active main/supplement.

Retain.

## Uncertainty

Context is N/A for the declared active main+supplement scope; no claim about legacy or historical-note uses is made.

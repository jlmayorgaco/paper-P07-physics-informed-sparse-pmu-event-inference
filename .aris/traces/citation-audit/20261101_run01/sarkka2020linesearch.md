# Isolated entry audit: sarkka2020linesearch

Verdict: KEEP; active: False; existence: YES; context: N/A.

## Input entry

```bibtex
@inproceedings{sarkka2020linesearch,
  author    = {S. S{\"a}rkk{\"a} and L. Svensson},
  title     = {Levenberg--Marquardt and Line-Search Extended Kalman Smoothers},
  booktitle = {Proc. IEEE Int. Conf. Acoustics, Speech and Signal Processing (ICASSP)},
  pages     = {5875--5879},
  year      = {2020},
  doi       = {10.1109/ICASSP40776.2020.9054686}
}
```

## Canonical metadata actually retrieved

```json
{
  "title": "Levenberg-Marquardt and Line-Search Extended Kalman Smoothers",
  "authors": [
    "Simo Sarkka",
    "Lennart Svensson"
  ],
  "venue": "ICASSP 2020 - 2020 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)",
  "publisher": "IEEE",
  "year": [
    [
      2020,
      5
    ]
  ],
  "volume": null,
  "issue": null,
  "pages": "5875-5879",
  "DOI": "10.1109/icassp40776.2020.9054686",
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
    "value": "10.1109/ICASSP40776.2020.9054686"
  }
}

## Context assessment

N/A: no citation in declared main.tex / supplement.tex dependency graph.
## Sources and isolation

- [publisher-deposited DOI registry metadata](https://api.crossref.org/works/10.1109/ICASSP40776.2020.9054686): Record actually fetched during this audit; see per-entry lookup JSON.
- [registered primary publication URL](https://ieeexplore.ieee.org/document/9054686/): URL recorded by Crossref; independent retrieval only if listed below.

Metadata response: `sarkka2020linesearch.lookup.json`. Contexts were assessed for this entry only; no support was transferred from an unrelated entry in the batch.
This was a fresh collaboration-subagent audit, not the unavailable gpt-5.4 Codex MCP workflow. Exact model identity and cross-model independence were not certified.

## Finding and action

Metadata verified; uncited in the active main/supplement.

Retain.

## Uncertainty

Context is N/A for the declared active main+supplement scope; no claim about legacy or historical-note uses is made.

# Isolated entry audit: zhang2025functional

Verdict: FIX; active: False; existence: YES; context: N/A.

## Input entry

```bibtex
@article{zhang2025functional,
  author  = {T. Zhang and T. L. Fernando and M. Darouach},
  title   = {Functional Observability, Functional Detectability, and Structural Functional Observability of Linear Systems},
  journal = {IEEE Transactions on Automatic Control},
  volume  = {70},
  number  = {3},
  pages   = {1592--1607},
  year    = {2025},
  doi     = {10.1109/TAC.2024.3462558}
}
```

## Canonical metadata actually retrieved

```json
{
  "title": "Functional Observability, Structural Functional Observability, and Optimal Sensor Placement",
  "authors": [
    "Yuan Zhang",
    "Tyrone Fernando",
    "Mohamed Darouach"
  ],
  "venue": "IEEE Transactions on Automatic Control",
  "publisher": "Institute of Electrical and Electronics Engineers (IEEE)",
  "year": [
    [
      2025,
      3
    ]
  ],
  "volume": "70",
  "issue": "3",
  "pages": "1592-1607",
  "DOI": "10.1109/tac.2024.3462558",
  "ISBN": null
}
```

## Metadata assessment

{
  "title": {
    "status": "wrong",
    "canonical": "Functional Observability, Structural Functional Observability, and Optimal Sensor Placement"
  },
  "authors": {
    "status": "wrong",
    "canonical": [
      "Yuan Zhang",
      "Tyrone Fernando",
      "Mohamed Darouach"
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
    "value": "10.1109/TAC.2024.3462558"
  }
}

## Context assessment

N/A: no citation in declared main.tex / supplement.tex dependency graph.
## Sources and isolation

- [publisher-deposited DOI registry metadata](https://api.crossref.org/works/10.1109/TAC.2024.3462558): Record actually fetched during this audit; see per-entry lookup JSON.
- [registered primary publication URL](https://ieeexplore.ieee.org/document/10681657/): URL recorded by Crossref; independent retrieval only if listed below.
- [primary/institutional metadata corroboration](https://research-repository.uwa.edu.au/en/publications/functional-observability-structural-functional-observability-and-/): Institutional published article record confirms final title and Yuan Zhang.

Metadata response: `zhang2025functional.lookup.json`. Contexts were assessed for this entry only; no support was transferred from an unrelated entry in the batch.
This was a fresh collaboration-subagent audit, not the unavailable gpt-5.4 Codex MCP workflow. Exact model identity and cross-model independence were not certified.

## Finding and action

The DOI is real, but the entry mixes a different title formulation with an incorrect first-author initial.

Set title to "Functional Observability, Structural Functional Observability, and Optimal Sensor Placement" and first author to "Y. Zhang" (Yuan Zhang). Retain 2025, 70(3):1592-1607 and DOI.

## Uncertainty

Context is N/A for the declared active main+supplement scope; no claim about legacy or historical-note uses is made.

Batch traces: .aris/traces/citation-audit/20261101_run01/web_batch08.txt

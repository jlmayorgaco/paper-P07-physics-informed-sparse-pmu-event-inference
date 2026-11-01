# Isolated entry audit: rotnitzky2000singular

Verdict: KEEP; active: False; existence: YES; context: N/A.

## Input entry

```bibtex
@article{rotnitzky2000singular,
  author  = {A. Rotnitzky and D. R. Cox and M. Bottai and J. M. Robins},
  title   = {Likelihood-Based Inference With Singular Information Matrix},
  journal = {Bernoulli},
  volume  = {6},
  number  = {2},
  pages   = {243--284},
  year    = {2000},
  doi     = {10.2307/3318576}
}
```

## Canonical metadata actually retrieved

```json
{
  "title": "Likelihood-Based Inference with Singular Information Matrix",
  "authors": [
    "Andrea Rotnitzky",
    "David R. Cox",
    "Matteo Bottai",
    "James Robins"
  ],
  "venue": "Bernoulli",
  "publisher": "JSTOR",
  "year": [
    [
      2000,
      4
    ]
  ],
  "volume": "6",
  "issue": "2",
  "pages": "243",
  "DOI": "10.2307/3318576",
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
    "value": "10.2307/3318576"
  },
  "registry_discrepancy": {
    "status": "resolved_by_primary_source",
    "note": "Author publication list confirms full title and pages 243-284, completing Crossref's first-page-only record."
  }
}

## Context assessment

N/A: no citation in declared main.tex / supplement.tex dependency graph.
## Sources and isolation

- [publisher-deposited DOI registry metadata](https://api.crossref.org/works/10.2307/3318576): Record actually fetched during this audit; see per-entry lookup JSON.
- [registered primary publication URL](https://www.jstor.org/stable/3318576?origin=crossref): URL recorded by Crossref; independent retrieval only if listed below.
- [primary/institutional metadata corroboration](https://www.biostat.washington.edu/sites/default/files/files/users/SPH%2520CV%2520Rotnitzky%25201-24-2023.pdf): Author publication list confirms full title and pages 243-284, completing Crossref's first-page-only record.

Metadata response: `rotnitzky2000singular.lookup.json`. Contexts were assessed for this entry only; no support was transferred from an unrelated entry in the batch.
This was a fresh collaboration-subagent audit, not the unavailable gpt-5.4 Codex MCP workflow. Exact model identity and cross-model independence were not certified.

## Finding and action

Metadata verified; uncited in the active main/supplement.

Retain.

## Uncertainty

Context is N/A for the declared active main+supplement scope; no claim about legacy or historical-note uses is made.

Batch traces: .aris/traces/citation-audit/20261101_run01/web_batch10.txt, .aris/traces/citation-audit/20261101_run01/web_batch12.txt

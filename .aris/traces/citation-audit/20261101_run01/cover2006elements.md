# Isolated entry audit: cover2006elements

Verdict: KEEP; active: False; existence: YES; context: N/A.

## Input entry

```bibtex
@book{cover2006elements,
  author    = {T. M. Cover and J. A. Thomas},
  title     = {Elements of Information Theory},
  edition   = {2},
  publisher = {Wiley-Interscience},
  address   = {Hoboken, NJ, USA},
  year      = {2006},
  doi       = {10.1002/047174882X},
  isbn      = {978-0-471-24195-9}
}
```

## Canonical metadata actually retrieved

```json
{
  "title": "Elements of Information Theory",
  "authors": [
    "Thomas M. Cover",
    "Joy A. Thomas"
  ],
  "venue": "Wiley",
  "publisher": "Wiley",
  "year": [
    [
      2005,
      4,
      7
    ]
  ],
  "volume": null,
  "issue": null,
  "pages": null,
  "DOI": "10.1002/047174882x",
  "ISBN": [
    "9780471241959",
    "9780471748823"
  ]
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
  "identifier": {
    "status": "correct",
    "value": "10.1002/047174882X"
  },
  "registry_discrepancy": {
    "status": "resolved_by_primary_source",
    "note": "Publisher confirms 2nd edition and July 2006 for the cited print ISBN. Crossref carries older 2005 electronic metadata and an inconsistent edition field; retain the print edition/year."
  }
}

## Context assessment

N/A: no citation in declared main.tex / supplement.tex dependency graph.
## Sources and isolation

- [publisher-deposited DOI registry metadata](https://api.crossref.org/works/10.1002/047174882X): Record actually fetched during this audit; see per-entry lookup JSON.
- [registered primary publication URL](https://onlinelibrary.wiley.com/doi/book/10.1002/047174882X): URL recorded by Crossref; independent retrieval only if listed below.
- [primary/institutional metadata corroboration](https://www.wiley.com/en-us/shop/general-introductory-computer-science/elements-of-information-theory-2nd-edition-p-9780471241959): Publisher confirms 2nd edition and July 2006 for the cited print ISBN. Crossref carries older 2005 electronic metadata and an inconsistent edition field; retain the print edition/year.

Metadata response: `cover2006elements.lookup.json`. Contexts were assessed for this entry only; no support was transferred from an unrelated entry in the batch.
This was a fresh collaboration-subagent audit, not the unavailable gpt-5.4 Codex MCP workflow. Exact model identity and cross-model independence were not certified.

## Finding and action

Metadata verified; uncited in the active main/supplement.

Retain.

## Uncertainty

Context is N/A for the declared active main+supplement scope; no claim about legacy or historical-note uses is made.

Batch traces: .aris/traces/citation-audit/20261101_run01/web_batch10.txt

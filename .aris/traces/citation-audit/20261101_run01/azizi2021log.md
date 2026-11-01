# Isolated entry audit: azizi2021log

Verdict: FIX; active: False; existence: YES; context: N/A.

## Input entry

```bibtex
@article{azizi2021log,
  author  = {S. Azizi and M. R. Rezaei Jegarluei and A. Salehi Dobakhshari and G. Liu and V. Terzija},
  title   = {Wide-Area Identification of the Size and Location of Loss of Generation Events by Sparse {PMUs}},
  journal = {IEEE Transactions on Power Delivery},
  volume  = {36},
  number  = {4},
  pages   = {2397--2407},
  year    = {2021},
  doi     = {10.1109/TPWRD.2020.3047228}
}
```

## Canonical metadata actually retrieved

```json
{
  "title": "Wide-Area Identification of the Size and Location of Loss of Generation Events by Sparse PMUs",
  "authors": [
    "Sadegh Azizi",
    "Mohammad Rezaei Jegarluei",
    "Ahmad Salehi Dobakhshari",
    "Gaoyuan Liu",
    "Vladimir Terzija"
  ],
  "venue": "IEEE Transactions on Power Delivery",
  "publisher": "Institute of Electrical and Electronics Engineers (IEEE)",
  "year": [
    [
      2021,
      8
    ]
  ],
  "volume": "36",
  "issue": "4",
  "pages": "2397-2407",
  "DOI": "10.1109/tpwrd.2020.3047228",
  "ISBN": null
}
```

## Metadata assessment

{
  "title": {
    "status": "correct"
  },
  "authors": {
    "status": "typo",
    "canonical_correction": "Rezaei Jegarluei, Mohammad"
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
    "value": "10.1109/TPWRD.2020.3047228"
  }
}

## Context assessment

N/A: no citation in declared main.tex / supplement.tex dependency graph.
## Sources and isolation

- [publisher-deposited DOI registry metadata](https://api.crossref.org/works/10.1109/TPWRD.2020.3047228): Record actually fetched during this audit; see per-entry lookup JSON.
- [registered primary publication URL](https://ieeexplore.ieee.org/document/9307251/): URL recorded by Crossref; independent retrieval only if listed below.
- [primary/institutional metadata corroboration](https://eprints.whiterose.ac.uk/id/eprint/169323/): Author institution record names Mohammad Rezaei Jegarluei and gives final publication metadata.

Metadata response: `azizi2021log.lookup.json`. Contexts were assessed for this entry only; no support was transferred from an unrelated entry in the batch.
This was a fresh collaboration-subagent audit, not the unavailable gpt-5.4 Codex MCP workflow. Exact model identity and cross-model independence were not certified.

## Finding and action

The second author is Mohammad Rezaei Jegarluei. "M. R. Rezaei Jegarluei" duplicates the Rezaei initial when Rezaei is retained as part of the surname.

Use "Rezaei Jegarluei, Mohammad" or the correctly abbreviated "M. Rezaei Jegarluei".

## Uncertainty

Context is N/A for the declared active main+supplement scope; no claim about legacy or historical-note uses is made.

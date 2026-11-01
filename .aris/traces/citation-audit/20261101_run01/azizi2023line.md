# Isolated entry audit: azizi2023line

Verdict: FIX; active: False; existence: YES; context: N/A.

## Input entry

```bibtex
@article{azizi2023line,
  author  = {S. Azizi and M. R. Rezaei Jegarluei and A. M. Kettner and A. Salehi Dobakhshari},
  title   = {Wide-Area Line Outage Monitoring by Sparse Phasor Measurements},
  journal = {IEEE Transactions on Power Systems},
  volume  = {38},
  number  = {4},
  pages   = {3621--3631},
  year    = {2023},
  doi     = {10.1109/TPWRS.2022.3201067}
}
```

## Canonical metadata actually retrieved

```json
{
  "title": "Wide-Area Line Outage Monitoring by Sparse Phasor Measurements",
  "authors": [
    "S. Azizi",
    "M. R. Jegarluei",
    "A. M. Kettner",
    "A. S. Dobakhshari"
  ],
  "venue": "IEEE Transactions on Power Systems",
  "publisher": "Institute of Electrical and Electronics Engineers (IEEE)",
  "year": [
    [
      2022
    ]
  ],
  "volume": null,
  "issue": null,
  "pages": "1-11",
  "DOI": "10.1109/tpwrs.2022.3201067",
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
    "status": "UNCERTAIN",
    "note": "2022 early-access record retrieved; existing final 2023 date not contradicted but final primary record was inaccessible."
  },
  "venue": {
    "status": "correct"
  },
  "volume_issue_pages": {
    "status": "UNCERTAIN",
    "note": "Current 38(4):3621-3631 has secondary corroboration, but retrieved primary record is early access. Retain pending final-record verification."
  },
  "identifier": {
    "status": "correct",
    "value": "10.1109/TPWRS.2022.3201067"
  }
}

## Context assessment

N/A: no citation in declared main.tex / supplement.tex dependency graph.
## Sources and isolation

- [publisher-deposited DOI registry metadata](https://api.crossref.org/works/10.1109/TPWRS.2022.3201067): Record actually fetched during this audit; see per-entry lookup JSON.
- [registered primary publication URL](https://ieeexplore.ieee.org/document/9865124/): URL recorded by Crossref; independent retrieval only if listed below.
- [primary/institutional metadata corroboration](https://eprints.whiterose.ac.uk/190192/1/Line%20Outage%20Paper.pdf): Original accepted paper identifies the author in the affiliation text as Mohammad Rezaei Jegarluei; byline uses M. R. Jegarluei.
- [primary/institutional metadata corroboration](https://eprints.whiterose.ac.uk/id/eprint/190192/): Author institution retains the 2022 early-access record. The final IEEE landing page was bot-blocked; final 2023 volume/page metadata was not directly confirmed from the version of record.

Metadata response: `azizi2023line.lookup.json`. Contexts were assessed for this entry only; no support was transferred from an unrelated entry in the batch.
This was a fresh collaboration-subagent audit, not the unavailable gpt-5.4 Codex MCP workflow. Exact model identity and cross-model independence were not certified.

## Finding and action

The second-author name has the same duplicated Rezaei initial. The publisher/author early-access record retrieved in this audit is incomplete for final volume/pages, so do not replace the existing 2023 final citation with its stale 2022, 1-11 values.

Use "Rezaei Jegarluei, Mohammad"; confirm final issue/page fields against the final IEEE PDF before changing them.

## Uncertainty

Final 2023 issue metadata remains unconfirmed from an accessible primary version-of-record page; do not treat stale registry fields as authoritative corrections.
Context is N/A for the declared active main+supplement scope; no claim about legacy or historical-note uses is made.

Batch traces: .aris/traces/citation-audit/20261101_run01/web_batch08.txt, .aris/traces/citation-audit/20261101_run01/web_batch11.txt, .aris/traces/citation-audit/20261101_run01/web_batch14.txt, .aris/traces/citation-audit/20261101_run01/web_batch15.txt, .aris/traces/citation-audit/20261101_run01/web_batch16.txt

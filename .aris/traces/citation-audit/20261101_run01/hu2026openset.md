# Isolated entry audit: hu2026openset

Verdict: FIX; active: False; existence: YES; context: N/A.

## Input entry

```bibtex
@article{hu2026openset,
  author  = {Y. Hu and Z. Cheng},
  title   = {Generative {AI} for Open-Set Event Detection and Classification in Power Systems Using Synchrophasor Data},
  journal = {IEEE Transactions on Industrial Informatics},
  year    = {2026},
  note    = {Early access},
  doi     = {10.1109/TII.2026.3690931}
}
```

## Canonical metadata actually retrieved

```json
{
  "title": "Generative AI for Open-Set Event Detection and Classification in Power Systems Using Synchrophasor Data",
  "authors": [
    "Yi Hu",
    "Zheyuan Cheng"
  ],
  "venue": "IEEE Transactions on Industrial Informatics",
  "publisher": "Institute of Electrical and Electronics Engineers (IEEE)",
  "year": [
    [
      2026,
      9
    ]
  ],
  "volume": "22",
  "issue": "9",
  "pages": "8104-8115",
  "DOI": "10.1109/tii.2026.3690931",
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
  "identifier": {
    "status": "correct",
    "value": "10.1109/TII.2026.3690931"
  },
  "volume_issue_pages": {
    "status": "incomplete",
    "canonical": "22(9):8104-8115"
  },
  "publication_status": {
    "status": "wrong",
    "canonical": "Final issue publication, September 2026"
  }
}

## Context assessment

N/A: no citation in declared main.tex / supplement.tex dependency graph.
## Sources and isolation

- [publisher-deposited DOI registry metadata](https://api.crossref.org/works/10.1109/TII.2026.3690931): Record actually fetched during this audit; see per-entry lookup JSON.
- [registered primary publication URL](https://ieeexplore.ieee.org/document/11527391/): URL recorded by Crossref; independent retrieval only if listed below.
- [primary/institutional metadata corroboration](https://ieeexplore.ieee.org/document/11527391/): Publisher-deposited Crossref metadata now provides final 22(9):8104-8115 (2026); the old early-access note is stale.

Metadata response: `hu2026openset.lookup.json`. Contexts were assessed for this entry only; no support was transferred from an unrelated entry in the batch.
This was a fresh collaboration-subagent audit, not the unavailable gpt-5.4 Codex MCP workflow. Exact model identity and cross-model independence were not certified.

## Finding and action

The early-access note is stale; a final September 2026 issue record is available.

Add volume={22}, number={9}, pages={8104--8115}; remove note={Early access}.

## Uncertainty

Context is N/A for the declared active main+supplement scope; no claim about legacy or historical-note uses is made.

Batch traces: .aris/traces/citation-audit/20261101_run01/web_batch16.txt

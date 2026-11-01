# Isolated entry audit: yildiz2024few

Verdict: KEEP; active: True; existence: YES; context: SUPPORTS.

## Input entry

```bibtex
@article{yildiz2024few,
  author  = {T. Yildiz and A. Abur},
  title   = {Convolutional Neural Network-Assisted Fault Detection and Location Using Few {PMUs}},
  journal = {Electric Power Systems Research},
  volume  = {235},
  pages   = {110705},
  year    = {2024},
  doi     = {10.1016/j.epsr.2024.110705}
}
```

## Canonical metadata actually retrieved

```json
{
  "title": "Convolutional Neural Network-assisted fault detection and location using few PMUs",
  "authors": [
    "Tuna Yildiz",
    "Ali Abur"
  ],
  "venue": "Electric Power Systems Research",
  "publisher": "Elsevier BV",
  "year": [
    [
      2024,
      10
    ]
  ],
  "volume": "235",
  "issue": null,
  "pages": "110705",
  "DOI": "10.1016/j.epsr.2024.110705",
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
    "value": "10.1016/j.epsr.2024.110705"
  }
}

## Context assessment

### sections/article_related.tex:50 — SUPPORTS

\subsection{Learned Diagnosis and Physical Uncertainty}
Learned and knowledge-driven representations identify PMU disturbances and
assets \cite{pandey2020realtime,li2024knowledge,yildiz2024few}. We compare
two fixed ExtraTrees adapters from the SGSMA project. Their performance
tests transfer of those implementations, not the limits of all supervised
learning. A known physical catalog and source-excluded supervised training
also impose different information constraints.

The source combines a CNN-assisted method and strategic sparse PMUs for fault detection/location, supporting the representation-based diagnosis claim.

## Sources and isolation

- [publisher-deposited DOI registry metadata](https://api.crossref.org/works/10.1016/j.epsr.2024.110705): Record actually fetched during this audit; see per-entry lookup JSON.
- [registered primary publication URL](https://linkinghub.elsevier.com/retrieve/pii/S0378779624005911): URL recorded by Crossref; independent retrieval only if listed below.
- [publisher abstract and method excerpt](https://www.sciencedirect.com/science/article/abs/pii/S0378779624005911): The source combines a CNN-assisted method and strategic sparse PMUs for fault detection/location, supporting the representation-based diagnosis claim.

Metadata response: `yildiz2024few.lookup.json`. Contexts were assessed for this entry only; no support was transferred from an unrelated entry in the batch.
This was a fresh collaboration-subagent audit, not the unavailable gpt-5.4 Codex MCP workflow. Exact model identity and cross-model independence were not certified.

## Finding and action

Metadata verified; active context uses supported within the qualifications recorded.

Retain.

## Uncertainty

No unresolved identity/metadata/context discrepancy beyond the global methodology limitations.

Batch traces: .aris/traces/citation-audit/20261101_run01/web_batch07.txt

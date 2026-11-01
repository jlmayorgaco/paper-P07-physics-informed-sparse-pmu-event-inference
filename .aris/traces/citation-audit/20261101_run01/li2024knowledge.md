# Isolated entry audit: li2024knowledge

Verdict: KEEP; active: True; existence: YES; context: SUPPORTS.

## Input entry

```bibtex
@article{li2024knowledge,
  author  = {Z. Li and J. Tian and H. Liu},
  title   = {A Joint Data and Knowledge-Driven Method for Power System Disturbance Localisation},
  journal = {IET Generation, Transmission \& Distribution},
  volume  = {18},
  number  = {24},
  pages   = {4078--4089},
  year    = {2024},
  doi     = {10.1049/gtd2.13331}
}
```

## Canonical metadata actually retrieved

```json
{
  "title": "A joint data and knowledge‐driven method for power system disturbance localisation",
  "authors": [
    "Zikang Li",
    "Jiyang Tian",
    "Hao Liu"
  ],
  "venue": "IET Generation, Transmission & Distribution",
  "publisher": "Institution of Engineering and Technology (IET)",
  "year": [
    [
      2024,
      12
    ]
  ],
  "volume": "18",
  "issue": "24",
  "pages": "4078-4089",
  "DOI": "10.1049/gtd2.13331",
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
    "value": "10.1049/gtd2.13331"
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

The source combines a spatiotemporal graph network with type/topology constraints to localize disturbances using sparse PMU measurements.

## Sources and isolation

- [publisher-deposited DOI registry metadata](https://api.crossref.org/works/10.1049/gtd2.13331): Record actually fetched during this audit; see per-entry lookup JSON.
- [registered primary publication URL](https://ietresearch.onlinelibrary.wiley.com/doi/10.1049/gtd2.13331): URL recorded by Crossref; independent retrieval only if listed below.
- [publisher abstract/full-text search excerpt and registry abstract](https://ietresearch.onlinelibrary.wiley.com/doi/10.1049/gtd2.13331): The source combines a spatiotemporal graph network with type/topology constraints to localize disturbances using sparse PMU measurements.

Metadata response: `li2024knowledge.lookup.json`. Contexts were assessed for this entry only; no support was transferred from an unrelated entry in the batch.
This was a fresh collaboration-subagent audit, not the unavailable gpt-5.4 Codex MCP workflow. Exact model identity and cross-model independence were not certified.

## Finding and action

Metadata verified; active context uses supported within the qualifications recorded.

Retain.

## Uncertainty

No unresolved identity/metadata/context discrepancy beyond the global methodology limitations.

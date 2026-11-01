# Isolated entry audit: boers2005m3h

Verdict: KEEP; active: True; existence: YES; context: SUPPORTS.

## Input entry

```bibtex
@article{boers2005m3h,
  author={Yvo Boers and Hans Driessen},
  title={A multiple model multiple hypothesis filter for {Markovian} switching systems},
  journal={Automatica}, year={2005}, volume={41}, number={4}, pages={709--716},
  doi={10.1016/j.automatica.2004.11.018}
}
```

## Canonical metadata actually retrieved

```json
{
  "title": "A multiple model multiple hypothesis filter for Markovian switching systems",
  "authors": [
    "Yvo Boers",
    "Hans Driessen"
  ],
  "venue": "Automatica",
  "publisher": "Elsevier BV",
  "year": [
    [
      2005,
      4
    ]
  ],
  "volume": "41",
  "issue": "4",
  "pages": "709-716",
  "DOI": "10.1016/j.automatica.2004.11.018",
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
    "value": "10.1016/j.automatica.2004.11.018"
  }
}

## Context assessment

### sections/article_related.tex:39 — SUPPORTS

The Adaptive Matrix CuSum derives sequential identification error/delay
results under specified observation laws \cite{warner2024matrix}.
Multiple-model filtering already propagates conditional state/mode
hypotheses \cite{blom1988imm}. The multiple-model multiple-hypothesis
filter maintains mode-sequence histories and adapts their number through
pruning and merging \cite{boers2005m3h}. Retaining histories or adapting
bank size is therefore not an original principle of our method.
Our pruned history bank uses these ideas,
but its approximate covariances, proposal screen and fitted startup context
do not inherit their general guarantees. The complete procedure evaluated
here makes retained recovery compete with later interventions and reports
timely attribution and alarm burden. These comparisons do not isolate
recovery memory from the other admission and publication rules.

The source explicitly combines pruning and merging, permits variable merging depth, and adapts computational load through a changing hypothesis count.

## Sources and isolation

- [publisher-deposited DOI registry metadata](https://api.crossref.org/works/10.1016%2Fj.automatica.2004.11.018): Record actually fetched during this audit; see per-entry lookup JSON.
- [registered primary publication URL](https://linkinghub.elsevier.com/retrieve/pii/S0005109804003243): URL recorded by Crossref; independent retrieval only if listed below.
- [publisher abstract and method/conclusion excerpts](https://www.sciencedirect.com/science/article/pii/S0005109804003243): The source explicitly combines pruning and merging, permits variable merging depth, and adapts computational load through a changing hypothesis count.

Metadata response: `boers2005m3h.lookup.json`. Contexts were assessed for this entry only; no support was transferred from an unrelated entry in the batch.
This was a fresh collaboration-subagent audit, not the unavailable gpt-5.4 Codex MCP workflow. Exact model identity and cross-model independence were not certified.

## Finding and action

Metadata verified; active context uses supported within the qualifications recorded.

Retain.

## Uncertainty

No unresolved identity/metadata/context discrepancy beyond the global methodology limitations.

Batch traces: .aris/traces/citation-audit/20261101_run01/web_batch05.txt

# Isolated entry audit: blom1988imm

Verdict: KEEP; active: True; existence: YES; context: SUPPORTS.

## Input entry

```bibtex
@article{blom1988imm,
  author = {H. A. P. Blom and Y. Bar-Shalom},
  title = {The Interacting Multiple Model Algorithm for Systems With Markovian Switching Coefficients},
  journal = {IEEE Transactions on Automatic Control},
  volume = {33},
  number = {8},
  pages = {780--783},
  year = {1988},
  doi = {10.1109/9.1299}
}
```

## Canonical metadata actually retrieved

```json
{
  "title": "The interacting multiple model algorithm for systems with Markovian switching coefficients",
  "authors": [
    "H.A.P. Blom",
    "Y. Bar-Shalom"
  ],
  "venue": "IEEE Transactions on Automatic Control",
  "publisher": "Institute of Electrical and Electronics Engineers (IEEE)",
  "year": [
    [
      1988
    ]
  ],
  "volume": "33",
  "issue": "8",
  "pages": "780-783",
  "DOI": "10.1109/9.1299",
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
    "value": "10.1109/9.1299"
  }
}

## Context assessment

### sections/article_related.tex:37 — SUPPORTS

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

The paper develops approximate Bayesian filtering and hypothesis merging for Markovian switching linear systems, supporting the stated multiple-model precedent.

## Sources and isolation

- [publisher-deposited DOI registry metadata](https://api.crossref.org/works/10.1109/9.1299): Record actually fetched during this audit; see per-entry lookup JSON.
- [registered primary publication URL](http://ieeexplore.ieee.org/document/1299/): URL recorded by Crossref; independent retrieval only if listed below.
- [author institution abstract](https://research.tudelft.nl/en/publications/the-interacting-multiple-model-algorithm-for-systems-with-markovi/): The paper develops approximate Bayesian filtering and hypothesis merging for Markovian switching linear systems, supporting the stated multiple-model precedent.

Metadata response: `blom1988imm.lookup.json`. Contexts were assessed for this entry only; no support was transferred from an unrelated entry in the batch.
This was a fresh collaboration-subagent audit, not the unavailable gpt-5.4 Codex MCP workflow. Exact model identity and cross-model independence were not certified.

## Finding and action

Metadata verified; active context uses supported within the qualifications recorded.

Retain.

## Uncertainty

No unresolved identity/metadata/context discrepancy beyond the global methodology limitations.

Batch traces: .aris/traces/citation-audit/20261101_run01/web_batch06.txt, .aris/traces/citation-audit/20261101_run01/web_batch10.txt, .aris/traces/citation-audit/20261101_run01/web_batch12.txt

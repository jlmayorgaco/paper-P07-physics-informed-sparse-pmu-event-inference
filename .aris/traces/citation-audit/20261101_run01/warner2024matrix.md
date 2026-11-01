# Isolated entry audit: warner2024matrix

Verdict: KEEP; active: True; existence: YES; context: SUPPORTS.

## Input entry

```bibtex
@article{warner2024matrix,
  author = {A. Warner and G. Fellouris},
  title = {Sequential Change Diagnosis Revisited and the Adaptive Matrix {CuSum}},
  journal = {Bernoulli},
  volume = {30},
  number = {3},
  pages = {2228--2252},
  year = {2024},
  doi = {10.3150/23-BEJ1671}
}
```

## Canonical metadata actually retrieved

```json
{
  "title": "Sequential change diagnosis revisited and the Adaptive Matrix CuSum",
  "authors": [
    "Austin Warner",
    "Georgios Fellouris"
  ],
  "venue": "Bernoulli",
  "publisher": "Bernoulli Society for Mathematical Statistics and Probability",
  "year": [
    [
      2024,
      8,
      1
    ]
  ],
  "volume": "30",
  "issue": "3",
  "pages": "2228-2252",
  "DOI": "10.3150/23-bej1671",
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
    "value": "10.3150/23-BEJ1671"
  }
}

## Context assessment

### sections/article_related.tex:35 — SUPPORTS

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

The source analyzes sequential change diagnosis with a finite family of post-change laws, unknown onset, error control and delay; the manuscript appropriately withholds transfer of those guarantees to its approximate bank.

## Sources and isolation

- [publisher-deposited DOI registry metadata](https://api.crossref.org/works/10.3150/23-BEJ1671): Record actually fetched during this audit; see per-entry lookup JSON.
- [registered primary publication URL](https://projecteuclid.org/journals/bernoulli/volume-30/issue-3/Sequential-change-diagnosis-revisited-and-the-Adaptive-Matrix-CuSum/10.3150/23-BEJ1671.full): URL recorded by Crossref; independent retrieval only if listed below.
- [publisher original-paper abstract](https://www.imstat.org/publications/bej/bej_30_3/bej_30_3.pdf): The source analyzes sequential change diagnosis with a finite family of post-change laws, unknown onset, error control and delay; the manuscript appropriately withholds transfer of those guarantees to its approximate bank.

Metadata response: `warner2024matrix.lookup.json`. Contexts were assessed for this entry only; no support was transferred from an unrelated entry in the batch.
This was a fresh collaboration-subagent audit, not the unavailable gpt-5.4 Codex MCP workflow. Exact model identity and cross-model independence were not certified.

## Finding and action

Metadata verified; active context uses supported within the qualifications recorded.

Retain.

## Uncertainty

No unresolved identity/metadata/context discrepancy beyond the global methodology limitations.

Batch traces: .aris/traces/citation-audit/20261101_run01/web_batch01.txt

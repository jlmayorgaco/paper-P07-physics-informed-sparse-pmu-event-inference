# Isolated entry audit: sarkka2013bayesian

Verdict: KEEP; active: True; existence: YES; context: SUPPORTS.

## Input entry

```bibtex
@book{sarkka2013bayesian,
  author    = {S. S{\"a}rkk{\"a}},
  title     = {Bayesian Filtering and Smoothing},
  publisher = {Cambridge University Press},
  address   = {Cambridge, U.K.},
  year      = {2013},
  doi       = {10.1017/CBO9781139344203},
  isbn      = {978-1-107-03065-7}
}
```

## Canonical metadata actually retrieved

```json
{
  "title": "Bayesian Filtering and Smoothing",
  "authors": [
    "Simo Särkkä"
  ],
  "venue": "Cambridge University Press",
  "publisher": "Cambridge University Press",
  "year": [
    [
      2013,
      9,
      5
    ]
  ],
  "volume": null,
  "issue": null,
  "pages": null,
  "DOI": "10.1017/cbo9781139344203",
  "ISBN": [
    "9781107030657",
    "9781139344203",
    "9781107619289"
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
    "value": "10.1017/CBO9781139344203"
  }
}

## Context assessment

### supplement/appendix_causal_walkthrough.tex:20 — SUPPORTS

The article retains the physical model, the defining evidence integral,
the recovery mechanism, the decision outputs and decisive results. This
supplement supplies the intermediate calculations. The Historical Technical
Notes develop functional observability, nuisance-profiled information and
source ambiguity, and distinguish the implemented batch estimator $\mathcal E_{\mathrm B}$ from
the proposed joint estimator $\mathcal E_{\mathrm J}$. Neither should be
silently substituted for the causal history bank, archived as R11.
The conditional Gaussian updates use standard filtering identities
\cite{sarkka2013bayesian}; the derivation below specifies their role and
the approximations made by the implemented bank.

The first edition covers Bayesian filtering, Gaussian filtering and smoothing. It supports the cited standard conditional Gaussian filtering identities; citing this edition is valid even though a second edition now exists.

## Sources and isolation

- [publisher-deposited DOI registry metadata](https://api.crossref.org/works/10.1017/CBO9781139344203): Record actually fetched during this audit; see per-entry lookup JSON.
- [registered primary publication URL](https://www.cambridge.org/core/product/identifier/9781139344203/type/book): URL recorded by Crossref; independent retrieval only if listed below.
- [publisher Gaussian-filtering chapter record; author edition listing and registry description](https://www.cambridge.org/core/product/97BF7ECDEA1C808257A0CBDB21A711A6): The first edition covers Bayesian filtering, Gaussian filtering and smoothing. It supports the cited standard conditional Gaussian filtering identities; citing this edition is valid even though a second edition now exists.

Metadata response: `sarkka2013bayesian.lookup.json`. Contexts were assessed for this entry only; no support was transferred from an unrelated entry in the batch.
This was a fresh collaboration-subagent audit, not the unavailable gpt-5.4 Codex MCP workflow. Exact model identity and cross-model independence were not certified.

## Finding and action

Metadata verified; active context uses supported within the qualifications recorded.

Retain.

## Uncertainty

No unresolved identity/metadata/context discrepancy beyond the global methodology limitations.

Batch traces: .aris/traces/citation-audit/20261101_run01/web_batch09.txt

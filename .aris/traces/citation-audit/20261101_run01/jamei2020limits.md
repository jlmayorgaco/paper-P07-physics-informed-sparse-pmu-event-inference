# Isolated entry audit: jamei2020limits

Verdict: KEEP; active: True; existence: YES; context: SUPPORTS.

## Input entry

```bibtex
@article{jamei2020limits,
  author  = {M. Jamei and R. Ramakrishna and T. Tesfay and R. Gentz and C. Roberts and A. Scaglione and S. Peisert},
  title   = {Phasor Measurement Units Optimal Placement and Performance Limits for Fault Localization},
  journal = {IEEE Journal on Selected Areas in Communications},
  volume  = {38},
  number  = {1},
  pages   = {180--192},
  year    = {2020},
  doi     = {10.1109/JSAC.2019.2951971}
}
```

## Canonical metadata actually retrieved

```json
{
  "title": "Phasor Measurement Units Optimal Placement and Performance Limits for Fault Localization",
  "authors": [
    "Mahdi Jamei",
    "Raksha Ramakrishna",
    "Teklemariam Tesfay",
    "Reinhard Gentz",
    "Ciaran Roberts",
    "Anna Scaglione",
    "Sean Peisert"
  ],
  "venue": "IEEE Journal on Selected Areas in Communications",
  "publisher": "Institute of Electrical and Electronics Engineers (IEEE)",
  "year": [
    [
      2020,
      1
    ]
  ],
  "volume": "38",
  "issue": "1",
  "pages": "180-192",
  "DOI": "10.1109/jsac.2019.2951971",
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
    "value": "10.1109/JSAC.2019.2951971"
  }
}

## Context assessment

### sections/article_related.tex:22 — SUPPORTS

Physical hypotheses support outage inference from phasor angles
\cite{tate2008outage}, Bayesian inference with uncertain states
\cite{zhao2014outages}, and sequential detection under stochastic operation
\cite{chen2016quickest,rovatsos2017outage}. Anguluri \emph{et al.} recover
sparse forcing locations, inputs and an unknown initial state using group
LASSO for linear dynamics \cite{anguluri2023group}. These are precedents
for source recovery; group LASSO is not an executed comparator in our
frozen campaign. Sensor placement also affects source distinguishability
\cite{jamei2020limits,conte2023fault,yildiz2025sparse}.\AIDraftingCredit{}

The source analyzes KL separation of fault hypotheses with insufficient PMUs and derives placement for localization resolution, directly supporting the placement/discrimination claim.

## Sources and isolation

- [publisher-deposited DOI registry metadata](https://api.crossref.org/works/10.1109%2FJSAC.2019.2951971): Record actually fetched during this audit; see per-entry lookup JSON.
- [registered primary publication URL](https://ieeexplore.ieee.org/document/8892526/): URL recorded by Crossref; independent retrieval only if listed below.
- [author-hosted original paper](https://www.cs.ucdavis.edu/~peisert/research/2020-JSAC-PMULocalization): The source analyzes KL separation of fault hypotheses with insufficient PMUs and derives placement for localization resolution, directly supporting the placement/discrimination claim.

Metadata response: `jamei2020limits.lookup.json`. Contexts were assessed for this entry only; no support was transferred from an unrelated entry in the batch.
This was a fresh collaboration-subagent audit, not the unavailable gpt-5.4 Codex MCP workflow. Exact model identity and cross-model independence were not certified.

## Finding and action

Metadata verified; active context uses supported within the qualifications recorded.

Retain.

## Uncertainty

No unresolved identity/metadata/context discrepancy beyond the global methodology limitations.

Batch traces: .aris/traces/citation-audit/20261101_run01/web_batch06.txt

# Isolated entry audit: anguluri2023group

Verdict: KEEP; active: True; existence: YES; context: SUPPORTS.

## Input entry

```bibtex
@article{anguluri2023group,
  author  = {R. Anguluri and O. Kosut and L. Sankar},
  title   = {Localization and Estimation of Unknown Forced Inputs: A Group {LASSO} Approach},
  journal = {IEEE Transactions on Control of Network Systems},
  volume  = {10},
  number  = {4},
  pages   = {1997--2009},
  year    = {2023},
  doi     = {10.1109/TCNS.2023.3258627}
}
```

## Canonical metadata actually retrieved

```json
{
  "title": "Localization and Estimation of Unknown Forced Inputs: A Group LASSO Approach",
  "authors": [
    "Rajasekhar Anguluri",
    "Oliver Kosut",
    "Lalitha Sankar"
  ],
  "venue": "IEEE Transactions on Control of Network Systems",
  "publisher": "Institute of Electrical and Electronics Engineers (IEEE)",
  "year": [
    [
      2023,
      12
    ]
  ],
  "volume": "10",
  "issue": "4",
  "pages": "1997-2009",
  "DOI": "10.1109/tcns.2023.3258627",
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
    "value": "10.1109/TCNS.2023.3258627"
  }
}

## Context assessment

### sections/article_related.tex:19 — SUPPORTS

Physical hypotheses support outage inference from phasor angles
\cite{tate2008outage}, Bayesian inference with uncertain states
\cite{zhao2014outages}, and sequential detection under stochastic operation
\cite{chen2016quickest,rovatsos2017outage}. Anguluri \emph{et al.} recover
sparse forcing locations, inputs and an unknown initial state using group
LASSO for linear dynamics \cite{anguluri2023group}. These are precedents
for source recovery; group LASSO is not an executed comparator in our
frozen campaign. Sensor placement also affects source distinguishability
\cite{jamei2020limits,conte2023fault,yildiz2025sparse}.\AIDraftingCredit{}

The abstract explicitly recovers sparse input locations, forcing signals and an unknown initial state with group LASSO for linear dynamics. The journal author order differs from the preprint: the bibliography correctly follows the journal record.

## Sources and isolation

- [publisher-deposited DOI registry metadata](https://api.crossref.org/works/10.1109/TCNS.2023.3258627): Record actually fetched during this audit; see per-entry lookup JSON.
- [registered primary publication URL](https://ieeexplore.ieee.org/document/10075525/): URL recorded by Crossref; independent retrieval only if listed below.
- [author preprint abstract; publisher-deposited metadata](https://arxiv.org/abs/2201.07907): The abstract explicitly recovers sparse input locations, forcing signals and an unknown initial state with group LASSO for linear dynamics. The journal author order differs from the preprint: the bibliography correctly follows the journal record.

Metadata response: `anguluri2023group.lookup.json`. Contexts were assessed for this entry only; no support was transferred from an unrelated entry in the batch.
This was a fresh collaboration-subagent audit, not the unavailable gpt-5.4 Codex MCP workflow. Exact model identity and cross-model independence were not certified.

## Finding and action

Metadata verified; active context uses supported within the qualifications recorded.

Retain.

## Uncertainty

No unresolved identity/metadata/context discrepancy beyond the global methodology limitations.

Batch traces: .aris/traces/citation-audit/20261101_run01/web_batch01.txt

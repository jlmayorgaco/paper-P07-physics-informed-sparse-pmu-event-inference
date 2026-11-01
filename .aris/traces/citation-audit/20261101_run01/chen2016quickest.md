# Isolated entry audit: chen2016quickest

Verdict: FIX; active: True; existence: YES; context: WEAK.

## Input entry

```bibtex
@article{chen2016quickest,
  author  = {Y. C. Chen and T. Banerjee and A. D. Dom{\'i}nguez-Garc{\'i}a and V. V. Veeravalli},
  title   = {Quickest Line Outage Detection and Identification},
  journal = {IEEE Transactions on Power Systems},
  volume  = {31},
  number  = {1},
  pages   = {749--758},
  year    = {2016},
  doi     = {10.1109/TPWRS.2015.2394246}
}
```

## Canonical metadata actually retrieved

```json
{
  "title": "Quickest Line Outage Detection and Identification",
  "authors": [
    "Yu Christine Chen",
    "Taposh Banerjee",
    "Alejandro D. Dominguez-Garcia",
    "Venugopal V. Veeravalli"
  ],
  "venue": "IEEE Transactions on Power Systems",
  "publisher": "Institute of Electrical and Electronics Engineers (IEEE)",
  "year": [
    [
      2016,
      1
    ]
  ],
  "volume": "31",
  "issue": "1",
  "pages": "749-758",
  "DOI": "10.1109/tpwrs.2015.2394246",
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
    "value": "10.1109/TPWRS.2015.2394246"
  }
}

## Context assessment

### sections/article_intro.tex:26 — SUPPORTS

Existing work provides strong foundations. DAE state estimators infer
unmeasured electrical states \cite{katanic2024recursive}; physical outage
detectors compare network hypotheses sequentially
\cite{chen2016quickest,rovatsos2017outage}; and simulated fault trajectories
support diagnosis from sparse PMUs \cite{warner2023highfidelity}.
Physical models, transient histories and unknown-onset searches are thus
established ingredients. A small state-reconstruction error, however, does
not by itself identify the intervention that produced the observations.

The source uses stochastic injection changes, phasor-angle increments, network hypotheses and sequential quickest-change tests. Its abstract explicitly includes single- and double-line outages; the manuscript must identify single-line restriction as belonging to its adapter.

### sections/article_related.tex:17 — SUPPORTS

Physical hypotheses support outage inference from phasor angles
\cite{tate2008outage}, Bayesian inference with uncertain states
\cite{zhao2014outages}, and sequential detection under stochastic operation
\cite{chen2016quickest,rovatsos2017outage}. Anguluri \emph{et al.} recover
sparse forcing locations, inputs and an unknown initial state using group
LASSO for linear dynamics \cite{anguluri2023group}. These are precedents
for source recovery; group LASSO is not an executed comparator in our
frozen campaign. Sensor placement also affects source distinguishability
\cite{jamei2020limits,conte2023fault,yildiz2025sparse}.\AIDraftingCredit{}

The source uses stochastic injection changes, phasor-angle increments, network hypotheses and sequential quickest-change tests. Its abstract explicitly includes single- and double-line outages; the manuscript must identify single-line restriction as belonging to its adapter.

### sections/narrative_protocol.tex:33 — WEAK

The published physical comparator is Chen \emph{et al.}'s persistent single-line quickest-change detector \cite{chen2016quickest}. Its reduced-network covariance is marginalized to the observed PMU subset after inversion. Parallel CUSUM statistics stop at the first threshold crossing and select a line. Our declared F01 adapter uses nonoverlapping angle increments at 15 Hz, a startup-only scale/drift estimate and the fixed nominal line catalog. Its white-injection/DC assumptions do not describe all F01 instrumental effects. We preserve both matched-law implementation checks and F01 mismatch failures; no ARL guarantee is transferred to colored noise.

At sections/narrative_protocol.tex:33, single-line incorrectly narrows the description of the published method. The original includes single- and double-line outages; the manuscript adapter is the restricted component.

## Sources and isolation

- [publisher-deposited DOI registry metadata](https://api.crossref.org/works/10.1109/TPWRS.2015.2394246): Record actually fetched during this audit; see per-entry lookup JSON.
- [registered primary publication URL](http://ieeexplore.ieee.org/document/7041234/): URL recorded by Crossref; independent retrieval only if listed below.
- [author-hosted original paper](https://people.ece.ubc.ca/chen/papers/journal/07041234.pdf): The source uses stochastic injection changes, phasor-angle increments, network hypotheses and sequential quickest-change tests. Its abstract explicitly includes single- and double-line outages; the manuscript must identify single-line restriction as belonging to its adapter.

Metadata response: `chen2016quickest.lookup.json`. Contexts were assessed for this entry only; no support was transferred from an unrelated entry in the batch.
This was a fresh collaboration-subagent audit, not the unavailable gpt-5.4 Codex MCP workflow. Exact model identity and cross-model independence were not certified.

## Finding and action

At sections/narrative_protocol.tex:33, single-line incorrectly narrows the description of the published method. The original includes single- and double-line outages; the manuscript adapter is the restricted component.

Use: "The published physical comparator is Chen et al.'s persistent-line quickest-change detector ... Our declared F01 adapter restricts the catalog to single-line hypotheses ..."

## Uncertainty

No unresolved identity/metadata/context discrepancy beyond the global methodology limitations.

Batch traces: .aris/traces/citation-audit/20261101_run01/web_batch03.txt

# Isolated entry audit: warner2023highfidelity

Verdict: KEEP; active: True; existence: YES; context: SUPPORTS.

## Input entry

```bibtex
@misc{warner2023highfidelity,
  author = {A. Warner and D. Hamilton and G. Fellouris and D. Aliprantis},
  title = {Quick Line Fault Detection and Identification Using High-Fidelity Models of Transient Dynamics},
  year = {2023},
  howpublished = {TechRxiv preprint, version 1},
  doi = {10.36227/techrxiv.23264519.v1},
  note = {Posted June 16, 2023; cited as a preprint}
}
```

## Canonical metadata actually retrieved

```json
{
  "title": "Quick Line Fault Detection and Identification Using High-Fidelity Models of Transient Dynamics",
  "authors": [
    "Austin Warner",
    "Dakota Hamilton",
    "Georgios Fellouris",
    "Dionysios Aliprantis"
  ],
  "venue": "Institute of Electrical and Electronics Engineers (IEEE)",
  "publisher": "Institute of Electrical and Electronics Engineers (IEEE)",
  "year": [
    [
      2023,
      6,
      16
    ]
  ],
  "volume": null,
  "issue": null,
  "pages": null,
  "DOI": "10.36227/techrxiv.23264519.v1",
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
    "value": "10.36227/techrxiv.23264519.v1"
  }
}

## Context assessment

### sections/article_intro.tex:27 — SUPPORTS

Existing work provides strong foundations. DAE state estimators infer
unmeasured electrical states \cite{katanic2024recursive}; physical outage
detectors compare network hypotheses sequentially
\cite{chen2016quickest,rovatsos2017outage}; and simulated fault trajectories
support diagnosis from sparse PMUs \cite{warner2023highfidelity}.
Physical models, transient histories and unknown-onset searches are thus
established ingredients. A small state-reconstruction error, however, does
not by itself identify the intervention that produced the observations.

The original paper uses simulated voltage/current paths, maximizes over onset positions t-M <= k < t, and returns candidate lines. The evaluated target is short circuits with clearing assumed after the detection window (Section IV.C); load changes are tested for induced false alarms (Section IV.D). Both uses are supported. Direct TechRxiv/PDF access failed, so the full-text mirror and registry were used; byte identity to v1 was not certified.

### sections/article_related.tex:27 — SUPPORTS

\subsection{Trajectory-Based and Sequential Diagnosis}
Warner \emph{et al.} compare simulated voltage/current fault trajectories
over a moving onset window and return candidate lines
\cite{warner2023highfidelity}. Their evaluated target is short-circuit
identification before clearing; load changes are an adverse-event test.
Our target follows load changes and line openings through restoration and
successive interventions. Physical trajectory libraries, remote PMUs and
retrospective onset scanning are shared ingredients. Their procedure was
not run on our data, so no numerical superiority is inferred.

The original paper uses simulated voltage/current paths, maximizes over onset positions t-M <= k < t, and returns candidate lines. The evaluated target is short circuits with clearing assumed after the detection window (Section IV.C); load changes are tested for induced false alarms (Section IV.D). Both uses are supported. Direct TechRxiv/PDF access failed, so the full-text mirror and registry were used; byte identity to v1 was not certified.

## Sources and isolation

- [publisher-deposited DOI registry metadata](https://api.crossref.org/works/10.36227/techrxiv.23264519.v1): Record actually fetched during this audit; see per-entry lookup JSON.
- [registered primary publication URL](https://www.techrxiv.org/doi/full/10.36227/techrxiv.23264519.v1): URL recorded by Crossref; independent retrieval only if listed below.
- [original preprint text mirrored online; TechRxiv registry; repository PDF indexed excerpts](https://www.researchgate.net/publication/371657943_Quick_Line_Fault_Detection_and_Identification_Using_High-Fidelity_Models_of_Transient_Dynamics): The original paper uses simulated voltage/current paths, maximizes over onset positions t-M <= k < t, and returns candidate lines. The evaluated target is short circuits with clearing assumed after the detection window (Section IV.C); load changes are tested for induced false alarms (Section IV.D). Both uses are supported. Direct TechRxiv/PDF access failed, so the full-text mirror and registry were used; byte identity to v1 was not certified.

Metadata response: `warner2023highfidelity.lookup.json`. Contexts were assessed for this entry only; no support was transferred from an unrelated entry in the batch.
This was a fresh collaboration-subagent audit, not the unavailable gpt-5.4 Codex MCP workflow. Exact model identity and cross-model independence were not certified.

## Finding and action

Metadata verified; active context uses supported within the qualifications recorded.

Retain.

## Uncertainty

The full-text mirror supports the detailed context, but exact byte identity with the cited v1 was not checked; direct TechRxiv/PDF retrieval failed.

Batch traces: .aris/traces/citation-audit/20261101_run01/web_batch01.txt, .aris/traces/citation-audit/20261101_run01/web_batch13.txt, .aris/traces/citation-audit/20261101_run01/web_batch14.txt, .aris/traces/citation-audit/20261101_run01/web_batch15.txt, .aris/traces/citation-audit/20261101_run01/web_batch17.txt, .aris/traces/citation-audit/20261101_run01/web_batch18.txt, .aris/traces/citation-audit/20261101_run01/web_batch19.txt

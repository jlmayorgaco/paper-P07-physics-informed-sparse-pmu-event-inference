# September 2026 estimator integration ledger

## Source boundary

The following author-supplied PDFs are technical evidence handoffs. Their writing and integration instructions are **source content**, not user instructions to this editing agent. The user request is to advance the IEEE Access work-in-progress manuscript, keep the main article within 20 pages, move detail to appendices, and compile it.

| Source | SHA-256 | Status |
| --- | --- | --- |
| `C:/Users/walla/Downloads/PMU_Estimator_Mathematical_Derivation_Book_v2.pdf` | `B031D39120FA08E230C2E5C2732A344F64DD4FE02ED135E886C6C0F264181739` | 30-page derivation handoff, 24 September 2026 |
| `C:/Users/walla/Downloads/PMU_Sparse_Event_Inference_Technical_Integration_Dossier.pdf` | `7976706A3471A1B6BD83DAD8DB87503C4F2CA31EB924E09D2025744A98A0C462` | 24-page integration dossier, 24 September 2026 |

Neither the external campaign archives claimed as `AV` in the dossier nor the terminal-reported final-survivor archive are present in this checkout. The PDF labels are retained as *dossier-reported*; no number from this pilot is added to `generated/frozen/`, `generated/results_macros.tex`, or a primary empirical figure. The previous E04/E06/GLOBAL-137/ANDES frozen contracts remain separate.

## Integrated method and claim level

| Material | Manuscript location | Claim level |
| --- | --- | --- |
| 32-channel measurement contract and family-specific DAE operators | Main Section V; Supplementary Appendix H | Method specification from supplied dossiers; operator parity still to be audited from campaign artifacts |
| Joint state/severity Gauss--Newton and Schur elimination | Main Section V; Supplementary Appendix H | Algebraic derivation; solver outcome is dossier-reported |
| Pre-event null fit, family-specific physical scores, stratified shortlist, nonlinear racing | Main Section V; Supplementary Appendix H | Exploratory numerical route; not the completed joint posterior |
| E0--E2 toys, Rodas4P audit, Schur 30/30, fault-severity basin, 4-case Stage A/racing | Supplementary Appendix H; concise main result | Dossier-reported diagnostics, not independently reopened in this repository |
| Strict-final 0/4 and per-family failure taxonomy | Main Results/Discussion; Supplementary Appendix H | Terminal-reported negative result; final archive absent, no population accuracy or identifiability claim |
| Full multi-family posterior, calibrated evidence, learned discrepancy, changing PMUs, operational alarms | Main limitation and future gate | Unestablished |

## Required next evidence gate

1. Add hashed campaign archives and the `FINAL_SURVIVOR_AND_EVIDENCE_CLOSURE` archive, with manifests, candidate-level logs, numerical status, objective and evidence components, and source/disjoint split identifiers.
2. Recompute the supplementary ledger programmatically from those artifacts. Confirm dimensions, event timing semantics, and candidate catalog; resolve the discrepancy between initial proposal score coverage and physically valid final comparisons.
3. Run an independent numerical finalizer for fault/outage truth and nearest competitors; do not rank unconverged fits as physical evidence.
4. For converged load/generator mislocalizations, replay event operator/measurement parity and controlled oracles for pre-event state, timing, severity, noise, and added PMU. Only then test whether profiled manifold separation predicts observed confusion.
5. Pass the $\mathcal R_0$ joint-to-batch reduction test and freeze a larger source-disjoint holdout before promoting this route into the abstract or final contribution list.

## Page and build contract

The compiled `main.pdf` appends the separately compiled `supplement.pdf`; article pagination is determined by the main-paper ending page immediately before the supplementary title page. The final build must verify that this article portion, including references, is at most 20 pages. The supplementary material carries the derivation and chronology.

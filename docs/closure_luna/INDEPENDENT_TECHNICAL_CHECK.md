# Independent technical check — P07 closure

Snapshot: 2026-11-02, approximately 16:53 America/Bogota. Read-only inspection of the P07 plan, current audit, both repository states, C01 seals, and A01 process/runtime status. No simulation or paper build was started by this audit. No result-level A01 outputs were inspected.

## State and decision

- **C01 is complete and integrated.** `run/COMPLETE.json` says `COMPLETE_WITH_ALL_INTENDED_DENOMINATORS`, `models_retuned: false`; `RECORD_PROGRESS.json` reports 342/342 intended observed records through S342. The confirmatory record count is 171 physical trajectories and 342 observed records. `PAPER_UPDATED.json` says outputs imported and PDF compiled, while submission remains unauthorized. Preserve the failures and full denominators in its result ledger; no repeat is indicated.
- **A01 is still running.** `run/PROGRESS.json` reports inference task 28/72, S173 / PROFILE_MEMORY. Controller PID 36740 is the original Anaconda command `python.exe -B .../PAPER_ABLATION_A01/pipeline.py run`; child worker PID 51704 runs `worker.py S173 PROFILE_MEMORY`. The current log progressed from report 1200 to 1500 of 3601 between observations. No A01 COMPLETE, BLOCKER, or PAPER_UPDATED stamp was present at inspection.
- A01 remains frozen as a post hoc four-arm ablation of 24 C01 records (72 new inferences, with the sealed baseline copy), not an independent confirmation. Retain its predeclared denominators, failures, and distinction between normalized scores and calibrated probabilities. Do not interpret partial predictions or use them to alter prose/thresholds.
- **An isolated light PDFLaTeX preview is allowed** if its input/output copy is separate and the command does not invoke bank preparation, large renders, or scripts that write to absolute active-paper paths. A01's automatic final import/build still owns the active article sections, tables, figures and PDFs, so do not compile or overwrite those paths. The 4.24 GB free of 31.54 GB and A01 worker's ~1.34 GB working/private memory make deferring heavy renders or builds a precautionary recommendation, not a project rule. Recheck available memory and process state before any heavier job.

## Runtime estimate (not a completion promise)

Twenty-seven A01 inference timing records have a mean of 352.4 s and median of 337.7 s (range 236.6–558.9 s). At task 28/72, roughly 44 inference tasks remain after the current one. This projects about 4.3 hours of inference time at the observed mean; allowing for the remaining per-record cache reconstructions and scheduling variance, use **roughly 4–5 hours to finish inference**, then add an unestimated duration for bootstrap/evaluation, artifact import and PDF compilation. This is a throughput estimate only, not an assessment of partial outcomes. The plan's original ~12-hour figure was a pre-run estimate and should not replace the observed runtime estimate.

## Git and safe publication

### P07 repository

- Working tree: `paper-P07-physics-informed-sparse-pmu-event-inference`, branch `main`, HEAD `a26289c`, tracking `origin/main`; initial status was clean. The only later untracked path observed was the shared `docs/closure_luna/` work area.
- The paper repository's AGENTS.md requires all work directly on `main`, and protects the event figure bytes and the IEEE-39 single-line figure, including their presence in the main PDF. The user's newer instruction authorizes pushing the completed P07 changes to `main`; apply it only to this P07 repository.
- GitHub API metadata reports this repository as `private: false`; the remote is publicly visible. The user has authorized publishing the intended P07 deliverables, including the final PDF, on `main`; no additional approval is needed for those deliverables. The connected GitHub tools include read access plus blob/tree/commit/ref operations, but use the local Git CLI for the publication so tracked history and binary files are preserved. Recheck the remote `main` SHA before pushing. Do not create a PR/branch contrary to P07's repository instructions.

### Science repository

- Working tree is on `exp/T2_static_vs_dynamic`, with modified `README.md` and `src/simulation/transient_scenarios.py`, and many untracked research, experiment, data, and generated paths. It has `origin`, but the current experimental branch has no upstream marker. Its state is unrelated to the requested P07 delivery.
- **Do not stage, commit, or push from the science repository for P07.** In particular, avoid `git add -A`, archive/cache/data trees, experiment run products, or files outside the P07 checkout.

### Final integration allowlist

1. Stage the reviewed P07 manuscript source, required reproducible source/metadata, article figures/tables, and intended final PDF; these P07 deliverables are authorized for `main`. Keep coauthor-specific review bundles and author-decision material local by minimization unless they are explicitly part of the intended P07 public deliverables. This is a handling recommendation, not a publication restriction.
2. Stage exact paths; inspect `git diff --cached --name-status` and `--stat`. Exclude auxiliary build files (`.aux`, `.blg`, `.fls`, `.log`), caches, temp folders, local review notes, backup/staging outputs, raw simulation artifacts, and credentials/private author material.
3. Before commit/push, recheck branch and remote tracking, inspect the staged diff, confirm protected-figure hashes and the PDF inclusion check, then fetch/check remote `main` to prevent overwriting concurrent work. Push only the reviewed P07 commit to `origin main`; do not publish either repository wholesale.
4. Because A01 imports automatically, do not copy staged article files into active paths or compile until A01 has completed evaluation/import and no A01 importer/build process remains. Then compare the automatic import with reviewed changes and run the paper's required protected-figure checks on the final PDF.

## Scope reminders for closure

The current plan and strict audit agree on a finite P07 closure: use the finished C01 denominator, wait for all A01 arms and preserve null/negative results, tighten claims to attribution within the evaluated catalog, explain the executed method/score-to-decision path, state operating-map limitations and unmatched alarm/restoration denominators, review citations/figures, and list author decisions separately from technical readiness. Do not turn the audit's conditional recommendations into new experiments by default. Do not open RAW0002, retune C01, edit baselines, or present A01 as an independent confirmation.


## Final independent preview check (2026-11-02, approximately 17:12 America/Bogota)

- Read-only final preview: `tmp/p07_closure_preview_v6/main.pdf`, 17 pages, SHA-256 `47B17D4A2419BF3166D48B2991C88D47B3178078245E5397BA288EDE6D50B0EB` (17:11:22 local). The page-13 render at 120 dpi shows all five columns and values of both restoration and cost tables within the column. The PDF text extraction has no unresolved `??` references. The Yang et al. bibliography entry renders an arXiv identifier; the staged BibTeX uses `arXiv:2107.06754 [eess.SY]`.
- Method check: the staged article defines the admitted set per network hypothesis as non-null histories plus null, and normalizes current report scores over that set exactly once. It describes birth proposals as replaying the prior suffix and replacing the prior no-event suffix likelihood before scoring the current report. It explicitly limits this to the implementation's admitted/pruned history bank, not a complete Markov transition or calibrated posterior. No source-level contradiction found in the inspected formula/text.
- Scope/metric check: abstract and restoration section call the restoration comparison posthoc and dependent, distinguish omissions/missing restoration values from open episodes, keep denominators, and state the limitations on external validation and real-time operation. C11 points to the specific current P07 audit and says RAW0002 remains unopened. These are bounded claims; do not add performance numbers or call the retrospective comparisons independent confirmation.
- Current repository snapshot: P07 remains `main...origin/main`; its untracked paths include `closure_compute_cost.tex`, `closure_restoration.tex`, and `docs/closure_luna/`. Science remains on `exp/T2_static_vs_dynamic`, dirty and unrelated. The P07 GitHub remote is `https://github.com/jlmayorgaco/paper-P07-physics-informed-sparse-pmu-event-inference.git`; `gh repo view` reports default branch `main` and `private:false`. The user has authorized pushing the intended P07 deliverables, but this audit performed no staging, commit, or push.
- A01 status refreshed read-only: controller PID 36740 is still the original Anaconda `pipeline.py run`; child PID 25536 is the worker. `PROGRESS.json` is now inference task 31/72, S121 / PROFILE_MEMORY. Using the previously observed 27-run mean of 352.4 s, about 41 inference tasks imply ~4.0 hours at that mean; this excludes uncertainty in cache/scheduling and unestimated evaluation, final import and PDF build. This is an estimate, not a prediction of completion. No partial result values were read or used.

### Integration recommendation

Once the active A01 import/evaluation and build are complete, compare the automatic import with the reviewed source and inspect an exact-path staged diff. Stage an explicit allowlist of the intended manuscript `.tex` inputs, bibliography, figures/tables required by those inputs, reproducibility metadata/scripts intended for release, and final `main.pdf` plus its supplement PDF if the final build supplies them. Include intended P07 closure documentation only after excluding coauthor-specific bundles and local review/backup/staging material. Exclude `tmp/`, `docs/closure_luna/staging/`, preview PDFs/renders/logs, auxiliary TeX files, raw experiment outputs, and all science-repository paths. Use Git CLI in the P07 checkout, check `git diff --cached --name-status` and `--stat`, verify protected-figure checks on the final active PDF, fetch and compare `origin/main`, then push only the reviewed P07 commit to `origin main`. This check does not authorize an indiscriminate `git add -A`.

## Superseding editorial rebuild check (2026-11-02, approximately 17:21 America/Bogota)

The earlier 17-page preview hash recorded above is **historical and superseded**; it is not the current candidate. Read-only verification of the newly reported files found:

- `tmp/p07_closure_preview_v6/main.pdf`: SHA-256 `5A2B5C9E082797F435D001BD70DAECAC229992801E7DA852C0B98650B6AA45E4`, 18 pages.
- `tmp/p07_closure_preview_v6/supplement.pdf`: SHA-256 `F43B6902AB7BB5303499A8E611574674EC9C3142774C2D8BCE1A0FFCBF84FC33`, 16 pages.
- Text extraction from both PDFs has no literal `??`. Visual spot-check of current supplied PNGs shows protected event Figure 2 still on p. 5 and the IEEE-39 unifilar on p. 6; the equation block is readable. Page 13 shows both restoration/cost tables complete and their columns visible. Supplement p. 6 shows the measurement contract; p. 16 says the controlled-component outputs are pending. These observations do not certify the current main PDF as final.
- **Blocking assembly defect:** the current main PDF contains the closure-restoration section, figure, and two tables twice. `staging/main.tex` already inputs `sections/article_closure_results` after `08c_c01_confirmatory`; `staging/scripts/prepare_preview.py` also inserts that same input after the same anchor. As compiled, one copy appears on p. 13 as Tables 6–7 and another on p. 15 as Tables 8–9. `main.aux` contains duplicate labels for `sec:closure-results`, `fig:closure-restoration`, `tab:closure-restoration`, and `tab:closure-compute-cost`; `main.log` reports each as multiply defined. The p. 13 text consequently says “Table 9” while the visible cost-table caption is “TABLE 7.” Do not use/publish this main PDF until the duplicate inclusion is removed and the resulting file is independently checked. This is the only concrete blocker found in this light audit; no edits or rebuilds were performed here.

## Corrected assembly recheck (2026-11-02, approximately 17:23 America/Bogota)

The prior 18-page file with SHA `5A2B5C9E...B6AA45E4` is superseded by the corrected preview below; its duplicated inclusion was the blocker documented above. The currently inspected files are:

- Main: `tmp/p07_closure_preview_v6/main.pdf`, SHA-256 `BF97A5D0BF48E0CCD2807DE3EE67A4672BE0185B5077E536FF57283B71AC5B95`, 18 pages.
- Supplement: `tmp/p07_closure_preview_v6/supplement.pdf`, SHA-256 `F43B6902AB7BB5303499A8E611574674EC9C3142774C2D8BCE1A0FFCBF84FC33`, 16 pages.

The corrected main PDF has one closure section, one Figure 11, Table 6 once and Table 7 once; the cited cost table is now Table 7, matching its caption. The relevant four labels occur once in `main.aux`; the log has no multiply-defined, unresolved-label or rerun-reference warning, and text extraction has zero `??`. I inspected the updated p. 13 and p. 15 PNGs: both tables fit; the restoration figure is present once as a float on p. 15, without duplicating the section. Supplement text extraction has zero `??`. No new blocker was found in this light audit. This only verifies the identified assembly issue and sampled layout; it is not a general proof or a replacement for the final active-path/protected-figure checks after A01 import.


## Superseding final preview checkpoint (2026-11-02T17:24:16-05:00)

The earlier 17-page preview hash above was superseded after an assembly defect was found: closure restoration/cost content was included twice. The duplicate input was removed, the preview builder gained a single-input/idempotence guard, and the isolated article was rebuilt. Current article SHA-256: `BF97A5D0BF48E0CCD2807DE3EE67A4672BE0185B5077E536FF57283B71AC5B95` (18 pages); supplement SHA-256: `F43B6902AB7BB5303499A8E611574674EC9C3142774C2D8BCE1A0FFCBF84FC33` (16 pages). Current preview has no duplicate closure labels, unresolved references, or visible internal run aliases.

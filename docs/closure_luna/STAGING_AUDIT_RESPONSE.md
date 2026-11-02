# Staging audit response

Updated automatically: 2026-11-02T17:25:44-05:00 (America/Bogota).

- Corrected the within-hypothesis history-mass normalization so the null is counted once; separated within-network history masses from outer network weights and described retrospective-birth suffix replacement without claiming a full Markov transition matrix.
- Fixed TeX row terminators and compacted the restoration/cost tables until all columns and values were visible.
- Replaced the cross-document numbered supplement reference with a plain textual reference; final article text has no `??` markers.
- Removed run aliases from visible article/supplement prose and captions while preserving file paths and technical identifiers in reproducibility metadata.
- Independent audit found a duplicate closure-section input in the first final-assembly attempt. Removed the extra input, added an exactly-once/idempotence guard to the preview preparer, rebuilt, and verified a single Figure 11 and Tables 6–7.
- Current article/supplement hashes and page counts are authoritative in `PRE_A01_PACKAGE_MANIFEST.json`; an earlier 17-page preview hash in the independent checkpoint is superseded.
- A01 remains pending; this response does not summarize partial outcomes.

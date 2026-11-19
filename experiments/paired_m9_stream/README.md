# Paired M9 window replay

The [frozen design](PLAN.md) is commit 75c63a2. One 120-s simulation supplies both decisions in a record. Each pair shares its target, onset and noise seed. The first 60 s were byte-identical across paired histories at all eight PMUs in all 27 pairs. The preceding fault occurs at 89.28 s and ends at 89.5 s. The target is a new onset in the final 30-s window. Class 0 following the fault means no new onset, even if a recovery signal remains. That distinction matters when counting false alarms. Latency is time to a published window decision among detections; misses remain in the sensitivity denominator.

Fresh physical target sites are checked against three earlier M9 catalogs. Each physical family has one target in this pilot. The original classifier's training-site list is unavailable. Spatial attenuation follows M9 templates. Pairing does not make the target positions, source physics or noise independent of the simulator family. The physical window procedure is the frozen Attributor II plus its established integrity readout. The P07 history bank has a different admission rule and operating domain.

Reproduce from the paper repository root using the same scientific archive as the nine-class pilot and the verified extracted original submission. Set OPENBLAS_NUM_THREADS and OMP_NUM_THREADS to 1. The original model was serialized under scikit-learn 1.7.2. Use empty output directories.

    python scripts/prepare_paired_m9_stream.py FRESH_DIR SCIENCE_ARCHIVE
    python scripts/predict_paired_m9_stream.py FRESH_DIR SCIENCE_ARCHIVE EXTRACTED_ZIP
    python scripts/score_paired_m9_stream.py FRESH_DIR SCORE_DIR

For a data-free scoring check use the archived predictions and truth in this directory as FRESH_DIR for the final command. predictions.json and seal.json identify the decision set; observations_sha256.json fingerprints the input buffers. metrics.json contains all six target confusion matrices (true class in rows) and the first-window and pooled counts. A positive family is a detection even when the predicted family or site is wrong. Macro-F1 averages the nine classes on the balanced target windows. The pooled rates use the actual exposure including class-0 windows after a fault and one possible alert per 30-s interval. These paired exposures do not support independent-window confidence limits.

The C03 context analysis is separate and retrospective. Run `python scripts/audit_c03_context.py` to regenerate c03_context.json from the repository's frozen results. Each parent contributes its first intervention and four short-gap interventions. The exploratory percentile intervals resample 36 whole parents and use 20,000 draws. The comparison uses nominal trajectories and the original thresholds without refitting.

The primary prediction seal uses the training library version (scikit-learn 1.7.2). A second environment using 1.6.1 gave identical family predictions, location hit counts, detection times and false alarms. Two incorrect composite-event source guesses changed between environments. All 108 initial buffers failed the voltage-angle noise admission check. The generator and physical expert source files were verified against the nine-class pilot hashes, and the extracted submission against its archived ZIP.

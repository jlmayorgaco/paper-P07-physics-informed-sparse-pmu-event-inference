# Frozen corrections to nine-class window inference

Code and development choices were frozen in dfdaf57. The model uses the eight installed sensors, the same 90-s causal buffer as its predecessor and the same decision cadence. Study design and primary denominators are in PLAN.md. Each candidate physical site is compared against the earlier catalogs by the preparation entry point. Pure instrument targets rotate among installed PMUs. This is a nine-class M9 replay with known templates, not communication-system or field validation.

Use scikit-learn 1.7.2 (the submitted model serialization version), set OPENBLAS_NUM_THREADS=1 and OMP_NUM_THREADS=1, and use empty output directories. To reproduce from the paper repository root:

    python scripts/paired_m9_successor.py prepare FRESH_DIR SCIENCE_ARCHIVE EXTRACTED_ZIP
    python scripts/paired_m9_successor.py predict FRESH_DIR SCIENCE_ARCHIVE EXTRACTED_ZIP
    python scripts/score_m9_successor.py FRESH_DIR SCORE_DIR

To rerun scoring alone use this directory as FRESH_DIR. metrics.json contains all four methods, confusion matrices with truth in rows, paired gains and losses, and separate physical and instrument location denominators. The location endpoint requires an exact asset and counts all true events. The joint endpoint additionally requires a correct family. False alarms count positive decisions in windows without a new onset, including recovery. Compare the three older development cohorts (two primary splits and the previous paired experiment) to regenerate model.json:

    python scripts/fit_pmu_window_correction.py EXTRACTED_ZIP/data OUTPUT_MODEL.json HELD_LOCATION_PRIMARY ELECTRICAL_PRIMARY PREVIOUS_PAIRED_ROOT

The development graph uses the shortest sum of branch impedance magnitudes and a positive exponential voltage-magnitude signature. Fit a common offset and nonnegative amplitude to the phase-averaged three-sample sag at the nadir. Rank length parameters on exact location with equal weight per development asset. The admittance dictionary remains the source model for all families except faults. All classifiers and safeguards, including the P07 admission test, use their frozen parameters.

## Results

At the shared frozen operating points, the revised and previous hybrids each classified all 54 isolated windows correctly. After the preceding fault the revised hybrid identified 53/54 families versus 51/54 (macro-F1 0.981 versus 0.943). Both detected 47/48 events. Both observed zero positives in 66 windows without a new onset, 33 minutes. The two corrections were bad-data events at PMUs 2 and 5. Exact source increased from 14/48 to 16/48. The physical subset remained 4/36. The persistent-frequency rule and the alternative fault dictionary yielded no additional exact hits on this cohort. The class with the remaining miss was load. The bootstrap interval conditions on this class mix; it does not address site or simulator uncertainty.

The M9 generator sources, physical expert and extracted submitted ZIP matched the earlier archived hashes. An empty-data fallback in the fault projection skips undefined rolling windows. Re-inference using the safeguarded projection was checked against the prediction seal. For the prespecified secondary voltage-only transfer see ac_m9_results.json and the accompanying files. The exploratory current transfer is archived separately in experiments/ac_load_transfer/current_m9.

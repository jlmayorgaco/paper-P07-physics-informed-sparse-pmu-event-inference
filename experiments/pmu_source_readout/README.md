# M9 source readout with frozen family decisions

The input is a 90-s PMU buffer and the released hybrid's class and site. It can replace only the site of a physical-family decision (1, 2, 3, 4, 6 or 8). It passes through quiet and instrument-only outputs. It searches every eligible site within the predicted family.

**Calibration.** Simulate each candidate once with and without the event at the same nominal point and common random seed. Project the ratio of the two voltage trajectories onto the eight PMUs. For each family and voltage component, remove separable time/space terms until the residual is below numerical precision (at most two terms on this M9 library). This factorization accelerates scoring and keeps the individual asset responses. An independent 200-s normal simulation supplies the frequencies used for ambient regression. No test buffer, test truth or test-site shortlist enters calibration. All candidates, including test sites, are represented by the simulator. The M9 spatial law depends on bus labels; this is a matched synthetic benchmark.

**Readout.** Within each PMU, align the three phase angles to their quiet reference and weight phase measurements by inverse quiet increment variance. Fit quiet harmonics on the first 48 s. When a coherent sag precedes the decision interval, estimate its per-sensor amplitude from the preceding reports and subtract its predicted tail. For every site and onset within the decision window, fit one nonnegative common severity, clipped to twice the nominal template value. Choose the largest reduction in residual energy with diagonal noise scaling, omitting missing entries from both the inner product and energy. The composite readout uses the previously defined integrity pulse, when available, to constrain onset; its PMU ID is not used as the source. Ties prefer the baseline site when eligible. The estimator is conditional on the supplied class, registered responses and assumed noise metric.

**Development.** A separate voltage/current contrast model for the weak composite event was evaluated on old records. It recovered zero of 12 composite sources on each of two older cohorts. It is stored as a development comparison (pmu_source_pulse.py, pulse.npz); the registered readout does not call it.

From the paper root with the extracted submission and scientific archive used in the paired replay, set OMP_NUM_THREADS=1 and OPENBLAS_NUM_THREADS=1. Use scikit-learn 1.7.2 for the frozen classifier.

    python scripts/build_pmu_source_readout.py SCIENCE_ARCHIVE EXTRACTED_ZIP/data CALIBRATION_DIR
    python scripts/benchmark_pmu_source_readout.py prepare FRESH_DIR SCIENCE_ARCHIVE EXTRACTED_ZIP
    python scripts/benchmark_pmu_source_readout.py predict FRESH_DIR SCIENCE_ARCHIVE EXTRACTED_ZIP
    python scripts/score_pmu_source_readout.py FRESH_DIR SCORE_DIR

Prediction uses the versioned bank in experiments/pmu_source_readout. To verify scoring without raw measurements, pass this directory as FRESH_DIR to the final command. results.json records all numerators, denominators and true-class breakdowns. The interval for the change in exact accuracy resamples paired predictions within each true class and is conditional on the simulated design.

The earlier and registered readouts scored 22/64 and 56/64 exact isolated locations; after a preceding fault they scored 23/64 and 56/64. All gains occurred in the physical-source subset and neither context lost a correct site. The physical site of the weak composite was missed in all 16 records. The classifier itself was accurate on every record here. This replay has only eight target windows per class and does not establish population performance. With frames already loaded, a separate single-process timing on 48 earlier physical-family calls measured 19 ms median and 38 ms at the 95th percentile for the additional readout; use scripts/time_pmu_source_readout.py to repeat on your machine.

# Nonlinear AC load-location tests

Run from the repository root with the data directory of the verified submission (RAW operating point and the two topology tables; hashes in summary.json). The commands need NumPy, SciPy and pandas, plus the classifier dependencies imported by the shared network builder. Use OPENBLAS_NUM_THREADS=1 for the small linear systems.

    python experiments/ac_load_transfer/run.py EXTRACTED_ZIP/data OUT
    python experiments/ac_load_transfer/joint_current.py EXTRACTED_ZIP/data OUT

The first experiment checks each sensitivity column against a small independently solved nonlinear perturbation, then scores 288 load steps under two observation conditions. The largest equilibrium mismatch is recorded in summary.json. Its noise is on the observed relative change, not on each raw report separately. The estimator receives the family and two equilibria, and uses the nominal linearization even when the operating point changes. The independently seeded current experiment keeps the same voltage draws for its two estimators; the additional six current channels have ten times the relative RMS error. The result assumes correct terminal assignment, balanced operation, fixed slack/PV controls and known load power factors. There is no field dataset or event detector in these tests.

For the cross-model check, first seal the primary revised M9 predictions. Run the following command before scoring against M9 truth.

    python experiments/ac_load_transfer/predict_m9.py M9_RUN EXTRACTED_ZIP/data OUT

The readout only changes the predicted source for class 4, using the relative change in phase voltages between the prefix and the last ten seconds. All target windows, including missed or misclassified loads, count in the primary benchmark.

To reproduce the post-score exploratory transfer of the current model, add --with-current to predict_m9.py and use a separate output directory. Run score_m9.py with the primary replay directory and that output directory. On M9, both AC estimators matched the fallback's load-location counts (4/6 isolated and 3/6 after a fault); no improvement transferred. Each M9 condition contains a single previously unused load asset.

## Updated AC operating point

Run `python experiments/ac_load_transfer/operating_location.py EXTRACTED_ZIP/data OUT`. The plan in OPERATING_POINT_PLAN.md predates the run. The update estimates load deviations from a noisy pre-event reading of the same eight voltages and six currents. Two signed AC secants per site yield a quadratic response around this estimate. The profile arm uses the best severity on the fixed grid; the marginal arm integrates over that grid under equal site priors. All arms use the same noisy differential phasors, given load family and given steady-state windows. In 432 fresh cases the nominal projection, updated profile and updated marginal estimator recovered 409, 417 and 422 sites. The marginal estimate corrected 13 nominal errors and lost none. This is a location experiment under known topology and terminal mapping.

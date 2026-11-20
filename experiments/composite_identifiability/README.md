# Weak composite source identifiability

The diagnostic uses every candidate bus with two fresh seeded trajectories and two measurement views per trajectory. It withholds site labels from ranking. The known-parameter arms deliberately receive the target onset and relative strength and are diagnostic, not deployable. The same physical trajectory, noise, sample timestamps and affected instruments are used across comparisons. diagnostic.csv reports each prediction, true rank, signed margin versus the best rival, and seed. Every class-8 diagnostic supplies the family. In the later blind test the frozen classifier supplies it.

The main diagnostic readout fits the registered eight-PMU voltage bank from the previous study. Current magnitude helps restrict onset in its final arm and is not a voltage channel. The standard M9 composite alters current magnitude and adds a full turn in voltage angle. The principal-angle voltage likelihood therefore changes by less than 1e-13 with the onset fixed. This specific overlay cannot test the consequence of arbitrary voltage corruption. The clean rank test compares with a uniform guess; it is only a trigger for an independent trial. It is not population-level validation of accurate source identification.

The noise-scale experiment was exploratory after the four-arm diagnosis. It retains M9 physical variation and the original noise realization but scales the exported voltage errors about the ideal voltage measurement. The onset and strength are supplied; a noise-free voltage reading is not available in deployment. The unit-scale arm reproduces the original clean scores.

The joint readout sums likelihoods over source, onset, relative strength, marker PMU and timing lag. It uses a half-normal prior on the local gain and an effective diagonal noise model. Its MAP site minimizes expected zero-one site loss under those assumptions and the discretization. The secondary model adds physical current-angle contrast after conditioning on voltage contrasts. The four-arm diagnostic and the nine-class primary trial were prespecified; the secondary readout was frozen later, before scoring the nine-class trial. Neither estimator changes an alarm or predicted family. SHA-256 checksums identify each frozen prediction file.

From the repository root, with the same M9 scientific archive and extracted original submission as the preceding replay, set OPENBLAS_NUM_THREADS and OMP_NUM_THREADS to 1 and use scikit-learn 1.7.2. Use fresh scratch directories for generation.

    python scripts/diagnose_class8.py SCIENCE_ARCHIVE DIAG_DIR --noise-control
    python scripts/blind_class8.py prepare FRESH_DIR SCIENCE_ARCHIVE EXTRACTED_ZIP
    python scripts/blind_class8.py predict FRESH_DIR SCIENCE_ARCHIVE EXTRACTED_ZIP
    python scripts/class8_physical_current.py FRESH_DIR FRESH_DIR
    python scripts/score_blind_class8.py FRESH_DIR SCORE_DIR

To reproduce only the nine-class scoring, use this directory as FRESH_DIR in the last command. In each context, all 72 target windows enter nine-class macro-F1 and family accuracy and all 64 nonnormal targets enter localization, including misses. Diagnostics and blind measurements use different seeds and the synthetic M9 forward model. Each method sees the same registered candidate catalog. Transfer outside this simulator or to unregistered sites was not tested.


In the independent nine-class trial the primary posterior gained BUS1 in both members of one pair. It located 54/64 isolated and 53/64 consecutive targets versus the released 53/64 and 52/64. Class 8 accounted for 2/8 hits per context versus 1/8. The current-phase variant gave 1/8 in each. The unchanged classifier attained macro-F1 1.000 and 0.986 and zero alarms over 44 no-onset minutes. With non-class-8 outputs fixed, even perfect class-8 site decisions would give 60/64 and 59/64 on this cohort. The noise-control finding relates to the voltage readout at supplied onset and severity. The blind trial does not support a 0.96 exact-location claim.

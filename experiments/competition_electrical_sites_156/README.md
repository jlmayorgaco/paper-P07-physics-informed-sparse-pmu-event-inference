# Prospective nine-class comparison on new physical assets

The electrical localizer was frozen at revision 20680c1 before predictions or scores. The two comparators are the original submitted window classifier and the frozen principal-angle residual hybrid. Both hybrids use the same family decision on every record. Only the physical source ranking changes.

The test has 12 records per class, three previously unused physical assets per physical family (four realizations per asset), and another 48 normal records for false alarms. Both mixed classes carry a physical target. PMU-only events reuse the fixed installation. Newness is checked against the source catalogs of both prior spatial studies. The original submission's training assets cannot be independently verified as disjoint. The test uses M9 synthetic data and a known composite template. Asset changes affect the simulator's imposed spatial pattern, which depends on numerical bus labels. The injected patterns are not solutions of the localizer's circuit equations.

The network uses the bundled IEEE-39 RAW operating point and Ybus, plus a common assumed 0.2 pu generator transient reactance. Bus injections use a column of the inverse admittance. Opening a branch removes its complex pi-model stamp before solving for the voltage change. The output is compared to the eight PMUs' fractional complex voltage changes. The source score profiles a complex amplitude and common spatial offset using quiet-prefix inverse-variance weights. Sources may include any of 39 buses, 46 branches, ten generators or 18 positive-load buses, according to the predicted family. There is no fit to the new event sites. A physical current gain or voltage drop need not uniquely identify a source in this measurement layout.

Use an empty output directory to regenerate and predict. The prediction process reads opaque measurement folders and startup decisions; score and audit run afterward.

    python scripts/prepare_electrical_sites.py SCIENCE_ARCHIVE FRESH_DIR
    python scripts/competition_electrical_localizer.py predict FRESH_DIR --submitted EXTRACTED_ZIP
    python scripts/competition_electrical_localizer.py score FRESH_DIR
    python scripts/audit_electrical_sites.py FRESH_DIR EXTRACTED_ZIP

To verify the archived counts, nine-class confusion matrices, and macro-F1 from the sealed predictions:

    python scripts/competition_electrical_localizer.py verify experiments/competition_electrical_sites_156

Exact localization counts all 96 true events including missed ones. The 60 negative windows cover 30 minutes. The provenance lists observation and model hashes. The extracted submission was verified byte for byte against its original ZIP and the M9 modules against the nine-class pilot's archived hashes.

## Result

The electrical hybrid scored 0.981352 macro-F1, 106/108 correct families, 24/96 exact sources and zero alarms in 60 normal windows. The residual hybrid scored 0.981352, 106/108, 22/96 and 0/60; the competition submission scored 0.193266, 32/108, 0/96 and 0/60. All 72 physical events had the correct family under both hybrids. Electrical ranking gained one exact line source and one exact load source and lost none. Twenty-two of 24 exact hits were instrument-only events. The 0.96 exact-location target failed. The static voltage-only dictionary contains 13 pairs of bus signatures indistinguishable to numerical tolerance after fitting the common offset and complex amplitude.

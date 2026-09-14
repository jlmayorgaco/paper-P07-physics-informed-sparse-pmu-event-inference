# Scripts

Place reproducible experiment and manuscript-artifact scripts here. Record input data, configuration, environment, and output contracts with each script.

`verify_theory_identities.py` regenerates `generated/theory_checks.json`. Its deterministic checks cover the adopted branch primitive and relative-contact toy model; they are algebraic guards, not IEEE 39-bus validation.

`generate_paper_artifacts.py` regenerates the empirical tables and figures from `generated/frozen/`. Figure 5 is reconstructed from `legacy_raw_event_figure_values.csv`; its light-gray clock trace is a schematic rendering of the recorded time coordinate and is not treated as a measured PMU channel.

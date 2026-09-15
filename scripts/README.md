# Scripts

Place reproducible experiment and manuscript-artifact scripts here. Record input data, configuration, environment, and output contracts with each script.

`verify_theory_identities.py` regenerates `generated/theory_checks.json` and its compact supplementary table. Its deterministic checks cover the branch primitive, regular and higher-order profiled separation, rank-deficient nuisance, and signed support geometry.

`verify_cone_bayes_identities.py` regenerates `generated/cone_bayes_checks.json` and two supplementary tables. It checks the exclusive-support quotient, one-sided cone projections, boundary-aware Bayes factors, the nuisance-profile limit, cone--Laplace scaling, and a singular-Hessian counterexample. Both verification scripts use explicit toy systems and are algebraic/numerical guards, not IEEE 39-bus validation.

`verify_information_limits.py` regenerates `generated/information_limit_checks.json` and two supplementary tables. Twelve deterministic checks cover exact redundancy, higher-order and mixed evidence rates, nested-support Occam factors, profiled prefix monotonicity, first- and second-order temporal rescue, Gaussian decision error, the beta-min boundary, a finite-hypothesis Fano illustration, and the frozen RAWSIM39 V1.2 identifiability-gate taxonomy. The first eleven are controlled identities or illustrations. The twelfth audits an archived IEEE 39-bus gate ledger; because that ledger contains no higher-derivative arrays, it does not assign a nonlinear contact order.

`generate_paper_artifacts.py` regenerates the empirical tables and figures from `generated/frozen/`. Figure 5 is reconstructed from `legacy_raw_event_figure_values.csv`; its full-height light-gray clock trace and right-hand axis are a schematic rendering of the recorded time coordinate and are not treated as a measured PMU channel.

`build_manuscript_bundle.ps1` regenerates all three theory-check suites, compiles `supplement.tex`, refreshes its tracked review artifact, and then compiles `main.tex`. The resulting `main.pdf` and tracked main review copy contain the principal article followed by the complete supplementary material; `supplement.pdf` is also retained independently.

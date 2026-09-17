# Pending research gates

## Submission veto: the full multi-family joint method is not yet executed

- Freeze $\mathcal E_{\mathrm B}$ as the reference batch event estimator. Do not replace its GH31 amplitude marginalization by EM, a point estimate, or a local Laplace approximation and still call the result the same reference method.
- Implement an exact prefix version of $\mathcal E_{\mathrm B}$ and verify the batch quadratic form, evidence, and posterior at every prefix, including the same initial AR(1) density.
- Before evaluating $\mathcal E_{\mathrm J}$, enforce the $\mathcal R_0$ reduction test against $\mathcal E_{\mathrm B}$ with the identical candidate bank, surrogate, covariance, priors, onset, and family.
- In $\mathcal E_{\mathrm J}$, retain GH31 or equivalent Rao--Blackwellized integration for one- and two-dimensional event amplitudes; reserve optimization/Laplace approximations for the remaining state and nuisance coordinates and audit their normalizers.
- Instrument the hybrid DAE event boundary: store the pre-event state, callback arrays, independently consistent post-event algebraic state, constraint residual, and first retained PMU frame.
- Validate the analytic algebraic terms $z_1,z_2$ with central finite differences and verify zeroth-, first-, and second-order residual scaling before calling the event tangent analytic.
- Repeat the semantic gate for load change, generation change, and a continuous line-admittance perturbation; use the binary outage only as a separate discrete-mode experiment.
- Resolve the current second-order analytic-to-TDS discrepancy before using full dynamic curvature as evidence.
- Freeze and run the local separation falsification test $2D(a)/a^2\rightarrow\gamma_1^2$ over declared candidate pairs, nuisance spaces, operating points, amplitudes, and numerical tolerances.
- Export the actual IEEE 39-bus nuisance-residual event dictionary and evaluate the support-to-support margin under the same sign and amplitude constraints used by the Bayesian likelihood.
- On those same frozen parents, compare diagnostic-quotient rank and restricted margin with posterior entropy, credible-set size, exact-support error, and resolution delay; quotient dimension alone is not a performance certificate.
- For every physical family, freeze whether severity is signed, one-sided, bounded, or discrete; compare relaxed span and physical cone margins and record which constraints are active at each nearest competitor.
- Evaluate the half-normal boundary factor and posterior sensitivity to proper slab scale on held-out fault, trip, and outage trajectories before using it as a multi-family result.
- Separate rank deficiency caused by redundant coordinates from genuine higher-order non-identifiability before applying cone--Laplace evidence; do not substitute a Hessian pseudoinverse for this audit.
- Recover or rerun the reported nonlinear controlled-DAE experiment with its exact equations, solver settings, seeds, CSV, and figures; its current `sandbox:/mnt/data` links are not repository evidence.
- Complete the independent-operating-point T120 physical bank and reconcile the absolute scale/name of the exported separation metric before freezing a prospective horizon contract.
- Export cumulative, prefix-consistent likelihood blocks for all 18 archived RAWSIM39 candidate directions; report the profiled increment, equality cases, and contact-order changes without blockwise renormalization.
- Export first-, second-, and, where needed, higher-directional derivative arrays for the archived gate. Use nonlinear TDS convergence to distinguish weak regular information, genuine order-$k$ contact, exact redundancy, and local-domain failure.
- Build a pairwise IEEE 39-bus distance atlas and compare the simple-hypothesis Gaussian oracle error with empirical candidate-pair decisions before translating geometry into an operational error probability.
- Extend the information limits to an explicit bounded model-discrepancy class and test whether the robust lower margin remains positive under independent operating points.
- After that audit, freeze a new 30/60/90/120-frame test reporting $p(K=2)$, exact support, Top-3, credible-set coverage/size, entropy, and resolution delay without retuning the likelihood.
- Extend the executed load-source likelihood to faults, line outages, generation changes, integrity events, and simultaneous compositions under one audited plant and PMU operator.
- Complete the analytic descriptor-DAE tangent or retain the numerical physical tangent terminology permanently.
- Estimate state/integrity nuisance tangent and curvature on disjoint development data; test whether the first- versus second-order contact predicted by Proposition 3 explains IEEE 39-bus detection and source-resolution thresholds.
- Compare four frozen paradigms on identical event parents: learned-only, physics-only, physics plus learned residual discrepancy, and diagnosability-aware inference with abstention.
- Compare the tractable candidate-conditioned posterior with a converged small-problem SMC or nested-sampling reference before making an approximation-quality claim.
- Test slow parameter adaptation first and weak/integral sparse model correction only after residual lack of fit remains; require an ablation showing that protected event-discriminant directions are not absorbed before adding SINDy-like adaptation to the method.
- Hold out physical source assets from every source-labeled training, tuning, threshold, and calibration operation.
- Test whether the nuisance-profiled pairwise margin predicts calibrated uncertainty, candidate-set size, and source-resolution delay prospectively. The retrospective global-distance result is encouraging but is not a frozen prospective bridge. Freeze and hash the theory-only predicted curve (pairwise distance, Gaussian error bound, and implied resolution horizon) before running the corresponding Monte Carlo campaign, so the comparison is a genuine prospective test and not a retrospective correlation.
- Compare the frozen fixed-covariance W2 likelihood against a hierarchical noise-scale-marginalized alternative (a shared scale factor with a conjugate prior, integrated out analytically) on identical candidates and data; report whether the fixed-covariance likelihood produces excess false positives or miscalibration under noise-scale mismatch between CAL and TEST before adopting either as the reference likelihood.
- Test whether adding frequency and ROCOF channels to the event likelihood (beyond voltage/current) changes localization accuracy or resolution delay, as a distinct question from validating those channels as candidate-conditioned outputs; report the channel-set ablation and do not assume unused virtual outputs are informative for localization.
- Add PMU loss/join, operating-point shift, parameter shift, line topology change, and at least one cross-simulator transfer campaign.
- Expose a long normal stream and report false alarms/hour, event recall, joint alarm precision, and duplicate-alarm scoring.
- Calibrate or rename the source evidence: classifier votes and uncorrected MAP scores are not probabilities.

## State-estimation gates

- Before reporting any candidate-conditioned or posterior-averaged state estimator (state model averaging over event hypotheses) as a headline result, evaluate it on trajectories whose severity, onset, and operating point are disjoint from those used to fit the response surrogate/dictionary. Near-zero error against trajectories that share dictionary-forming points is not evidence of generalization.
- Extend the successful regularized M6 recentering to a causal sequential recentering and Jacobian-rebuild protocol with disjoint DEV/TEST manifests.
- Resolve the under-dispersed joint uncertainty using a profile, sandwich, bootstrap, or nonlinear posterior approximation.
- Expand the independent-solver check or permanently narrow solver-independence wording.
- Freeze candidate-conditioned validation targets for branch-terminal current, bus injection, active/reactive power, model-implied frequency, and ROCOF at uninstrumented buses. Report phasor error in rectangular/TVE-style form, absolute and base-normalized current error near zero current, and uncertainty coverage at the trajectory level.
- Compare model-implied frequency and ROCOF against the exact causal filtering used by the PMU backend; do not validate them against ideal derivatives alone or evaluate derivatives across a topology jump.
- Treat positive-sequence ABC output only as balanced waveform synthesis. Any claim about unbalanced phase recovery requires a sequence-complete or phase-domain plant and corresponding measurements.

## Evidence-integrity rules

- Keep PowerDynamics state metrics and ANDES event metrics separate; never average across campaigns.
- Keep physical events distinct from missing, corrupt, or timing-quality measurements.
- Report failed solves and rejected trajectories in the planned denominator.
- Generate every numerical table and empirical plot from frozen artifacts. Do not replace a missing experiment with stronger prose.
- Keep deterministic toy identity checks separate from simulator validation and from primary IEEE 39-bus evidence.

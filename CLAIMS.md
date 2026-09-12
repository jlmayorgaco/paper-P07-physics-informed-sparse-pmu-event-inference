# Current manuscript claim boundary

The paper establishes that, on the audited PowerDynamics IEEE 39-bus benchmark, eight voltage/current PMUs support accurate nominal reconstruction of 31 unobserved bus voltages; a preregistered functional residual is associated with bus-level difficulty; network and operating-point mismatch dominate the tested shifts; observed innovations can flag much of this inadequacy; and oracle recentering shows that stale local physics explains most excess error.

The paper also establishes negative evidence: positive fixed-lag smoothing does not improve TVE, nominal marginal calibration does not transfer under physical shift, the tested low-rank discrepancy placements do not improve hidden-state inference, and causal grouped-offset recentering does not recover the oracle benefit.

The paper does **not** establish event detection, source localization, full nonlinear Hybrid-DAE superiority, learned-discrepancy benefit, optimal PMU placement, field validity, cross-simulator transfer, continuous false-alarm control, or real-time/edge deployment. See `docs/claims-and-evidence.md` for the artifact-level register.

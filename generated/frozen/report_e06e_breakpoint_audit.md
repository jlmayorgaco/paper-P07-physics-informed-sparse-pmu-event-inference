# E06-E breakpoint consistency audit

Canonical definition: for each STANDARD B2 trajectory, `r_i(m)=TVE_i(m)/median(TVE_nominal)` where the denominator is the median hidden-31 TVE over all 140 m=0 STANDARD cases. Cell values are the median of these per-trajectory ratios across the 20 independent seeds, retaining the E-A…E-D strata. No mean-based breakpoint is mixed into the canonical table.

The previous M7 `[0.00,0.25]` label came from the separate refinement-seed table and a different direct-median aggregation; it is not comparable to the main-grid table. Canonical breakpoints are in `e06e_breakpoints_canonical.csv`.

Reference TVE = **0.014744044%**. Full audit fields are in `e06e_breakpoint_audit.csv`.

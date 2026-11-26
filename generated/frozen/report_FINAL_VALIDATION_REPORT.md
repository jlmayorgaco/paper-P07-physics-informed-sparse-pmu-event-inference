# PowerDynamics IEEE-39 independent validation campaign

## Decision

**Final classification: LEVEL C — NUMERICALLY VALID PEDAGOGICAL BENCHMARK.** All PowerDynamics-native numerical gates pass: official tutorial reproduction, exact PD-G0 static parity, equilibrium, descriptor/eigenanalysis, nonlinear modal confirmation, ε-convergence, official and additional dynamic disturbances, synthetic PD-G1, and VI-only functional observability. The model is package-defined/pedagogical rather than traceable to a published parameter set. The PD tutorial is a distinct parameterization from ANDES canonical; dynamic equality is neither required nor claimed. MATPOWER case39 was not available for the optional comparison.

**PRIMARY_DYNAMIC_BENCHMARK = YES** (PowerDynamics backend only; not a claim of ANDES equivalence).

## A–Q handoff

**A — Branch/HEAD/commits:** `research/pmu-hybrid-dae-bayes-v1`, HEAD `ac69099c0ec2e9699f43ed06ca75c0ca0e6d6ce8`; no push and no E04 work.

**B — Julia:** juliaup 1.22.3, Julia 1.11.9 x64; isolated project with PowerDynamics 5.0.0, NetworkDynamics 1.3.0, ModelingToolkitBase 1.69.2.

**C — Machine/controller:** 10 machines on buses 30–39; 8 controlled composites plus buses 31/39 machine+load representations; 9 AVRs and 9 TGOV1 governors on buses 30–38. Bus 39 is an uncontrolled fixed-input machine/load tutorial representation, not proven external grid.

**D — Provenance:** original PD CSV bytes and tutorial source hashes frozen. Network, machine, AVR, TGOV1 and ZIP parameters classify as `PACKAGE_DEFINED`/`PEDAGOGICAL`; no published identity or ANDES equivalence asserted.

**E — PD-G0:** PASS. Exact PD→pandapower same-case parity: max ΔY=1.14e−13, relative Frobenius 1.07e−16, max |V| error 4.64e−13 pu, max terminal-flow error 2.74e−09 MVA.

**F — Variants:** topology counts are 39 buses/46 branches. ANDES canonical↔pandapower passes its own gate, while PD vs ANDES canonical differs up to 0.06813 pu in |V|. `pandapower.networks.case39()` is 39 buses, 35 lines, 11 transformers, 21 loads, 9 generators, 1 ext_grid and converges. MATPOWER case39 unavailable.

**G — Descriptor:** 192×192, rank(M)=114, 114 differential and 78 zero-mass rows; reduced ODE dimension 114; one reference candidate; every state mapped to component/device/bus/state in `pd_descriptor_inventory.csv`.

**H — Equilibrium:** official PF-to-dynamic initialization PASS; residual 4.66e−13.

**I — Spectrum:** spectral abscissa −6.99e−13 s⁻¹ (reference-only marginal); physical least-damped pair −0.09818 ± 0.42948i s⁻¹. Participation factors exported and support AVR/machine dominance for this pair.

**J — Nonlinear modal:** Rodas5P probes cover both members of the physical least-damped conjugate pair (Re=−0.09818 s⁻¹); both are finite with `retcode=Success`.

**K — Linearization convergence:** ε={1e−2,3e−3,1e−3,3e−4,1e−4,3e−5}; modal, governor-reference and ZIP-load scenarios all finite/Success; fitted p=1.9987, 2.0003 and 1.9820; log–log PNG emitted.

**L — Dynamics sanity:** official fault/clear line 11 at 0.1/0.2 s over 15 s PASS. Additional +1% governor-reference and +1% ZIP-load runs are Success, finite; voltage ranges and speed extrema are in `pd_dynamic_sanity.csv`.

**M — PD-G1:** synthetic branch/operator PASS for all 8 requested links (orientation swaps explicit), max terminal discrepancy 1.45e−11 MVA. No real PMU channel file is claimed.

**N — E03 observability:** PASS (structural VI-only). At 30 fps, horizons 0,3,10,30,60,120,180 frames were evaluated using `A_d=exp(A/30)`. Rank reaches 39/114 at 180 frames; functional residual, worst hidden bus and σ=1e−3 Gramian information bound are reported. This does not require or claim full-state observability.

**O — Final level:** `LEVEL C — NUMERICALLY VALID PEDAGOGICAL BENCHMARK`.

**P — Exact benchmark flag:** `PRIMARY_DYNAMIC_BENCHMARK = YES` (PD backend only).

**Q — One next action:** if cross-backend comparability is needed, freeze an explicit ANDES↔PD machine/controller/state contract and perform a separate comparison; do not alter this validated PD benchmark.

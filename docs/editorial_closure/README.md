# P07 editorial closure

This directory preserves the completed pre-A01 technical preparation and the guarded path for final integration. The current manuscript remains pre-A01 until the frozen ablation finishes and passes its completion checks.

## Current gate

See [STATUS.json](STATUS.json) for the latest A01 progress and [FINAL_READINESS.md](FINAL_READINESS.md) for the completed pre-A01 checks. As of 2026-11-02, A01 is at inference task 61/72 (record S321, PROFILE_MEMORY); partial outcomes have not been used.

After the run completes, use [the guarded verification and staging script](scripts/verify_a01_gate_and_apply_staging.ps1). It refuses to proceed while an A01 process is active, verifies the completion/seal/parity/import contracts, checks the current source baseline, and applies only its explicit editorial allowlist when invoked with `-Apply`. First run it without `-Apply` and inspect every reported check and the staged diff.

## Retained pre-A01 work

- [Pre-A01 readiness record](FINAL_READINESS.md)
- [Pre-A01 article, supplement and coauthor brief PDFs](PRE_A01_REVIEW_OUTPUTS.json)
- [C01 metric coverage and closure decisions](METRIC_COVERAGE_AND_CLOSURE.md)
- [Grouped ML protocol status](ML_70_30_PROTOCOL_STATUS.md)
- [Claim/evidence register](staging/CLAIM_EVIDENCE.csv)
- [Derived C01 coverage metrics](derived_c01/README.md)

The complete staging source, C01 input snapshots, R2 checks, and derived restoration, runtime and domain metrics are under `staging/`. Their original pre-cleanup copy remains in the private provenance folder.

## Current-source baseline

`BASELINE_MANIFEST.json` records hashes for the active sources checked by the guarded integration script. It was refreshed after the public cleanup removed the tool-only citation and empty attribution macros. The original pre-cleanup manifest is retained privately.

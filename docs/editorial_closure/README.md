# P07 editorial closure

This directory preserves the pre-A01 preparation, the completed post-A01 integration record, and the final readiness audit. The active manuscript now includes the frozen ablation outcomes and bounded C01 closure analysis. Pre-A01 review outputs remain retained as historical checkpoints.

## Current gate

See [STATUS.json](STATUS.json) for the completed gate and [FINAL_READINESS.md](FINAL_READINESS.md) for the final artifact and visual checks.

The [guarded verification and staging script](scripts/verify_a01_gate_and_apply_staging.ps1) passed in check-only and apply modes. Its process check filters out Git inventory scans and the guard itself while checking for experiment runner processes; it still verifies the completion, seal, parity, denominator, import and source-baseline contracts before applying its explicit allowlist.

## Retained pre-A01 work

- [Final readiness record](FINAL_READINESS.md)
- [Final artifact manifest](FINAL_MANIFEST.json)
- [Retained pre-A01 article, supplement and brief PDFs](PRE_A01_REVIEW_OUTPUTS.json)
- [C01 metric coverage and closure decisions](METRIC_COVERAGE_AND_CLOSURE.md)
- [Grouped ML protocol status](ML_70_30_PROTOCOL_STATUS.md)
- [Claim/evidence register](staging/CLAIM_EVIDENCE.csv)
- [Derived C01 coverage metrics](derived_c01/README.md)

The complete staging source, frozen C01 input snapshots, review checks, and derived restoration, runtime and domain metrics remain under `staging/`. The applied staging record is `A01_STAGING_APPLIED.json`.

## Current-source baseline

`BASELINE_MANIFEST.json` records hashes for the active sources checked by the guarded integration script. It was refreshed after the public cleanup removed the tool-only citation and empty attribution macros. The original pre-cleanup manifest is retained privately.

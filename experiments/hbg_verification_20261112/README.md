# HBG derivation reproduction and audit

This folder preserves the supplied ZIP members byte for byte and adds a separate set of independent, lightweight numerical checks. It is an illustrative mathematics reproduction, not a new P07 result or an IEEE-39/DAE evaluation.

## Contents

- `verify_hamiltonian_graph_bayes.py`: original user-supplied 4-bus/5-branch demonstration.
- `DERIVACION_HAMILTONIANA_BAYES_GRAFOS.md`: original derivation document from the ZIP.
- `verify_extended.py`: independent gates for Gaussian evidence, truncated-normal normalization, recovery-state MAP, profiled channel distances, and reduced swing energy balance.
- `gates_20261112.json`: captured results from the extended gate run.
- `original_run_20261112.txt`: captured stdout from the supplied script.
- `manifest_20261112.json`: hashes for source inputs, code, and captured outputs.
- `../../docs/HBG_REPRODUCTION_AUDIT_20261112.md`: source inventory, hashes, reproduction results, and limitations.

## Reproduce

From this folder, with Python, NumPy, and SciPy installed:

```powershell
$env:OPENBLAS_NUM_THREADS='1'
$env:MKL_NUM_THREADS='1'
$env:OMP_NUM_THREADS='1'
python verify_hamiltonian_graph_bayes.py
python verify_extended.py
```

The extended script emits JSON and exits nonzero if any gate fails. All checks are small (at most 7-dimensional observation covariance); no DAE solver or project dataset is loaded.

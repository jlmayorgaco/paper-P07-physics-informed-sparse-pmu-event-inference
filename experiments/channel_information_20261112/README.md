# Reproducing the channel diagnostic

The committed `input_snapshot.npz` is the minimal nominal input. It contains only `T`, `J`, `g`, `u`, `j`, `v`, `group`, the quiet/null gain `K0`, and `S`/`Sinv0`. It is extracted from a finished CAL bank; it contains no observations or event truth. `snapshot_metadata.json` records the source-bank and snapshot hashes.

From the P07 repository root, run:

```powershell
python experiments/channel_information_20261112/run_channel_diagnostic.py
```

This writes the summary JSON, all directed pair separations (918 rows), and nearest competitors (162 rows). The run does not access C03: it reads the compact snapshot and local asset/map files only. `prepare_snapshot.py` is an optional provenance step for maintainers who still have the read-only CAL bank at the documented path; it does not execute experiment code and does not read truth or TEST.

Requirements: Python 3, NumPy, and SciPy. The inputs are small enough for a single process; the largest covariance is 1,410 by 1,410. No manuscript, estimator, C03 run product, or figure is generated or modified.

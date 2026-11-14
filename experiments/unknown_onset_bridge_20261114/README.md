# Unknown-onset recovery ablation

This is a synthetic development study. It does not use F01, P2, C03,
RAW0001, or RAW0002. The source files retained here match the applicable
entries in the supplied manifest. The archive
`PMU_P07_Ablacion_Inicio_Desconocido_Posterior_2026.zip` has SHA-256
`b430adb1e6323b7da81aa4050a0adfc415a4b90ea7c649650494677fad6de298`.
All 16 listed entries were checked against that manifest before running
the Python code. The attached Julia module was not adopted or validated.

Reproduce in this directory (Python 3.13.14, NumPy 2.3.5, SciPy 1.16.3):

```powershell
$env:OPENBLAS_NUM_THREADS = '1'
python -B -m pytest -p no:cacheprovider -q
python -B unknown_onset.py --ncal 1300 --ntest 2300 --seed 20261114 --out ../../build/bridge-seed1
python -B unknown_onset.py --ncal 1300 --ntest 2300 --seed 20261115 --out ../../build/bridge-seed2
python -B present.py
```

All 13 Python checks passed. Two tests return a diagnostic value in addition
to their assertions. Seed 20261114 reproduces every event count and paired
interval, with only floating-point precision differences in continuous
scores. Seed 20261115 repeats the design on new synthetic draws; it is a
sensitivity check after development, with the same four scenarios and
separate normal calibration per arm and scenario.

Each arm targets 5% false alarms per normal window in CAL. Rates in TEST
are not constrained to match. The base-setting coverage difference for
full moments versus within-component covariance is positive on both
seeds; the incremental effect of the mixture changes sign. The study
assumes a prescribed recovery distribution and matched linear dynamics.
It does not evaluate early reporting, normal FAR per hour, or real-PMU
inputs. Even a positive result does not imply that semantic history
labels have prediction value beyond the represented state and mode.

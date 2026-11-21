# June ExtraTrees vs frozen M9 response successor

## Result

Retrospective paired evaluation on exactly the released `tmp/spatial264` records: 216 primary records (24 per class, 192 positive) and 48 added quiet records. Both arms receive the same opaque case IDs and source CSVs. Each decision uses the final 30-second window after the 60-second quiet prefix. No traces were generated and no model was refit.

| Metric | June original | Frozen M9 response successor |
|---|---:|---:|
| Nine-class macro-F1 | 0.2031 | 0.9907 |
| Exact family | 67/216 | 214/216 |
| Exact source on positive records | 12/192 | 188/192 |
| Exact family and source on positives | 12/192 | 188/192 |
| False alarms among primary class-0 windows | 0/24 | 0/24 |
| False alarms among 48 added quiet windows | 0/48 | 0/48 |
| False alarms across all quiet windows | 0/72 | 0/72 |

The denominator for exact source includes every positive primary record, including family misses. The quiet total combines the 24 class-0 primary records and 48 added quiet records.

## Reproduction

From the repository root, using the verified extracted June submission and the already sealed successor predictions:

```powershell
python experiments/modal_recovery/consolidated/m9/predict_june.py --workers 4
python experiments/modal_recovery/consolidated/m9/score_pair.py
```

`predict_june.py` calls the June model through the same API and final-window feature path used by `scripts/competition_held_locations.py`; model code and weights are loaded from `tmp/competition_zip_verified`. `score_pair.py` checks the saved successor prediction seal, validates exact case-set equality and cohort balance, then writes opaque paired predictions, their SHA-256, `results.json`, and this report.

The frozen successor arm is the saved `response` decision from `experiments/competition_spatial_264/predictions.json`; its response bank and spatial localizer were frozen before this retrospective scoring. No alternate method was tested. This remains an M9 cohort result, not an official hidden competition score.

## Provenance

- Python: `3.13.14` (`C:\Users\walla\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe`)
- Runtime packages: NumPy `2.3.5`, pandas `2.3.3`, scikit-learn `1.6.1`
- Compatibility note: the June joblib estimators report serialization under scikit-learn `1.7.2`; the installed scikit-learn `1.6.1` emitted version-mismatch warnings during model loading. This runtime meets the ZIP's unpinned `scikit-learn>=1.3` requirement, but the warning is a reproducibility limitation.
- Cohort: `tmp/spatial264`, 2116 source/truth/admission files, 1,573,230,690 bytes
- Cohort SHA-256: `3c24d050ebcb58afd5b4582ee937f14778b7a818b74fd6d61c0412fafdab72a5`
- June ZIP SHA-256: `e0bfc17e4c5ee9b595fa51fd94d736145c2f48755696c8d2eadcff00cb23a243`
- June extracted classifier SHA-256: `e6c629019a64bb732133d96ae75a865bb3bd6b48b8f44a7002b900e7d0aef98a`
- June decisions SHA-256: `f0947e1123bab0241622bb73e7dbd9bd1414535fde4fcd69c0af26651b0c2b06`
- Frozen successor decisions SHA-256: `14cc652de45ea413d10e9a78491ad16c4a4e9928c866e82e132f1b26293f1cca`
- Paired opaque predictions SHA-256: `3d42d3ddf69eba6a41a2e7fa68151225960689334ccfe983b8ead3431c74918f`

Full input, code, model, prediction, and split-truth hashes are recorded in `results.json`.

A second complete replay loaded the June estimators with their original scikit-learn 1.7.2 serialization version. All 264 class and source predictions exactly matched the first replay.

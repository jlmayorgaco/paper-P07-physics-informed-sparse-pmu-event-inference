# Frozen C01 metric restatement

These outputs are a descriptive restatement of `generated/frozen/c01_20261029/`; they are not new observations, a new evaluator run, ROC/PR analysis, or a significance test.

- `report_f1_by_condition.csv`: TP/FP/FN summed over continuous-event and normal-control records and both noise strata; F1 = 2TP/(2TP+FP+FN).
- `event_coverage_by_family_condition.csv`: detected, timely, exact joint, and Top-3 counts/fractions by method, family, and condition. Each fraction denominator is all 108 truth event rows for that family-condition across the two noise strata; missed detections remain in it.
- `c01_report_and_event_coverage.png` and `.pdf`: two-panel view of report-level F1 and the timely/joint/Top-3 event fractions.
- `derivation_checks.csv`: complete-denominator, failure/rejection, and parity checks.

Aggregated availability, abstention, and `open_eof` counts remain in the report F1 table. The figure uses a 0-to-1.03 vertical range in both panels and descriptive method labels; exact values are in the CSV. C01 has no physical rejections or inference failures in its frozen audit. No uncertainty interval is added here: the source analysis uses the physical parent cluster, and the plotted ratios are descriptive.

# Resultados verificados del corpus

Generados desde archivos con hashes. C01 está excluida hasta su cierre; no se leen sus predicciones parciales. Los resultados externos del chat no se mezclan con los ejecutados localmente.

El CSV adjunto conserva fuente, hash, denominador y límite de cada cifra. Una comparación entre contratos diferentes no es una mejora porcentual válida.

| Evidencia | Método / régimen | Métrica | Valor | Denominador |
|---|---|---|---:|---|
| state_nominal | B0_NOMINAL | hidden_voltage_relative_error_mean | 0.3402 % | 100 |
| state_nominal | B1_SNAPSHOT_WLS | hidden_voltage_relative_error_mean | 0.00990398 % | 100 |
| state_nominal | B2_KALMAN | hidden_voltage_relative_error_mean | 0.0096344 % | 100 |
| AC_recenter | regularized_AC | oracle_gap_closure_median | 98.089 % | 60 |
| legacy_known_sources | hierarchical_448_availability | detection_f1 | 0.988529 fraction | historical grouped evaluation |
| legacy_known_sources | hierarchical_448_availability | family_macro_f1 | 0.90512 fraction | historical grouped evaluation |
| legacy_known_sources | hierarchical_448_availability | physical_top1 | 0.591535 fraction | historical grouped evaluation |
| legacy_known_sources | hierarchical_448_availability | physical_top3 | 0.719225 fraction | historical grouped evaluation |
| legacy_known_sources | hierarchical_448_availability | integrity_top1 | 0.973779 fraction | historical grouped evaluation |
| legacy_source_holdout | historical_supervised | exact_source_correct | 3 count | 303 |
| GLOBAL137_archived | FINITE | top1 | 100 % | 1440 |
| GLOBAL137_archived | FINITE | top3 | 100 % | 1440 |
| GLOBAL137_archived | MODERATE | top1 | 98.8194 % | 1440 |
| GLOBAL137_archived | MODERATE | top3 | 100 % | 1440 |
| GLOBAL137_archived | WEAK_STRONG | top1 | 66.25 % | 1440 |
| GLOBAL137_archived | WEAK_STRONG | top3 | 95.8333 % | 1440 |
| GLOBAL137_archived | WEAK_WEAK | top1 | 24.375 % | 5760 |
| GLOBAL137_archived | WEAK_WEAK | top3 | 59.8437 % | 5760 |
| GLOBAL137_archived | GH31 | unique_physical_trajectories | 3488 count | campaign |
| GLOBAL137_archived | GH31 | noise_rows | 10564 count | campaign |
| GLOBAL137_archived | GH31 | hypotheses_per_case | 137 count | campaign |
| T120_representation | D | median_whitened_response_error | 0.205272 whitened norm | 32 |
| T120_representation | D_Q | median_whitened_response_error | 0.469027 whitened norm | 32 |
| T120_representation | D_Q_Qij | median_whitened_response_error | 0.00307012 whitened norm | 32 |
| H04_development | R11 | detected | 54 count | 54 |
| H04_development | R11 | eventual_joint | 54 count | 54 |
| H04_development | R11 | timely_joint | 53 count | 54 |
| H04_development | R11 | load_timely | 26 count | 27 |
| H04_development | R11 | line_timely | 27 count | 27 |
| H04_development | R11 | extras | 4 count | full H04 exposure |
| H04_development | R11 | normal_FA | 0 count | full H04 exposure |
| H04_development | R11 | normal_exposure_s | 204 s | full H04 exposure |
| H04_development | R11_NOMINAL | detected | 54 count | 54 |
| H04_development | R11_NOMINAL | eventual_joint | 54 count | 54 |
| H04_development | R11_NOMINAL | timely_joint | 54 count | 54 |
| H04_development | R11_NOMINAL | load_timely | 27 count | 27 |
| H04_development | R11_NOMINAL | line_timely | 27 count | 27 |
| H04_development | R11_NOMINAL | extras | 7 count | full H04 exposure |
| H04_development | R11_NOMINAL | normal_FA | 0 count | full H04 exposure |
| H04_development | R11_NOMINAL | normal_exposure_s | 204 s | full H04 exposure |
| H04_development | ET_REFERENCE | detected | 27 count | 54 |
| H04_development | ET_REFERENCE | eventual_joint | 27 count | 54 |
| H04_development | ET_REFERENCE | timely_joint | 27 count | 54 |
| H04_development | ET_REFERENCE | load_timely | 0 count | 27 |
| H04_development | ET_REFERENCE | line_timely | 27 count | 27 |
| H04_development | ET_REFERENCE | extras | 3 count | full H04 exposure |
| H04_development | ET_REFERENCE | normal_FA | 0 count | full H04 exposure |
| H04_development | ET_REFERENCE | normal_exposure_s | 204 s | full H04 exposure |
| H04_development | ET_CANDIDATE | detected | 27 count | 54 |
| H04_development | ET_CANDIDATE | eventual_joint | 27 count | 54 |
| H04_development | ET_CANDIDATE | timely_joint | 27 count | 54 |
| H04_development | ET_CANDIDATE | load_timely | 0 count | 27 |
| H04_development | ET_CANDIDATE | line_timely | 27 count | 27 |
| H04_development | ET_CANDIDATE | extras | 3 count | full H04 exposure |
| H04_development | ET_CANDIDATE | normal_FA | 0 count | full H04 exposure |
| H04_development | ET_CANDIDATE | normal_exposure_s | 204 s | full H04 exposure |
| H04_development | R12 | detected | 53 count | 54 |
| H04_development | R12 | eventual_joint | 53 count | 54 |
| H04_development | R12 | timely_joint | 52 count | 54 |
| H04_development | R12 | load_timely | 25 count | 27 |
| H04_development | R12 | line_timely | 27 count | 27 |
| H04_development | R12 | extras | 0 count | full H04 exposure |
| H04_development | R12 | normal_FA | 0 count | full H04 exposure |
| H04_development | R12 | normal_exposure_s | 204 s | full H04 exposure |
| X01_local_synthetic | existing_support_Gram | p50_ms | 51.2206 ms | 30 |
| X01_local_synthetic | existing_support_Gram | p95_ms | 80.1585 ms | 30 |
| X01_local_synthetic | existing_support_Gram | p99_ms | 91.9634 ms | 30 |
| X01_local_synthetic | shared_Gram_candidate | p50_ms | 50.6545 ms | 30 |
| X01_local_synthetic | shared_Gram_candidate | p95_ms | 83.7661 ms | 30 |
| X01_local_synthetic | shared_Gram_candidate | p99_ms | 89.0664 ms | 30 |
| X01_local_synthetic | batched_GH31_candidate | p50_ms | 40.8865 ms | 30 |
| X01_local_synthetic | batched_GH31_candidate | p95_ms | 65.5716 ms | 30 |
| X01_local_synthetic | batched_GH31_candidate | p99_ms | 70.5966 ms | 30 |
| X01_local_synthetic | batched_GH31 | maximum_log_evidence_error | 2.27374e-13 absolute error | 6 |
| X02_IEEE39_signature | nominal | joint_correct | 114 count | 240 |
| X02_IEEE39_signature | nominal | conditional_source_correct | 114 count | 240 |
| X02_IEEE39_signature | nominal | normal_selected_event | 12 count | 15 |
| X02_IEEE39_signature | nominal | median_incremental_error | 0.0125134 fraction | 80 |
| X02_IEEE39_signature | recentered | joint_correct | 240 count | 240 |
| X02_IEEE39_signature | recentered | conditional_source_correct | 240 count | 240 |
| X02_IEEE39_signature | recentered | normal_selected_event | 0 count | 15 |
| X02_IEEE39_signature | recentered | median_incremental_error | 0.0125134 fraction | 80 |
| X02_IEEE39_signature | conditioned | joint_correct | 240 count | 240 |
| X02_IEEE39_signature | conditioned | conditional_source_correct | 240 count | 240 |
| X02_IEEE39_signature | conditioned | normal_selected_event | 0 count | 15 |
| X02_IEEE39_signature | conditioned | median_incremental_error | 0.000560709 fraction | 80 |
| X02_IEEE39_signature | nominal | median_relative_amplitude_error | 3.45221 % | 240 |
| X02_IEEE39_signature | recentered | median_relative_amplitude_error | 1.20317 % | 240 |
| X02_IEEE39_signature | conditioned | median_relative_amplitude_error | 0.328828 % | 240 |

## Lectura correcta

- Estado: el error de voltaje no mide localización ni calibra la incertidumbre conjunta.
- E_B: exactitud histórica bajo un prior efectivo auditado; Top-3 usa K=2 conocido.
- T120: mejor ajuste físico no demuestra mejor decisión de soporte.
- H04: desarrollo, catálogo restringido y 204 s normales; no score oficial de hackathon.
- X01: equivalencia sintética y coste local; no nuevas simulaciones IEEE-39.
- C01: incorporar solo tras verificar finalización, denominadores e importación de P07.

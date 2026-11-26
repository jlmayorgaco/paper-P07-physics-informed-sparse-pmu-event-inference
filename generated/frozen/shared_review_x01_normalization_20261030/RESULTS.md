# X01 — resultados ejecutados

**Alcance:** controles algebraicos y fixtures sintéticos; ninguna simulación IEEE-39 nueva ni cambio en C01.

Se compararon 6 fixtures, 137 soportes, 115817 nodos GH31 y 960 coordenadas.

Error máximo de log-evidencia (lotes): 2.274e-13. Error máximo de masa: 4.208e-15. Top-1 y Top-3 coinciden en los seis fixtures.

| Variante | p50 ms | p95 ms | p99 ms |
|---|---:|---:|---:|
| existing_support_Gram | 51.22 | 80.16 | 91.96 |
| shared_Gram_candidate | 50.65 | 83.77 | 89.07 |
| batched_GH31_candidate | 40.89 | 65.57 | 70.60 |

Caché por soporte: 4.632 MB; compartida: 1.381 MB. Reducción: 3.35x. No incluye memoria de los intermediarios de cuadratura.

Control gaussiano lineal independiente: 136 soportes, error máximo log Z = 2.274e-13.

La variante normalizada recupera el prior declarado en ausencia de información. La variante legacy conserva el defecto histórico para replay exacto. No se conoce todavía el cambio en exactitud física al corregirlo.

Los p99 medidos exceden 33.3 ms y el benchmark excluye observador, adquisición y onsets: no demuestra 30 fps. El código histórico ya usaba Gram; compartirlo no constituye una nueva identidad matemática.

Bloqueo para replay físico E_B: faltan D/Q/Qij y las trayectorias originales en esta copia. No se reconstruyen ajustándolos a RAW0001.

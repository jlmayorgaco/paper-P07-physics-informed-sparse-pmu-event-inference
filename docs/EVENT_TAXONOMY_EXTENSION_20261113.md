# Ampliación aditiva de la Figura 2 — 13 de noviembre de 2026

Autorización: el usuario pidió añadir los eventos faltantes sin cambiar lo existente.
La figura mantiene literalmente la inclusión del PDF protegido event_signatures.pdf,
a la misma anchura .98 textwidth. Se añade debajo event_taxonomy_extension.pdf.
Los paneles (a)–(f), el PDF/PNG protegidos y todas sus copias congeladas no cambiaron.

- (g), clase 6: datos RAW0001, generación en bus 2 mientras PMU 29 está ausente.
  Se muestra frecuencia de PMU 2/39 centrada en los tres segundos anteriores
  al onset etiquetado, y disponibilidad observada de PMU 29. El área sombreada
  corresponde al intervalo etiquetado clase 6: 2976.366–2994.800 s.
  La pérdida de PMU ya estaba presente antes del inicio de generación.
- (h), clase 8: definición de la guía, página 13; esquema de observación anormal
  sin correspondencia clara con las clases 1–7. No es una señal medida, un nuevo
  experimento ni una capacidad validada del banco.

El CSV compacto y sus huellas/procedencia están en
generated/event_taxonomy_extension_20261113/. Los timestamps por fila difieren
entre archivos hasta aproximadamente 1e-11 s por representación decimal; se
comprobó alineamiento con tolerancia absoluta 1e-9 s, sin interpolación.
No se abrieron RAW0002 ni resultados C03.

Regeneración: python scripts/build_event_taxonomy_extension.py.
El script verifica el CSV, dibuja solo los paneles añadidos y comprueba que
el PDF protegido no cambió. La vista conjunta event_taxonomy_complete.pdf/png
es un sucesor separado para previsualización; el artículo incluye original
y extensión por separado para conservar también la comprobación automática.

Verificación: Figura 2 en página 5; 19 páginas en artículo, 31 en suplemento;
16 hashes protegidos y ambas figuras presentes. Inspección de PNG a tamaño de
página sin solapamientos nuevos. El escaneo de texto devuelve cero hallazgos.

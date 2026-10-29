# R12 — resultado H04

Gate empírico frente a R11: **False**. No es una versión oficial.

Cada fila usa las mismas observaciones. Acierto = familia y activo correctos antes de OFF.

| Condición | Método | Correctos/18 | BUS31 antes OFF/3 | Extras | FA normal | Abiertos | Restauraciones espurias | F1 detección | Demora diagnóstico s |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
|MATCH|R12|18|3|0|0|0|0|0.9267|0.266|
|MATCH|R11|18|3|0|0|0|0|0.9267|0.266|
|MATCH|R11_NOMINAL|18|3|0|0|0|0|0.9267|0.266|
|MATCH|ET_REFERENCE|9|0|1|0|0|1|0.6196|0.196|
|MATCH|ET_CANDIDATE|9|0|1|0|0|1|0.6254|0.193|
|IN_SUPPORT|R12|18|3|0|0|0|0|0.9267|0.266|
|IN_SUPPORT|R11|18|3|0|0|0|0|0.9267|0.266|
|IN_SUPPORT|R11_NOMINAL|18|3|1|0|0|0|0.9055|0.266|
|IN_SUPPORT|ET_REFERENCE|9|0|1|0|0|1|0.6196|0.196|
|IN_SUPPORT|ET_CANDIDATE|9|0|1|0|0|1|0.6257|0.193|
|OUT_SUPPORT|R12|16|2|0|0|0|0|0.8542|0.198|
|OUT_SUPPORT|R11|17|2|4|0|0|4|0.8180|0.266|
|OUT_SUPPORT|R11_NOMINAL|18|3|6|0|0|4|0.8277|0.266|
|OUT_SUPPORT|ET_REFERENCE|9|0|1|0|0|1|0.6188|0.196|
|OUT_SUPPORT|ET_CANDIDATE|9|0|1|0|0|1|0.6257|0.193|

R12 cambia publicación, no el posterior físico. Los estados y M son idénticos a R11.
No se multiplicó el testigo como otra verosimilitud. No hay período refractario.
La regla usa el inicio estimado, nunca el verdadero. Umbral y seis reportes son heredados.
Puede rechazar eventos con evidencia inicial tardía; este ensayo no demuestra cobertura universal.
12 trayectorias continuas80s;18eventos únicos y54realizaciones pareadas; tres padres de eventos y uno normal.
Solo carga/línea y catálogo conocido. Un punto de operación y ruido1. RAW0002 cerrado.
No hay nueva comparación oficial completa de hackathon ni validación de campo.

![Comparación](figures/comparison.png)

El balance de publicación y la evidencia aún pendiente para el artículo están en paper_closure/PUBLICATION_CLOSURE.md.
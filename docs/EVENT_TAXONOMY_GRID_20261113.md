# Figura 2: sucesor 3×3 autorizado

La instrucción del usuario del 13-nov-2026 solicita paneles iguales, un caso
normal y un pulso visible de pérdida de datos sobre una respuesta física gris.
La figura presenta nueve etiquetas (0–8), no nueve mecanismos físicos validados.

- 0: intervalo RAW0001 de 100–110 s. Se comprobó etiqueta 0 y disponibilidad
  en las ocho PMU. Se muestran tensiones de PMU 2/39, normalizadas por la
  mediana de cada canal en esa ventana.
- 1–5 y 7: las 16 curvas originales se reconstruyen desde los valores congelados,
  comprobando identidad de tiempos y ordenadas. Se conserva el significado
  de los ejes. Por corrección expresa del usuario se conserva el tren de reloj
  ilustrativo en los paneles 5 y 6 (periodos 2 y 4 s, respectivamente;
  el ancho de cada pulso del panel 6 se duplicó a 2 s). Por la siguiente corrección
  del usuario, los pulsos recorren exactamente No/Yes (0/1) sobre el eje
  de disponibilidad de ambos paneles. No representa la cadencia real de informes de 30 Hz.
- 6: frecuencia original de PMU 2 con una máscara ilustrativa de pérdida
  entre −15 y +15 s respecto al inicio de generación (2976.366 s).
  Por nueva instrucción, todo el eje del panel 6 se desplaza +15 s:
  la pérdida aparece de 0 a 30 s y la generación en 15 s. Se conserva
  la ventana previa completa y todas las posiciones relativas; el eje
  se identifica como tiempo desde el inicio de pérdida de datos.
  La respuesta y el nivel Yes son naranja cuando hay datos; el nivel No
  es azul durante la pérdida. La respuesta oculta se conserva en gris
  para explicar qué dejaría de observarse, sin atribuirla a una reconstrucción
  del detector. Leyenda y pie explican que la máscara es ilustrativa,
  no la disponibilidad registrada. El extracto original
  `composite_trace.csv`, incluida `pmu29_missing`, permanece intacto.
- 8: esquema de la clase desconocida, explícitamente sin traza medida ni
  afirmación de validación del detector.

`generated/event_taxonomy_grid_20261113/PROVENANCE.json` conserva hashes de
los ocho CSV de origen, ventanas, normalización y hashes de los extractos.
La alineación temporal de los registros se comprobó a 1 ns de tolerancia
por diferencias de serialización decimal, sin interpolar.
`BUILD_AUDIT.json` registra los 16 canales, sus tamaños y la integridad de
todos los archivos protegidos. El manifiesto protegido permanece intacto.

Regeneración: `python scripts/build_event_taxonomy_grid.py`.
Revisión: `python scripts/verify_protected_figures.py --pdf main.pdf`.
No se ejecuta ni modifica C03, SIM0001 o RAW0002.

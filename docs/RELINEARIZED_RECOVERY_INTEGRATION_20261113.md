# Integración del refinamiento físico — 13 noviembre 2026

Se preservan F01, C03 y todas las campañas previas. El experimento sucesor
está en `experiments/relinearized_recovery_20261113`; protocolo, código de
ejecución y análisis se fijaron antes de sus respectivas etapas. El sello
de resultados enumera 113 archivos. Siete trayectorias no lineales y cuatro
predictores por trayectoria completaron; los once criterios pasan.

Resultado primario: refresco cada tres reportes (0,1 s), sin corrección por
medidas. RMSE de fase de recuperación sobre ocho PMU: 3,19095895 →
0,13878930 grados en la línea 23–24 abierta durante un segundo. Los otros
tres casos de línea también mejoran más del 50%; los controles normal y
de carga cumplen. El refresco cada reporte es solo convergencia; no se
seleccionó retrospectivamente. La observación no lineal sin refrescar la
dinámica mantiene el error alrededor de 3,19 grados.

Solo se integra como validación de predicción condicional. No prueba
inferencia con evento desconocido, FAR, transferencia, IEKF, Hamiltoniano
completo ni utilidad de nuevos priors. El banco necesita tratar de forma
consistente incertidumbre, severidad y evidencia antes de incorporar esta
dinámica. Las ideas adicionales y sus contraejemplos están en
`SHARED_IDEAS_AUDIT_20261113.md`.

## C03: lectura operativa

A las 16:36 Bogotá el proceso 32480 seguía activo. El registro termina en
`INFERENCE F01 TEST 58 72 C03_d6916b53604a`; esa línea se escribe al terminar
los brazos nominales del registro. No existen el resultado final ni su
bloqueo de evaluación. No se consultaron predicciones, verdad ni métricas
parciales de TEST. No se modificó ni reinició la campaña.

## Integración y comprobaciones

- Apéndice U: ecuación de propagación, Tabla 29, Figura 18 y límites.
- Figura 15: módulo de refinamiento con estado predicho, restricciones y
  Jacobiano; conexión con grafos y Bayes sin presentar módulos pendientes
  como ejecutados dentro del banco. Se preserva la versión anterior.
- Artículo 19 páginas; suplemento 38 tras corregir el orden del flotante.
- Inspección visual de artículo p.6 y suplemento pp.32, 37 y 38: texto,
  ecuaciones, tabla, leyenda y flujo legibles; sin solapamientos observados.
- Dieciséis hashes protegidos verificados; las figuras protegidas siguen
  visibles en páginas 5 y 6. Nueve paneles y dieciséis curvas heredadas.
- Escaneo editorial: cero coincidencias. Referencias resueltas; persisten
  advertencias de la clase y fuentes, por lo que no se afirma un log vacío.
- Compilación aislada y manifiesto: véase el registro generado
  `output/source/SOURCE_PACKAGE_VALIDATION.json` para el resultado final.
  Resultado PASS: 794 entradas verificadas, texto y paginación idénticos
  en artículo (19) y suplemento (38). SHA-256 del paquete:
  `0e953512b2c7a8d30e88b3004b28f968a12ba0cda25d9a340c70841bfe7449e4`.
  El generador de resultados también se ejecutó dentro de la copia aislada
  y verificó sus 113 entradas selladas. Los mismos hashes coinciden con los
  bytes preparados en el índice de Git.
- El ZIP de fuentes se conserva localmente y queda excluido de Git por
  tamaño. La publicación sigue Git→Overleaf; no se verificó una compilación
  remota autenticada ni se abrió Overleaf.

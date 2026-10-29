# R11: discrepancia observacional constante

Modelo y banco R10B conservados: y_k = M_theta(x_k,z_k) + b_theta + epsilon_k.
Se estima b_theta = media del prefijo - referencia fisica theta, usando solo
los primeros 300 reportes. Se congela desde entonces, Q_b=0. No se ajusta con
ventanas de evento ni se proyectan canales o firmas. Solo se modifica el origen
observacional del filtro; matrices dinamicas, firmas, ruido, pesos, umbrales y
publicacion son identicos a R10B. F01 no se recalibra. R/X siguen constantes.
El termino b es discrepancia de observacion/modelo; no identifica impedancias.
La estimacion es plug-in: su covarianza no se marginaliza completamente y no
se afirma inferencia optima o calibracion de probabilidades. Requiere prefijo
estacionario sin intervenciones; no valida arranque dentro de un evento.

Puertas: intercepto usa exclusivamente prefijo; no actualizacion tras arranque;
invariancia de toda firma temporal; nominal b=0 reduce a R10B; causalidad;
referencia fisica y bancos del padre conservados; estados continuos sin resets.

H03 nuevo, antes de sortear: tres padres de seis cargas/lineas y un padre normal,
80 s cada uno, MATCH/IN_SUPPORT/OUT_SUPPORT. 12 registros,18 eventos unicos,
54 realizaciones pareadas; un nivel de ruido, catalogo conocido. Semillas PLAN.
Comparadores R10B, R08, V9 y ambos ExtraTrees congelados; ablaciones nominales.
Predicciones selladas antes de verdad. No retocar tras examen.
Criterio por condicion frente R10B: no perder aciertos/BUS31, no aumentar extras,
FA normales ni abiertos; al menos una mejora estricta OUT. No promocion automatica.
Recursos maximo3 registros, BLAS/Julia1; fases secuenciales. RAW0002 excluido.

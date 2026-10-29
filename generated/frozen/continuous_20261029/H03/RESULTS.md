# R11 — discrepancia inicial congelada

Cumple el criterio empírico predeclarado en este holdout pequeño.

Modelo: y = medicion fisica(theta,x,z) + b_theta + ruido. El intercepto b se
estima una sola vez desde 300 reportes iniciales y permanece constante. No se
proyectan firmas temporales ni se reajusta la planta. La incertidumbre del
intercepto se trata de forma plug-in; no se afirma inferencia optima.

Doce trayectorias continuas de80s:18eventos unicos y54realizaciones pareadas,
tres padres de eventos y uno normal. Carga/linea, fuentes conocidas, ruido1.
Cada columna beforeOFF exige familia y origen correctos antes de restauracion.

| Condición | Método | Correctos antes OFF | Extras | FA normal | Sin cierre | F1 detección (%) | Demora diagnóstico (s) | Demora cierre (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MATCH | R11 | 18/18 | 0 | 0 | 0 | 92.339 | 0.267 | 0.180 |
| MATCH | R11_NOMINAL | 18/18 | 0 | 0 | 0 | 92.339 | 0.267 | 0.180 |
| MATCH | R10B | 18/18 | 0 | 0 | 0 | 92.339 | 0.267 | 0.180 |
| MATCH | R10B_NOMINAL | 18/18 | 0 | 0 | 0 | 92.339 | 0.267 | 0.180 |
| MATCH | R08 | 18/18 | 0 | 0 | 0 | 92.339 | 0.267 | 0.180 |
| MATCH | V9 | 18/18 | 0 | 0 | 0 | 89.122 | 0.684 | 0.480 |
| MATCH | ET_REFERENCE | 10/18 | 0 | 0 | 0 | 63.944 | 0.198 | 0.192 |
| MATCH | ET_CANDIDATE | 10/18 | 0 | 0 | 0 | 65.037 | 0.191 | 0.192 |
| IN_SUPPORT | R11 | 18/18 | 0 | 0 | 0 | 92.339 | 0.267 | 0.180 |
| IN_SUPPORT | R11_NOMINAL | 18/18 | 0 | 0 | 0 | 92.339 | 0.267 | 0.180 |
| IN_SUPPORT | R10B | 18/18 | 0 | 0 | 0 | 92.339 | 0.267 | 0.180 |
| IN_SUPPORT | R10B_NOMINAL | 16/18 | 14 | 1 | 3 | 37.082 | 0.197 | 0.180 |
| IN_SUPPORT | R08 | 16/18 | 14 | 1 | 3 | 37.082 | 0.197 | 0.180 |
| IN_SUPPORT | V9 | 16/18 | 14 | 1 | 3 | 36.528 | 0.688 | 0.480 |
| IN_SUPPORT | ET_REFERENCE | 10/18 | 0 | 0 | 0 | 63.884 | 0.198 | 0.192 |
| IN_SUPPORT | ET_CANDIDATE | 10/18 | 0 | 0 | 0 | 65.037 | 0.191 | 0.192 |
| OUT_SUPPORT | R11 | 18/18 | 6 | 0 | 0 | 86.758 | 0.267 | 0.180 |
| OUT_SUPPORT | R11_NOMINAL | 18/18 | 6 | 0 | 0 | 86.785 | 0.267 | 0.180 |
| OUT_SUPPORT | R10B | 12/18 | 18 | 1 | 4 | 30.818 | 0.197 | 0.187 |
| OUT_SUPPORT | R10B_NOMINAL | 12/18 | 15 | 1 | 4 | 32.756 | 0.193 | 0.187 |
| OUT_SUPPORT | R08 | 12/18 | 15 | 1 | 4 | 32.756 | 0.193 | 0.187 |
| OUT_SUPPORT | V9 | 12/18 | 15 | 1 | 4 | 32.360 | 0.688 | 0.487 |
| OUT_SUPPORT | ET_REFERENCE | 10/18 | 0 | 0 | 0 | 63.884 | 0.198 | 0.192 |
| OUT_SUPPORT | ET_CANDIDATE | 10/18 | 0 | 0 | 0 | 65.037 | 0.191 | 0.192 |

F1 es deteccion por reporte, no score oficial de hackathon. Demoras condicionales
a eventos disponibles; leerlas con omisiones y extras. Ambas versiones ExtraTrees
son modelos congelados, sin reentrenar. La ablacion nominal separa la mezcla de
redes del intercepto comun. R10B usa exactamente los mismos bancos fisicos.

## Recuperaciones y regresiones

| Condición | Referencia | Recupera R11 | Pierde R11 | Ambos aciertan | Ambos fallan |
| --- | --- | --- | --- | --- | --- |
| IN_SUPPORT | ET_CANDIDATE | 8 | 0 | 10 | 0 |
| MATCH | ET_CANDIDATE | 8 | 0 | 10 | 0 |
| OUT_SUPPORT | ET_CANDIDATE | 8 | 0 | 10 | 0 |
| IN_SUPPORT | ET_REFERENCE | 8 | 0 | 10 | 0 |
| MATCH | ET_REFERENCE | 8 | 0 | 10 | 0 |
| OUT_SUPPORT | ET_REFERENCE | 8 | 0 | 10 | 0 |
| IN_SUPPORT | R08 | 2 | 0 | 16 | 0 |
| MATCH | R08 | 0 | 0 | 18 | 0 |
| OUT_SUPPORT | R08 | 6 | 0 | 12 | 0 |
| IN_SUPPORT | R10B | 0 | 0 | 18 | 0 |
| MATCH | R10B | 0 | 0 | 18 | 0 |
| OUT_SUPPORT | R10B | 6 | 0 | 12 | 0 |
| IN_SUPPORT | R10B_NOMINAL | 2 | 0 | 16 | 0 |
| MATCH | R10B_NOMINAL | 0 | 0 | 18 | 0 |
| OUT_SUPPORT | R10B_NOMINAL | 6 | 0 | 12 | 0 |
| IN_SUPPORT | R11_NOMINAL | 0 | 0 | 18 | 0 |
| MATCH | R11_NOMINAL | 0 | 0 | 18 | 0 |
| OUT_SUPPORT | R11_NOMINAL | 0 | 0 | 18 | 0 |
| IN_SUPPORT | V9 | 2 | 0 | 16 | 0 |
| MATCH | V9 | 0 | 0 | 18 | 0 |
| OUT_SUPPORT | V9 | 6 | 0 | 12 | 0 |

## Hipotesis estaticas

| Registro | Condición | Tipo | Red verdadera | Red con más masa al final | Masa de la verdadera |
| --- | --- | --- | --- | --- | --- |
| S001 | MATCH | event | nominal | nominal | 1.000 |
| S002 | MATCH | normal | nominal | local_plus3 | 0.028 |
| S003 | MATCH | event | nominal | nominal | 1.000 |
| S004 | IN_SUPPORT | event | local_plus3 | local_plus3 | 1.000 |
| S005 | OUT_SUPPORT | event | outside_finite_support | nominal | — |
| S006 | IN_SUPPORT | normal | global_minus2 | global_minus2 | 0.490 |
| S007 | MATCH | event | nominal | nominal | 1.000 |
| S008 | IN_SUPPORT | event | local_minus3 | local_minus3 | 1.000 |
| S009 | OUT_SUPPORT | event | outside_finite_support | local_minus3 | — |
| S010 | IN_SUPPORT | event | global_plus2 | global_plus2 | 1.000 |
| S011 | OUT_SUPPORT | event | outside_finite_support | nominal | — |
| S012 | OUT_SUPPORT | normal | outside_finite_support | global_minus2 | — |

Los pesos relativos pueden concentrarse aunque todas las redes esten equivocadas.
No son probabilidades calibradas. Prefijo estacionario requerido; no se valida
arranque en un evento, todos los39buses o todas lasfamilias. RAW0002 excluido.

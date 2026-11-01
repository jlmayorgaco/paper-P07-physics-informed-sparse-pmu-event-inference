# X04: comprobación física de recuperación en F01

Se ejecutaron 38 trayectorias de 8 s: una integración por
trayectoria, 241 reportes a 30 fps, cero reinicios. Todos los estados y parámetros
estructurales F01 se preservaron. Los prefijos contrafactuales coinciden
exactamente; 90 archivos protegidos conservan hash.

Diseño: cargas previas BUS7/BUS24 de +8%, ON 2 s/OFF 3 s; nueva carga de
+0.06% tras 0.5 o 2 s. Pares 18/27,16/21,3/21; horizonte 1.5 s.
Cinco fuentes, cuatro historias de recuperación, 12 celdas comparativas.
Las 38 integraciones incluyen controles y diferencias para incertidumbre.
No son 38 ensayos independientes de clasificación.

## Resultados

- Razón mediana de separación con trayectoria conocida: 1.000594.
- Con una dirección incierta de severidad previa: 0.853185.
- Celdas de separación incierta mayor que equilibrio: 0/12.
- Exactitud binaria media de firmas de equilibrio: 98.3472%.
- Exactitud binaria media de firmas condicionadas: 98.3472%.
- Diferencia media: 0.000000 puntos; 2 celdas empeoran.

No se observa ventaja media de clasificación. No interpretar los muchos draws
de ruido como padres independientes ni convertir este empate en prueba de
equivalencia universal. El control de incertidumbre aumenta la covarianza:
su penalización de separación a firma fija es esperable algebraicamente.
La comparación conocida muestra por separado cómo cambia la geometría física.

## Lo que no se ejecutó

No es R11 ni M3H: familia, onset, dos candidatos y recuperación sin nuevo
evento son conocidos. Se emplean secantes de amplitud finita, no operadores
tangentes analíticos. Los 47 canales son los del operador F01, sin ángulo de
corriente BUS39. El ruido es gaussiano en innovaciones del filtro congelado,
no una nueva identificación del ruido ni una realización completa del modelo
truncado. La severidad previa entra mediante una aproximación lineal de rango
uno; no se estima todo el estado causal ni se muestrean historias no lineales.

La distancia perfila amplitudes no negativas; la evidencia integra una amplitud
gaussiana firmada. Son dos diagnósticos diferentes, no una cota de error común.
No se comparan porcentajes con el prototipo X03, cuyos sensores/planta difieren.

## Decisión editorial

Incluir el control como límite de una hipótesis física, sin cambiar R11/C01
ni afirmar un nuevo algoritmo. La recuperación cambia la referencia y puede
cambiar la firma, pero no se ha probado que aumente información o aciertos.
Adjuntos, soportes simultáneos, calibración y refinamiento certificado siguen
siendo propuestas, no resultados del artículo.

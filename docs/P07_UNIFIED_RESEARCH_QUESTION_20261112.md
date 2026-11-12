# Pregunta unificadora: medición, incertidumbre y recuperación

El problema central sigue siendo atribuir una intervención nueva mientras
persiste la respuesta de otra. Dos recursos pueden ayudar: conservar la
distribución del estado de recuperación y observar una diferencia eléctrica
que las causas competidoras no puedan explicar. Son mecanismos distintos;
conviene medir su interacción sin confundir memoria con mediciones nuevas.

## Argumento científico

1. El estado físico no vuelve al equilibrio cuando termina la intervención.
2. Su media no contiene por sí sola toda la incertidumbre de recuperación.
3. Una diferencia de voltaje puede parecer compatible con varias causas;
   las corrientes terminales pueden aportar una componente discriminativa.
4. El beneficio depende de la covarianza conjunta, el horizonte y la planta.
5. Conservar historias solo merece su costo si cambia decisiones oportunas
   bajo un presupuesto de alarmas predefinido.

La aportación aspiracional es establecer cuándo la memoria de recuperación y
la información eléctrica complementaria resuelven esa ambigüedad, y cuándo
fallan. No se reivindica una nueva ecuación de Kirchhoff, una nueva identidad
de Schur ni superioridad sobre toda distribución Markoviana de estados.

## Evidencia y orden

| Pregunta | Evidencia | Alcance |
|---|---|---|
| ¿El procedimiento completo supera a comparadores? | C02 cerrado | Comparación de procedimientos con 18 padres, no mecanismo aislado |
| ¿La continuidad física importa? | A01; contraste carry/reset de C03 cuando cierre | A01 a umbral fijo; C03 pendiente |
| ¿La representación de recuperación cambia decisiones? | history/carry en C03; futuro C04 | C03 también cambia compresión de incertidumbre y memoria de propuestas |
| ¿Qué añaden las corrientes? | Nuevo diagnóstico nominal de canales | Firmas y covarianza de referencia; no cobertura ni FAR del detector |
| ¿Sobrevive al cambio de planta? | C03 P2 cuando termine | Predictor y umbrales fijados en F01 |
| ¿Memoria e información de corriente se complementan? | Hipótesis para sucesor independiente | Requiere controles cruzados con nueva calibración y holdout |

## Integración editorial

La figura de separación debe mostrar qué cambia con la observación disponible
y evitar presentar energía determinista como probabilidad de éxito. El texto
principal resume el resultado validado y su límite. El suplemento conserva
operadores, hipótesis de ruido, derivación, comprobaciones y procedencia.

El prototipo externo corregido es material de desarrollo: permite comprobar
terminales y mostrar por qué una observación aparentemente local puede estar
mal definida. Sus tasas sintéticas no se suman a las poblaciones de P07.

## Próxima prueba causal si el diagnóstico lo justifica

Cruzar representación de recuperación (media frente a media+covarianza, con
la misma política de propuestas) y canales (V frente a V+I). Reconstruir cada
filtro con su medición y covarianza; recalibrar cada brazo en CAL al mismo
objetivo. Un nuevo TEST independiente mide interacción por padre, cobertura
oportuna, exposición normal, extras y cómputo. Este experimento no se añade
retroactivamente a C03 ni se presenta como ejecutado.

La fuerza del artículo vendrá de responder esta pregunta con controles que
puedan refutarla, incluyendo resultados pequeños o negativos. Más componentes
por sí solos no resuelven la objeción científica.

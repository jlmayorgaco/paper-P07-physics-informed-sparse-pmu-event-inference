# Auditoría e integración de los prototipos físicos externos

Estado: exploración reproducida; no incorporada como resultado del estimador P07.
Entradas: `PMU_Investigacion_Fisica_IEEE39_Experimentos.zip`, informe técnico y
texto adjunto del 12 de noviembre. Procedencia y hashes en
`generated/external_physics_audit_20261112.json`. El ZIP se extrajo únicamente
en `build/external_physics_20261112`; sus programas se leyeron antes de ejecutar
`python -B build/external_physics_20261112/tests.py`. Esa ejecución importa y
regenera ambos prototipos. Los originales en Downloads se conservaron.

## Dictamen

El aporte aprovechable es una hipótesis experimental: las corrientes terminales
pueden separar fuentes cuyas firmas de voltaje se parecen, y la utilidad depende
de la incertidumbre de recuperación y del modelo de medición. Esto puede
explicar éxitos y fallos del banco actual. No demuestra una mejora de ese banco,
una nueva teoría de observabilidad ni transferencia a otra planta.

El informe usa manuscritos anteriores y no tenía acceso al repositorio científico.
Sus propuestas deben reconciliarse con P07: ya existen operadores DAE conmutados,
47 coordenadas de medición, diagnósticos de firmas, incertidumbre de severidad,
C02, C03 en ejecución y el diseño C04. No hay que presentar estos componentes
como capacidades recién añadidas por el ZIP.

## Qué se verificó

- Las seis tasas estáticas redondeadas se reproducen: V 89.96/68.44/40.15 % y
  V+I 95.63/85.56/64.85 % en escalas de ruido 1/5/20.
- Rango complejo 14 reproducido para el operador construido en el paquete.
- Las medianas y máximos temporales coinciden con los JSON entregados a precisión
  numérica; el error máximo queda en el artefacto de auditoría.
- Las cuatro funciones de prueba entregadas terminan con PASS.
- La tabla de 46 ramas y las cinco columnas de buses utilizadas coinciden con
  la fuente primaria MATPOWER descargada durante esta auditoría.
- No se ejecutó ni modificó C03, ni se abrió su verdad TEST.

## Hallazgos que impiden importar las cifras directamente

1. **Extremo de corriente incorrectamente identificado.** `admittance` forma
   únicamente filas de corriente FROM. `branch_voltage_current_response` aplica
   esas filas también cuando la PMU está en TO. Ocurre en 7/8 sitios: 2, 5, 6,
   19, 22, 29 y 39. Son corrientes sintéticas de ramas, pero no las corrientes
   locales declaradas por los comentarios. En un circuito pi no basta cambiar
   el signo: el charging y los taps distinguen los extremos. Para tap real a,
   las filas correctas son I_f=(y+jb/2)V_f/a²-yV_t/a e
   I_t=(y+jb/2)V_t-yV_f/a. Recalcular firmas, ruido, rango y ablaciones en una
   copia sucesora antes de usar ese prototipo como ejemplo instrumental.
2. **Pruebas más débiles que sus nombres.** `test_ybus_passivity` comprueba
   simetría y reconstrucción de una inyección construida con el mismo Y; no
   comprueba pasividad ni orientación física. `test_temporal_continuity` no
   compara estados a ambos lados de OFF y usa `any`, no `all`, para recuperación.
   El código sí pasa el estado final entre intervalos, pero esa propiedad no
   queda probada por la aserción. Añadir verificaciones independientes si se
   reutiliza el ejemplo.
3. **Convención de OFF.** El reporte de t=2 s procede del intervalo anterior,
   y el flujo abierto se mantiene para t<=2. Es una convención izquierda;
   no coincide con el reporte posterior al cambio del contrato F01. La similitud
   temporal excluye muestras próximas a OFF, lo que limita su efecto en esa
   métrica, pero no valida pasos, continuidad ni estimación PMU en el cambio.
4. **Información incremental no identificada por cosenos.** Frecuencia y ROCOF
   son derivadas ideales; las escalas elegidas no representan su covarianza
   conjunta con ángulos ni entre reportes. Un pequeño cambio de coseno depende
   de esas escalas y no prueba que dichos canales reales aporten poco.
5. **Contrato estadístico distinto.** Son 18 firmas y realizaciones de ruido
   condicionadas al mismo modelo; 2700 réplicas no son trayectorias físicas
   independientes. Permiten evaluar precisión Monte Carlo en ese modelo fijo,
   sin sostener generalización entre fuentes, plantas o puntos de operación.
   El perfilado admite amplitud real de cualquier signo también para líneas:
   mide forma espacial, no la intervención de apertura fija usada por P07.
6. **El rango no equivale a observabilidad dinámica.** 14/39 concierne a un
   operador complejo instantáneo con inyecciones arbitrarias y ese mapa proxy.
   No determina el rango del estado DAE aumentado, de las 47 coordenadas reales
   ni de un catálogo de causas. No extrapolar el déficit de 25 dimensiones.

## Qué integrar y dónde

| Idea | Disposición en P07 | Evidencia necesaria |
|---|---|---|
| Utilidad incremental de corrientes | Prioridad alta: diagnóstico complementario a la figura de separación | Operadores F01 y terminales originales; covarianza marginal/condicional correcta |
| Ambigüedad por pareja y horizonte | Prioridad alta: explicar fallos, además del promedio de cobertura | Diagnóstico congelado en DEV y contraste posterior con errores |
| Incertidumbre de recuperación | Prioridad alta: enlazar con C04 media/covarianza | Covarianza propagada; igual política de propuestas entre controles de fusión |
| Mapa de impacto en buses ocultos | Suplemento o estudio posterior | Validación contra estado de simulación reservado para scoring; intervalos y fallos |
| Kron y propagación espacial | Contexto o ejemplo didáctico | Identificar claramente el modelo reducido; no una contribución novedosa |
| Group LASSO, TV y wavelets | Posponer | Cambian estimador/alcance; requieren nueva calibración, contratos y comparación |
| Porcentajes y ranking de PMU del ZIP | No incluir en resultados principales | Primero corregir terminales y trasladar el contraste al contrato P07 |

## Formulación útil para el diagnóstico de canales

Para dos medias candidatas fijas, mismo horizonte y covarianza gaussiana común
positiva definida, partir la diferencia d=(d_V,d_I) y Sigma en bloques. Entonces

    S = Sigma_II - Sigma_IV Sigma_VV^{-1} Sigma_VI
    d_I|V = d_I - Sigma_IV Sigma_VV^{-1} d_V
    D_VI = 1/2 d_V' Sigma_VV^{-1} d_V + 1/2 d_I|V' S^{-1} d_I|V.

El segundo término mide separación adicional de I condicionada a V, para esas
hipótesis. Es una identidad estándar; no una nueva garantía del banco. Usar
soluciones lineales estables, no inversiones numéricas explícitas. Con canales
derivados y covarianza singular, no aplicar directamente la fórmula SPD.
Con covarianzas distintas, conservar los términos de traza y log-determinante.
Si se perfila severidad u otra nuisance, optimizar consistentemente en cada
contrato; no interpretar automáticamente la diferencia perfilada como KL.

La propuesta K=C Phi B también necesita el término directo D delta(t-s) cuando
la eliminación algebraica lo introduce. Una carga puede producir salto
algebraico instantáneo. Para líneas hacen falta operadores/topología, offsets
y condiciones de salto/continuidad; una columna B genérica no los sustituye.
Estos detalles conectan con las ecuaciones existentes del artículo.

## Experimento acotado propuesto, separado de C03

1. Terminar primero la implementación y verificación del control C04 ya diseñado.
2. Crear un diagnóstico sucesor de canales con el predictor nominal y el mismo
   prefijo, eventos, terminales y realizaciones de ruido. Conservar la hipótesis
   BUS5 5–6 y su procedencia. No rediseñar C03 al mirar sus resultados.
3. Comparar V; V+I; V+I+f+ROCOF. Empezar con separación de firmas en DEV; para
   evaluar decisiones hay que reconstruir los filtros con sus submatrices de
   covarianza y seleccionar umbrales propios en CAL con el presupuesto común.
   Poner canales a cero no constituye esta ablación.
4. Fijar antes del nuevo TEST los horizontes, nivel de ruido, parejas a estudiar,
   medidas de incertidumbre, métricas y denominadores. Las parejas 16/24 y 7/31
   son hipótesis surgidas de este ZIP, no dificultades demostradas en F01.
5. Reportar cobertura oportuna, omisiones, extras, exposición normal y costo;
   intervalos por padre y todas las fallas. Medir si la separación predice los
   errores, incluyendo contraejemplos. No añadir pruebas grandes si el diagnóstico
   DEV no cambia la explicación científica.

## Plan visual y narrativo

Mantener una tesis: explicar una intervención nueva cuando otra aún se recupera.
Las figuras 1 y 4 ya presentan problema y física; no añadir otro diagrama de
arquitectura equivalente. Si la nueva evidencia aporta explicación, transformar
la figura actual de firmas en tres paneles: separación por pareja/horizonte,
ganancia condicional de las corrientes y contraste con errores reales. Enviar
el mapa espacial condicionado al suplemento. Las imágenes externas enlazadas
en el texto pegado no constituyen figuras de estos experimentos.

La novedad defendible será una respuesta medible sobre continuidad, compresión
de incertidumbre y atribución durante recuperación bajo presupuesto calibrado.
Las ecuaciones de red, Kron, funciones de respuesta y Group LASSO son antecedentes.

## Fuentes primarias consultadas

- [MATPOWER case39](https://raw.githubusercontent.com/MATPOWER/matpower/master/data/case39.m): contraste directo de la transcripción; modelo público distinto del SGSMA.
- [Anguluri, Sankar y Kosut](https://arxiv.org/abs/2201.07907): localización de entradas dispersas y estado inicial desconocido mediante Group LASSO; antecedente directo, ya reconocido en P07. Verificar orden de autores frente al informe.
- [Barati, LCQP/ACOPF](https://arxiv.org/abs/2406.11899): optimización de flujo de potencia; no respalda atribución de eventos PMU ni la ganancia de las corrientes. Citar solo si se usa su formulación o algoritmo de optimización.

No se añadieron cifras exploratorias, nuevas reivindicaciones ni citas ornamentales
al manuscrito. Esta auditoría y su artefacto son la propuesta de integración.

# E_i en IEEE-39: resultado del candidato separado

Se completaron 142 trayectorias: 57 para diccionario/comprobación y 85 de prueba. Las 80 intervenciones y cinco controles se observaron con tres semillas, para 255 registros. No se cambió la planta, la medición, R11 o C01.

| Modelo | Error mediano de respuesta (%) | Presencia y origen correctos | Selecciones de evento en controles | Error relativo mediano de intensidad (%) |
|---|---:|---:|---:|---:|
| Nominal | 1.251 | 114/240 | 12/15 | 3.452 |
| Recentered | 1.251 | 240/240 | 0/15 | 1.203 |
| Conditioned | 0.05607 | 240/240 | 0/15 | 0.3288 |

El recentrado corrige el origen en este piloto. E_i mejora el modelo de respuesta y la intensidad, pero no suma aciertos de localización: ambos comparadores corregidos están en el techo de la prueba. No se sube retrospectivamente el ruido ni se cambian umbrales para fabricar una diferencia.

Cambio medio pareado de error de respuesta: -1.154 puntos porcentuales, intervalo [-1.305, -0.9999]. Cambio medio de error relativo de intensidad: -0.7383 puntos, intervalo [-0.8978, -0.5816].

El error de respuesta se evalúa con origen y amplitud generadores para aislar la aproximación. El error de intensidad usa la estimación bajo el origen verdadero; para los dos modelos corregidos ese origen coincide con su selección en todos los casos. Las tres semillas comunes se reutilizan entre casos. Los intervalos describen variación de casos condicionada a esas realizaciones, no toda la población de ruido.

Alcance: una carga P/Q, cuatro buses, un parámetro escalar de operación, onset y OFF conocidos. El contexto y la intensidad se estiman solo desde las PMU; el origen verdadero queda reservado. No es una prueba del detector causal ni una evaluación de todas las familias. El recentrado es un offset del prefijo observado, no el algoritmo histórico de reconstrucción AC.

Todas las trayectorias conservaron estados en ON/OFF, emitieron 301 reportes y conservaron parámetros estructurales. Los controles de semipasos y la frontera de lectura están en los JSON/CSV. Las masas saturadas y log-loss cero no certifican calibración.

Fuentes: protocol/PLAN.json y FREEZE.json; results/SUMMARY.csv, PER_RECORD.csv, FIDELITY.csv, PAIRED_INTERVALS.csv y DERIVATIVE_CHECKS.csv. La copia utilizada por P07 se verifica mediante generated/frozen/ei_x02_20261030/MANIFEST.json.

El cambio de la figura de eventos está prohibido. El unifilar y el diagrama causal aprobado permanecen intactos. RAW0002 no se abrió.

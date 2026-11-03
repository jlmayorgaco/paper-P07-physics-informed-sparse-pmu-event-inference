# Revisión de claridad del artículo

## Diagnóstico y resultado

El borrador mezclaba el método causal, la historia de los estimadores de
estado, el banco simultáneo y una propuesta futura. La versión revisada
sigue un argumento: qué observa la PMU, qué historia física predice el método,
cómo compara historias, qué decide y qué añade cambiar una firma.
Los resultados históricos permanecen disponibles con sus límites.

## Cinco pasadas de escritura

| Pasada | Hallazgo concreto | Revisión aplicada |
|---|---|---|
| Claridad y concisión | La introducción competía entre reconstrucción, atribución e información límite | Una situación física abre el texto; cada contribución lleva a una comparación concreta |
| Actor y operación | “Physical prediction” podía sugerir una simulación DAE completa por reporte | Se distinguen predictor local causal y trayectorias no lineales del ensayo E_i |
| Arquitectura | Auditorías del banco antiguo interrumpían el argumento entre resultados y conclusión | Se conserva ese estudio en suplemento/corpus; el artículo presenta método, prueba causal y componente X02 |
| Terminología | Diez segundos de historia podía leerse como 300 onsets evaluados en cada reporte | Se especifican el estado retenido y la propuesta congelada de lags 0–18; no se cambia el código |
| Cifras y alcance | Mejor ajuste, mejor origen y mejor intensidad podían confundirse | Tabla y figura separan las tres métricas; se mantiene el empate de origen y la mejora de intensidad |

## Correcciones prioritarias completadas

1. Se separan hipótesis físicas y reglas estadísticas; no aparece una PINN
   o un componente aprendido que no exista.
2. Se define la diferencia entre ON/OFF verdadero, alarma y recuperación.
3. El ensayo X02 declara familia y tiempos conocidos, contexto escalar,
   prefijo PMU, cuatro fuentes y semillas comunes; no adopta el score causal.
4. El generador produce cifras y gráficos desde la copia con hashes. No se
   corrigen parámetros después de leer el test.
5. La imagen de eventos y el diagrama causal aprobado se conservan. El nuevo
   diagrama corresponde a las tres ecuaciones realmente comparadas.

## Alcance de esta revisión

Es una revisión técnica y editorial local, no tres arbitrajes independientes
ni una certificación de novedad mundial. La contribución no se atribuye a
Bayes, Kalman, el nombre tensor o una proyección clásica. Queda completar
C01, interpretar sus resultados, revisar las referencias y cerrar metadatos
y aprobación de coautores. El estado de envío sigue pendiente.

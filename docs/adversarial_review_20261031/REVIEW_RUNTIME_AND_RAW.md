# Disponibilidad del runtime y transferencia a RAW0001

Auditoría de alcance y capacidad, no ensayo de desempeño. Se leyeron código y configuraciones congeladas y, de RAW0001, únicamente columnas `Event` y `DATA_PRESENT` de los ocho CSV ya abiertos para calibración histórica. No se ejecutó R11 sobre estos datos. No se leyó RAW0002 ni salidas parciales/verdad de C01.

## Hallazgo reproducido: faltantes después del arranque

En [core_v6.py](C:/Users/walla/Documents/Github/SGSMA26-Physics-Informed-AD/experiments/PAPER_CONFIRMATORY_C01/run/runtime/core_v6.py:35), `Observations.process` rechaza valores no finitos fuera de los cuatro reportes iniciales de frecuencia/ROCOF.

`checks/runtime_scope_checks.py` extrae únicamente la clase mediante AST, evita su constructor y cualquier carga de modelos/datos de campaña, configura transformaciones identidad e introduce un NaN en una magnitud de tensión a `t=20 s`. La clase real devuelve:

```text
Unsupported missing data outside initial f/ROCOF warmup
```

Esto prueba que esa ruta no admite pérdida de datos posterior al arranque. No prueba que un adaptador futuro no pueda gestionarla. El runner actual además contiene una prohibición explícita de acceso RAW en [run.py](C:/Users/walla/Documents/Github/SGSMA26-Physics-Informed-AD/experiments/E5_VALIDATION_PAPER/M03_R11_FROZEN_DISCREPANCY/observer/run.py:52). Esa guardia se preservó.

## Inventario observado

Los ocho CSV tienen 161.379 filas por PMU. BUS29 tiene 9.200 filas con `DATA_PRESENT=0`; las otras siete PMU tienen `DATA_PRESENT=1` en todas las filas. En BUS29 hay 8.646 etiquetas `Event=5` y 554 `Event=6`. BUS2 y BUS39 incluyen, respectivamente, 22 y 55 etiquetas `Event=7`. Las filas son muestras correlacionadas, no ensayos independientes ni predicciones de un clasificador.

El catálogo leído en `physics/source_runtime/model/assets.json` de R11 contiene:

- Cargas: BUS3, BUS4, BUS7, BUS15, BUS16, BUS20, BUS24, BUS26 y BUS31.
- Líneas: 3–4, 4–14, 9–39, 14–15, 16–17, 17–18, 23–24, 26–27 y 26–29.

La limitación a cargas/líneas también está declarada en el manuscrito. El inventario de faltantes junto al comportamiento del runtime muestra una incompatibilidad concreta con un replay directo completo. No se midió cuántas decisiones perdería el método, ni se infiere una precisión global de estos conteos.

## Condiciones de F01 que impiden extrapolar una precisión SIM

El [contrato F01](C:/Users/walla/Documents/Github/SGSMA26-Physics-Informed-AD/SIM0001_JuliaPD_F01/START_HERE.md:60) documenta que el piloto no reproduce toda la historia de RAW0001, omite cambios previos de generación y no iguala los estados físicos con sólo restar medias. BUS5 usa la hipótesis histórica 5–6; las asignaciones CT no están confirmadas y BUS39 sigue parcialmente validado. El generador no aplica el campo de covarianza entre familias y añade ruido de frecuencia/ROCOF después del estimador. Por ello, una perturbación de R/X no cubre todos los errores relevantes de dominio.

El mismo contrato clasifica RAW0001 como calibración retrospectiva. Congelar el código hoy evita nuevo ajuste, pero no borra esa dependencia histórica.

## Cero alarmas y exposición

H04 publica 204 s normales por método entre condiciones pareadas. Como ilustración de planificación, suponiendo un proceso Poisson homogéneo, cero alarmas en esa exposición deja una cota unilateral del 95% de `-log(0.05)/(204/3600) = 52.8659` alarmas/h. La independencia y homogeneidad no están establecidas en H04, por lo que no se presenta como intervalo válido de esa campaña. Sí muestra por qué cero alarmas en unos minutos no certifica operación segura durante horas.

## Archivos reproducibles

Ejecutar desde el repositorio P07:

```powershell
python docs/adversarial_review_20261031/checks/runtime_scope_checks.py
```

El JSON asociado conserva el hash del código inspeccionado, inventario completo, catálogo y limitaciones de la comprobación. No contiene nuevas métricas de desempeño. El protocolo sucesor está en [PROTOCOLO_SIM_RAW.md](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/docs/adversarial_review_20261031/PROTOCOLO_SIM_RAW.md).

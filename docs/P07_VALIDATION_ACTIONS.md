# P07: trabajo para demostrar la ventaja del método

La meta científica es atribuir una intervención nueva desde ocho PMU durante la recuperación de una anterior, manteniendo cobertura oportuna y un presupuesto de alarmas declarado. El manuscrito presenta primero las capacidades demostradas; las comparaciones siguientes buscan fortalecer la ventaja operativa.

## En ejecución: calibración física y aprendizaje desde SIM

B01 conserva el banco actual y compara umbrales calibrados y error predictivo aprendido exclusivamente de TRAIN. Su examen permanece independiente. Las predicciones y resultados completos decidirán qué variante mejora el equilibrio entre aciertos y alarmas; no se incorporan resultados parciales al paper.

## Preparado: comparación independiente con las mismas fuentes

C02 tiene 102 padres de simulación diseñados y sellados: 24 TRAIN, 36 CAL y 42 TEST. Todas las nueve cargas y nueve líneas aparecen seis veces en TRAIN. Se comparan un observador físico continuo de un estado con GLR, el banco nominal de historias con los mismos operadores y ExtraTrees entrenado de nuevo con todas las fuentes presentes. La información física se equipara entre los dos observadores; la cobertura de fuentes y los datos permitidos se equiparan al clasificador, sin afirmar que ambas representaciones usan la física del mismo modo.

Hay 24 pruebas aprobadas para el diseño, las ecuaciones del comparador continuo, causalidad de features, cobertura de fuentes, selección CAL y cierre del TEST hasta el sellado. Ya están implementados el entrenamiento causal de 1.457 features y la entrada genérica del GLR. Falta conectar/completar la preparación física, exportación, banco nominal, demás ejecutores y evaluación antes de lanzar simulaciones.

CAL reserva 24 normales de 600 s: 3,92 h monitorizadas. Permite comprobar el presupuesto de 1 alarma/h bajo el supuesto Poisson declarado, en vez de seleccionar un umbral con poca exposición. Cada umbral del GLR se ejecuta de nuevo porque afecta su trayectoria de estado. La selección usa solo CAL; TEST se abre tras congelar código, modelo y umbral.

La ejecución pesada comienza después de B01, con un trabajador y suficiente disco. No hay resultados de C02 todavía. Los intervalos agruparán trayectorias completas y conservarán todos los fallos, cierres, demoras y denominadores. No se desarrolla otra versión para un bus concreto.

## Siguiente evidencia de generalidad

Después del contraste central, la prioridad es comprobar transferencia a un modelo dinámico distinto y estudiar si la separación física entre fuentes predice errores/demoras. Se formulan como pruebas del método, con criterios fijados antes del examen; no se añaden resultados o teoremas aún no ejecutados al artículo.

C01/A01/B01, las versiones anteriores y la imagen de eventos se conservan. RAW0002 sigue cerrado. El repositorio científico no se publica.

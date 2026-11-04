# P07: trabajo para demostrar la ventaja del método

La meta científica es atribuir una intervención nueva desde ocho PMU durante la recuperación de una anterior, manteniendo cobertura oportuna y un presupuesto de alarmas declarado. El manuscrito presenta primero las capacidades demostradas; las comparaciones siguientes buscan fortalecer la ventaja operativa.

## En ejecución: calibración física y aprendizaje desde SIM

B01 conserva el banco actual y compara umbrales calibrados y error predictivo aprendido exclusivamente de TRAIN. Su examen permanece independiente. Las predicciones y resultados completos decidirán qué variante mejora el equilibrio entre aciertos y alarmas; no se incorporan resultados parciales al paper.

## Implementado: comparación independiente con las mismas fuentes

C02 tiene 102 padres de simulación diseñados y sellados: 24 TRAIN, 36 CAL y 42 TEST. Todas las nueve cargas y nueve líneas aparecen seis veces en TRAIN. Se comparan un observador físico continuo de un estado con GLR, el banco nominal de historias con los mismos operadores y ExtraTrees entrenado de nuevo con todas las fuentes presentes. La información física se equipara entre los dos observadores; la cobertura de fuentes y los datos permitidos se equiparan al clasificador, sin afirmar que ambas representaciones usan la física del mismo modo.

La cadena completa está implementada: física/exportación aisladas, ajuste nominal desde el prefijo PMU, banco compartido por ambos observadores, aprendizaje de 1.457 features, inferencia CAL, selección, sellado y evaluación TEST de una sola apertura. Pasaron 43 pruebas sobre causalidad, cobertura, semillas, estados secuenciales, denominadores y guardas. El GLR reprodujo exactamente seis salidas del control S01 sobre 1.050 reportes de desarrollo; el flujo de 47 coordenadas y sus features aprendidas fueron idénticos bit a bit. No se entrenó con ese registro ni se seleccionaron umbrales con él.

La revisión independiente de guardas aprobó 11 pruebas dirigidas: se rechazan observaciones de otro split, ID/ruta/hash incorrectos, sustituciones de runtime/banco y cambios de dependencias numéricas entre CAL y TEST. El sello abarca las copias numéricas además de sus manifiestos. La ejecución Julia de física y derivadas del candidato completo sigue pendiente; una prueba de desarrollo no la sustituye.

CAL reserva 24 normales de 600 s: 3,92 h monitorizadas. El criterio de selección de 1 alarma/h usa la población balanceada completa y el supuesto Poisson declarado. Los 12 padres por ruido aportan 1,96 h: aun con cero alarmas no certifican ese presupuesto por estrato al 95 %. Se reportarán tasas y límites por ruido/condición; el criterio CAL elegido no es un certificado posterior a selección. Cada padre tiene un único nivel de ruido, sin replays. Cada umbral del GLR se ejecuta de nuevo porque afecta su trayectoria de estado. La selección usa solo CAL; TEST se abre tras congelar código, modelo y umbral.

La cola local se inició el 3-nov-2026 a las 23:23:49 UTC; se verificó su estado WAITING por B01 activo. Permite un único intento tras una espera máxima de 24 h. Exige B01 terminado y sellado, ausencia de sus procesos y 30 GiB libres para arrancar; revisa una reserva de 16 GiB entre unidades y 18 GiB para TRAIN. El disco tenía aproximadamente 19 GiB: también falta cumplir ese umbral. No borra datos ni reintenta fallos automáticamente. La ejecución usa un trabajador. Su estado exacto está en `experiments/PAPER_RECOVERY_C02/run/QUEUE_STATUS.json` del repositorio científico. No hay resultados de C02 incorporados al artículo. Los intervalos agruparán trayectorias completas y conservarán todos los fallos, cierres, demoras y denominadores. No se desarrolla otra versión para un bus concreto.

## Siguiente evidencia de generalidad

Después del contraste central, la prioridad es comprobar transferencia a un modelo dinámico distinto y estudiar si la separación física entre fuentes predice errores/demoras. Se formulan como pruebas del método, con criterios fijados antes del examen; no se añaden resultados o teoremas aún no ejecutados al artículo.

C01/A01/B01, las versiones anteriores y la imagen de eventos se conservan. RAW0002 sigue cerrado. El repositorio científico no se publica.

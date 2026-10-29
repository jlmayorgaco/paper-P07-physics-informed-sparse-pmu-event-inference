# R12: testigo causal de inicio
Antes de sortear H04. El observador R11, estados, M/DeltaM, firmas, ruido, b fijo
y umbrales no cambian. Solo se cambia publicacion: una carga diagnosticada en
celda c con inicio estimado tau necesita source_F[c] superior al umbral existente
en round(30*tau)+confirmation_frames. Ambas constantes son heredadas (6reportes
y umbral fisico del padre). Se consulta solo cuando ese reporte ya fue recibido.
La misma regla aplica a todos los buses. No hay tiempo refractario tras OFF ni
umbral ajustado con las seis extras. Las lineas mantienen el operador discreto.
Una carga se publica al disponer de diagnostico y testigo; no se retrodata la
alarma. Sin episodio admitido nunca se publica una restauracion. Esto cambia
salidas, no corrige el posterior interno ni su calibracion. Puede abstenerse
ante eventos debiles con evidencia inicial insuficiente; debe reportarse.

Test: doce trayectorias80s, tres padres de6eventos mas un normal cruzados con
MATCH/IN_SUPPORT/OUT_SUPPORT. Nuevas semillas PLAN;18eventos unicos y54realizaciones
pareadas, catalogo conocido, mismo ruido1/operacionF01. Comparadores R11,
R11_NOMINAL, R08/V9 y dos ExtraTrees congelados. Mismos datos/evaluador.
Criterio: ninguna regresion por evento ni perdidaBUS31 frente R11, no aumentar
extras/FA/abiertos; reducir extras y restauraciones espurias OUT. Si no cumple,
no promover. No exige cero errores para escribir un paper acotado.
Pruebas previas: causalidad frente cambio futuro, no restauracion huerfana,
testigo de fuente correcta y no de otra fuente, preservacion estado/firma,
paridad de episodio admitido, ensayo sobre H03 ya abierto sin cambiarparametros.
Limites: requiere prefijo estacionario; carga/linea conocidas; no se afirma
latencia maxima, todos39buses, todasfamilias, Bayes optimo ni novedad establecida.
Una instalacion limpia, comparadorfisico publicado y prueba confirmatoria con
mas padres/exposicion normal siguen fuera de este gate exploratorio.
RAW0002 cerrado, F01 sinrecalibrar, baselines intactos, max3procesos/BLASJulia1.

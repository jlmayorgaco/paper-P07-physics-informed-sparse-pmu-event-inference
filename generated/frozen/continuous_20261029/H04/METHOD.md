# R12: coherencia causal de la admisión

Sea h=(familia,c,tau,...) un diagnóstico R11 recibido en el reporte k. tau es
inicio estimado, no el tiempo verdadero. Sea F_c(j) el score físico causal que
R11 calculó para la fuente c cuando llegó el reporte j. Definir

    j_h = round(tau / Delta_t) + n_conf
    AdmitirCarga(h,k) = I(j_h<=k) I(F_c(j_h)>gamma).

Delta_t=1/30s. n_conf=6 y gamma=recovery_proposal.threshold son los valores
heredados, no umbrales ajustados al nuevo holdout. Los seis reportes especifican
una ventana de evidencia inicial; no constituyen una garantía estadística de
potencia o de falsas alarmas. Cada fuente usa su propio score, no el máximo de
otro bus. Las líneas mantienen la confirmación del operador discreto de R11.

La alarma de carga se publica cuando están disponibles diagnóstico y testigo;
no se retrodata a tau ni a una alarma anterior. Su onset estimado se conserva
como otra variable. Si se rechaza el episodio, tampoco se publica su restauración.
Una restauración pública requiere un episodio admitido con el mismo identificador.
No hay un tiempo refractario tras OFF: un evento nuevo puede admitirse durante
la recuperación si tiene evidencia de inicio. Los estados físicos/estimados,
M/DeltaM, amplitudes y matriz de firmas de R11 no se cambian ni reinician.

La implementación guarda F solamente al recibir cada reporte. Nunca consulta
j>k. Una modificación de reportes futuros no puede cambiar lo ya emitido, por
construcción del estado almacenado; test_gate.py comprueba esa propiedad, fuente
correcta, ausencia de restauración huérfana y coexistencia sin período refractario.
No se introduce el testigo como otra likelihood ni se cambia la masa posterior.

Es una corrección del nivel de decisión/publicación. Un M incorrecto puede seguir
existiendo aunque la alarma no se publique: no se afirma reparación del estimador
Bayesiano ni calibración probabilística. Los inicios retrospectivos con evidencia
inicial débil pueden rechazarse aun siendo reales. El siguiente contrato debe
medir ese límite en amplitudes débiles, aumentos lentos y fuentes nuevas.

H03 ya abierto es desarrollo: se retuvieron54eventos y se eliminaron6extras.
H04 es el nuevo examen congelado. Su resultado, no el desarrollo, decide el gate.

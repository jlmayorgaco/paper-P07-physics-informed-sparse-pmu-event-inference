# R11: origen observacional fijo, firmas dinamicas conservadas

La planta y sus sensibilidades DAE son las de R10B. Cada hipotesis theta mantiene
R/X constantes. Se amplía unicamente el modelo de observacion:

    y_k = mu_theta + H_theta(delta x_k, h_k, a) + b_theta + epsilon_k
    b_theta = mean_startup(y) - mu_theta;   b_(k+1) = b_k

mu_theta proviene del ajuste inverso AC y equilibrio condicional R10B. Las
primeras300 muestras, hasta299/30s, estiman b; se congela antes de vigilancia.
Angulos usan coordenadas desenvueltas de la referencia instrumental F01.
Frecuencia y ROCOF ya tenian medias empiricas: el cambio afecta31fasores.
La referencia efectiva es mu_theta+b_theta. Esto declara una discrepancia de
modelo/observacion; no convierte la red incorrecta en la red verdadera.

Para una firma temporal s de carga y una referencia fija:

    T_b(y+s) - T_b(y) = s,    T_b(y)=y-mu_theta-b_theta.

No se elimina ninguna direccion del espacio de observaciones. Se conservan el
escalon durante la intervencion y su restauracion. Si b se reajustara durante
eventos, esta interpretacion perderia validez; el codigo no lo hace. Las matrices
A,B,C,D, las firmas y los umbrales permanecen los del padre.

Los estados condicionales y la evidencia secuencial son los de R10B; cada reporte
actualiza los pesos theta una sola vez. M es su mezcla y DeltaM conserva la
descomposicion en revision de red y cambio de atribucion condicional. El valor
b no se actualiza al cerrar episodios ni reinicia estados.

Limites: estimacion plug-in de b y del punto de operacion, sin marginalizacion
completa de su incertidumbre; covarianzas y poda heredadas. Se requiere arranque
estacionario. No corrige necesariamente sensibilidades dinamicas erroneas ni
identifica R/X individuales. Ninguna de estas ecuaciones acredita por si sola
novedad editorial o inferencia optima. H03 determina utilidad empirica.

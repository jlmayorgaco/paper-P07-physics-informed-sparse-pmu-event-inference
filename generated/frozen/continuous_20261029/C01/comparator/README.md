# Comparador físico publicado: núcleo reproducido y adaptador declarado

Referencia primaria: Chen, Banerjee, Domínguez-García y Veeravalli,
“Quickest Line Outage Detection and Identification”, IEEE TPWRS 31(1),
749–758, 2016. DOI: [10.1109/TPWRS.2015.2394246](https://doi.org/10.1109/TPWRS.2015.2394246).
[Texto de autores](https://aledan.ece.illinois.edu/files/2017/04/TPWRS_2016_b.pdf).

## Contrato ejecutado

`chen2016.py` implementa covarianzas de incrementos de ángulo reducidas por
referencia (ecuaciones 7/13), marginalización de mediciones no observadas
(40/41), CUSUM paralelo positivo (30), parada estricta (31), umbral (32) e
identificación al parar (33). El resultado nativo es UNA parada. No carga,
despeje, recierre, múltiples episodios ni actualización oracle del estado.

`test_chen2016.py`: matriz de tres buses, marginal después de invertir,
log-density contra SciPy, máximo de sufijos, parada/localización, causalidad,
ángulos e islas. `validate_matched.py`: 400 secuencias independientes bajo la
ley gaussiana del núcleo; se conservan parada temprana y censura. No reproduce
la tabla de 118 buses de los autores. No se ajusta el umbral al resultado.

## Adaptación F01 (no es parte del teorema original)

`run_f01.py` usa las ocho PMU originales y nueve líneas del catálogo congelado.
La pendiente DC es 1/(X*tap), resistencia y shunts se omiten bajo la hipótesis
del comparador. Covarianza de inyecciones = sigma² I. Solo los 300 reportes
iniciales estiman sigma² y la deriva media de incrementos en cada PMU. Cada par
no solapado usa diferencia circular; 30 fps de entrada producen 15 incrementos/s.
beta=3600s equivale a 54000 observaciones; A=log(9*54000). Esta beta es una
configuración, NO un ARL demostrado sobre ruido instrumental coloreado.

La referencia DC es BUS1; el adaptador no observa directamente su ángulo. La
corrección de deriva desde el prefijo no elimina toda dinámica del marco común.
Esta incompatibilidad, la covarianza isotrópica y el ruido coloreado limitan la
transferencia. No se optimizan ni blanquean con residuos de eventos. El estrés
H04 conserva los fallos: 3/3 registros normales producen alarma. No se usa ese
fallo para declarar inferior el algoritmo original bajo sus propios supuestos.

## Elegibilidad

La campaña C01 tendrá un carril de apertura persistente y controles normales.
Carga/línea con restauración usa R11, nominal y los ExtraTrees congelados.
No se inventa un operador de cierre para hacer parecer general al comparador.
Yang–Chen–Zhai (arXiv:1911.01733v2) se auditó como alternativa: su Jacobiano
PMU-reducido requiere vecinos medidos; varios sensores del mapa actual quedan
aislados. No se introduce una pseudoinversa nueva llamándola método publicado.

## Reproducir

Desde la raíz SGSMA:

```powershell
python -B -X utf8 experiments/PAPER_CONFIRMATORY_C01/comparator/test_chen2016.py
python -B -X utf8 experiments/PAPER_CONFIRMATORY_C01/comparator/validate_matched.py
python -B -X utf8 experiments/PAPER_CONFIRMATORY_C01/comparator/run_f01.py --observation RUTA_PMU.npz --output CARPETA_NUEVA
```

El proceso de inferencia prohíbe rutas RAW, verdad privada y motor. La evaluación
de estrés lee verdad H04 solo después de sellar las predicciones.

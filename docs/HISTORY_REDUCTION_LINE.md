# Línea de reducción de historias: resultado del experimento decisivo (06-11-2026)

Estado: **ejecutada y descartada como mejora de P07.** Código y resultados en `experiments/history_conditioning/`; sección del suplemento `sections/article_history_conditioning.tex`.

## Qué se probó

La segunda revisión externa propuso condicionar la evidencia por la historia (firma relinealizada, interacción bilineal, marginalización analítica de la severidad previa por Woodbury) y comparar contra un observador relinealizado y un banco completo. Se construyó una planta reducida de IEEE-39 en Python (máquinas clásicas, regulador con estatismo, cargas de impedancia constante, red del `.raw`), independiente de la planta del banco, y se reprodujo el escenario del chat: carga p ON/OFF y, durante la recuperación, una carga débil que hay que atribuir entre ocho candidatas.

Seis predictores sobre las mismas observaciones: nominal, bilineal, relinealizado, plug-in no lineal, marginalizado (Woodbury) y cuadratura de siete nodos. Ocho celdas congeladas con hash antes de la cohorte (ruido ×1, ×10, ×100 de la covarianza empírica de RAW0001; historia de 6,5, 1 y 0,5 s; desajuste de inercia 20 %; ventana de decisión de 1,5 y 0,5 s), 200 escenarios por celda, una pasada.

## Resultado

- Ningún predictor condicionado supera a la firma nominal recentrada: diferencias de acierto de 0 a 0,5 puntos con intervalos bootstrap que contienen 0 o lo tocan (criterio previo no cumplido en ninguna celda).
- La severidad previa se recupera con error ≤ 0,3 puntos de la carga base en todas las celdas, así que no queda incertidumbre histórica que marginalizar. La mejora de 70,92 % a 73,76 % del chat dependía de un ensayo de 3 buses en el que esa incertidumbre era grande.
- Coste por decisión: 0,5 ms (nominal), 0,8 s (planta no lineal), 6,4 s (cuadratura). La marginalización por Woodbury cuesta lo mismo que el plug-in porque necesita las simulaciones no lineales.
- La cota de error blanqueado certificó entre el 93 y el 99 % de los escenarios sin ningún cambio de decisión entre los certificados, pero necesita la predicción no lineal que acota: valida, no ahorra cómputo.
- RAW0001: la misma planta pone la carga de BUS7 en primer lugar entre 16 cargas y explica el 99,5 % de la energía del cambio cuasi-estacionario. No discrimina entre métodos (su única carga llega unos diez minutos después de la recuperación del evento anterior).

## Qué queda abierto

Un régimen con historia mal observada de verdad (otra planta, otras dinámicas, sensores con pérdida) donde el condicionamiento cambie una decisión. En la planta reducida y con el ruido real de RAW0001 no apareció. Esa pregunta, y la prueba sobre la planta del banco, quedan fuera de P07.

## Adenda H02 (6 nov 2026): regímenes extremos
Se exploraron cuatro regímenes más duros con semillas 1–30 (severidad previa 30–60 %, nueva fuente 0,2 s tras la primera, desajuste 40/80 %, ruido ×100–×1000, historia 0,5–1 s): empate total de los seis predictores. Se congelaron dos (E1, E2 = celdas I y J) y se corrieron una vez con semillas 3000–3199: I: nominal 61,5 %, marginalizado 60,5 % (peor, NLL +0,9 nats); J: 38,0 % en todos. Error de severidad previa 0,8–5,4 puntos y aun así no cambia la decisión. El certificado baja a 78 % en el nominal. Conclusión reforzada: la historia desplaza a todas las hipótesis casi por igual. Código: `run_h02.sh`, variables H_TNEW/H_APRIOR/H_ACLIP; resultados en `results/ROWS_cell9..10.json`.

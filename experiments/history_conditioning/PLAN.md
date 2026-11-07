# H01: ¿condicionar por la historia mejora la atribución? Protocolo congelado

Congelado antes de ver la cohorte de prueba. Semillas de desarrollo 1–40 (solo para depurar el código; ningún parámetro del método se ajustó). Prueba: semillas 1000–1199, una pasada por celda.

Planta: IEEE-39 reducida (máquinas clásicas, regulador con estatismo del 5 %, cargas de impedancia constante, red del `.raw`), distinta de la planta del banco. Medición: log-módulo y ángulo de la secuencia positiva en las 8 PMU, 30 reportes/s. Ruido: covarianza empírica 16×16 de RAW0001 (ventana 100–300 s, sin eventos según el calendario público), multiplicada por el factor de la celda.

Escenario: carga p ON a 2 s, OFF a 5 s (severidad A ~ U(8,16 %)), segunda carga c ON a 6,5 s (severidad b ~ U(2,6 %)). Ocho cargas candidatas {3,4,7,15,16,20,24,26}. El estimador conoce p y los instantes; estima A por Gauss–Newton y su varianza P_A con las lecturas anteriores a 6,5 s.

Métodos con las mismas observaciones, priors, instante y horizonte: N (firma de reposo), Q (bilineal), R1 (relinealizada, primer orden), F (planta no lineal en A estimada), M (F con covarianza R + J P_A Jᵀ por Woodbury), QA (cuadratura de 7 nodos sobre A, referencia).

Celdas (factor de ruido; ventana de historia usada; desajuste de inercia y amortiguamiento; ventana de decisión):
C1 1, completa, 0, 1,5 s · C2 100, completa, 0, 1,5 s · C3 1, 1 s, 20 %, 1,5 s · C4 100, 1 s, 20 %, 1,5 s · C5 100, 1 s, 20 %, 0,5 s · C6 10, completa, 0, 1,5 s · C7 10, 1 s, 20 %, 1,5 s · C8 100, 0,5 s, 0, 1,5 s.

Criterio previo: un método mejora a otro si el intervalo bootstrap pareado (por escenario) de la diferencia de acierto excluye 0 y el NLL medio baja; si no, no hay ganancia. Se informa el coste (tiempo y simulaciones por escenario) y el certificado ρ (cota computable de la distorsión de la evidencia respecto de F) con su tasa de cambios de decisión entre los certificados.

Validación contra RAW0001 (`exp2_raw.py`, solo lectura, sin ajuste): fidelidad de la respuesta predicha a la carga de BUS7 y orden de candidatos. RAW0001 no tiene secuencias de eventos con recuperación incompleta (la carga llega 583 s después de recuperarse el evento anterior), así que no puede discriminar entre métodos con y sin historia.

---
## Adenda H02 (regímenes extremos), congelada antes de generar la cohorte de prueba
Las semillas 1–30 se usaron solo para explorar cuatro regímenes más duros (severidad previa U(30,60 %), segunda fuente a 5,2 s, es decir 0,2 s tras apagarse la primera, tope de severidad 0,8): en todos, los seis predictores dieron el mismo acierto. Se confirman dos de ellos con semillas nuevas 3000–3199, una pasada:
E1: ruido ×100, historia 1 s, desajuste 40 % (inercia) / 80 % (amortiguamiento), ventana 1,5 s.
E2: ruido ×1000, historia 0,5 s, desajuste 40 %/80 %, ventana 0,5 s.
Mismo criterio previo que H01 (intervalo bootstrap pareado excluye 0 y baja el NLL). Variables: H_TNEW=5.2, H_APRIOR=0.3,0.6, H_ACLIP=0.8.

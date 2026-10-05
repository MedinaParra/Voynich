# 02 — Estadística lingüística

**Estado: PASS** para la reproducción puntual de H0–H4 y MI posicional en STA1; otras pruebas **NOT_RUN**.

## Entropía condicional

El parser de `03_entropy_spectral.ipynb` produce H0–H4 = 4.140848, 2.960829, 2.989824, 3.316503 y 3.773891 bits. El cálculo usa secuencias concatenadas entre palabras, tal como hace la notebook. Se reprodujo la fórmula del notebook desde los conteos.

**Defecto comprobado:** la fórmula de suavizado usada para órdenes 1–4 no asigna probabilidad total 1 a cada contexto. La masa mínima por contexto es 0.973955, 0.972017, 0.965301 y 0.966636; los máximos también son menores que 1. La salida de la notebook muestra además “monotonicity violations” en N=2,3,4, aunque el docstring afirma garantía de monotonicidad. La secuencia de entropía publicada crece 0.028995, 0.326679 y 0.457388 bits entre órdenes 1→2, 2→3 y 3→4.

Al renormalizar por contexto, H1–H4 = 2.964188, 2.997258, 3.331267, 3.794710. Con variante Witten–Bell que reparte explícitamente masa sobre glifos no vistos: 2.984718, 3.029367, 3.372860, 3.835745. Ambos diagnósticos retienen el rebote, pero no resuelven la escasez de muestras, dependencia ni selección del estimador. El plug-in sin suavizado da 2.888663, 2.665821, 2.429611, 2.006159; tampoco es por sí solo un estimador imparcial de la entropía poblacional.

## Información mutua posicional

MI(glifo;posición) = 0.657811 bits al asignar palabras de longitud uno a `inicio`, siguiendo la notebook 02. Excluirlas da 0.663380 bits; ubicarlas en clase propia da 0.669989 bits. Hay 883 palabras singleton (2.38%). En 999 reordenamientos independientes dentro de palabra, seed 20261005, el nulo tiene media 0.007980, DE 0.000313, percentil 99 = 0.008652; p empírico unilateral = 0.001 (resolución mínima con 999 permutaciones).

Esto demuestra que la forma del glifo se asocia con las posiciones definidas más allá del orden al azar dentro de palabras; no distingue lengua, código, morfología ni semántica.

## No ejecutado

Zipf, n-gramas comparativos, bootstrap por folio, Currier/sección, espectro, clustering, clasificadores, EVA, controles de lenguas y cifrados, SilPart y controles sintéticos. Se requieren dependencias/notebooks originales y emparejamiento de unidades antes de informar comparaciones.

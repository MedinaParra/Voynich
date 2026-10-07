# 32. Auditoría del holdout de bifolios en otros quires

Fecha: 2026-10-07

## Corrección de estado

La lectura rápida inicial de este experimento fue demasiado pesimista. El artefacto completo del workflow `experiment/all-quiro-bifolio-holdout` muestra **señal agregada positiva y estadísticamente fuerte**, no un fallo global.

El experimento no ordena páginas. Usa bifolios físicos conocidos como verdad de evaluación y pregunta si una métrica textual, sin usar esos pares durante la selección, puede reconstruirlos entre todos los emparejamientos perfectos posibles. Q13 y Q20 se excluyen del holdout porque motivaron la hipótesis.

## Holdout principal, controlando distancia entre folios

Siete quires son elegibles en el corpus ZL3b:

| quire | folios | bifolios físicos | rango ajustado | p exacto ajustado | efecto ajustado |
|---|---|---|---:|---:|---:|
| A | 1–8 | `1|8, 2|7, 3|6, 4|5` | 25/105 | 0,2381 | +0,01115 |
| B | 9–16 parcial | `9|16, 10|15, 11|14` | 3/15 | 0,2000 | +0,02313 |
| C | 17–24 | `17|24, 18|23, 19|22, 20|21` | **1/105** | **0,00952** | **+0,07419** |
| D | 25–32 | `25|32, 26|31, 27|30, 28|29` | 10/105 | 0,09524 | +0,05523 |
| E | 33–40 | `33|40, 34|39, 35|38, 36|37` | **2/105** | **0,01905** | **+0,12042** |
| F | 41–48 | `41|48, 42|47, 43|46, 44|45` | **1/105** | **0,00952** | **+0,10528** |
| G | 49–56 | `49|56, 50|55, 51|54, 52|53` | 9/105 | 0,08571 | +0,04293 |

Resumen agregado:

- los 7/7 efectos ajustados por distancia son positivos;
- test de signos unilateral: `p = 0,0078125`;
- Fisher sobre p ajustados por distancia: `p = 0,0001131283`;
- 3/7 quires tienen p<0,05;
- 5/7 tienen p<0,10;
- percentil ajustado mediano: `92,38%`.

**Interpretación:** existe señal textual de acoplamiento físico de bifolios a escala manuscrito. Esto no determina el orden de lectura ni demuestra que todos los quires fueran pilas de singuliones sueltos.

## Reconstrucción ciega de pares

Con ZL3b, el máximo matching ajustado por distancia recupera:

- A: 2/4;
- C: **4/4**;
- D: 1/4;
- E: 2/4;
- F: **4/4**;
- G: 1/4.

Con la transcripción independiente Takahashi IT2a:

- A: 2/4;
- C: **4/4**;
- D: 1/4;
- E: **4/4**;
- F: **4/4**;
- G: 1/4.

La replicación IT2a global recupera 16/24 pares frente a 3,43 esperados por azar; el exacto conjunto reportado por el experimento es `p = 1,52×10⁻⁶`.

## Control exacto por mano Davis + Currier

El null se restringió a emparejamientos con el mismo perfil de categorías “misma/diferente mano Davis” y “mismo/diferente Currier”. El resultado global sigue siendo positivo en las dos transcripciones:

- ZL3b: 14/24 pares, p condicional exacto `0,01821`;
- IT2a: 16/24 pares, p condicional exacto `0,002470`.

Pero el tamaño del null se vuelve muy pequeño para algunos quires. A nivel individual:

- C: 4/4, `p = 0,00952`, null 105 — **robusto**;
- E: ZL 2/4, p=0,5556; IT2a 4/4, p=0,1111 — ambiguo;
- F: 4/4 en ambos antes del doble residual, pero null condicionado sólo 3 emparejamientos y p=0,3333 — poca capacidad discriminante;
- D/G: no sobreviven;
- A: parcial.

## Doble residual: distancia + mano/Currier

Se sustraen aditivamente tanto el efecto de distancia absoluta entre folios como la categoría exacta de la pareja Davis-H/Currier-L, antes de elegir el matching.

### ZL3b

- A: 2/4;
- **C: 4/4, p=0,00952**;
- D: 1/4;
- E: 1/4;
- F: 2/4;
- G: 0/4.

Global: 10/24; p exacto ordinario `0,00359`; p condicionado por metadata `0,001322`.

### IT2a

- A: 2/4;
- **C: 4/4, p=0,00952**;
- D: 1/4;
- E: 1/4;
- F: 0/4;
- G: 0/4.

Global: 8/24; p exacto ordinario `0,02630`; p condicionado por metadata `0,006734`.

## Regla de elegibilidad para intentar ordenamiento

No basta con que un quire tenga p<0,05 en el primer holdout. Para pasar a una reconstrucción de orden exigimos, como mínimo:

- recuperación fuerte del emparejamiento físico;
- replicación entre ZL3b e IT2a;
- supervivencia al control de distancia;
- supervivencia razonable a mano Davis/Currier;
- no confundir emparejamiento de bifolios con secuencia de lectura.

Con esa regla:

### Tier 1 — elegible ahora

**Quire C, f17–f24.**

Es el único que recupera 4/4 bifolios en ambas transcripciones y mantiene 4/4 después del doble residual distancia + metadata, con exacto `1/105`.

### Tier 2 — prometedores, no ordenar todavía

**E (f33–f40)** y **F (f41–f48)**.

Tienen señales fuertes en análisis simples y replicación IT2a, pero pierden especificidad al retirar metadata/distancia simultáneamente o tienen null condicionado demasiado pequeño.

### Tier 3 — evidencia insuficiente

A, B, D y G.

## Consecuencia metodológica

Para Quire C no se debe aplicar directamente el modelo de “fila de singuliones” usado en Q13/Q20. C es un cuaderno normal anidado. El problema correcto es:

> dados los cuatro bifolios físicos `17|24`, `18|23`, `19|22`, `20|21`, ¿qué orden de anidamiento outer→inner maximiza continuidad de lectura entre las hojas resultantes?

Para un anidamiento `(a₁|b₁, a₂|b₂, …, aₙ|bₙ)`, con orientación física fija, la secuencia de hojas es:

`a₁, a₂, …, aₙ, bₙ, …, b₂, b₁`.

El orden encuadernado actual de C produce naturalmente:

`17,18,19,20,21,22,23,24`.

La próxima prueba enumera los `4! = 24` anidamientos posibles y puntúa las transiciones `verso(hoja i) → recto(hoja i+1)` en ZL3b e IT2a por separado. No se usa el número de folio como predictor.
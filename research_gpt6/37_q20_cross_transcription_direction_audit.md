# 37. Q20 — auditoría direccional cruzada con GC/v101

Fecha: 2026-10-07
Estado: **resultado ejecutado; recalibración adversarial**

## Objetivo

La reconstrucción Q20 venía usando seis flechas direccionales derivadas de fronteras textuales EVA. Las réplicas H/F/IT2a preservaban las cuatro flechas internas entre los cinco bifolios `104|115` a `108|111`, pero H e IT2a comparten linaje Takahashi/LSI y por tanto no son controles plenamente independientes.

Para reducir ese sesgo se repitió la prueba con **GC2a**, la transliteración completa de Glen Claston en alfabeto **v101**, realizada independientemente y con decisiones gráficas distintas.

Se analizaron nativamente los límites:

- `S2 = 104|115`: cabeza `f104r`, cola `f115v`;
- `S3 = 105|114`: cabeza `f105r`, cola `f114v`;
- `S4 = 106|113`: cabeza `f106r`, cola `f113v`;
- `S5 = 107|112`: cabeza `f107r`, cola `f112v`;
- `S6 = 108|111`: cabeza `f108r`, cola `f111v`.

Las ventanas fueron 2, 3, 4, 5, 6, 7 y 8 líneas. Se combinaron, sin ajuste de pesos, TF-IDF de palabras v101, n-gramas de glifos v101 3–5 y coincidencia palabra-final→palabra-inicial. Debido a la extrema dispersión del último componente, también se reportó la ablación palabra+glifo.

## Resultado 1 — sólo dos de cuatro flechas sobreviven de forma limpia

### `105|114 → 107|112`

Margen combinado positivo en **7/7** ventanas. La ablación palabra+glifo también es positiva en **7/7**.

Clasificación: **ROBUST_POSITIVE_GC**.

### `106|113 → 107|112`

Margen combinado positivo en **7/7** ventanas y palabra+glifo positivo en **7/7**.

Es la precedencia más sólida del conjunto independiente.

Clasificación: **ROBUST_POSITIVE_GC**.

### `106|113 → 108|111`

Positiva sólo en ventanas 2–4. Desde 5 líneas el margen combinado cambia de signo; el componente exacto de palabra de borde produce además una penalización muy grande por una coincidencia escasa en el sentido inverso.

Clasificación: **DOWNGRADED / MIXED**.

### `106|113 → 104|115`

Es negativa en 6/7 ventanas y sólo en 8 líneas aparece un margen positivo prácticamente nulo.

Clasificación: **NO REPLICADA EN GC**.

## Resultado 2 — las flechas no son adyacencias directas

Se puntuaron las `5! = 120` cadenas dirigidas como secuencias de continuidad inmediata de borde. Nuestro candidato de cinco unidades:

`105|114 → 106|113 → 107|112 → 104|115 → 108|111`

obtiene rangos, con la métrica completa, de:

`13, 64, 24, 33, 25, 41, 38 / 120`

para ventanas de 2 a 8 líneas.

Con sólo palabra+glifo:

`13, 64, 24, 20, 11, 25, 19 / 120`.

No es una cadena consistentemente top-1 ni top-5. Esto replica la advertencia que ya había aparecido en H/F/IT2a: las señales direccionales deben interpretarse como **precedencia relativa**, no como continuación narrativa inmediata A→B.

## Resultado 3 — reconstrucción Q20 recalibrada

La pérdida de dos flechas parecía inicialmente debilitar mucho el orden Q20. Se rehízo entonces la selección utilizando únicamente:

1. pista externa `105|114` como primera unidad;
2. pista externa `103|116` como terminal;
3. precedencia GC robusta `105|114 < 107|112`;
4. precedencia GC robusta `106|113 < 107|112`.

Con los extremos fijados, la primera precedencia es redundante y la segunda elimina exactamente la mitad de las 24 permutaciones internas, dejando **12 órdenes**.

Sobre esos 12 se reaplicaron las dos métricas simétricas que ya estaban congeladas antes de abrir GC:

- frecuencia bootstrap de aristas;
- similitud residual después de retirar el efecto medio S/T.

El mismo candidato:

**`105|114 → 106|113 → 107|112 → 104|115 → 108|111 → 103|116`**

queda:

- **1.º/12 por bootstrap**, suma = **2.560**;
- **1.º/12 por residual**, suma = **1.9413276674**.

Por tanto el orden principal **sobrevive a la auditoría independiente aun después de retirar dos restricciones direccionales que no replicaron**.

Esto es metodológicamente mejor que el antiguo argumento “6/6 flechas”: el candidato ahora depende de menos supuestos direccionales y de un control realmente independiente.

## Impacto sobre el gap `109|110`

La localización del bifolio perdido después de `105|114` fue calculada sobre este mismo orden de seis supervivientes, pero su fuerza debe reinterpretarse: ya no se apoya en una red de seis precedencias independientes. Se mantiene como **predicción de trabajo**, respaldada por la debilidad Pareto de la interfaz `105|114 — 106|113` y por la corroboración exploratoria de layout, no como consecuencia inevitable de todas las flechas.

Orden aumentado de trabajo:

**`105|114 → [109|110] → 106|113 → 107|112 → 104|115 → 108|111 → 103|116`**

## Clasificación revisada

**`ROBUST_MULTI_CRITERION_Q20_ORDER_CANDIDATE / DIRECTION_PARTIALLY_REPLICATED / DIRECT_CONTINUATION_REJECTED / PHYSICAL_VALIDATION_PENDING`**

No afirmar:

- seis flechas independientes confirmadas;
- continuidad narrativa directa entre todos los bifolios;
- orden histórico demostrado;
- desciframiento.

Sí podemos afirmar de manera defendible:

> Una transliteración independiente en alfabeto v101 elimina dos de las cuatro precedencias internas previamente consideradas estables, pero conserva dos de ellas en todas las escalas probadas. Al recalcular el espacio de órdenes con sólo esas precedencias replicadas y los extremos externos, el candidato Q20 original sigue siendo el único mejor orden bajo las dos métricas simétricas previamente congeladas.

## Reproducibilidad

- `research_gpt6/code/q20_gc_direction_audit.py`
- `research_gpt6/results/q20_gc_direction_audit.json`

Fuente GC usada: `GC2a-n.txt`, cabecera `#=IVTFF v101 2.0 M 6`, versión 2a modificada el 25/06/2025.

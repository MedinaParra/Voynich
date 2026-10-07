# Resultado 29 — Señal textual de bifolio: Q13, Q20 y hold-out A–G

Fecha: 2026-10-07

## Resumen

La hipótesis fuerte de recuperar un **orden exacto entre bifolios** había fallado en Q13. Al aislar una hipótesis distinta —si el texto identifica la **unidad física bifolio**— aparece una señal reproducible.

No es desciframiento, no asigna semántica y no determina orden de lectura. El resultado apoya únicamente un acoplamiento estadístico entre páginas que pertenecen a la misma hoja física plegada.

## Corpus y política fija

- Corpus: ZL EVA v3b, blob Git `2a4533ab9bdfa85db9bad602d590978953055df1`.
- Parser conservador: sólo chunks EVA minúsculos literales en loci de párrafo; segmentos inciertos se separan y nunca se adivinan.
- Unidad de comparación: folio agregado `recto + verso`.
- Métrica primaria: coseno TF–IDF.
- Null: todos los perfect matchings de exactamente los mismos folios.
- Robustez: centrar cada similitud por la media de todos los pares con la misma distancia absoluta entre números de folio.

## Q13 — 10 folios / 945 emparejamientos

Pares físicos:

`75|84, 76|83, 77|82, 78|81, 79|80`

### Test bruto

- TF–IDF: rango **3/945**, `p = 0.0031746`.
- char-3gram: rango **3/945**, `p = 0.0031746`.
- Jensen–Shannon: rango **1/945**, `p = 0.0010582`.
- Jaccard: no significativo (`p = 0.1101`).

### Ajustado por distancia

- TF–IDF: rango **14/945**, `p = 0.0148148`.
- char-3gram: rango **22/945**, `p = 0.0232804`.
- Jensen–Shannon: rango **4/945**, `p = 0.0042328`.
- Jaccard: no significativo (`p = 0.3608`).

Resultado: **PASS_DISTANCE_ADJUSTED**.

## Q20 — réplica independiente con missing-data conservador

`f116v` no contiene párrafos EVA limpios comparables; el corpus la marca como escritura extránea / “key-like” en locus `@Lx`. La regla se fijó antes de inspeccionar scores Q20: excluir el bifolio incompleto completo `103|116`; no usar evidencia asimétrica de `f116r` solamente y no imputar nada.

Pares completos evaluados:

`104|115, 105|114, 106|113, 107|112, 108|111`

Null exacto: **945** perfect matchings.

### Test bruto

- TF–IDF: rango **10/945**, `p = 0.0105820`.
- char-3gram: rango **6/945**, `p = 0.0063492`.
- Jaccard: rango **13/945**, `p = 0.0137566`.
- Jensen–Shannon: rango **3/945**, `p = 0.0031746`.

### Ajustado por distancia

- TF–IDF: rango **12/945**, `p = 0.0126984`.
- char-3gram: rango 56/945, `p = 0.0592593`.
- Jaccard: rango **32/945**, `p = 0.0338624`.
- Jensen–Shannon: rango 53/945, `p = 0.0560847`.

La métrica primaria replica antes y después del control de distancia.

Resultado: **PASS_REPLICATION**.

Como resumen post-hoc, Fisher sobre los p ajustados TF–IDF de Q13 y Q20 da aproximadamente `p = 0.00180`; no se trata como nueva prueba preregistrada.

## Hold-out: quires no usados para construir la hipótesis

Q13 (`Q=M`) y Q20 (`Q=T`) fueron excluidos. Se analizaron automáticamente todos los demás quires con al menos tres bifolios físicos completos y sin selección basada en score. Resultaron elegibles siete: **A, B, C, D, E, F, G**.

| Quire | Bifolios | Rango ajustado | p ajustado | Efecto |
|---|---:|---:|---:|---:|
| A | 4 | 25/105 | 0.23810 | positivo |
| B | 3 | 3/15 | 0.20000 | positivo |
| C | 4 | **1/105** | **0.00952** | positivo |
| D | 4 | 10/105 | 0.09524 | positivo |
| E | 4 | **2/105** | **0.01905** | positivo |
| F | 4 | **1/105** | **0.00952** | positivo |
| G | 4 | 9/105 | 0.08571 | positivo |

### Resumen hold-out

- **7/7** quires con efecto ajustado positivo.
- Test de signos unilateral: `p = 0.0078125`.
- 3/7 con `p < 0.05`.
- 5/7 con `p < 0.10`.
- Fisher bruto sobre los siete quires: `p = 6.25e-6`.
- Fisher ajustado por distancia: **`p = 1.1313e-4`**.
- Percentil ajustado mediano: 92.38.

El hold-out reduce fuertemente la explicación de que Q13/Q20 fueran dos casos seleccionados por casualidad.

## Qué demuestra y qué no

### Apoyado por estos experimentos

1. Los folios que pertenecen al mismo bifolio físico tienden a ser textualmente más parecidos de lo esperado bajo emparejamientos alternativos exactos.
2. La señal aparece en Q13, replica en Q20 y mantiene dirección positiva en siete quires previamente no usados.
3. Un efecto trivial de distancia entre números de folio no explica la señal completa.
4. La unidad física parece conservar una “huella textual” detectable.

### No demostrado

1. No se recuperó un orden inter-bifolios único para Q13.
2. No se demuestra que los bifolios fueran originalmente singuliones independientes, aunque el resultado es compatible con esa hipótesis.
3. No se demuestra orden de producción ni orden de lectura.
4. No hay desciframiento, traducción ni inferencia semántica.
5. Los siete quires del hold-out con datos completos son principalmente los primeros quires/herbales; no equivalen por sí solos a todas las secciones del manuscrito.

## Posicionamiento frente a trabajo previo

La similitud elevada dentro de bifolios no debe reclamarse como descubrimiento original: observaciones relacionadas se remontan al menos a Torsten Timm y a discusiones posteriores bajo la idea BAAFU (Bifolio As A Functional Unit), y Layfield–Davis 2026 desarrollan la hipótesis de singuliones.

La contribución potencial de esta rama es más estrecha y metodológica:

- null exacto sobre **todos** los emparejamientos físicamente posibles de los mismos folios;
- control explícito de distancia foliar;
- réplica Q13 → Q20;
- hold-out automático A–G excluyendo los casos que motivaron el método;
- separación estricta entre **pairing físico** y **orden entre pairings**.

Esto responde directamente a una debilidad señalada en críticas recientes: mejoras de similitud sin un null de permutación son difíciles de interpretar.

## Siguiente prueba

Se implementó además una reconstrucción predictiva ciega: sobre quires completos no vistos, eliminar conceptualmente `$B`, escoger el maximum-weight perfect matching usando únicamente TF–IDF ajustado por distancia y después comparar con los bifolios físicos reales. Para evitar leakage, los quires con grupos `$B` incompletos se excluyen de esa prueba predictiva.

Esa prueba debe considerarse el paso siguiente porque transforma el resultado de “los pares verdaderos son improbables bajo el null” a “la señal textual puede reconstruir una fracción cuantificable de la arquitectura física sin conocerla”.

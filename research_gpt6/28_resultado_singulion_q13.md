# Experimento Q13: orden singulion/bifolio

Fecha: 2026-10-07

## Pregunta

¿Puede una señal textual/predictiva independiente recuperar el orden Q13 atribuido a Layfield–Davis mejor que el encuadernado actual y mejor que órdenes alternativos físicamente comparables?

Orden evaluado: `77|82 → 78|81 → 75|84 → 76|83 → 79|80`.

Corpus congelado: ZL EVA v3b, blob Git `2a4533ab9bdfa85db9bad602d590978953055df1`.

## Diseño

Se ejecutaron tres brazos:

1. **Continuidad léxica exacta**: TF–IDF, char-3gram, Jaccard, Jensen–Shannon y continuidad de borde. Null exacto: las 120 permutaciones de los cinco bifolios, conservando orientación interna.
2. **Ataque adversarial**: 3.840 secuencias al permitir además inversión del orden de las hojas de cada bifolio. Es un test de sensibilidad, no una afirmación de factibilidad codicológica.
3. **TimesFM congelado**: `google/timesfm-2.5-200m-pytorch`, representación de 10 variables por párrafo idéntica al experimento TimesFM previo. Se genera una sola predicción por página fuente, sin adaptar el modelo al destino ni al orden evaluado. Horizonte H=4; escalas obtenidas fuera de Q13. Null exacto: 120 permutaciones.

Regla confirmatoria: el orden Layfield–Davis sólo pasa si mejora el encuadernado actual **y** queda por sobre el percentil 95 del null exacto.

## Resultados

| Brazo | Actual | Layfield–Davis | Rango exacto | p exacto | Decisión |
|---|---:|---:|---:|---:|---|
| TF–IDF (mayor=mejor) | 0.42317 | 0.43949 | 39/120 | 0.3250 | FAIL_ORDER |
| TimesFM loss (menor=mejor) | 1.34761 | 1.28925 | 26/120 | 0.2167 | FAIL_ORDER |

TimesFM reduce el loss frente al encuadernado actual en ~4.33%, pero el orden publicado no es excepcional dentro del espacio de órdenes de bifolios. El mejor orden TimesFM fue:

`75|84 → 78|81 → 77|82 → 79|80 → 76|83`

con loss `1.22267`.

El mejor orden TF–IDF fue:

`79|80 → 76|83 → 77|82 → 75|84 → 78|81`

con cosine `0.44951`.

En el ataque adversarial, ninguna de las 10 métricas (5 globales + 5 de borde) situó el orden Layfield–Davis sobre el percentil 95 del null fijo. En el null ampliado de 3.840 secuencias, sus mejores posiciones quedaron alrededor de los percentiles 90–92, todavía sin significación confirmatoria.

## Hallazgo que sí sobrevivió

La mejora frente al encuadernado actual parece estar asociada principalmente a **tratar el bifolio/singulion como unidad física**, no a recuperar el orden exacto entre esas unidades:

- En TF–IDF, las 120 permutaciones de bifolios superaron al orden encuadernado actual.
- En char-3gram y Jensen–Shannon ocurrió lo mismo; en Jaccard ocurrió en 96.7% de los órdenes.
- En TimesFM, 62.5% de los órdenes de bifolios superaron al encuadernado actual.
- La métrica estricta de borde TF–IDF no mostró el mismo patrón (49.2% superó al actual), lo que impide vender la señal como una continuidad local universal.

Esto separa dos hipótesis que antes estaban mezcladas:

**H1 — estructura por bifolios/singuliones:** recibe apoyo descriptivo independiente.

**H2 — orden exacto Layfield–Davis entre singuliones:** no recibe apoyo confirmatorio en Q13.

## Conclusión

Resultado principal: **FAIL_ORDER**.

El experimento no recupera de manera independiente el orden Q13 atribuido a Layfield–Davis. Sin embargo, produce un resultado más específico y útil: la representación textual y TimesFM favorecen con frecuencia la reorganización por unidades físicas de bifolio frente al orden encuadernado actual. La señal está en la **unidad física**, no en una secuencia inter-bifolios única.

Esto no es desciframiento y no permite inferir semántica. Tampoco debe presentarse todavía como descubrimiento independiente de la hipótesis singulion, porque esa estructura ya fue propuesta codicológicamente. Sí constituye una corroboración computacional candidata que merece réplica en Q20 y en otros cuadernos.

## Próxima falsación necesaria

1. Extraer y verificar contra la fuente primaria la secuencia exacta publicada para Q20.
2. Repetir el torneo sin cambiar representación, métricas ni umbrales.
3. Separar estadísticamente el efecto **dentro del bifolio** del efecto **entre bifolios** mediante un modelo de pares emparejados.
4. Repetir por Currier/mano/sección y con otra transliteración independiente.
5. Sólo si la señal de unidad física replica, formular un paper sobre reconstrucción codicológica asistida por señales textuales; no sobre desciframiento.

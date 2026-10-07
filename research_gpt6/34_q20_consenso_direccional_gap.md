# 34. Q20 — consenso direccional y relocalización del bifolio perdido

Fecha: 2026-10-07
Estado: **hipótesis de trabajo falsable; no desciframiento**

## 1. Reducción del espacio de órdenes

Se recombinaron únicamente diagnósticos ya congelados: seis flechas direccionales estables, frecuencias bootstrap de adyacencia y similitudes residuales tras retirar la ventaja media de los bloques S/T.

De `6! = 720` órdenes de los seis bifolios supervivientes de Q20:

- 28 satisfacen las seis flechas direccionales;
- al imponer además las hipótesis externas `105|114` primero y `103|116` último quedan sólo **6**;
- entre esos seis, un único orden maximiza simultáneamente la suma bootstrap y la suma residual:

**`105|114 → 106|113 → 107|112 → 104|115 → 108|111 → 103|116`**

Métricas congeladas del ganador:

- bootstrap edge sum: **2.560**;
- residual edge sum: **1.9413276674**;
- restricciones direccionales: **6/6**.

## 2. Relocalización de `109|110`

El análisis previo del gap estaba condicionado a una variante que sólo satisfacía 5/6 flechas. Al repetir exactamente el criterio de debilidad de interfaz sobre el nuevo ganador 6/6, las cinco interfaces observadas son:

| interfaz | bootstrap | residual | flecha estable |
|---|---:|---:|---|
| `105|114 — 106|113` | 0.173 | 0.02358 | no |
| `106|113 — 107|112` | 0.727 | 1.05436 | sí |
| `107|112 — 104|115` | 0.406 | 0.25002 | no |
| `104|115 — 108|111` | 0.348 | 0.11531 | no |
| `108|111 — 103|116` | 0.906 | 0.49805 | sí |

Bajo Pareto de **debilidad** —menor bootstrap, menor residual y menor apoyo direccional— queda una sola interfaz no dominada:

**`105|114 ↔ 106|113`**

Por tanto la reconstrucción aumentada de trabajo pasa a ser:

**`105|114 → [109|110] → 106|113 → 107|112 → 104|115 → 108|111 → 103|116`**

Esto reemplaza como hipótesis principal al hueco `104|115 ↔ 108|111`, que dependía del candidato anterior.

## 3. Corroboración de layout — exploratoria

Usando conteos externos de estrellas marginales, las cuatro fronteras observables después del gap son:

- `113v → 107r`: 15 → 15;
- `112v → 104r`: 13 → 13;
- `115v → 108r`: 13 → 16;
- `111v → 103r`: 19 → 19.

Tres de cuatro coinciden exactamente. Entre las 24 permutaciones de las unidades intermedias condicionadas a los extremos y a colocar el gap después de `105|114`, el candidato es el único con suma `Σ|Δ estrellas| = 3`, rango **1/24**.

Esta métrica se examinó después de conocer el candidato y por tanto se etiqueta **post-hoc / exploratoria**. No se interpreta su rango como p-value confirmatorio.

Un audit adicional de layout mostró que, entre los seis órdenes que cumplen 6/6 flechas y los dos extremos, el candidato es simultáneamente no peor y al menos una vez mejor que cada alternativa en tres medidas: variación de conteo de estrellas, cantidad de marcas rojas y número de líneas. Estas variables están correlacionadas y fueron inspeccionadas post-hoc, por lo que constituyen convergencia exploratoria, no tres replicaciones independientes.

## 4. Evidencia adversarial

Transferencias de pigmento y wormholes de Q20 prueban que existieron estados físicos de apilamiento distintos, pero no fijan automáticamente el orden original de producción. Algunas transferencias conocidas contradicen nuestro orden sólo si se demuestra que ocurrieron en el primer ensamblaje; trabajos de Pelling las interpretan en varios casos como contactos de estados de encuadernación posteriores.

La reconstrucción de Pelling de 2010 coincide con nuestro prefijo `105|114 → 106|113 → 107|112`, pero invierte el orden relativo de `108|111` y `104|115` respecto de nuestro candidato. Esa comparación se documenta por separado en `35_q20_external_2010_comparison.md`.

## Clasificación

**`STRONG_TEXTUAL_ORDER_CANDIDATE / MISSING_BIFOLIUM_LOCATION_PREDICTION / PHYSICAL_VALIDATION_PENDING`**

No afirmar todavía:

- orden histórico demostrado;
- ubicación física probada de `109|110`;
- desciframiento.

La predicción físicamente falsable es ahora concreta: evidencia material de producción original que coloque `109|110` en una interfaz distinta de `105|114 ↔ 106|113` debería degradar o descartar esta reconstrucción.

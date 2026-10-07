# 37. Protocolo congelado — exceso local de borde tras retirar similitud global

Fecha: 2026-10-07

## Motivación

El control adversarial de interfaz (`35`/`36`) produjo **FAIL_EDGE_SPECIFIC**: la interfaz físicamente motivada `tail(verso) → head(recto)` (TH) no superó de forma consistente a HH, TT o HT. Eso sugiere que el score previo puede estar capturando similitud global entre folios, sección, mano o distribución léxica, más que continuidad local de lectura.

Este protocolo congela una prueba de seguimiento **antes** de ejecutar cualquier resultado nuevo. No se modifica el resultado negativo anterior.

## Hipótesis falsable

Si existe continuidad local específica en el borde correcto, entonces, una vez retirado el componente lineal explicable por similitud global de página, el residuo TH debería ordenar los bifolios físicos mejor que los residuos obtenidos con interfaces geométricamente incorrectas.

## Unidades

Se mantienen exactamente los siete quires del control anterior:

- A (`1–8`)
- B parcial (`9|16`, `10|15`, `11|14`; gap `12|13` no imputado)
- C (`17–24`)
- D (`25–32`)
- E (`33–40`)
- F (`41–48`)
- G (`49–56`)

Q13 y Q20 siguen excluidos porque originaron hipótesis de orden no estándar.

## Datos congelados

- ZL3b desde el commit fuente `47e6a77dc9d5cd570c375f4aff710fa4a0567278`.
- Takahashi IT2a con el SHA-256 ya fijado por `order_quire_c_nesting.py`.
- mismas parejas físicas y orientación interna de bifolio;
- mismas tres componentes del score: TF-IDF de tokens, TF-IDF de caracteres 3–5 y Jaccard de tokens;
- z-normalización por componente y promedio simple.

## Ventanas

La prueba primaria usa sólo ventanas locales `25, 50, 100, 200` tokens.

Se excluye `whole_page` porque allí la “ventana local” coincide esencialmente con la similitud global usada como nuisance predictor y el residuo dejaría de tener interpretación local.

## Predictor global de nuisance

Para cada quire y transcripción se calcula una matriz global `G(a,b)` entre la página completa `verso(a)` y la página completa `recto(b)` usando exactamente las mismas tres componentes y el mismo promedio que el score previo.

Esta matriz **no usa el orden físico candidato** ni la verdad de emparejamiento; se calcula para todos los pares dirigidos `a != b`.

El predictor global contiene también los bordes locales y por ello este control es deliberadamente conservador: puede retirar parte de una señal local genuina. Un PASS sería por tanto más fuerte; un FAIL cerraría la interpretación específica de borde con mayor confianza.

## Matrices locales

Para cada ventana se calculan los mismos cuatro modos del protocolo 35:

1. TH: `tail(verso origen) → head(recto destino)` — interfaz físicamente motivada.
2. HH: `head(verso origen) → head(recto destino)`.
3. TT: `tail(verso origen) → tail(recto destino)`.
4. HT: `head(verso origen) → tail(recto destino)`.

## Residualización global preregistrada

Para cada quire, transcripción, ventana y modo se ajusta por mínimos cuadrados simples sobre **todos los pares dirigidos de folios del quire**:

`L(a,b) = alpha + beta * G(a,b) + epsilon(a,b)`

La matriz usada para ordenar es `epsilon(a,b)`.

- No se usa la identidad del orden correcto al ajustar `alpha` o `beta`.
- No se seleccionan pares, ventanas ni modos según el resultado.
- Si `Var(G)=0`, se fija `beta=0` y se centra `L` por su media; el caso debe reportarse.

Se reportan `beta`, correlación de Pearson local-global y varianzas para auditar cuánto score se retiró.

## Ranking

- A/C/D/E/F/G: se enumeran los `4! = 24` anidamientos congelados.
- B parcial: `3! = 6`, puntuando sólo las cuatro interfaces observadas y nunca el gap central.

Para comparar quires con distinto número de candidatos:

`rango_normalizado = (rango - 1) / (N - 1)`.

Para cada quire/modo se toma la mediana de sus `2 transcripciones × 4 ventanas = 8` rangos normalizados.

Las ocho observaciones son correlacionadas y no se tratan como réplicas independientes.

## Comparación primaria

Para cada quire:

`best_wrong = min(HH, TT, HT)`

TH cuenta como victoria sólo si `mediana_TH < best_wrong`; los empates no cuentan.

## Regla de decisión congelada

- **PASS_LOCAL_EDGE_SPECIFIC_EXPLORATORY** si TH vence al mejor control incorrecto en `>= 6/7` quires **y** la mediana global TH es menor que la mediana global de HH, TT y HT por separado.
- **FAIL_LOCAL_EDGE_SPECIFIC** si TH vence al mejor control incorrecto en `<= 3/7` quires.
- **INCONCLUSIVE** en cualquier otro caso.

Como resultado secundario se reportan tests exactos de signos unilaterales por quire, pero no cambian la decisión congelada.

## Control secundario de metadata

Después de retirar la similitud global se repetirá el ranking aplicando además la residualización exacta Davis-H + Currier-L ya congelada en experimentos anteriores. Este análisis es secundario y no puede rescatar un FAIL primario.

## Criterio de cierre de rama

Si el resultado primario es **FAIL_LOCAL_EDGE_SPECIFIC**, se considera refutada para este programa la interpretación de que el score actual identifica continuidad de lectura localizada en bordes verso→recto. Se podrán conservar resultados de estructura global/pairing, pero no se seguirá optimizando órdenes con esta métrica de borde salvo que aparezca una fuente de evidencia independiente.

## Techo de interpretación

Incluso un PASS sólo apoyaría especificidad estructural local de borde. No implica semántica, idioma, traducción ni descifrado.
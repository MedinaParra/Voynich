# 74 — Mejora pequeña del lector mediante suma de alineaciones CTC

27 de octubre de 2026. Rama `experiment/kraken-voynich`.

**El nuevo decodificador reduce ocho errores EVA en la hoja 7, con las mismas probabilidades y pesos:** 442/709, CER 62,3413 %, pasa a 434/709, **61,2130 %**. En el criterio principal —76 formas no vistas, 446 caracteres— reduce sólo dos errores, de 310 a 308, **69,5067 % a 69,0583 %**. Se mantiene en **0/76 transcripciones completas exactas**. Es una mejora mecánica pequeña y reproducible en estas muestras, sin evidencia de haber resuelto la generalización ni obtenido una traducción.

## Intervención fijada antes de ejecutar

Tras el resultado negativo del [ensayo de agrupación 72](72_eva_unit_composition_result.md), el [protocolo 73](73_ctc_posterior_protocol.md) fijó un haz de 32 prefijos, sin diccionario, modelo de lenguaje, poda de caracteres o ajuste de temperatura. El algoritmo CTC y la búsqueda por prefijos son conocidos y citados; no se presenta esta aplicación como un método inédito.

Se conservó el modelo ampliado del ensayo 70, SHA-256 `35092d9baf56083eb6c70a2e32c478d8910ef5e685d0cee33fc5a935ca1c71d8`, sin otro entrenamiento. Se capturaron exactamente las matrices que recibe el decodificador original de Kraken 7.1. La ruta más probable por instante se comparó con la acumulación de probabilidades de alineaciones conservadas por un haz finito. El haz es aproximado, no una enumeración global exhaustiva. Las referencias sólo puntúan el texto una vez decodificado.

La [ejecución 40575635206](https://github.com/MedinaParra/Voynich/actions/runs/40575635206), commit `08dd2af824dd632dfb29b1c274614a81a04b0726`, completó los seis controles matemáticos y la inferencia. Se trabajó con las mismas 147 palabras de la hoja 4 y 135 de la 7, ya exploradas. f5r sigue excluido y las referencias continúan siendo candidatas sin revisión experta nueva.

## Comprobación de la interfaz y controles

Un máximo por instante independiente reprodujo los textos originales de Kraken en **564/564 comprobaciones**. Se hicieron dos pasadas completas de 282 muestras, con **564 llamadas reales a la red**. Las matrices guardadas coincidieron exactamente entre pasadas, y también los textos de los tres decodificadores. Los catorce registros tensoriales del modelo antes y después coincidieron.

`beam32` usa únicamente los vectores de probabilidad. `shuffled_beam32` conserva todos esos vectores y altera su orden mediante una permutación fijada por muestra. Es un control temporal del decodificador; no son imágenes independientes ni una prueba de causalidad semántica. La primera pasada estaba fijada como comparación principal; no se escogió la más favorable.

| Método | Formas no vistas de hoja 7: errores / 446 | CER principal | Exactas / 76 | Toda hoja 7: errores / 709 | CER hoja 7 | Exactas / 135 |
|---|---:|---:|---:|---:|---:|---:|
| Kraken original, ruta máxima | 310 | 69,5067 % | 0 | 442 | 62,3413 % | 9 |
| Haz 32, suma de alineaciones retenidas | **308** | **69,0583 %** | 0 | **434** | **61,2130 %** | 9 |
| Haz 32, instantes permutados | 438 | 98,2063 % | 0 | 679 | 95,7687 % | 0 |
| Vecino por imagen, cálculo conservado | 332 | 74,4395 % | 0 | 467 | 65,8674 % | **11** |

En la hoja 4, la ruta máxima obtiene 416/744, CER 55,9140 %, y el haz 412/744, **55,3763 %**. Ambos tienen 9/147 palabras exactas; el comparador por imagen conserva 14/147. El control temporal obtiene 722/744 errores y una coincidencia exacta. Todos los desgloses por longitud y vocabulario se conservan completos.

En la hoja 7 cambiaron 15 textos: nueve redujeron su distancia de edición, uno la aumentó y los restantes conservaron el error. En la hoja 4 cambiaron 13: seis redujeron error y dos lo aumentaron. La mejora no es uniforme y no aumentó el número de palabras exactas. Ocho errores menos sobre 709 equivalen a **1,1283 puntos porcentuales**; dos sobre 446, a **0,4484 puntos**. No se estimó significación estadística con esta única hoja reservada y una sola semilla/modelo.

Las cifras se comparan con la ruta máxima obtenida de las mismas matrices, no con otro servidor. El 62,4824 % publicado en el ensayo 70 corresponde a otra inferencia del mismo archivo; ya se documentó variación entre equipos. Se evita atribuir a este decodificador la diferencia adicional de ese otro cálculo.

## Qué mejora y qué permanece abierto

La modificación cambia cómo se leen las probabilidades, no los pesos del modelo ni los textos de referencia. La coincidencia con el original antes de aplicar el haz verifica que la comparación usa la misma señal de entrada al decodificador. No se han forzado palabras del corpus ni elegido salidas por su parecido con la referencia.

Los dos ensayos realizados en esta continuación permiten acotar cambios concretos: agrupar EVA no mejoró el criterio principal y sumar alineaciones sí redujo ligeramente el error. Ninguno produjo una transcripción completa correcta de las 76 formas no vistas. Esto no identifica una causa única del fallo: siguen abiertos la diversidad de ejemplos, la calidad de las asociaciones imagen/texto y la representación visual. Los controles de geometría y hashes tampoco sustituyen una revisión paleográfica.

Se conserva el modelo anterior como candidato principal y el haz 32 queda como **opción experimental**. La evidencia no justifica declarar listo un lector del manuscrito completo, una clave o una traducción.

## Verificación y reproducción

La [auditoría independiente](results/kraken_ctc_posterior/audit.json) pasó **13.008 comprobaciones sin discrepancias**. Reimplementa la recurrencia con multiplicación, sumas y reescalado en espacio de probabilidades, separada de la versión principal en logaritmos. Recalcula textos y masas del haz en todas las matrices originales y permutadas de ambas pasadas; comprueba codec, hashes, probabilidades, máximos, selecciones, distancias con matriz completa y todos los grupos. No vuelve a ejecutar la red.

Los seis controles previos incluyen enumeración exhaustiva de todos los caminos en ejemplos pequeños, una situación donde la suma CTC supera a la ruta máxima, repetición separada por blanco, entradas inválidas, secuencia vacía y desempates. Son controles del algoritmo; no son nuevas muestras del manuscrito.

Se conserva el [artefacto completo y su procedencia](results/kraken_ctc_posterior/provenance.json), incluido su digest ZIP verificado. Las dos matrices NPZ, codec, registros de captura, prueba de interfaz y todas las predicciones están guardados en Git, además del artefacto temporal de Actions. Los NPZ se leen sin permitir objetos pickle. Los JSON grandes usan compresión reversible con inventario de hashes.

```bash
python research_gpt6/code/audit_kraken_ctc_posterior.py \
  --bundle research_gpt6/results/kraken_ctc_posterior \
  --repo research_gpt6 --out work/ctc_posterior_audit.json
```

El auditor requiere numpy y Pillow por el helper de distancia ya conservado; no necesita Torch ni Kraken ni acceso a artefactos que puedan caducar. La inferencia completa se reproduce con el entorno del workflow y:

```bash
python research_gpt6/code/kraken_ctc_posterior.py \
  --plan research_gpt6/data/kraken_ctc_posterior_plan.json \
  --repo research_gpt6 --out work/ctc_posterior_replay
```

El helper `ctc_prefix_tools.prefix_beam` recibe matrices tiempo×clase y devuelve prefijos con masa logarítmica aproximada; la conversión a EVA utiliza el codec, no un diccionario de palabras. No proporciona por sí solo anotaciones paleográficas de cortes ni una interpretación de los textos.

Fuentes primarias del método: [Graves et al., ICML 2006](https://www.cs.toronto.edu/~graves/icml_2006.pdf) y el código fijado de [Kraken 7.1](https://github.com/mittagessen/kraken/blob/7.1/kraken/lib/ctc_decoder.py). Implementación nueva propia, con todas las comparaciones y resultados negativos preservados. Identificación de lengua y traducción: **NOT_RUN**.

# Filtro de mecanismos: resultados ejecutados
6 de octubre de 2026. [Protocolo fijado localmente antes de ejecutar](18_protocolo_mecanismos.md). No es prerregistro externo, ni réplica exacta de un paper.

## Hallazgo principal
Un generador sin significado, aprendido de las hojas de entrenamiento, reproduce la magnitud de la MI de bordes de 20 grupos de hoja reservados bajo ambas segmentaciones. No reproduce simultáneamente las repeticiones, vecindad por edición y estructura interna. La dependencia de borde es por tanto insuficiente como evidencia de cifrado o semántica. Ninguno de los cinco controles cubre las seis métricas dentro de los intervalos de simulación. Esto describe su insuficiencia, no rechaza familias completas.

## Comparación
Los valores de controles son medianas de 50 muestras; el manuscrito es un único conjunto reservado. Exceso MI: observado menos media de 19 permutaciones intra-tramo por muestra. Distancia de edición ≤1 incluye identidad. Entropía H1 usa transiciones dentro de tokens, en caracteres EVA/ASCII; no glifos establecidos ni fonemas.

### Comas separadoras
Test: 7003 tokens, 5819 pares, 1184 tramos y 20 grupos de hoja.

| Texto / mecanismo | Exceso MI borde bits | H1 interno bits | Repetición exacta | Edición ≤1 | Longitud media |
|---|---:|---:|---:|---:|---:|
| Voynich reservado | 0.18613 | 1.97831 | 1.306% | 5.241% | 5.026 |
| Palabras independientes | -0.00016 | 2.04056 | 0.378% | 2.148% | 4.962 |
| Palabras con enlace | 0.17933 | 2.03462 | 0.378% | 2.251% | 4.956 |
| Copia literal 15% (control ilustrativo) | 0.00369 | 2.03632 | 15.381% | 16.979% | 4.972 |
| Latín: Apicio | 0.07707 | 3.08071 | 0.086% | 0.361% | 5.683 |
| Latín: César | 0.03566 | 3.12282 | 0.000% | 0.369% | 5.997 |

Generador con enlace: exceso MI en intervalo descriptivo 0.16756–0.19660; observado 0.18613. Las otras cuatro métricas (H1, repetición, edición y longitud) quedan fuera del intervalo del generador.

### Comas unidas
Test: 6498 tokens, 5323 pares, 1175 tramos y 20 grupos de hoja.

| Texto / mecanismo | Exceso MI borde bits | H1 interno bits | Repetición exacta | Edición ≤1 | Longitud media |
|---|---:|---:|---:|---:|---:|
| Voynich reservado | 0.15047 | 2.00026 | 1.371% | 4.772% | 5.405 |
| Palabras independientes | -0.00017 | 2.06109 | 0.301% | 1.794% | 5.342 |
| Palabras con enlace | 0.14772 | 2.05740 | 0.310% | 1.822% | 5.335 |
| Copia literal 15% (control ilustrativo) | 0.00222 | 2.05949 | 15.236% | 16.494% | 5.349 |
| Latín: Apicio | 0.07939 | 3.07287 | 0.113% | 0.395% | 5.685 |
| Latín: César | 0.03435 | 3.12090 | 0.000% | 0.376% | 5.981 |

Generador con enlace: exceso MI en intervalo descriptivo 0.13709–0.16247; observado 0.15047. Las otras cuatro métricas (H1, repetición, edición y longitud) quedan fuera del intervalo del generador.

## Mecanismos y controles
El generador con enlace elige la inicial según carácter final anterior y banda de posición; después muestrea un token de entrenamiento con esa inicial. No tiene lexicón semántico, traducción o mensaje oculto. Las longitudes de tramos del test se imponen como condición de simulación; no se generan páginas completas libremente. El muestreo independiente también aprende frecuencias por banda. Estos generadores agrupan cuadernos/manos del entrenamiento; parte de su desajuste de longitud o H1 puede reflejar diferencias de composición entre entrenamiento y test. No se los presenta como controles estratificados completos. La copia 15% es una demostración con probabilidad fija, no un ajuste al test ni un sustituto del algoritmo histórico publicado de autocita; su fallo no refuta dichos algoritmos.

Los controles latinos emplean recetas de Apicio (libros 1–5) y César (Gallia 1–3), normalizados a ASCII minúsculo y con líneas de encabezado en mayúsculas excluidas. Se verificaron los ocho blobs originales y sus SHA-256. Las ventanas contiguas mantienen número de tokens y geometría de tramos del test, pero no igualan frecuencia, época, tema, mano o longitud de palabra. Las ventanas se solapan y en Apicio hay poca variedad de posiciones disponibles: sus intervalos no representan incertidumbre de todo el latín.

**PASS de invariancia:** una sustitución monoalfabética bijectiva fija conserva estas seis métricas, comprobado con rotación 7 y mismo barajado. Por tanto, sustituir letra a letra estos dos corpus conservando espacios no resuelve sus diferencias. Esto no descarta latín abreviado, otras fuentes, homofonía, sílabas, unidades multicaracter, eliminación de vocales, segmentación distinta ni otras lenguas. La comparación directa de H1 depende de la representación EVA.

## Evidencia y reproducción
Python 3.12.14; ejecución terminada con exit 0; compilación sintáctica exit 0. Semilla 20261006, 50 simulaciones/mecanismo/modo, 19 barajados/muestra. Los intervalos usan el segundo y penúltimo valor ordenado de 50 muestras: son descriptivos y no p-valores ni intervalos de confianza de una hipótesis histórica. Métricas correlacionadas; no se ajustó un ranking conjunto ni se calcularon rechazos estadísticos de familias.

[Código](code/mechanism_controls.py), [resultados y hashes](results/mechanism_controls.json), [fuentes latinas en base64](data/latin_sources.json) y [licencia de origen](data/LATIN_LICENSE.md). Los bytes latinos se conservan dentro del JSON; el script los verifica automáticamente. Fuente [CLTK Latin Library](https://github.com/cltk/lat_text_latin_library/tree/76229acaf02efd1964ac32009408a90b6f279758) procedente de The Latin Library. La licencia de origen identifica Public Domain Mark 1.0. No implica respaldo de CLTK a este análisis.

Desde la raíz del repositorio, con corpus EVA exacto fijado en el informe 15:

```bash
python research_gpt6/code/mechanism_controls.py --corpus corpus/voynich_eva.txt --latin research_gpt6/data/latin_sources.json --out research_gpt6/results/mechanism_controls.json
```

## Decisión de investigación
Se mantiene la vía contextual, pero se abandona la idea de usar el borde como prueba suficiente de una clave. El siguiente mecanismo debe explicar también copia/modificación local y unidades internas, aprender todos sus parámetros en entrenamiento y predecir hojas o cuadernos reservados. La comparación de lenguaje/cifrado debe ampliar idiomas y fuentes y controlar unidades antes de seleccionar una lengua.

| Afirmación | Estado |
|---|---|
| Los modelos se ejecutaron sobre reserva y fuentes verificadas | PASS ejecución |
| El borde distingue por sí solo significado/cifrado de generación | No respaldado: control sin semántica reproduce esa métrica |
| Uno de los cinco controles explica todas las métricas medidas | FAIL de adecuación descriptiva en este test |
| Se descartó toda una familia de cifrados o todo el latín | NOT_RUN |
| Se identificó idioma y clave inversa | NOT_RUN |
| Se tradujo texto con correspondencias validadas | BLOCKED: correspondencia semántica ausente |

No se produce una traducción aproximada rellenando correspondencias no identificadas. El avance es que el experimento separa una regularidad reproducible de una condición suficiente para descifrar.

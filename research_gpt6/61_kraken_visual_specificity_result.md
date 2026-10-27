# 61 - Kraken responde a las imágenes, pero transfiere poco entre hojas

Fecha: **27 de octubre de 2026**. Rama `experiment/kraken-voynich`. Ejecución corregida [40512656009](https://github.com/MedinaParra/Voynich/actions/runs/40512656009), commit `469761426e9fb3879f47f7cc129d151860936b23`.

**Resultado: hay sensibilidad visual, con una ventaja pequeña de la imagen correcta en desarrollo.** El modelo conservado del ensayo 59 cambia sus salidas cuando se reflejan o desordenan las imágenes. En las páginas usadas para ajustar el modelo, esas alteraciones empeoran mucho el error; en la otra hoja, la diferencia es de solo 4,29 puntos. No se entrenó ningún modelo nuevo y no hubo avance de traducción.

El [protocolo 60](60_kraken_visual_specificity_protocol.md) fija las condiciones, las semillas y las agrupaciones. Las hojas y el modelo ya se habían explorado; esta es una prueba de desarrollo del funcionamiento del sistema. La repetición corrigió una incidencia de instrumentación después de ver los primeros resultados. No constituye una evaluación ciega ni dos réplicas estadísticas independientes.

## Resultado del modelo congelado

Se mantuvieron los mismos pesos, etiquetas y recortes. Se regeneraron los 122 registros de ambas extracciones anteriores y coincidieron con sus referencias congeladas. Se intervinieron únicamente los 61 recortes corregidos: 34 de entrenamiento, con 980 unidades de referencia, y 27 de desarrollo, con 699. Cada unidad es un código convencional de Boxer o un espacio, sin interpretación fonética.

| Entrada del mismo modelo | Errores en entrenamiento / 980 | Error en entrenamiento | Errores en desarrollo / 699 | Error en desarrollo |
| --- | ---: | ---: | ---: | ---: |
| Imagen intacta | 244 | **24,8980 %** | 516 | **73,8197 %** |
| Reflejo horizontal | 669 | 68,2653 % | 546 | 78,1116 % |
| Ocho franjas verticales reordenadas | 616 | 62,8571 % | 546 | 78,1116 % |
| Imagen blanca | 980 | 100 % | 699 | 100 % |

En desarrollo, tanto el reflejo como las franjas añaden **30 errores**, o **4,2918 puntos porcentuales**. Las 27 predicciones cambian bajo cada alteración. Esto acredita sensibilidad de la salida al contenido visual, pero el beneficio de la imagen intacta es pequeño respecto del alto error residual. Las transformaciones también introducen entradas fuera de distribución y no aíslan una única capacidad del modelo.

En entrenamiento, el reflejo empeora el error en **43,3673 puntos**, y las franjas en **37,9592 puntos**. La diferencia respecto del comportamiento en desarrollo es compatible con un ajuste muy específico de estas páginas o con otros desajustes de datos. Este ensayo no reparte causalmente el error entre recortes, referencias y modelo ni prueba una causa única.

Todas las unidades presentes en las referencias de desarrollo aparecen también en entrenamiento: 20 unidades distintas en desarrollo y 21 en entrenamiento, contando el espacio. La falta de categorías completamente nuevas no explica por sí sola el error alto. Esto no asegura suficientes ejemplos de cada categoría ni corrección paleográfica de las etiquetas.

Las 27 predicciones intactas de desarrollo reproducen exactamente las preservadas en el ensayo 59. En la alineación mínima elegida se cuentan 279 sustituciones, 200 eliminaciones y 37 inserciones: 516 errores. El reparto por tipos depende del desempate de alineaciones y no identifica causas físicas de los errores.

## Control de llamadas y de imágenes blancas

La ejecución corregida detecta llamadas reales a la red en los **183 registros de condiciones no blancas**, incluidos los 61 intactos exigidos como control positivo. Las 61 entradas blancas producen cadenas vacías con cero llamadas al módulo observado: el sistema las omite antes de pasar por la red.

Por tanto, el resultado de la fila blanca describe el comportamiento del pipeline. No se realizó una prueba de la red sobre un tensor blanco introducido directamente, ni se interpreta esa fila como prueba de ausencia de salidas espurias de la red.

El hook se instaló en `TorchSeqRecognizer.nn.nn`, módulo que usa el [código de Kraken 7.1](https://github.com/mittagessen/kraken/blob/7.1/kraken/lib/models.py). Si cualquier intacto carece de llamada, el programa marca `INSTRUMENTATION_INVALID` y termina con error.

## ¿La predicción coincide mejor con su renglón que con otro parecido?

Se guardaron 9.999 reasignaciones de referencias por rol, usando las mismas reasignaciones entre condiciones. Los grupos preservan folio y mitad de relación ancho/alto. Son simulaciones de asignaciones, no modelos nuevos, muestras independientes o ciclos de evolución del software.

Para la entrada intacta de desarrollo, el error observado es 516. La media de las asignaciones permutadas es **534,06**, equivalente a aproximadamente **76,40 %** de error. La ventaja observada frente a esa media es de **18,06 errores**, o **2,58 puntos porcentuales**.

| Entrada en desarrollo | Errores observados | Media de errores bajo permutación | Fracción diagnóstica de cola inferior, con +1 |
| --- | ---: | ---: | ---: |
| Intacta | 516 | 534,0624 | 0,0197 |
| Reflejada | 546 | 557,1368 | 0,1646 |
| Franjas reordenadas | 546 | 553,5904 | 0,2702 |
| Blanca | 699 | 699,0000 | 1,0000 |

En la condición intacta, 196 de las 9.999 reasignaciones dan un error menor o igual al observado. Esa comparación sugiere asociación entre la imagen y su referencia dentro de estos grupos. **La intercambiabilidad no está garantizada**, quedan diferencias geométricas y las referencias son provisionales. La fracción no se presenta como significación confirmatoria, identificación de una lengua o evidencia de desciframiento. Tampoco establece cuánto se generaliza a otras hojas.

## Incidencia preservada y estabilidad de las salidas

El primer [run 40511667932](https://github.com/MedinaParra/Voynich/actions/runs/40511667932), commit `9b7c6f85978d571d27129b75f4b7fb2ff36d7aeb`, completó las cuatro condiciones, pero el contador estaba conectado al contenedor `net.nn`, que no recibe la llamada de esta API. Marcó cero incluso con predicciones no vacías. Sus campos de llamadas y supuestos cortocircuitos son **inválidos**. El estado `success` de GitHub solo certificaba que el programa había terminado.

Se corrigió el módulo observado y se añadió el control positivo obligatorio. Las condiciones, semillas, grupos, puntuación y modelo permanecieron fijos. Se preservan el [resultado bruto del intento](results/kraken_visual_specificity/attempts/01_counter_invalid/result.json), sus predicciones y la [evaluación de la incidencia](results/kraken_visual_specificity/attempts/01_counter_invalid/assessment.json).

La [comparación entre ejecuciones](results/kraken_visual_specificity/attempt_comparison.json) verifica **244 imágenes de entrada idénticas byte por byte**. Hay una diferencia de predicción en `3v.p2.l3`, condición intacta de entrenamiento: se emite una unidad adicional, y el error agregado pasa de 243/980 a 244/980. No se atribuye a una causa numérica única ni se afirma invariancia bit a bit entre las pasadas. Las 27 salidas intactas de desarrollo son iguales al ensayo anterior y entre ambos intentos. Se usan los datos del segundo intento, que pasó el control de instrumentación, sin seleccionar la mejor puntuación de entrenamiento.

## Auditoría y evidencia reproducible

- Pasaron cuatro controles distintos del harness, localmente y en CI: distancias conocidas, conservación de píxeles, grupos de permutación y un predictor constante que no debe obtener ventaja de asignación.
- Se intentaron y preservaron **244 registros por ejecución**, sin fallos de fila. Son cuatro condiciones sobre los mismos 61 renglones, no 244 muestras independientes.
- La [auditoría de exportación](code/audit_kraken_visual_specificity.py) verificó archivos PNG, etiquetas, transformaciones, tamaños, hashes, reproducción anterior y cálculos. Recalculó las distancias con una implementación separada y reprodujo todos los recuentos de permutación: **3.425 comprobaciones, cero discrepancias**. No ejecutó otra vez las redes ni validó las etiquetas como lecturas expertas. [Resultado](results/kraken_visual_specificity/audit.json).
- Los SHA-256 de ambos ZIP se verificaron contra los digests de GitHub. Cada ZIP contiene 567 archivos. Los manifiestos son inventarios calculados de esos archivos; no se presenta una referencia externa individual por archivo.

Se preservan [resultado corregido](results/kraken_visual_specificity/result.json), [predicciones por condición](results/kraken_visual_specificity/predictions), [todos los recuentos de permutación](results/kraken_visual_specificity/permutation_counts.json), [comparación de intentos](results/kraken_visual_specificity/attempt_comparison.json) y [procedencia](results/kraken_visual_specificity/provenance.json). Los modelos y fuentes congeladas siguen en el ensayo 59. Los árboles completos de PNG quedan en los artefactos, con retención hasta el **26 de noviembre de 2026**; las entradas se pueden regenerar desde el código y las fuentes preservadas.

Modelo SHA-256: `b5df9eef0a783bec696b33636fbfb8d4807bfaa256d74ad6b34df4c58db66acb`.

Plan corregido SHA-256: `4bd10c8ad5bc2ee639258e5ca213bfe58b6abb1377cd4fc91f4c92ae81e19ea5`.

ZIP corregido SHA-256: `787b5a8a36a4ab663b661350bd7e76d9cf2869fdbdd1c776be8d39c1d16f80b3`.

```bash
python research_gpt6/code/kraken_visual_specificity.py \
  --plan research_gpt6/data/kraken_visual_specificity_plan.json \
  --repo research_gpt6 --out work/kraken_visual_specificity
python research_gpt6/code/audit_kraken_visual_specificity.py \
  --bundle work/kraken_visual_specificity --repo research_gpt6 \
  --output work/kraken_visual_specificity_audit.json
```

## Decisión de investigación

Esta prueba acota lo que puede aportar el modelo actual: responde a cambios visuales y muestra una asociación condicionada con las referencias, pero su reconocimiento en la hoja de desarrollo sigue siendo pobre. No se usarán estas salidas como texto fiable para adjudicar una lengua o fabricar una traducción.

La prioridad siguiente es mejorar las parejas entre imagen y transcripción: registrar coordenadas de la fuente de etiquetas contra Yale, revisar límites y trazos ambiguos y ampliar las hojas de entrenamiento. Una futura prueba confirmatoria necesita hojas físicas nuevas fijadas antes de ajustar el modelo. Este diagnóstico no convierte las referencias actuales en anotaciones expertas ni demuestra que resolver OCR baste para resolver el manuscrito.

Fuentes y atribución: Yale University Library, Beinecke MS 408; etiquetas y mapa de Alexander Boxer, CC BY 4.0, fijados y acreditados en [59](59_kraken_crop_repair_result.md). Código del diagnóstico propio; consulta del código público de Kraken para corregir la instrumentación. Identificación de lengua, traducción y revisión experta nueva: **NOT_RUN**.

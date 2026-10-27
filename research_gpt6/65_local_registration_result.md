# 65 - La corrección espacial habilita f4r como referencia geométrica candidata

Fecha: **27 de octubre de 2026**. Rama `experiment/kraken-voynich`. [Comparación 40531601364](https://github.com/MedinaParra/Voynich/actions/runs/40531601364), commit `b73fcbb472891c9ef75b5a153ae1ef272775f436`.

**f4r pasó las cinco particiones espaciales con el método fijado en el protocolo 64.** Se construyeron 64 polígonos candidatos adicionales, sin cambiar las 280 referencias antiguas ni borrar el rechazo del ensayo 63. El resultado es una mejora geométrica de desarrollo. No se entrenó otro reconocedor ni se obtuvo una traducción.

## Comparación emparejada

Se reutilizaron las correspondencias SIFT congeladas; no se eligieron coincidencias nuevas por su error en esta prueba. Cada color de una cuadrícula fuente 8×8 se reservó una vez. Los puntos de ajuste próximos a los reservados quedan excluidos por una banda de tres píxeles fuente. La homografía se ajusta sólo con el resto. La corrección local aprende la mediana de residuos vecinos únicamente de esa partición de ajuste.

Se compararon tres condiciones sobre exactamente los mismos puntos reservados: homografía global, homografía más mediana espacial y esa misma corrección con residuos permutados entre posiciones. Radio, cantidad de vecinos, umbrales, semillas y criterios de aceptación estaban [publicados antes de la ejecución](64_local_registration_protocol.md). La hipótesis surgió de un diagnóstico exploratorio del ajuste anterior; estas páginas y las correspondencias ya estaban exploradas.

| Página | Correspondencias puntuadas al agrupar las cinco reservas | P90 global | P90 con corrección local | Particiones globales que pasan | Particiones locales que pasan |
| --- | ---: | ---: | ---: | ---: | ---: |
| f3r | 796 | 2,98 px | 1,73 px | 5/5 | 5/5 |
| f3v | 608 | 5,25 px | 2,79 px | 2/5 | 5/5 |
| f4r | 414 | **7,19 px** | **3,25 px** | **0/5** | **5/5** |
| f4v | 588 | 4,66 px | 2,36 px | 4/5 | 5/5 |

Son 20 casos de página/partición y tres condiciones por caso. No son 60 experimentos independientes, veinte hojas nuevas ni veinte ciclos de evolución del sistema. Las 2.406 correspondencias se puntúan una vez cada una al agrupar las reservas de su página; varias pueden representar rasgos visuales relacionados o repetidos.

La homografía pasa 11/20 casos; el método local 20/20; el control permutado 10/20. Esto también muestra que la aceptación antigua de una sola reserva en f3v y f4v no garantiza que la homografía pase todas las nuevas particiones. Los archivos antiguos se mantienen como resultados históricos con su alcance original.

En f4r, la mediana de error pasa de **1,77 a 1,15 píxeles Yale** y la fracción dentro de cinco píxeles pasa de **79,23 % a 96,86 %**. Este último porcentaje describe correspondencias visuales propuestas por el detector, no palabras reconocidas correctamente. La homografía global y el control permutado pasan 0/5 casos; la corrección local pasa 5/5.

| Condición de f4r | P90 agrupado | Fracción dentro de 5 px | Particiones aceptadas |
| --- | ---: | ---: | ---: |
| Global | 7,1935 px | 79,2271 % | 0/5 |
| Mediana espacial | 3,2503 px | 96,8599 % | 5/5 |
| Residuos permutados | 7,1569 px | 79,7101 % | 0/5 |

El valor 9,72 píxeles del ensayo 63 corresponde a una única reserva de f4r. El 7,19 de esta tabla agrupa cinco reservas y no lo sustituye como si fuera el mismo denominador. En la partición cero, el global conserva P90 9,72 y la corrección lo reduce a 4,28; las otras cuatro particiones locales también pasan el límite de cinco píxeles.

## Interpretación y límites

La asociación espacial de los residuos contiene información útil: permutarlos elimina la mejora que permite aceptar f4r. Esto es compatible con que una homografía global sea insuficiente para representar el desajuste de estas imágenes. **No identifica su causa física**: deformación del soporte, procesado de la imagen y sesgos de localización del detector pueden producir patrones espaciales.

Todos los puntos reservados, incluidos los atípicos, permanecen en la puntuación. El error máximo de f4r sigue cerca de **1.745 píxeles**: el método no convierte todas las coincidencias en correctas. Los límites de P90 y de fracción dentro de cinco píxeles toleran una cola de errores. No se interpreta el resultado como correspondencia experta certificada ni como precisión de los bordes de cada signo.

La banda de guarda evita coordenadas casi duplicadas entre particiones, pero no garantiza independencia de los descriptores visuales o del contenido. En las cinco particiones de f4r no había puntos de ajuste a esa distancia y se excluyeron cero; no se atribuye la mejora a una eliminación de sus casos difíciles. Tampoco son estas reservas una muestra nueva del manuscrito.

## Construcción inicial de f4r

Después de pasar los criterios fijados, se ajustó el mapa final con todas las 414 correspondencias de f4r. Ese ajuste completo no recibe una nueva puntuación de reserva. Se verificó orientación positiva en una cuadrícula 17×25 y geometría convexa, orientación e inclusión en Yale de los 64 polígonos. Una cuadrícula finita no acredita ausencia de pliegues a todas las escalas.

Se conserva [el modelo geométrico](results/voynichese_local_registration/final_model.json), [la cuadrícula](results/voynichese_local_registration/orientation_grid.json), [los polígonos](results/voynichese_local_registration/word_polygons.json) y [la superposición de f4r](results/voynichese_local_registration/f4r_candidate_overlay.jpg). La vista general sigue aproximadamente las palabras, con límites de anotación y solapes todavía pendientes de revisión; no se verificaron las 64 lecturas una por una.

## Controles, auditoría y procedencia

Pasaron cinco controles numéricos, localmente y en CI: campo suave conocido frente al control permutado, exclusión de discrepancias grandes, guarda de casi duplicados, ausencia de desplazamiento sin soporte y detección de una reflexión de cuadrícula. El workflow completó todos los casos y la geometría final con estado `success`.

La [auditoría separada](code/audit_local_residual_registration.py) reconstruyó las particiones, campos locales, controles permutados, cada predicción y error reservado, criterios, anclas finales, cuadrícula y polígonos mediante otro cálculo numérico: **1.200 comprobaciones de exportación sin discrepancias**. No volvió a estimar las homografías de OpenCV ni validó independientemente las correspondencias del detector o las lecturas. [Resultado](results/voynichese_local_registration/audit.json).

Se verificó el ZIP de 927.369 bytes contra el digest de GitHub, SHA-256 `82b97a95c158f4b345c8e44eb543c874a662333b1db7e75015decc77e0d747b9`. Sus seis archivos se preservan en el repositorio, junto con [todos los casos](results/voynichese_local_registration/cases.json), [resumen](results/voynichese_local_registration/result.json), [diagnóstico previo de ajuste](results/voynichese_local_registration/fit_only_diagnosis.json) y [procedencia](results/voynichese_local_registration/provenance.json). Retención del artefacto: 26 de noviembre de 2026. El manifiesto individual es un inventario calculado, no una referencia externa por archivo.

## Versión uniforme para revisar antes de entrenar

El [protocolo 66](66_uniform_local_reference_protocol.md) fija la construcción posterior de una versión nueva con el mismo método en las cuatro páginas, consumiendo la evidencia congelada de este ensayo. No modifica los archivos antiguos ni agrega otra puntuación de validación. Estado al publicar el protocolo de construcción: **NOT_RUN**. Su resultado se incorporará una vez ejecutado y auditado.

El error de reconocimiento anterior sigue en **73,8197 % de unidades convencionales Boxer**. No se ha medido todavía el OCR con estos candidatos EVA; las dos notaciones tampoco se equiparan automáticamente. La lengua y el significado del manuscrito siguen sin resolver.

Fuentes, datos y atribución: ensayos [63](63_voynichese_registration_result.md) y [64](64_local_registration_protocol.md), fotografías Yale Beinecke MS 408, datos de Voynichese acreditados con la licencia de sus fuentes. Código nuevo propio. Las referencias siguen siendo provisionales, sin revisión experta independiente ni asignación fonética o semántica.

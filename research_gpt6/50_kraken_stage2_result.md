# 50. Kraken: reconocimiento ejecutado y resultado negativo

Ejecución: 15-10-2026. Recuperación y publicación: 26-10-2026.
Rama: `experiment/kraken-voynich`. No hay traducción validada.

El [ensayo 38707533236](https://github.com/MedinaParra/Voynich/actions/runs/38707533236), commit `19e12c1585697ff1e0cd596ed4381704115e15ef`, completó entrenamiento e inferencia. Pasó 19 controles del código, pero falló los dos criterios científicos. El [protocolo](49_kraken_stage2_protocol.md) se fijó antes de observar las nuevas predicciones, en `76815c7e9902de04f6319893a3255bdc60ad056f`.

## Segmentación asistida

Se calibraron seis configuraciones sobre las hojas 1/2 y se seleccionó tolerancia 0,45 con corrección de pendiente. En la hoja 4 reservada, las regiones manuales y el ensamblado recuperaron las 27 filas esperadas: 13 en f4r y 14 en f4v.

| Resolución | F1 sin corrección | F1 ensamblado | Filas / referencia |
|---|---:|---:|---:|
| 1800 px | 0,4000 | 0,8519 | 27 / 27 |
| 1200 px | 0,4286 | 0,7778 | 27 / 27 |

El emparejamiento usa IoU ≥0,5 contra referencias provisionales. Se exigió F1 ≥0,80 en ambas resoluciones; resultado: **FAIL_OPERATOR_ASSISTED_LAYOUT_PILOT**. Un conteo correcto no garantiza localización correcta. Las máscaras de la hoja reservada son aportadas por el operador: no es una prueba de segmentación autónoma.

## Reconocimiento condicionado a recortes

Se ajustó desde cero una red VGSL pequeña con Kraken 7.1: 34 filas de f3r/f3v, 40 épocas, batch 4, learning rate 0,001 y semilla 20261014. El ajuste terminó en 83,75 segundos y se usó exclusivamente el checkpoint final, índice 39. La única medición durante el ajuste utiliza los mismos datos de entrenamiento; no es validación independiente. Las 27 filas de f4r/f4v no se suministraron al ajuste ni a selección de checkpoint.

La referencia de test contiene 699 unidades convencionales de Boxer, incluidos espacios; 583 al excluirlos. No se han asignado sonidos o significados a esos códigos. GCR significa distancia de edición dividida por unidades de referencia, no error de traducción.

| Método | Errores / 699 | GCR |
|---|---:|---:|
| Kraken, época final | 668 | 95,5651% |
| Vecino más cercano por imagen | 652 | 93,2761% |
| Repetición de la unidad más frecuente | 685 | 97,9971% |
| Salida vacía | 699 | 100,0000% |

Kraken emitió 32 unidades para las 27 filas: todas son el código convencional `o` de Boxer. El reconocedor colapsó a una sola clase. **FAIL_CONDITIONAL_OCR_PILOT**: supera el máximo fijado de 50% y pierde contra el vecino por imagen. El GCR secundario sin espacios es 94,6827%; no reemplaza el criterio principal. Todas las unidades del test aparecen en entrenamiento; se conservan seis marcas de incertidumbre.

No se ensayaron aquí los reconocedores PP-OCRv6 preentrenados. Este fracaso no demuestra que Kraken sea inútil, ni permite aislar una causa: hay pocos ejemplos, entrenamiento desde cero y recortes imperfectos.

## Defectos y límites de referencia

Las 61 cajas fueron anotadas por el asistente, sin revisión humana independiente. El campo histórico `Human-reference` del JSON es una etiqueta inexacta del software: el anotador real fue el asistente. Las cajas pueden contener ascendentes y tinta de filas vecinas. La puntuación es condicional a estas referencias y no acredita precisión frente a una transcripción experta.

No se corrigió el test después de observar el resultado. Las hojas 3/4 pasan a ser material de desarrollo; una evaluación confirmatoria futura necesita otras hojas. El [protocolo 51](51_crop_quality_protocol.md) mide ahora repetición literal de posiciones entre recortes, sin reentrenar ni modificar los criterios anteriores.

## Evidencia y recuperación

El ZIP recuperado tiene SHA-256 `62adffc467e2008c402fd91a0d9a2576fd158351d4521c1e6ce3e3cf86270d58`. Se verificaron sus 152 archivos sin discrepancias. Una nueva [auditoría numérica](results/kraken_stage2/audit.json), con [implementación separada](code/audit_kraken_stage2.py), pasó 2.207 comprobaciones: hashes, geometría, emparejamiento, errores por fila, comparadores y criterios. No vuelve a ejecutar la red ni valida paleográficamente las anotaciones.

Se conservan el [resultado completo](results/kraken_stage2/stage2_result.json), [resumen](results/kraken_stage2/stage2_summary.json), [modelo final](results/kraken_stage2/ocr/final_epoch.mlmodel), [datos de las filas](results/kraken_stage2/ocr/dataset.json), [log](results/kraken_stage2/ocr/training.log), [configuración](results/kraken_stage2/ocr/training_config.json) y [procedencia](results/kraken_stage2/provenance.json). El modelo sirve como evidencia de un ensayo negativo; no es un OCR utilizable.

SHA-256 del resultado: `2885560464c395fab2a3a584d932e588dcedce70b56e280d82cb08caf3eeb396`. Modelo: `2c64034def4486a09134257f457a06d1664700c958482f3f0d671d9c5283e45d`.

Los tres [intentos fallidos](results/kraken_stage2/attempts/) también se preservan. El primero no entrenó por nombres de etiquetas; el segundo entrenó pero falló por un argumento de `Segmentation`; el tercero entrenó pero cargó la red sin su adaptador de reconocimiento. Ninguno produjo una puntuación de test para escoger entre modelos.

El [artefacto íntegro](https://github.com/MedinaParra/Voynich/actions/runs/38707533236/artifacts/11959915100), con imágenes, recortes, overlays y checkpoint, tiene retención hasta el 14-11-2026. El repositorio conserva el modelo final y las salidas esenciales; el manifiesto del artefacto se refiere al ZIP completo. Los originales se identifican por URL y hash.

Fuentes fijadas: imágenes de Yale, transcripción de [Alexander Boxer](https://github.com/alexanderboxer/voynich-attack/tree/255bd632e45459230eaf2a994e0557ed6c682869) (CC BY 4.0) y [Kraken 7.1](https://github.com/mittagessen/kraken/tree/eff0571e4c8b4930b476ef6af55851c62a938d15). No se atribuye valor lingüístico a los códigos PUA.

Traducción e identificación de idioma: **NOT_RUN**. Estos resultados no sostienen un paper de desciframiento.

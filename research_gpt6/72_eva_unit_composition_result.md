# 72 — Agrupar secuencias EVA no mejoró el criterio principal

27 de octubre de 2026. Rama `experiment/kraken-voynich`.

**Se completaron dos entrenamientos adicionales de 200 épocas y 5.600 pasos cada uno. La agrupación no mejoró las formas no vistas de la hoja 7:** 311 errores / 446 caracteres EVA, frente a 310 del modelo fuente. Ambos obtienen 0/76 palabras exactas. El control con salida por letras obtiene 325/446 y también cero exactas. La diferencia de un error entre fuente y grupos es demasiado pequeña para sostener una conclusión general de empeoramiento; en esta prueba no apareció la mejora buscada.

El modelo ampliado anterior, SHA-256 `35092d9baf56083eb6c70a2e32c478d8910ef5e685d0cee33fc5a935ca1c71d8`, se conserva como candidato principal. Los nuevos modelos permanecen disponibles para reproducir el ensayo; no se presentan como sustitutos superiores.

## Hipótesis y diagnóstico anterior

El [protocolo 71](71_eva_unit_composition_protocol.md), publicado en `0e51f51d5b66ac7deb20e198a42c2cce8033d116`, fijó las condiciones antes de entrenar. Agrupa de forma reversible `cfh`, `ckh`, `cph`, `cth`, `ch`, `sh`, siguiendo una convención de conectividad de EVA documentada por Gabriel Landini. Eso no prueba que sean unidades fonéticas o letras históricas indivisibles. Se ensayó una representación de salida de OCR, sin asignar significados.

El [diagnóstico de las salidas anteriores](results/kraken_eva_units/baseline_diagnostic.json) corrige una interpretación demasiado fuerte de la memorización: de las 76 referencias no vistas, 59 predicciones tampoco pertenecen al vocabulario de entrenamiento. El sistema no se limita a devolver palabras de un diccionario cerrado; produce muchas combinaciones nuevas incorrectas. Además, las referencias no vistas de esa hoja miden en promedio 5,8684 caracteres, frente a 4,4576 de las vistas. La longitud contribuye a la dificultad de acertar una palabra completa.

Un [análisis de edición descriptivo](results/kraken_eva_units/length_edit_diagnostic.json), sin nuevas inferencias, verificó las 282 distancias archivadas: 508 sustituciones, 253 omisiones y 97 inserciones. Usa una alineación textual con desempate declarado; sus pares no son una anotación paleográfica de confusiones entre glifos. Dentro de longitud cinco, el grupo visto tenía 31/75 errores EVA y el no visto 59/90; el contraste de longitud por sí solo tampoco explica toda la diferencia observada. Son subgrupos pequeños, no una prueba causal.

## Comparación controlada

Se mantuvieron las mismas 442 imágenes de entrenamiento, 147 palabras de desarrollo de la hoja 4 y 135 de evaluación de la hoja 7. No se añadieron ejemplos ni se modificó la exclusión de f5r. Son las mismas referencias candidatas del seguimiento exploratorio 69b, ya examinadas y sin nueva revisión experta.

Las dos condiciones cargaron el mismo backbone y reiniciaron toda la capa de salida. Se verificaron los doce tensores internos contra el original y los dos de salida, y después la conservación de todos los tensores y el codec al serializar. Se ajustaron todas las capas, con semilla 20261027, CPU/dos hilos, lote 16, tasa 0,001 constante, sin aumento y monitor exclusivamente de entrenamiento. Se usó siempre el checkpoint final de índice 199.

| Condición | Unidades de entrenamiento | Alfabeto de unidades | Salidas CTC con blanco | Épocas | Pasos reales | Exactas de entrenamiento |
|---|---:|---:|---:|---:|---:|---:|
| `reset_letters` | 2.087 | 19 | 20 | 200 | 5.600 | 442/442 |
| `reset_groups` | 1.765 | 25 | 26 | 200 | 5.600 | 442/442 |

En ambos, los errores de entrenamiento fueron cero. En la condición agrupada, los códigos privados sólo identifican unidades de máquina. Todas las salidas se expanden a EVA antes de calcular el error. Se conserva una [tabla de expansión](results/kraken_eva_units/group_mapping.json) y el helper `eva_unit_tools.expand`. El tamaño de salida y la longitud de las etiquetas cambian juntos; no se aísla un efecto paleográfico puro.

## Resultados del mismo proceso de evaluación

La [ejecución corregida 40571882695](https://github.com/MedinaParra/Voynich/actions/runs/40571882695), commit `554875da0770aa1b8df10df72120cbb4efc3adf0`, terminó correctamente en ambos entrenamientos y en la evaluación posterior. Esta última cargó fuente y modelos nuevos secuencialmente en un mismo proceso y efectuó dos pasadas. Se fijó la primera como principal. Las predicciones coincidieron entre pasadas y se registraron **1.692 llamadas a la red**.

| Modelo | No vistas de hoja 7: errores / 446 | CER principal | Exactas / 76 | Toda hoja 7: CER | Exactas / 135 | Hoja 4: CER |
|---|---:|---:|---:|---:|---:|---:|
| Fuente congelada | **310** | **69,5067 %** | 0 | **62,3413 %** | **9** | 55,9140 % |
| Salida nueva por letras | 325 | 72,8700 % | 0 | 64,0339 % | 8 | **55,2419 %** |
| Salida nueva por grupos | 311 | 69,7309 % | 0 | 64,0339 % | 7 | 57,2581 % |

El control por letras mejora ligeramente la hoja 4 y empeora la hoja 7. Elegirlo sólo por desarrollo histórico habría ocultado ese fallo de transferencia. La agrupación no ofrece un beneficio práctico en el criterio principal; ambas redes vuelven a memorizar las muestras de entrenamiento.

El modelo fuente tuvo tres predicciones distintas respecto de la evaluación común del ensayo 70, con los mismos hashes: dos en la hoja 4 y una en la 7. Aquí suma 416/744 y 442/709 errores, frente a los anteriores 415 y 443. Se conservan los cambios. Las comparaciones de esta tabla usan un mismo proceso y las mismas muestras; no se atribuye esa variación entre servidores a una mejora de pesos. No se aisló su causa.

Los tiempos observados de entrenamiento, conversión e inferencia de entrenamiento fueron 573,34 s para letras y 309,11 s para grupos, en servidores distintos. No constituyen una comparación controlada de velocidad.

## Incidencia de preparación y conservación

La [ejecución inicial 40571319398](https://github.com/MedinaParra/Voynich/actions/runs/40571319398), commit `789acf56f32df9ec22192252984a739b92178e63`, falló antes de entrenar. La preparación usó el helper heredado `add_codec`, que deja texto JSON en la metadata, mientras que el escritor safetensors esperaba un objeto estructurado. La corrección sólo adapta ese tipo y mantiene la comprobación de ida y vuelta. Los catorce estados tensoriales iniciales de cada condición resultaron idénticos entre el intento fallido y el corregido. Se conservan ficheros fallidos, errores, logs, inventarios y digests; no se contabiliza ese fallo como entrenamiento.

La [auditoría independiente](results/kraken_eva_units/audit.json) pasó **15.254 comprobaciones sin discrepancias**. Implementa la agrupación con otra expresión regular y la expansión por tabla, recalcula distancias con matriz completa y verifica etiquetas, hashes, registros tensoriales, capas reiniciadas, datos, selección final, 5.600 pasos, codecs, predicciones crudas/expandidas, grupos por vocabulario/longitud y repeticiones. No vuelve a inferir ni revisa paleográficamente los textos.

Se verificaron los SHA-256 de los cinco ZIP: dos fallidos, dos entrenados y evaluación común. La [procedencia](results/kraken_eva_units/provenance.json) vincula ejecuciones y artefactos.

| Modelo conservado | SHA-256 |
|---|---|
| [Letras, cabeza reiniciada](results/kraken_eva_units/runs/reset_letters/final_epoch.mlmodel) | `90228c1a3a7adfcd7bc9652b889a5b55b41331a3ce15c17cdb1b0373c97f43e3` |
| [Grupos, cabeza reiniciada](results/kraken_eva_units/runs/reset_groups/final_epoch.mlmodel) | `81b4f7b39052877972537672dda255fd76cf9f2b557f111243327123c1153faf` |

Se guardan también checkpoints finales, pesos iniciales, pruebas de reinicio, configuraciones, comandos, logs, etiquetas completas y todas las predicciones. Las imágenes originales se reconstruyen con sus hashes; las copias repetidas de entrenamiento no se duplican en los artefactos. Los JSON grandes se conservan comprimidos sin pérdida y el auditor admite ese formato.

```bash
python research_gpt6/code/audit_kraken_eva_units.py \
  --bundle research_gpt6/results/kraken_eva_units \
  --repo research_gpt6 --out work/eva_units_audit.json
```

El siguiente [ensayo 73](73_ctc_posterior_protocol.md) examina el decodificador sobre los mismos pesos, sin otro entrenamiento. Este resultado no permite concluir que las convenciones de conectividad de EVA sean incorrectas ni identifica una lengua. Traducción y revisión experta nueva: **NOT_RUN**.

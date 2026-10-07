# 39. Resultado exploratorio de adyacencia entre rosetas

Fecha: 2026-10-06. SINGLE_FOLDOUT_EXPLORATORY_NOT_TRANSLATION.

## Ejecución

Fuente: https://github.com/epilectrik/voynich/blob/main/data/rosettes_annotated.json . Blob congelado en `results/relational_external_sources.json`. Se usaron entidades y palabras literales de loci revisados; NO los campos interpretativos `middle`, `is_bridge`, glosas ni la hipótesis de taller del autor. Solo palabras `[a-z]+`; se excluyen ambigüedades, con posible sesgo de selección.

Grafo descrito por la fuente: ocho conexiones del perímetro y cuatro del centro a puntos cardinales. Nueve nodos, 12 parejas conectadas y 24 no conectadas, UNA lámina física. No se verificó aquí la topología contra la imagen Yale ni la ceguera de la anotación externa.

Estadístico: media de semejanza coseno de frecuencias de bigramas/trigramas de caracteres entre nodos conectados menos media entre no conectados. Permutación de textos completos entre nueve nodos; 9.999 permutaciones, semilla 408. Tres modalidades exploratorias, con corrección Bonferroni.

| Modalidad | Diferencia coseno | p unilateral | p ajustado |
|---|---:|---:|---:|
| Todo el texto aceptado | 0,00727 | 0,3032 | 0,9096 |
| Solo rótulos | 0,01813 | 0,3197 | 0,9591 |
| Solo anillos | 0,01623 | 0,1510 | 0,4530 |

Ejecución: PASS_EXECUTED. No hay evidencia favorable con esta prueba. No significación NO demuestra ausencia de relación ni refuta toda notación relacional.

## Límites y decisión

Las 36 parejas no son muestras independientes. Conectividad confundida con proximidad; no se demostró efecto adicional a geometría. Las permutaciones no igualan volumen, longitud ni rol textual. La agregación pierde orden y unas instrucciones relacionales podrían utilizar palabras distintas, no similares. Selección posterior a inspeccionar la fuente: exploratorio, no confirmatorio.

No ajustar nuevas representaciones sobre esta misma lámina buscando p pequeño. Conservar resultado negativo y obtener grafos visuales independientes de otros cuadernos. El piloto de transferencia del protocolo 38 sigue BLOCKED. Traducción: NOT_RUN.

## Auditoría de recursos

El recurso espacial Placa ofrece en `interpretation` glosas latinas; no son verdad semántica independiente y no se incorporaron. La colección vigibygg-cmyk ofrece mapas candidatos de f75r, f75v, f76r, f77r, f78r, f80v y f82r. Su `fRos_mapping.json` recuperado carece de sintaxis JSON válida (sin comillas y con abreviaciones); no convertirlo silenciosamente en datos ni usar interpretaciones mecánicas como aristas observadas. Localizar páginas distintas no acredita cuadernos independientes ni anotaciones ciegas completas.

## Reproducción

`python research_gpt6/code/rosette_adjacency_pilot.py rosettes_annotated.json`

Python 3.12, scikit-learn 1.8.0, ejecución local real. Archivo fuente no redistribuido; blob y hash registrados. Resultados completos: `results/rosette_adjacency_result.json`. Sin TimesFM ni glosas generadas por un LLM.

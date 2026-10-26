# 52. Calidad de recortes y fuentes espaciales: investigación ejecutada

Fecha: 26-10-2026. Rama: `experiment/kraken-voynich`.

**Se confirmó un defecto importante en los datos del piloto: las mismas posiciones oscuras del original aparecen en múltiples recortes etiquetados como filas diferentes.** Es un hallazgo sobre nuestra preparación de datos, no una solución del manuscrito. No se ha vuelto a entrenar un reconocedor ni se ha obtenido una traducción.

## Prueba fijada antes de la medición

El [protocolo 51](51_crop_quality_protocol.md) y su [implementación](code/kraken_crop_quality.py) se publicaron en `46430b4c3a8d6053927c9bf16bd65f8e53c77648` antes de calcular las nuevas métricas. Se conservaron las 61 cajas existentes y las máscaras, sin modificarlas después de observar el error del OCR. Son páginas ya exploradas: este diagnóstico no es una evaluación confirmatoria nueva.

Se marcan candidatos oscuros por diferencia con un fondo local de 31×31 píxeles; el umbral principal es 0,10 sobre gris normalizado. La métrica cuenta posiciones del original presentes en dos o más recortes, entre las posiciones oscuras incluidas al menos una vez. No se usa similitud visual entre páginas ni texto reconocido.

| Página | Filas | Posiciones oscuras distintas | Repetidas en varios recortes | Fracción repetida |
|---|---:|---:|---:|---:|
| f3r | 20 | 111.890 | 60.447 | 54,02% |
| f3v | 14 | 69.469 | 44.717 | 64,37% |
| f4r | 13 | 54.079 | 35.771 | 66,15% |
| f4v | 14 | 70.517 | 53.866 | 76,39% |
| Total | 61 | 305.955 | 194.801 | **63,67%** |

Las 61 filas tienen alguna posición repetida. Al sumar todos los recortes hay 509.738 exposiciones de esos píxeles; 203.783 son exposiciones adicionales de posiciones ya incluidas (39,98%). Esta segunda razón tiene otro denominador y no debe confundirse con el 63,67% principal.

La sensibilidad fijada produce 61,75% con delta 0,06 y 65,13% con delta 0,14. No se eligió un umbral después de observar cuál daba una cifra mayor. Pasaron seis controles sintéticos: blanco, filas separadas, caja que atraviesa otra fila, caja duplicada, ausencia de cajas y exclusión por máscara.

La [verificación separada](code/audit_kraken_crop_quality.py) leyó los PNG reales preservados del entrenamiento/test y contó las coordenadas de los píxeles originales que efectivamente permanecen visibles. Reprodujo el cálculo sin rasterizar de nuevo las cajas: **475 comprobaciones, cero discrepancias**. Se verificó también el hash de cada recorte.

Archivos: [resultado completo](results/kraken_crop_quality/crop_quality_result.json), [auditoría](results/kraken_crop_quality/audit.json), [procedencia](results/kraken_crop_quality/provenance.json), [vista de f3r](results/kraken_crop_quality/3r_repeated_positions.jpg) y [vista de f4r](results/kraken_crop_quality/4r_repeated_positions.jpg). Rojo: candidatos oscuros repetidos. Verde: las cajas provisionales.

## Lo que esta cifra permite concluir

La exportación genera mucha evidencia visual repetida bajo etiquetas de filas distintas. Se debe revisar antes de ampliar el entrenamiento. Parte de esa repetición puede corresponder a ascendentes legítimos, y el detector también puede marcar pintura o ruido. No determina qué fila es dueña de un trazo, no acredita etiquetas correctas y no prueba que sea la única causa del colapso del reconocedor.

Las hojas de entrenamiento y evaluación son distintas; no se detectó aquí fuga de píxeles entre ambas particiones. La repetición sucede dentro de cada página. El error de reconocimiento del [ensayo anterior](50_kraken_stage2_result.md), 95,5651%, continúa siendo FAIL. No se reinterpretó como una medida de precisión sobre una referencia experta.

La prueba se ejecutó en Python local con CPU; no se presenta como una nueva ejecución de Kraken en GitHub Actions. El modelo de reconocimiento evaluado sigue siendo el del run 38707533236 del 15 de octubre.

## Investigación de fuentes espaciales existentes

Se consultaron fuentes primarias y se distinguieron datos de transcripción, coordenadas e hipótesis interpretativas. Son recursos existentes localizados para esta continuación, no herramientas recién publicadas esta semana.

| Recurso | Utilidad comprobada | Límite para nuestro trabajo |
|---|---|---|
| [Voynichese, documentación de datos](https://github.com/voynichese/voynichese/blob/wiki/DataSets.md) y [archivo XML original](https://www.voynichese.com/1/data/folio/voynichese_data.zip) | Palabras EVA con coordenadas, dimensiones de encuadre y licencia Apache 2.0 documentada. | El encuadre es una imagen recortada propia. Debe registrarse con el escaneo Yale actual. |
| [Archivo de Rozanova y Temerev](https://github.com/lrozanova/voynich-units/tree/956a7c4fc39981f4d116fa3f4edfccce6d065571) | Distribuye coordenadas y código de medición de separadores; se inspeccionaron datos de f3r/f5r. | Es un archivo de reproducción, no una nueva referencia experta de nuestras 61 filas. Su código es MIT y los datos de terceros conservan sus términos. |
| [Placa, datos espaciales](https://github.com/alessandroplaca-uro/voynich-spatial-data/tree/7580dafa624cf23a63665f4819022003f8d128ef) | Ofrece 539 tokens posicionados del desplegable de rosetas y geometría regional; declara CC BY 4.0. | El alcance espacial detallado consultado es el desplegable, no nuestras páginas herbales. Sus glosas latinas son una hipótesis del autor, no etiquetas válidas de traducción. |
| [Kraken 7.1, entrenamiento](https://kraken.re/7.1/user_guide/training_recognition.html) | Admite ALTO/PAGE-XML y extracción por baseline; recomienda eScriptorium para anotar. | La infraestructura no sustituye la exactitud de las parejas imagen-transcripción. Cambiar a PP-OCRv6 no resuelve por sí solo la anotación. |

La investigación de unidades de [Rozanova y Temerev, arXiv:2608.17096](https://arxiv.org/abs/2608.17096) también justifica mantener separados signo visible, unidad de transcripción, palabra y significado. Es un preprint con hipótesis y controles propios; no se adopta su conclusión como un desciframiento ni se declara aquí una réplica de sus resultados.

## Auditoría del archivo XML de Voynichese

Se descargó el archivo original de 715.214 bytes, SHA-256 `402d99ca8191ae53a4f25912ee0af0a7e6b6d9a3714b2beaf86404a27d5b7ad5`, y se inspeccionaron sus 225 XML. Todos contienen la cabecera Apache 2.0. El [auditor propio](code/audit_voynichese_coordinates.py) no ejecuta código descargado.

La revisión contó **37.886 palabras** y **33 cajas con ancho no positivo en 28 folios**. No encontró índices duplicados ni diferencias entre el número declarado de palabras y el número de registros. Una caja de área positiva tampoco demuestra que contenga el signo correcto. El [resultado íntegro](results/kraken_crop_quality/voynichese_coordinate_audit.json) incluye las geometrías señaladas.

| Página | Palabras en nuestras filas Boxer | Palabras en el XML Voynichese |
|---|---:|---:|
| f3r | 115 | 115 |
| f3v | 82 | 83 |
| f4r | 62 | 64 |
| f4v | 81 | 83 |

La igualdad de conteos en f3r no prueba correspondencia uno a uno; allí existe además una caja de ancho cero. En las otras páginas, las diferencias impiden emparejar las dos secuencias por índice sin resolver previamente divisiones y fusiones de palabras. No se aplicaron las coordenadas a Yale mediante un simple cambio de escala ni se sustituyó nuestra referencia por estos datos.

Esta auditoría de fuente es exploratoria: surgió al observar una caja de ancho cero en una muestra. No está cubierta por la prerregistración de la prueba de repetición de píxeles y no se presenta como un contraste estadístico confirmatorio. Los 33 registros no invalidan automáticamente todo el recurso; identifican casos que requieren reparación y revisión antes de extraer imágenes.

## Decisión de investigación

La siguiente ruta concreta combina dos evidencias: geometría y lectura convencional. Primero se debe verificar el registro entre imágenes, reparar las geometrías imposibles y alinear las diferencias de transcripción con cambios de división/fusión explícitos. Después se deben producir polígonos de fila que preserven los signos y excluyan tinta de otras filas, y revisar muestras contra los originales. Sólo entonces tiene sentido comparar reconocimiento desde cero y transferencia con una validación separada.

Las hojas 3/4 sirven para desarrollar esa corrección; ya no son una reserva nueva. Una evaluación confirmatoria debe fijar otras hojas físicas antes de entrenar. No se ha ejecutado todavía ese registro, una alineación Boxer–EVA ni un nuevo entrenamiento: **NOT_RUN**.

El avance de esta continuación es una medición reproducible de un defecto de nuestros datos y la evaluación de una fuente espacial utilizable con revisiones. No es un método de desciframiento nuevo ni sustenta una traducción del manuscrito.

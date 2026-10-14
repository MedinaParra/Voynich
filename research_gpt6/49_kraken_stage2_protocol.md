# 49. Corrección de regiones y primer reconocedor Kraken: protocolo

Fecha: 14-10-2026. Estado inicial: NOT_RUN. Rama: experiment/kraken-voynich.

Se fija el protocolo antes de ejecutar el modelo sobre las hojas 3 y 4. Las imágenes se consultaron para crear anotaciones visuales; no se han observado las predicciones nuevas. El ZIP anterior fue recuperado, su SHA-256 coincide con GitHub y se verificaron 29 archivos sin discrepancias.

## Layout asistido

Se compararán los segmentos de página completa, el filtrado por regiones de párrafo y el filtrado más ensamblado de fragmentos. El predictor sólo recibe regiones generales: no recibe cajas de fila, cantidad de filas ni transcripciones. Los parámetros se eligen de una rejilla de seis combinaciones, usando exclusivamente conteos del piloto de las hojas 1 y 2. Las hojas 3 son diagnósticas y las hojas 4 son la prueba primaria. Se conserva la misma separación en las dos resoluciones.

El ensamblado usa posición de baseline, pendiente local y altura de los segmentos. La evaluación usa 27 cajas aproximadas de filas lógicas en f4r/f4v, IoU >=0,5 y emparejamiento uno-a-uno. El criterio primario exige F1 >=0,8, mejora frente a página completa y desviación de conteo <=15%, en todas las condiciones primarias.

Las máscaras de la hoja reservada se suministran manualmente. Una mejora probaría utilidad del flujo asistido, no capacidad autónoma de encontrar las regiones.

## Reconocimiento supervisado condicionado a recortes

Se prepararon 61 referencias de fila vinculadas a la transcripción de Boxer: 34 en f3r/f3v y 27 en f4r/f4v. Una red VGSL pequeña se entrenará sólo sobre las 34 filas de la hoja 3. Se aplicará sobre las 27 filas de la hoja 4, completa y reservada.

Los recortes se obtienen de las cajas y máscaras anotadas; la medición de reconocimiento está condicionada a esa segmentación manual. Los códigos PUA de la tabla de Boxer representan unidades convencionales de transcripción, sin asignar fonemas o significados. Se conserva el código de incertidumbre y se informa la cobertura del alfabeto.

La red fija 40 épocas, learning rate constante, batch 4 y una sola comprobación al terminar sobre los datos de entrenamiento. Esa comprobación no es validación independiente. La hoja 4 nunca se suministra a fit ni a selección de checkpoint; se usa el checkpoint de la época final. Los comparadores son salida vacía, repetición del signo más frecuente y vecino más cercano por imagen.

La prueba exige error micro de unidades <=0,50 y ventaja frente a los dos comparadores no vacíos. Ese umbral sólo define este piloto: no certifica un OCR utilizable del manuscrito.

## Calidad y límites de anotación

Las referencias y regiones fueron marcadas por el asistente, con una única revisión visual sobre imágenes sin predicciones nuevas. Son provisionales, no tienen verificación independiente de un experto y no son polígonos exactos de tinta. Las cajas pueden solaparse en ascendentes; las filas pueden contener fragmentos separados por dibujos. La incertidumbre de la anotación debe acompañar cualquier resultado.

Se guardan geometría, correspondencias, recortes, etiquetas, predicciones, errores, modelo y hashes. Se mantienen todos los fallos. No se traduce texto y no se identifica idioma.

[Plan completo](data/kraken_stage2_plan.json), [regiones](data/kraken_region_masks.json) y [referencias provisionales](data/kraken_line_reference.json).


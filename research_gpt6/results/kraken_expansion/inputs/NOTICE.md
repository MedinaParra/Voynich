# Fuentes de los seis folios fijados en el protocolo 69

Imágenes: Yale University Library, Beinecke Rare Book and Manuscript Library, MS 408. Se conservan copias de fotografías obtenidas de sus servicios IIIF, sin modificar los bytes de las descargas anteriores del 26 de octubre de 2026. Los recibos originales, enlaces, tamaños y SHA-256 están en `data/kraken_expansion_inputs.json`.

Las vistas previas y los datos JSON de palabras proceden de Voynichese. Las respuestas con extensión `.js` son datos JSON puros; se guardan como `.json`, se analizan con `json.loads` y no se ejecutan. No se copia el código de la aplicación.

Los XML son los seis archivos correspondientes del archivo de datos publicado en https://www.voynichese.com/1/data/folio/voynichese_data.zip, SHA-256 `402d99ca8191ae53a4f25912ee0af0a7e6b6d9a3714b2beaf86404a27d5b7ad5`. Conservan sus cabeceras Apache 2.0. Se verificó que la secuencia EVA completa de cada folio coincide exactamente entre ese archivo y el JSON actual; las cajas pertenecen a encuadres distintos. El texto completo de Apache 2.0 ya se conserva en `results/voynichese_registration/inputs/APACHE-2.0.txt` y se aplica a los datos XML en los términos de sus cabeceras, sin extender esa afirmación a otros activos por inferencia.

Los recortes y registros geométricos no son nuevas lecturas paleográficas verificadas. Fuentes, atribución y límites se mantienen con los resultados. El código nuevo es propio y utiliza dependencias declaradas.

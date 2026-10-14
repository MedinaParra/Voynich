# 47. Piloto Kraken sobre imágenes reales de Voynich

Fecha: 14-10-2026. Estado inicial: `NOT_RUN`.

Kraken es un proyecto Apache-2.0 disponible en [mittagessen/kraken](https://github.com/mittagessen/kraken). Reconoce/transcribe escritura y segmenta líneas; no traduce una lengua desconocida. La versión [7.1](https://github.com/mittagessen/kraken/releases/tag/7.1), publicada el 05-08-2026, añade una arquitectura de reconocimiento PP-OCRv6 y modelos base multilingües. Esta es una actualización del informe 46, que consultó la documentación 6.0. El piloto fija 7.1 y su modelo de segmentación; no evalúa ni atribuye capacidad Voynich a los nuevos reconocedores.

## Pregunta y diseño fijados antes de ejecutar

Comparar dos segmentadores de Kraken sobre las páginas f1r, f1v, f2r y f2v. Se usan imágenes de Yale y una segunda transcripción independiente, la de Alexander Boxer. Los recuentos fijados son 24, 9, 12 y 8 líneas de texto de bloque: 53 en total. Su notación propia no se trata como EVA ni como sonidos.

- Modelo neuronal de baselines incluido en Kraken: blob `f64b630c2b40f132f1acb1ffc90b617d5ada54a4`.
- Segmentador clásico de cajas con binarización nlbin, sin máscaras ni ajustes posteriores.
- Imagen a ancho 1800 como condición primaria y la misma imagen reducida a 1200 como robustez.
- Comparación descriptiva de desviación de conteo. No es precisión geométrica ni CER.
- Control positivo: una página de escritura histórica conocida con PAGE-XML del repositorio Kraken. Se calcula F1 de cajas de línea con emparejamiento uno-a-uno e IoU >= 0,5. No se afirma que fuera reservada en el entrenamiento del modelo original.
- Control negativo: imagen completamente blanca.
- Se guardan imágenes, geometría, versiones, hashes, tiempos, excepciones y todos los resultados; las condiciones fallidas no desaparecen del resumen.

El protocolo completo está en [kraken_pilot_plan.json](data/kraken_pilot_plan.json). Se registra en un commit previo al código ejecutable. El corpus y el mapeo de imágenes están fijados a commits independientes anteriores al corte.

## Criterios y alcance

El estado `PASS_COUNT_PROXY_ONLY` exige las cuatro páginas y ambas resoluciones, desviación relativa de conteo <= 0,15, cambio de conteo <= 1 en cada página y cero detecciones neuronales en blanco. Si falla se informa `FAIL_COUNT_PROXY`. Fallos de datos o del entorno se informan `BLOCKED_DATA_OR_RUNTIME`.

Contar 24 segmentos donde hay 24 líneas no demuestra que estén bien localizados. Por eso el piloto incluye geometría y visualización; no asigna transcripciones a recortes sólo porque coincida el conteo. No hay prueba de generalización a otros cuadernos, manos o desplegables. La tolerancia del piloto es una decisión de ingeniería, no un umbral científico universal.

El paso de reconocimiento supervisado permanece `BLOCKED_PENDING_REVIEWED_LINE_IMAGE_TRANSCRIPT_ALIGNMENTS`; entrenamiento y traducción están `NOT_RUN`. Para medir CER hacen falta pares de recorte de línea y transcripción revisados, y hojas reservadas completas.

## Ejecución autorizada

Rama: `experiment/kraken-voynich`, derivada de `797f9ea64ba88e9c63c7c2a5c402d0a6e0fafda1`. El entorno local de esta sesión no está disponible; el experimento se ejecutará en GitHub Actions sobre CPU. Se observarán los logs y la conclusión del job antes de informar resultados.

Fuentes: [Kraken 7.1](https://github.com/mittagessen/kraken/tree/eff0571e4c8b4930b476ef6af55851c62a938d15), [Boxer](https://github.com/alexanderboxer/voynich-attack/tree/255bd632e45459230eaf2a994e0557ed6c682869), [mapeo literal de imágenes](https://github.com/xenoglyph-ai/voynich-public/blob/d4b31a245ba8133b727dc4255278b5e8349bbe39/data/public/voynich_semantic_profiles/corpus_metadata.csv), [Yale](https://collections.library.yale.edu/catalog/2002046). Los perfiles semánticos del repositorio del mapeo no se usan.

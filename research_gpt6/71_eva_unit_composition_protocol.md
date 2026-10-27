# 71 — Unidades de salida EVA y reconocimiento de formas no vistas

27 de octubre de 2026. Base `f9cbd9f6632c484ca65d2953efd7c6b834e7f66b`. Rama `experiment/kraken-voynich`.

El ensayo 70 deja una mejora modesta y cero coincidencias exactas en 76 formas ausentes del entrenamiento de la hoja 7. Eso no demuestra que el modelo funcione como un diccionario cerrado: 59 de sus 76 predicciones en ese grupo tampoco pertenecen al vocabulario de entrenamiento. Las referencias no vistas son además más largas: media 5,8684 caracteres frente a 4,4576 en las vistas. Se conservará esta confusión de longitud al interpretar los resultados.

Se probará una hipótesis de representación: agrupar algunas secuencias conectadas de EVA puede facilitar la correspondencia temporal CTC entre imagen y texto. La documentación de EVA de Gabriel Landini enumera `ch`, `sh`, `cfh`, `ckh`, `cph`, `cth` entre los grupos cuya conexión se da por supuesta. Esa convención motiva la prueba; no demuestra que sean letras lingüísticas indivisibles, fonemas o unidades históricas reales. Cambiar unidades de OCR es una técnica conocida; no se afirma novedad bibliográfica ni desciframiento.

## Datos y dos condiciones fijados antes de entrenar

Se mantienen exactamente las 442 parejas de entrenamiento y los 282 recortes de evaluación del ensayo 70. No se incorpora f5r ni se modifica su rechazo geométrico. Hoja 4: desarrollo histórico, 147 palabras/744 caracteres EVA. Hoja 7: evaluación ya explorada, 135/709. La prueba es de desarrollo, no una nueva reserva confirmatoria.

1. `reset_letters`: etiquetas EVA por carácter, sin agrupación.
2. `reset_groups`: segmentación determinista de izquierda a derecha por coincidencia más larga de `cfh`, `ckh`, `cph`, `cth`, `ch`, `sh`; cada grupo se representa por un código privado de máquina, sin significado. El resto conserva su carácter EVA. Se requiere reversibilidad exacta en todas las muestras.

Las etiquetas de entrenamiento pasan de 2.087 caracteres a 1.765 unidades en la segunda condición; su alfabeto pasa de 19 a 25 unidades. **Todas las predicciones se expanden de vuelta a EVA antes de puntuar.** No se compara el error por unidad privada con el CER EVA anterior ni se asigna valor fonético a esos códigos.

Ambas condiciones parten del mismo backbone del modelo ampliado del ensayo 70, SHA-256 `35092d9baf56083eb6c70a2e32c478d8910ef5e685d0cee33fc5a935ca1c71d8`. Se reinicia íntegramente la capa de salida en ambas, evitando que sólo el tratamiento tenga que aprender una cabeza nueva. Se verifican antes de entrenar los doce tensores del backbone contra el original y los dos de salida, las dimensiones y el codec. La inicialización no reanuda el optimizador ni sus épocas. Se permite ajustar todas las capas.

Las dos condiciones usan las mismas 442 imágenes y orden, semilla 20261027, CPU/dos hilos, lote 16, tasa 0,001 constante, 200 épocas, 5.600 pasos esperados, sin aumento y monitor sólo de entrenamiento. Se selecciona siempre el checkpoint final de índice 199. El tamaño de salida y la longitud de las etiquetas cambian con la representación: cualquier diferencia no aísla un efecto paleográfico puro.

## Evaluación común

Después de ambos ajustes, un trabajo separado evaluará el modelo fuente congelado y los dos nuevos, secuencialmente en el mismo proceso. Dos pasadas completas; la primera se fija como principal. Se guardarán todas las predicciones de ambas, discrepancias y llamadas reales a la red. Ninguna puntuación decidirá pesos, épocas o checkpoint.

Medida principal: CER EVA micro de las **76 referencias no vistas de la hoja 7, 446 caracteres**, definidas por el vocabulario verdadero de las 442 parejas. Secundarias: CER y palabras exactas de toda la hoja 7; hoja 4 por separado; subgrupos vistos/no vistos y longitudes 1–4, 5–6 y 7 o más. Los grupos se muestran sin tratarlos como muestras independientes. El vecino por imagen ya calculado con las mismas 442 imágenes se conserva como comparador determinista, sin nuevo entrenamiento.

Una semilla, páginas exploradas y referencias candidatas sin nueva revisión experta limitan el ensayo. Se conservarán resultados negativos, protocolos, modelos, checkpoints, predicciones crudas y expandidas, hashes, logs, codecs y auditoría aritmética separada. No se usará el texto de evaluación para construir el codec, inicializar pesos ni entrenar. Identificación de lengua y traducción: **NOT_RUN**.

## Fuentes primarias consultadas

- Gabriel Landini, [EVA Alphabet](https://www.ic.unicamp.br/~stolfi/EXPORT/projects/voynich/work/programs/c/projects/voynich/alphabet-gabriel/eva.htm), definición y conectividad; y [referencia EVA-2](https://www.voynich.nu/hist/gabriel/eva2_reference.pdf). Se usa su convención, sin copiar el tipo de letra ni otros activos.
- Kraken 7.1, [modelo VGSL](https://github.com/mittagessen/kraken/blob/7.1/kraken/lib/vgsl/model.py), [codec](https://github.com/mittagessen/kraken/blob/7.1/kraken/lib/codec.py) y [serialización](https://github.com/mittagessen/kraken/blob/7.1/kraken/models/writers.py). Las llamadas a redimensionado, inicialización y escritura se verificaron en esta versión fijada.

La implementación nueva es propia y conserva atribución y licencias de las fuentes ya publicadas. Estos agrupamientos son un experimento de reconocimiento, no una traducción.

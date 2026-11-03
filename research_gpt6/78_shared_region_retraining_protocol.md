# 78 — Dos vistas y perturbación espacial controlada de regiones compartidas

3 de noviembre de 2026. Rama `experiment/kraken-voynich`. Base `e7bdfb1f5678633ea9e34f134e083484084d24c3`.

El ensayo 76 mostró que buscar el máximo CTC no recuperaría las 76 referencias no vistas de la hoja 7 con los posteriors actuales. También cuantificó solapamientos, sin demostrar propiedad de tinta o etiquetas erróneas. Se ensaya ahora una intervención de aprendizaje sobre esa incertidumbre de región. No se certifican ni corrigen transcripciones.

## Hipótesis y novedad limitada

Hipótesis: aprender de una vista intacta y otra que atenúa suavemente píxeles oscuros compartidos por varias máscaras puede reducir la dependencia del contexto vecino. Alternativa: la alteración funciona sólo como regularización genérica, o elimina trazos legítimos y empeora la lectura. Se contrasta con un control aleatorio de igual número de píxeles y otro de imágenes repetidas.

La combinación y su diseño son nuevos en este repositorio. Augmentación, CTC y evaluación por hoja son técnicas existentes; no se afirma prioridad mundial ni un nuevo algoritmo de desciframiento. La literatura de generalización HTR y las limitaciones del canal visual motivan una hipótesis, no garantizan su éxito. Véase la revisión 77 de esta continuación.

## Tres condiciones fijadas

Se mantienen las 442 palabras de entrenamiento y 2.087 caracteres EVA. Por cada palabra se exportan dos vistas y sus etiquetas idénticas: **884 muestras derivadas, no 884 palabras independientes**.

1. `repeat`: dos copias exactas de la imagen original.
2. `random_ink`: original más una vista que atenúa píxeles oscuros elegidos uniformemente sin reposición. El número es exactamente el de píxeles oscuros compartidos de esa misma palabra.
3. `shared_ink`: original más una vista que atenúa esos píxeles oscuros compartidos.

Oscuro significa gris ≤ mediana dentro de la máscara menos 40. Compartido significa pertenecer a la máscara del objetivo y a al menos otra del mismo folio, con la dilatación original de cuatro píxeles. En la segunda vista cada canal seleccionado se sustituye por la semisuma redondeada hacia arriba de su valor y la mediana RGB local redondeada; la geometría no cambia y los demás píxeles permanecen idénticos. No se llama a esto eliminación certificada de tinta ajena. El control aleatorio puede incluir píxeles compartidos; se cuenta y preserva.

Los identificadores de muestra y la semilla 20261103 determinan el control aleatorio. No se consultan salidas de OCR ni etiquetas de evaluación para generar perturbaciones. Se guardan máscaras seleccionadas, hashes, conteos, RGB de referencia y todas las parejas. La vista original se conserva en cada condición.

Las tres condiciones utilizan además el mismo `DefaultAugmenter` de Kraken 7.1: puerta 0,5 y hasta tres operaciones por muestra, con receta de la versión fijada y registro de su código instalado. Esto añade variación durante el entrenamiento en las tres condiciones. El efecto de activarlo frente a experimentos antiguos queda mezclado con continuar el ajuste; el contraste espacial válido es entre las tres condiciones nuevas.

## Ajuste comparable

Todos cargan el modelo `expanded_200`, SHA-256 `35092d9baf56083eb6c70a2e32c478d8910ef5e685d0cee33fc5a935ca1c71d8`. Se verifica que la conversión a safetensors conserva los catorce tensores y el codec. No se reinicia la salida ni se añade un alfabeto procedente de evaluación. Se reinician optimizador y contador de épocas.

Semilla 20261103, CPU/dos hilos, lote 16, tasa constante 0,001, todas las capas entrenables, 100 épocas de 884 vistas: **5.600 pasos de optimizador por condición**. Es el mismo número de pasos que 200 épocas de 442 imágenes. Se usa siempre el checkpoint final de índice 99. El monitor recibe sólo las vistas de entrenamiento; no determina el checkpoint a publicar.

## Reserva nueva para este ensayo OCR

Se fijan ahora **f8r y f8v**, sin consultar su OCR, y sin incorporarlas a entrenamiento o al monitor. Ya existían fotografías y referencias a esas páginas en otros trabajos del repositorio; son una reserva nueva para este ensayo OCR, no una afirmación de ceguera absoluta de toda la investigación.

Las fotografías Yale se fijan con los SHA-256 de recibos anteriores. Se adquieren JSON, vista previa y XML de Voynichese, verificando la igualdad de secuencia y el archivo licenciado de origen. Las referencias siguen siendo candidatas de esa tradición, sin una revisión experta independiente.

El registro usa los mismos parámetros del ensayo 69: SIFT recíproco, cinco particiones espaciales con zona de exclusión, homografía y corrección local, umbrales de mediana/P90/cobertura y control de orientación 17×25. Se exigen al menos veinte palabras utilizables por página. Si falla una de las dos páginas, se conservan todos los intentos y no se sustituye ni relaja la regla. Los entrenamientos pueden terminar independientemente; la medida primaria nueva queda **BLOCKED**, no se reemplaza silenciosamente por la hoja 7.

## Evaluación fijada y límites

Fuente congelada y tres modelos nuevos se evalúan en un mismo proceso y sobre recortes originales sin modificar. Se capturan los posteriors recibidos por el decodificador de Kraken, se exige paridad con el máximo por instante y se aplica el mismo haz 32 sin diccionario ni modelo de lenguaje. Se hacen dos pasadas; la primera está fijada como principal y se informa cualquier diferencia. Se cuentan llamadas reales a la red y se conservan matrices y textos.

Medida primaria: CER EVA en la hoja física 8, comparando `shared_ink` con **ambos controles nuevos** y la fuente. Se informan también palabras completas exactas, palabras presentes/ausentes del vocabulario de entrenamiento, folio y longitud. Las hojas 4 y 7 son medidas secundarias ya exploradas. Un solo folio físico nuevo y una semilla no permiten declarar superioridad general, significación por tratar palabras como hojas independientes ni desciframiento.

Se publican plan y protocolo antes de ejecutar. Se preservan controles, código, entradas, máscaras, modelos, checkpoints finales, configuraciones, logs, errores y auditoría independiente de datos y puntuaciones. Se distinguen archivo ZIP verificado y digest sólo reportado por GitHub. Identificación de lengua, revisión experta nueva y traducción: **NOT_RUN**.

### Incidencia de entorno conservada

En el run inicial `41643719527`, el trabajo de reserva falló antes de adquirir imágenes o textos porque faltaba SciPy, importado de forma transitiva por el helper de recortes. Se añade SciPy 1.15.3 al entorno geométrico. No cambian páginas, datos, umbrales, método, semilla ni configuración de entrenamiento. Los tres trabajos originales de ajuste continúan; un workflow de recuperación completa sólo la adquisición y la evaluación usando sus artefactos, sin repetirlos. El estado global de la primera ejecución puede ser `failure` aunque sus tres entrenamientos terminen correctamente; se conservan ambos estados por separado.

# 69 — Reajuste de Kraken con expansión de ejemplos y control de continuación

27 de octubre de 2026. Base `f31c312e562ee8c9e63ba3b3e6853fdfb4d6aaec`, rama `experiment/kraken-voynich`.

El ensayo 68 obtuvo CER EVA 62,5 % y ninguna palabra multicaracteres exacta en desarrollo, pese a 191/197 coincidencias en entrenamiento. Se probará añadir ejemplos de otras hojas, sin elegirlos según nuevas predicciones de OCR. Este protocolo se publica antes de adquirir y registrar sus referencias.

## Selección de datos y control geométrico

Se fijan f5r/f5v/f6r/f6v como candidatos adicionales de entrenamiento, y f7r/f7v como reserva de evaluación para este reajuste. f3r/f3v mantienen las 197 parejas originales; f4r/f4v mantienen las 147 parejas de desarrollo, píxeles y textos del ensayo 68. No se añaden parejas de las hojas 4 o 7 al entrenamiento ni al monitor. Son referencias EVA de una tradición de transcripción ya utilizada en la investigación, no una nueva verdad paleográfica independiente. La reserva de la hoja 7 sólo corresponde a este experimento de OCR, no a toda la historia del proyecto.

Fuentes: datos y vistas previas de Voynichese; fotografías de Yale ya conservadas en el trabajo de reordenación, con comprobación de recibos y SHA-256. Se conservan los datos originales, atribución y licencia del archivo fuente. Se comprobará que la secuencia EVA publicada coincide con la del archivo XML fijado; no se ejecuta JavaScript de la página. Se utilizan las cajas de la vista previa actual directamente, sin hacer pasar las coordenadas XML antiguas por el mismo encuadre.

Registro por SIFT recíproco, razón 0,72, máximo 6.000 puntos, contraste 0,02. Se reutiliza la corrección residual espacial del ensayo 64 con los mismos parámetros: bloques 8×8, cinco particiones por `(columna+2*fila)%5`, exclusión de ajuste a ≤3 píxeles de puntos reservados, homografía RANSAC con umbral 3 píxeles Yale, hasta 10.000 iteraciones, confianza 0,999; anclas con residual ≤20 píxeles, agrupación 0,1 píxeles, hasta 20 vecinos en 80 píxeles, mínimo tres grupos, mediana por componente y corrección limitada a 20 píxeles. Se retienen todos los puntos reservados al puntuar.

Cada página debe pasar las cinco particiones: al menos 50 inliers de ajuste, extensión ≥0,5 en cada eje, al menos diez puntos reservados, mediana ≤2 píxeles, P90 ≤5 y fracción dentro de 5 ≥0,8. El ajuste final debe conservar orientación positiva en una malla 17×25. Se exportan únicamente cajas de tamaño positivo, polígonos convexos dentro de la imagen y textos ASCII minúsculos sin marcadores de incertidumbre. Cada folio debe conservar al menos 20 palabras. Se preservan todos los rechazos y métricas. Si falla alguna página, se detiene esta expansión; no se reemplaza por otra que puntúe mejor. La geometría aceptada no certifica la lectura.

## Entrenamientos y evaluación

Ambas condiciones cargan el modelo EVA final `aligned_200` del ensayo 68, SHA-256 `c2b93256804d4697b56990e6bae0ae132942308ab9038b220a06352f8b013e8b`. Se conservan pesos de inicialización y se permite añadir caracteres de las etiquetas de entrenamiento al codec con `--resize add`; ningún carácter de evaluación define el codec. Se reinician optimizador y épocas, conservando pesos, y se ajustan todas las capas.

1. `continuation_200`: sólo las 197 parejas originales de f3r/f3v.
2. `expanded_200`: esas mismas 197 parejas más todos los candidatos admitidos de f5r/f5v/f6r/f6v.

Semilla 20261027, CPU/dos hilos, lote 16, 200 épocas, tasa 0,001 constante, sin aumento, monitor sólo de entrenamiento. Checkpoint final de índice 199, sin selección por desarrollo o reserva. Igualar épocas no iguala número de pasos ni tiempo de cómputo, pues la expansión contiene más ejemplos; se informarán ambos. No se atribuirá una diferencia exclusivamente a diversidad de datos.

Se evaluará también el modelo de inicialización congelado, sin entrenarlo, sobre exactamente las mismas muestras. Medidas: CER EVA micro y número/proporción de palabras completas exactas, con desglose de las palabras de dos o más caracteres, por folio y por vocabulario visto/no visto. Desarrollo histórico y reserva de hoja 7 se informan por separado; no se mezclan sus denominadores. Comparadores por imagen, palabra más frecuente, carácter repetido y vacío usan exclusivamente las referencias de entrenamiento de cada condición y se identifican como tales.

El efecto principal de interés es el error de `expanded_200` frente al modelo inicial congelado en la hoja 7; el contraste con `continuation_200` ayuda a interpretar el reajuste. No hay criterio binario científico inventado después de ver las cifras. Una semilla y una hoja reservada no permiten una afirmación general de superioridad ni de desciframiento. El CER del ensayo 68 sí es comparable sobre sus 147 parejas exactamente conservadas; los errores Boxer anteriores siguen teniendo otro denominador.

Se guardarán fuentes, hashes, particiones, recortes reconstruibles, rechazos, predicciones completas, modelos, checkpoints, configuración, logs, versiones, fallos y auditoría numérica separada. Las predicciones de la hoja 7 no se usarán para elegir parámetros o prolongar este ajuste. Traducción, identificación de lengua y nueva revisión experta: **NOT_RUN**.

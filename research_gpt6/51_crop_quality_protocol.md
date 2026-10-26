# 51. Auditoría de repetición de píxeles entre recortes: protocolo

Fecha: 26-10-2026. Estado: NOT_RUN. Rama: `experiment/kraken-voynich`.

El fallo de reconocimiento del 15 de octubre y la inspección de recortes motivan una prueba diagnóstica. Se usará exclusivamente el conjunto ya explorado de las hojas 3 y 4: no es una evaluación confirmatoria nueva ni una prueba de desciframiento.

Pregunta: ¿qué fracción de las posiciones oscuras de la imagen original se presenta en más de un recorte con etiquetas de filas distintas? El cálculo usa coordenadas originales, no semejanza entre imágenes ni texto reconocido. La superposición dentro de una página no implica fuga entre las hojas separadas de entrenamiento y test.

Se fijan las 61 cajas existentes y las mismas máscaras de párrafo, sin corregirlas. Los originales de Yale se recuperan del artefacto 11959915100, verificando su manifiesto. Se convierte cada imagen a gris de 8 bits con Pillow y se divide por 255. Un filtro de media de 31×31, borde reflectante, estima fondo local. Se marcan candidatos oscuros si `fondo - gris >= delta`, dentro de las máscaras. Delta principal: 0,10. Sensibilidad predefinida: 0,06 y 0,14.

Métrica principal: número de posiciones oscuras cubiertas por dos o más cajas dividido por el número de posiciones oscuras cubiertas por al menos una. Se informan las cuatro páginas por separado, el conjunto y la exposición redundante al sumar los recortes. Se usa la geometría exacta del exportador: suelo para izquierda/arriba, techo para derecha/abajo.

Controles previos: imagen blanca (cero candidatos); filas sintéticas oscuras con cajas separadas (cero duplicación); mismas filas con una caja adicional que cruza texto (duplicación positiva); cajas repetidas (fracción 1); ausencia de cajas (cero denominador tratado explícitamente). Un control fallido bloquea la interpretación de la medición.

No hay umbral para declarar anotaciones correctas. Una duplicación detectada exige revisión; ausencia de duplicación no prueba buena correspondencia ni integridad de los signos. Los candidatos oscuros pueden incluir pintura o ruido; los ascendentes legítimos pueden ocupar zonas de cajas vecinas. Esta prueba mide repetición literal de posiciones visibles, no identifica al propietario paleográfico de cada trazo ni demuestra la causa del fallo de CTC.

Se conservarán código, parámetros, métricas, controles y vistas. El resultado no se utilizará para ajustar retrospectivamente el reconocedor o sus criterios.

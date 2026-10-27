# 69b — Seguimiento exploratorio tras el fallo geométrico de f5r

27 de octubre de 2026. El protocolo 69 se publicó antes de adquirir las referencias, commit `9f2163cf953f1a6b34ae4fad6b72f8c7e55f9263`. Su ejecución geométrica `40544897322`, commit `8c6141623db3e0aaa9c3918ddca962f42d3126a2`, **falló el criterio original de seis páginas aceptadas**: f5r pasó cuatro de cinco particiones. No se entrenó ese experimento ni se redefine su resultado como aprobado.

Se fija este seguimiento separado antes de ejecutar nuevas predicciones de OCR: se excluye f5r por el control geométrico ya observado y se utilizan las cinco páginas que cumplieron todos los criterios originales. No se sustituyen páginas, no se relajan umbrales ni se vuelven a ajustar las transformaciones para hacerlas pasar. Se reutilizan los casos y campos conservados: f5v/f6r/f6v aportan 245 referencias de entrenamiento y f7r/f7v aportan 135 referencias de evaluación. Se conservan las 197 parejas originales de entrenamiento y las 147 de desarrollo: 442 palabras de entrenamiento en la condición ampliada y 197 en la continuación.

El seguimiento es **exploratorio y adaptado después de observar resultados geométricos**, aunque antes de observar predicciones de OCR sobre la nueva reserva. No se presentará como la prueba original preespecificada ni como validación confirmatoria. No se seleccionaron páginas por sus errores de reconocimiento, pero sí por la calidad geométrica observada; esa selección limita la generalización.

Se mantienen el mismo modelo inicial, las dos condiciones `continuation_200` y `expanded_200`, semilla, tasa, lote, 200 épocas adicionales, monitor de entrenamiento, checkpoint final y medidas del protocolo 69. Se informan por separado la evaluación histórica y la hoja 7, el modelo inicial congelado, los pasos de optimizador y tiempos. Las diferencias entre entrenamientos con distinto tamaño de datos incluyen distinto cómputo.

Se publican este cambio y sus hashes antes de entrenar. Se conserva íntegro el fallo original, incluidos los treinta casos de validación geométrica. El seguimiento no añade revisión experta y no traduce ni identifica una lengua.

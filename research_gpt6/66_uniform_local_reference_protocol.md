# 66 - Construcción de una referencia candidata v2 uniforme

Fecha: 27 de octubre de 2026. Seguimiento del ensayo 64, run 40531601364. Este protocolo se fija **después** de conocer la comparación geométrica y **antes** de construir la nueva versión de los polígonos. Es preparación derivada de datos; no una nueva evaluación ciega.

La corrección local pasó las cinco particiones en las cuatro páginas, mientras que la homografía global pasó 5/5, 2/5, 0/5 y 4/5 respectivamente. La referencia antigua combina criterios de una sola reserva y deja f4r sin polígonos. Para un futuro ensayo de OCR se necesita una versión explícita con el mismo método geométrico en las cuatro páginas, sin sustituir los archivos históricos.

## Construcción fijada

- Fijar por hash el código de compensación del ensayo 64, su plan, las correspondencias, la calibración anterior, sus 20 casos, resultado y auditoría. Exigir cinco casos locales aceptados por página y auditoría sin discrepancias.
- Usar el mismo ajuste final posterior a la comparación: homografía RANSAC sobre todas las correspondencias de cada página, semilla 20261027+10000, y el campo local de medianas con los parámetros ya fijados. Reutilizar el modelo final de f4r ya preservado y comprobar sus anclas; no volver a contar ese ajuste como otro experimento.
- Ajustar de esa forma los mapas finales de f3r, f3v y f4v. No volver a puntuar esos ajustes completos como si fueran reservas. El rendimiento de referencia sigue siendo la comparación espacial anterior, condicionada a los puntos del detector.
- Comprobar orientación en una cuadrícula 17×25 y que cada polígono exportado sea convexo, mantenga orientación positiva y esté dentro de Yale. Una cuadrícula finita no prueba ausencia de pliegues a todas las escalas.
- Conservar los 345 registros de fuente. La única exclusión de tamaño prevista es f3r, índice 2, ancho cero. Exigir exactamente 344 polígonos candidatos y ninguna exclusión geométrica inesperada. No completar ni inferir ese ancho.
- Preservar textos EVA, índices, cajas originales, método, modelos, anclas y fuentes. Registrar cualquier marcador de incertidumbre de lectura; una geometría válida no certifica su texto. Mantener los 280 candidatos antiguos y los 64 del primer resultado en sus ubicaciones originales.
- Revisar vistas generales y detalles, sin atribuir a una revisión del asistente el carácter de revisión experta independiente.

La construcción se ejecutará en otro workflow de GitHub Actions que consume la evidencia congelada del ensayo 64. No repite sus veinte casos ni añade muestras al resultado de validación. Si alguna condición de construcción falla, se preserva el intento y no se declara lista la versión candidata.

Resultado esperado: un catálogo geométrico **provisional** de cuatro páginas para revisar antes de preparar un ensayo de reconocimiento. No se entrena Kraken, no se equiparan automáticamente las unidades EVA y Boxer y no se asignan significados o fonemas. OCR y traducción nuevos: **NOT_RUN**.

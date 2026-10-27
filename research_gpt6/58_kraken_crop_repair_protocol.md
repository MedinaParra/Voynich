# 58 - Reparar los recortes y comparar Kraken en material de desarrollo

27 de octubre de 2026. Rama `experiment/kraken-voynich`.

Se retoma el defecto del informe 52: posiciones oscuras de una imagen aparecen en recortes etiquetados como filas diferentes. La siguiente implementación asigna posiciones a un solo recorte, conservando los candidatos de tinta dentro del dominio previamente usado. **Eliminar duplicados por construcción no demuestra que los signos hayan sido asignados a la fila correcta.**

## Alcance y datos

Se conservan las cuatro páginas, las 61 asociaciones provisionales de imagen-texto y la notación de Boxer del piloto anterior. Las hojas 3 y 4 ya fueron exploradas. Esta comparación es de ingeniería y desarrollo, sin una nueva reserva confirmatoria ni revisión paleográfica experta.

La guía inicial son las cajas de fila antiguas y las máscaras de párrafo: no se presenta como segmentación autónoma. Se verifican sus huellas, las de las imágenes de Yale y el mapa Unicode de Boxer. Las 61 etiquetas deben permanecer idénticas. Los casos ambiguos se marcan para revisión, sin cambiarlos después para mejorar una puntuación.

## Extracción provisional

1. Definir el dominio como la unión de las cajas anteriores dentro de las máscaras de párrafo. No se acredita recuperación de tinta fuera de ese dominio.
2. Detectar candidatos por contraste local de 31 píxeles, umbral 0,06. No se supone que todo candidato sea tinta de escritura.
3. Escoger conjuntamente anclas verticales ordenadas por densidad de candidatos, dentro de las guías antiguas, con penalización de desplazamiento y separación mínima fijadas en el plan.
4. Asignar cada componente conectado al propietario mayoritario de sus píxeles según las anclas y las cajas elegibles. Señalar componentes de soporte dividido. Mantener exclusividad al añadir un halo de dos píxeles.
5. Extraer recortes con tres píxeles de margen sobre los candidatos asignados, preservando los valores originales donde la máscara lo permite. Guardar máscaras de propiedad, coordenadas y vistas anterior/corregida.

Se exige cero duplicación y conservación de todos los candidatos que usó la métrica anterior, con umbrales 0,06, 0,10 y 0,14. Los controles verifican conservación, fidelidad de píxeles y fallos por guías indistinguibles o filas vacías. Estas comprobaciones son de integridad, no de exactitud de glifos.

## Comparación de reconocimiento

Se fijan tres variantes antes de entrenarlas:

| Variante | Recortes | Épocas | Propósito |
| --- | --- | --- | --- |
| original_40 | Algoritmo anterior | 40 | Comparador contemporáneo |
| repaired_40 | Propiedad provisional | 40 | Aislar el cambio de extracción |
| repaired_200 | Propiedad provisional | 200 | Diagnóstico separado con más entrenamiento |

Las tres usan la misma arquitectura VGSL pequeña, semilla 20261014, 34 filas de f3r/f3v para ajustar y 27 de f4r/f4v para medir en desarrollo. Se conserva el último checkpoint fijado; el monitor recibe solo entrenamiento. No se escoge época ni variante a partir de la puntuación sobre la hoja 4. Todas las salidas, métricas y fallos se preservan.

Se mide distancia de edición por unidades convencionales de Boxer, incluidos espacios, y se comparan vecino por imagen, repetición de la unidad más frecuente y salida vacía. También se informa ajuste sobre entrenamiento para distinguir colapso del modelo y transferencia entre hojas. Ningún resultado se interpreta como traducción o acierto lingüístico.

El plan ejecutable está en [kraken_crop_repair_plan.json](data/kraken_crop_repair_plan.json). El código y la configuración se guardan antes de los nuevos entrenamientos. El desarrollo local de la extracción puede descubrir fallos; cualquier corrección debe quedar registrada, sin ocultar ejecuciones fallidas.

## Pendientes que esta prueba no sustituye

- Una revisión experta e independiente de geometría y transcripciones.
- El registro geométrico de Voynichese con Yale y las diferencias de división/fusión de palabras entre transcripciones.
- Una evaluación confirmatoria en otras hojas físicas, fijada antes de usarlas.
- La identificación de lengua o una traducción.

Fuentes: [Kraken 7.1, preparación y entrenamiento](https://kraken.re/7.1/user_guide/training_recognition.html), imágenes de Yale, transcripción de Alexander Boxer con atribución CC BY 4.0 y los archivos congelados del ensayo anterior. El código de propiedad de píxeles es una implementación propia del proyecto.

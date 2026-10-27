# 59 - Kraken retomado: reparación provisional y tres entrenamientos ejecutados

Ejecución: **27 de octubre de 2026**, [GitHub Actions 40504398717](https://github.com/MedinaParra/Voynich/actions/runs/40504398717), commit `21df988532b71227e9fc7646df6aa5805fe932ce`, rama `experiment/kraken-voynich`.

**Resultado: mejora medible en desarrollo; todavía no hay un OCR fiable ni una traducción.** Se implementó una propuesta de extracción y se ejecutaron tres entrenamientos fijados en el [plan 58](58_kraken_crop_repair_protocol.md). Las páginas y las etiquetas son las mismas del piloto anterior, ya exploradas y sin revisión experta independiente. No se presenta una evaluación confirmatoria nueva.

## Reconocimiento: qué cambió

Se ajustaron 34 filas de f3r/f3v y se midieron 27 filas de f4r/f4v, con 699 unidades convencionales de Boxer, incluidos espacios. La arquitectura, semilla, codec y parámetros comunes permanecieron fijos; se usa el último checkpoint de cada presupuesto, no el mejor resultado sobre la hoja 4.

| Variante ejecutada | Épocas | Errores / 699 en desarrollo | Error en desarrollo | Error sobre entrenamiento | Vecino por imagen en desarrollo |
| --- | --- | --- | --- | --- | --- |
| Recortes anteriores | 40 | 668 | **95,5651 %** | 95,7143 % | 93,2761 % |
| Recortes de propiedad provisional | 40 | 574 | **82,1173 %** | 83,4694 % | 86,1230 % |
| Recortes de propiedad provisional | 200 | 516 | **73,8197 %** | 24,8980 % | 86,1230 % |

El comparador contemporáneo reproduce los 668 errores del ensayo del 15 de octubre. Entre las dos variantes de 40 épocas, el cambio de extracción reduce el error observado en **13,4478 puntos porcentuales**. La variante de 200 épocas alcanza una reducción de **21,7454 puntos** respecto del comparador original. Son diferencias en estas páginas de desarrollo, con una ejecución por variante; no estiman incertidumbre ni generalización a todo el manuscrito.

El cambio de extracción incluye límites de recorte y máscaras de propiedad. Esta comparación no separa cuánto contribuye cada componente de la extracción. La variante de 200 épocas también cambia el presupuesto de entrenamiento y se informa como diagnóstico distinto.

Con recortes originales el modelo vuelve a emitir exclusivamente la unidad convencional `o`. Con los nuevos recortes a 40 épocas produce cuatro unidades no espaciales y espacios; a 200 épocas produce 16 unidades no espaciales y espacios. Son nombres de códigos de transcripción: no se interpretan como letras, sonidos o números del manuscrito.

La repetición de la unidad más frecuente conserva 685/699 errores, y la salida vacía 699/699. Las dos variantes corregidas superan al vecino por imagen de su propia extracción. El resultado de 200 épocas sigue por encima del objetivo anterior de 50 % de error incluso sobre este material de desarrollo.

**La brecha de ajuste importa:** 24,9 % de error en los datos usados para entrenar y 73,8 % en la otra hoja. El reconocimiento no se transfiere bien entre estas páginas. Pocos datos, diferencias entre manos y referencias provisionales siguen siendo limitaciones; esta prueba no identifica una causa única.

Todos los valores de error son distancias de edición por unidades de Boxer y espacios. No son porcentajes de traducción correcta, de palabras comprendidas ni de exactitud lingüística. Los valores de ajuste sobre entrenamiento son métricas del propio entrenamiento; sus salidas individuales no se exportaron y no se usan como validación independiente.

Archivos: [resumen de las tres variantes](results/kraken_crop_repair/result.json), resultados individuales de [original_40](results/kraken_crop_repair/runs/original_40/result.json), [repaired_40](results/kraken_crop_repair/runs/repaired_40/result.json) y [repaired_200](results/kraken_crop_repair/runs/repaired_200/result.json). Cada resultado conserva las 27 referencias, predicciones, errores y comparadores.

## Extracción: se eliminó la duplicación medida, no la incertidumbre de lectura

La extracción recibe las guías antiguas de fila y las máscaras de párrafo. Escoge anclas verticales de densidad de candidatos, asigna componentes conectados a un solo propietario y conserva máscaras y coordenadas de exportación. Es un procedimiento asistido por anotaciones previas, no segmentación autónoma.

| Umbral de contraste local | Posiciones distintas analizadas | Posiciones repetidas antes | Posiciones repetidas después | Posiciones candidatas perdidas |
| --- | --- | --- | --- | --- |
| 0,06 | 492.082 | 303.853 | 0 | 0 |
| **0,10** | **305.955** | **194.801** | **0** | **0** |
| 0,14 | 174.899 | 113.916 | 0 | 0 |

Al umbral principal, la fracción de posiciones oscuras repetidas pasa de 63,6698 % a cero. **La exclusividad se impone por construcción y no es una puntuación de reconocimiento.** La conservación solo cubre los candidatos definidos dentro de la unión de recortes antiguos; no acredita recuperación de tinta fuera de ese dominio ni conservación de todos los trazos débiles.

Los componentes de soporte dividido quedan marcados para revisión. Hay al menos uno en **54 de los 61 renglones**: 16/20 en f3r, 14/14 en f3v, 11/13 en f4r y 13/14 en f4v. Esto no significa que 54 etiquetas estén equivocadas: el detector puede incluir pintura o ruido, y una conexión puede atravesar varios trazos. La asignación correcta de cada signo continúa sin validar.

Se revisaron visualmente las 61 parejas anterior/corregida en nueve segmentos de hojas de contacto. Se observa menor inclusión de material vecino, con residuos y conexiones ambiguas todavía visibles. La revisión es de un asistente, no de un paleógrafo independiente. Se conservan [notas de revisión](results/kraken_crop_repair/visual_review.json), [preparación](results/kraken_crop_repair/preparation.json), [datos de fila](results/kraken_crop_repair/dataset.json) y vistas de [f3r](results/kraken_crop_repair/previews/3r_comparison.jpg) y [f4r](results/kraken_crop_repair/previews/4r_comparison.jpg).

## Controles, auditoría y ejecución real

- Pasaron seis controles sintéticos de conservación, fidelidad de píxeles, ascendentes, máscara, guías indistinguibles y filas vacías.
- Los tres jobs completaron la preparación, el ajuste, la conversión del modelo y la inferencia. El flujo de GitHub terminó correctamente; su estado `success` describe la ejecución del software.
- Se comprobaron los 122 registros PNG/etiqueta de preparación entre las tres ejecuciones: son idénticos salvo las rutas de ejecución. Las 61 etiquetas de cada extracción coinciden con las anteriores.
- La [auditoría separada](code/audit_kraken_crop_repair.py) leyó los PNG y las máscaras exportadas, comparó valores contra las imágenes fuente, reconstruyó coberturas y recalculó las distancias de edición mediante una matriz completa. **1.302 comprobaciones, cero discrepancias.** También verificó los tres hashes de modelo y los índices finales de época. No volvió a ejecutar las redes ni validó los glifos paleográficamente. [Resultado íntegro](results/kraken_crop_repair/audit.json).
- Se verificó el SHA-256 de cada ZIP contra el digest de GitHub. Cada ZIP contiene 325 archivos; se generó un manifiesto por variante. No se afirma que existiera una referencia externa individual para cada hash de esos manifiestos.

Una preparación local inicial se detuvo al importar un helper antiguo que requería `requests`, antes de preparar datos o entrenar. Se sustituyó esa dependencia por adquisición con la biblioteca estándar antes de publicar la ejecución definitiva. Se preserva el [registro de ese intento](results/kraken_crop_repair/attempts/local_preparation_01.json). No cuenta como entrenamiento.

## Evidencia preservada

El repositorio conserva los tres modelos finales, resultados por fila, configuraciones, logs, fuente de extracción, imágenes de entrada congeladas y mapeo de Boxer. Los checkpoints con estado del optimizador y los árboles completos de exportación quedan en los artefactos, con retención indicada hasta el **26 de noviembre de 2026**. [Procedencia y hashes](results/kraken_crop_repair/provenance.json).

| Variante | Modelo final SHA-256 |
| --- | --- |
| original_40 | `7313b1573e496b9af491e4da883919e0073583df47f09fb096ab30e4f5e18e43` |
| repaired_40 | `6e0acbc4f8d62fc7134c7bf4bf8ac8bb79e0c36dbf8422332b4f31872e488156` |
| repaired_200 | `b5df9eef0a783bec696b33636fbfb8d4807bfaa256d74ad6b34df4c58db66acb` |

Modelos: [original_40](results/kraken_crop_repair/runs/original_40/final_epoch.mlmodel), [repaired_40](results/kraken_crop_repair/runs/repaired_40/final_epoch.mlmodel), [repaired_200](results/kraken_crop_repair/runs/repaired_200/final_epoch.mlmodel). Son evidencia de diagnósticos de desarrollo, no reconocedores certificados o una solución del manuscrito.

Para reproducir la preparación sin descargar nuevamente las imágenes:

```bash
python research_gpt6/code/kraken_repair_experiment.py \
  --plan research_gpt6/data/kraken_crop_repair_plan.json \
  --repo research_gpt6 \
  --cache research_gpt6/results/kraken_crop_repair/source_cache \
  --out work/kraken_repair
```

Añadir `--variant original_40`, `--variant repaired_40` o `--variant repaired_200` ejecuta el ajuste correspondiente con Kraken 7.1 y el entorno CPU fijado en el workflow. No hay que usar las puntuaciones conocidas de la hoja 4 para escoger nuevos checkpoints.

Para auditar los resultados guardados, después de regenerar los recortes:

```bash
python research_gpt6/code/audit_kraken_crop_repair.py \
  --data work/kraken_repair --repo research_gpt6 \
  --ocr-result research_gpt6/results/kraken_crop_repair/runs/original_40/result.json \
  --ocr-result research_gpt6/results/kraken_crop_repair/runs/repaired_40/result.json \
  --ocr-result research_gpt6/results/kraken_crop_repair/runs/repaired_200/result.json \
  --output work/kraken_repair/audit.json
```

La auditoría ejecutada también recibió `--previous-bundle` con el artefacto recuperado del piloto del 15 de octubre para añadir 61 comparaciones exactas de píxeles. Sin ese argumento se omiten esas comparaciones y cambia el número total de controles, no el alcance paleográfico.

## Siguiente cuello de botella

La exclusividad de píxeles ya se puede comprobar. El problema pendiente es una referencia fiable y suficientemente amplia: decidir la propiedad de trazos ambiguos, excluir pintura sin borrar escritura, revisar las parejas imagen/transcripción y ampliar hojas de entrenamiento. Una evaluación confirmatoria necesita otras hojas físicas fijadas antes de ajustar el modelo.

El registro de las coordenadas Voynichese contra Yale no se ha implementado en esta iteración. Tampoco se ha identificado una lengua ni traducido el texto: **NOT_RUN**. La mejora de este ensayo es una reducción de error de OCR convencional en material de desarrollo.

Fuentes: Yale University Library, Beinecke MS 408; [Kraken 7.1, entrenamiento y preparación](https://kraken.re/7.1/user_guide/training_recognition.html); [Alexander Boxer, transcripción fijada](https://github.com/alexanderboxer/voynich-attack/tree/255bd632e45459230eaf2a994e0557ed6c682869/transcription), copyright 2022, CC BY 4.0. Se conserva la [licencia y atribución](results/kraken_crop_repair/source_cache/BOXER_LICENSE.txt). El mapa y las etiquetas permanecen idénticos; cambió la extracción de imágenes.

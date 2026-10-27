# 70 — Kraken reentrenado con más ejemplos: mejora modesta y generalización léxica pendiente

27 de octubre de 2026. Rama `experiment/kraken-voynich`.

**Se completaron dos reentrenamientos de 200 épocas adicionales desde el mismo modelo EVA conservado.** En una evaluación conjunta posterior sobre la hoja 7, la ampliación reduce el error de 501/709 caracteres EVA, **70,6629 %**, a 443/709, **62,4824 %**, y pasa de 1/135 a **9/135 transcripciones completas exactas**. Continuar sólo con las 197 parejas anteriores obtiene 72,2144 % de error. La mejora observada requiere más ejemplos en este ensayo, pero no permite atribuir el efecto exclusivamente a diversidad: la ampliación también ejecuta más pasos de optimizador.

Los nueve aciertos de la ampliación en la hoja 7 son palabras que ya aparecen en su vocabulario de entrenamiento. En las 76 referencias de esa hoja ausentes del vocabulario ampliado obtiene **0/76 coincidencias exactas**. Ambos modelos memorizan todas sus muestras de entrenamiento. La calidad sigue siendo insuficiente para transcribir automáticamente el manuscrito y no aporta una traducción.

## El protocolo original falló; el seguimiento es exploratorio

El [protocolo 69](69_kraken_expansion_protocol.md), commit `9f2163cf953f1a6b34ae4fad6b72f8c7e55f9263`, se publicó antes de adquirir las nuevas referencias. Fijó cuatro páginas adicionales de entrenamiento —f5r/f5v/f6r/f6v— y dos de evaluación —f7r/f7v—, exigiendo cinco particiones geométricas aceptadas por página.

La [ejecución geométrica 40544897322](https://github.com/MedinaParra/Voynich/actions/runs/40544897322), commit `8c6141623db3e0aaa9c3918ddca962f42d3126a2`, pasó 29/30 casos y **falló el criterio original**. En f5r, partición 0, P90 fue 5,57898 píxeles frente al máximo fijado de 5; la mediana fue 1,06367 y la fracción dentro de 5 fue 0,87640. La orientación final de esa página no se estimó porque no pasó todas las particiones. No se entrenó la expansión original ni se presenta su geometría como aprobada.

Después de observar ese fallo se publicó el [seguimiento 69b](69b_geometry_filtered_followup.md), antes de ejecutar el OCR nuevo. Excluye f5r y utiliza las cinco páginas que sí cumplieron todos los umbrales. No sustituye páginas, no reduce umbrales y no hace nuevos ajustes geométricos. **Es una selección adaptada por geometría ya observada**, sin selección por errores de OCR. Se conserva íntegro el fallo original; el seguimiento no equivale a superar el protocolo original ni constituye validación confirmatoria.

## Datos e inicialización

| Función | Folios | Palabras | Caracteres EVA |
|---|---|---:|---:|
| Entrenamiento original, conservado exactamente | f3r/f3v | 197 | 944 |
| Entrenamiento adicional admitido en 69b | f5v/f6r/f6v | 245 | 1.143 |
| Entrenamiento ampliado total | Hoja 3 y partes de 5/6 | **442** | **2.087** |
| Desarrollo histórico, conservado exactamente | f4r/f4v | 147 | 744 |
| Hoja reservada para este reajuste | f7r/f7v | **135** | **709** |

La reserva de la hoja 7 corresponde a este experimento de OCR: sus imágenes y la tradición de transcripción ya existían en otras partes del proyecto. No se afirma que sean un corpus nunca explorado. Ninguna muestra de las hojas 4 o 7 entró en el entrenamiento ni en su monitor. Las 344 parejas anteriores mantienen sus imágenes, máscaras y textos; la reconstrucción comprobó sus bytes.

Las fuentes nuevas son respuestas JSON puras y vistas de Voynichese, con fotografías de Yale ya conservadas. Las seis secuencias EVA coinciden exactamente con los XML del archivo fijado; no son seis lecturas nuevas independientes. Se mantienen XML, cabeceras Apache 2.0, atribución, recibos, SHA-256 y diferencias de encuadre. Las cajas nuevas usan directamente las coordenadas de la vista previa actual. La coincidencia entre fuentes y el registro SIFT no certifican una lectura paleográfica. Véase [NOTICE](results/kraken_expansion/inputs/NOTICE.md).

Los dos ajustes cargaron el modelo final `aligned_200` del ensayo 68, SHA-256 `c2b93256804d4697b56990e6bae0ae132942308ab9038b220a06352f8b013e8b`. Se verificó que la conversión a safetensors conserva sus 14 tensores y codec. Se reiniciaron optimizador y contador de épocas, manteniendo los pesos. `--resize add` permite ampliar el codec sólo con entrenamiento; en estos datos los dos alfabetos contienen los mismos 19 caracteres EVA.

Semilla 20261027, CPU/dos hilos, lote 16, tasa 0,001 constante, sin aumento, todas las capas ajustables. Monitor exclusivamente de entrenamiento. Se usó el checkpoint final de índice 199, sin elegirlo por desarrollo o por la hoja 7.

## Entrenamientos realmente ejecutados

La [ejecución 40545818493](https://github.com/MedinaParra/Voynich/actions/runs/40545818493), commit `544c197aa49d6aa2c4e9cfcca4db54853032afc0`, terminó correctamente en las dos condiciones. Los controles sintéticos comprobaron recortes y separación física, incluidos intentos de introducir una muestra reservada como entrenamiento.

| Condición | Palabras de entrenamiento | Épocas adicionales | Pasos de optimizador | CER de entrenamiento | Exactas en entrenamiento |
|---|---:|---:|---:|---:|---:|
| `continuation_200` | 197 | 200 | 2.600 | 0 % | 197/197 |
| `expanded_200` | 442 | 200 | 5.600 | 0 % | 442/442 |

Entrenamiento, conversión y evaluación tardaron 303,01 y 330,06 segundos respectivamente, en servidores distintos. Estos tiempos no son una comparación controlada de velocidad. Igualar épocas no igualó pasos de optimizador ni volumen de trabajo.

## Variación de inferencia y comparación conjunta

Los propios trabajos de entrenamiento produjeron ligeras diferencias al inferir el mismo modelo inicial: 465 frente a 464 errores en desarrollo, y 501 frente a 503 en la hoja 7. Los dos textos discrepantes fueron f4r_w0039 y f7v_w0001. Se conservan ambas salidas y sus referencias. Los hashes de pesos y recortes coinciden; no se aisló la causa de esa variación.

Por ese motivo se publicó el [diagnóstico 69c](69c_common_evaluation_protocol.md) antes de repetir la inferencia. La [ejecución común 40547524429](https://github.com/MedinaParra/Voynich/actions/runs/40547524429), commit `546030b414c58de1e2a2218d0495f04716dda259`, evaluó secuencialmente los tres modelos congelados en un mismo proceso, CPU AMD EPYC 7763, dos hilos y el mismo entorno fijado. Hizo dos pasadas, recargando cada modelo. La primera estaba fijada como comparación principal del diagnóstico; no se eligió la mejor.

Las dos pasadas coincidieron en todas las predicciones. Se registraron 282 llamadas a la red por modelo y pasada: **1.692 llamadas**. Respecto de los trabajos de entrenamiento, en el entorno común cambiaron tres salidas del modelo ampliado y dos de su inicial congelado; no se reemplazaron los resultados originales. La coincidencia en un proceso no garantiza igualdad en otros equipos. Este diagnóstico posterior no es una nueva reserva independiente ni otro entrenamiento.

Las siguientes cifras proceden de la **primera pasada común**, con idénticas muestras y entorno para los tres modelos:

| Modelo | Desarrollo: errores / 744 | CER desarrollo | Exactas / 147 | Hoja 7: errores / 709 | CER hoja 7 | Exactas / 135 |
|---|---:|---:|---:|---:|---:|---:|
| Inicial congelado, ensayo 68 | 465 | 62,5000 % | 2 | 501 | 70,6629 % | 1 |
| Continuación con 197 parejas | 474 | 63,7097 % | 5 | 512 | 72,2144 % | 2 |
| Ampliación con 442 parejas | **415** | **55,7796 %** | **9** | **443** | **62,4824 %** | **9** |

La ampliación reduce 58 errores, o **8,1805 puntos porcentuales**, frente al inicial en la hoja 7. Frente a la continuación reduce 69 errores, o 9,7320 puntos. En desarrollo histórico reduce 50 errores frente al inicial. Son diferencias descriptivas: una semilla y una hoja física de reserva no permiten estimar una superioridad general o significación estadística.

En desarrollo, siete de las nueve coincidencias de la ampliación contienen dos o más caracteres; las otras dos son `s`. En la hoja 7 las nueve son multicaracteres. Sus referencias son `daiin`, `chol`, `chor`, `daiin`, `dor`, `chor`, `daiin`, `dy`, `daiin`: todas figuraban en el vocabulario ampliado. De las 135 referencias de la hoja 7, 59 están en ese vocabulario y 76 están ausentes; ninguna de las 76 ausentes fue reconocida exactamente. La condición ampliada conserva así una dependencia fuerte de formas conocidas.

El vecino por imagen usando las 442 referencias de entrenamiento obtiene, en los trabajos originales, 467/709 errores, CER 65,8674 %, y **11/135 palabras exactas** en la hoja 7. En desarrollo obtiene 488/744, CER 65,5914 %, y 14/147 exactas. Son comparadores deterministas sobre los mismos recortes y referencias; el diagnóstico común sólo volvió a inferir las redes. El menor CER del modelo ampliado sigue coexistiendo con menos palabras exactas que este comparador sencillo. Se conservan también los comparadores de palabra frecuente, carácter repetido y salida vacía.

El error EVA sobre las 147 muestras conservadas sí puede compararse con el ensayo 68 y con la evaluación común del modelo inicial. Los antiguos errores Boxer sobre filas y espacios mantienen un denominador diferente.

## Auditoría, archivos y reproducción

La [auditoría de datos y entrenamientos](results/kraken_expansion/training_audit.json) pasa **26.987 comprobaciones sin discrepancias aritméticas o de archivos**. Incluye los treinta casos geométricos, el rechazo de f5r, las transformaciones y referencias exportadas, píxeles y hashes, conservación de muestras previas, selección de entrenamiento, ausencia de hojas compartidas, pesos convertidos, configuración, checkpoints, pasos reales, predicciones, distancias y comparadores. Registra las diferencias de inferencia entre servidores separadamente; no las oculta como una igualdad supuesta.

La [auditoría de la evaluación común](results/kraken_expansion/common_evaluation/audit.json) pasa **3.135 comprobaciones**, con cero discrepancias. Recalcula distancias con una matriz completa, métricas, inventarios de ambas pasadas, diferencias respecto de los trabajos y contadores registrados. No vuelve a inferir ni verifica paleográficamente las referencias. La auditoría preliminar de 8.728 comprobaciones es parte de la misma cadena de datos, no otra validación independiente que deba sumarse a la posterior.

Se verificaron los digests de los cuatro ZIP: geometría original, dos entrenamientos y evaluación común. Se conservan [procedencia y recibos](results/kraken_expansion/provenance.json), todos los fallos, modelos finales, checkpoints de índice 199, configuración, comandos, logs, pesos iniciales convertidos y predicciones completas.

| Modelo nuevo conservado | Tamaño | SHA-256 |
|---|---:|---|
| [Continuación de 197 parejas](results/kraken_expansion/runs/continuation_200/final_epoch.mlmodel) | 950.712 bytes | `08e3586bc39103eaea3a984e85ec050531f46ef1a79c2d97b0ff06344b8eeaab` |
| [Ampliación de 442 parejas](results/kraken_expansion/runs/expanded_200/final_epoch.mlmodel) | 950.712 bytes | `35092d9baf56083eb6c70a2e32c478d8910ef5e685d0cee33fc5a935ca1c71d8` |

Los JSON grandes se archivan con gzip sin pérdida de bytes; sus hashes originales y comprimidos se registran en [lossless_json_archives.json](results/kraken_expansion/lossless_json_archives.json). Los 724 recortes, máscaras y parejas se reconstruyen desde las fotografías y metadata. La [comprobación de restauración](results/kraken_expansion/restoration_check.json) verificó 2.172 archivos. Los pesos safetensors `best` no se usaron para seleccionar resultados y permanecen inventariados en los artefactos; los checkpoints finales y modelos evaluados se guardan en Git.

Auditoría reproducible sin entrenar ni inferir, con Pillow 12.3.0, numpy y scipy:

```bash
python research_gpt6/code/audit_kraken_expansion.py \
  --primary research_gpt6/results/kraken_expansion/primary_geometry \
  --prepared research_gpt6/results/kraken_expansion/followup_prepared \
  --runs research_gpt6/results/kraken_expansion/runs \
  --repo research_gpt6 --restore-inputs --out work/expansion_audit.json

python research_gpt6/code/audit_kraken_expansion_common.py \
  --bundle research_gpt6/results/kraken_expansion/common_evaluation \
  --prepared research_gpt6/results/kraken_expansion/followup_prepared \
  --runs research_gpt6/results/kraken_expansion/runs \
  --repo research_gpt6 --out work/common_audit.json
```

Después de restaurar las entradas se puede reejecutar el reajuste con `retrain_kraken_expansion.py`, el plan `kraken_expansion_followup_plan.json` y metadata `kraken_expansion_execution.json`, usando otra carpeta de salida para cada condición. Los workflows conservan las versiones y comandos completos. Una repetición posterior puede diferir en inferencia entre equipos, como ya se documentó; conservar los hashes de pesos no garantiza salidas idénticas en todos ellos.

El resultado orienta el siguiente trabajo hacia más diversidad de escritura y evaluación explícita de palabras ausentes del entrenamiento. Seguir aumentando épocas sobre las mismas parejas no resolvió esa transferencia en el control. Nueva revisión experta, identificación de lengua y traducción: **NOT_RUN**.

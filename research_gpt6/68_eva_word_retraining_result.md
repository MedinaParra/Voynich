# 68 — Kraken reentrenado: mejora de error EVA, generalización insuficiente

Fecha: 27 de octubre de 2026. Rama: `experiment/kraken-voynich`.

**Se completaron dos ajustes reales de 200 épocas desde el modelo conservado `repaired_200`.** En las 147 palabras de desarrollo, el ajuste con las parejas originales obtiene 465 errores sobre 744 caracteres EVA: **CER 62,5 %**. El control con etiquetas permutadas obtiene 76,6129 %. El vecino por imagen obtiene 68,4140 % y acierta más palabras completas que Kraken. El reajuste se ejecutó y es verificable; su calidad de reconocimiento todavía es insuficiente.

## Qué se ejecutó

El [protocolo 67](67_eva_word_retraining_protocol.md), el [plan fijado](data/kraken_eva_words_plan.json), el código y el workflow se publicaron antes del entrenamiento. Se usaron las 344 referencias candidatas de la versión geométrica uniforme v2, sin añadir una revisión experta:

- Entrenamiento en f3r/f3v: 197 palabras, 944 caracteres EVA. Desarrollo en f4r/f4v: 147 palabras, 744 caracteres. No se comparten hojas físicas entre ambos conjuntos; las páginas ya habían sido exploradas anteriormente.
- Inicialización desde `repaired_200`, SHA-256 `b5df9eef0a783bec696b33636fbfb8d4807bfaa256d74ad6b34df4c58db66acb`. Se convirtió a safetensors y se verificaron los 14 tensores y el codec contra el original antes de cargar sus pesos.
- `ketos train --load ... --resize new` adaptó la salida a los 19 caracteres EVA del entrenamiento. Los logs muestran aproximadamente 237.000 parámetros entrenables y cero no entrenables. Se reiniciaron optimizador y contador de épocas; se continuaron los pesos del modelo.
- Misma semilla 20261027, CPU con dos hilos, lote 16, tasa 0,001 constante y sin aumento en las dos condiciones. Monitor sólo de entrenamiento. Se evaluó el checkpoint final de índice 199; no se eligió un checkpoint por los resultados de desarrollo.
- El control reasigna textos dentro de cada folio de entrenamiento y longitud exacta: cambian realmente 186/197 etiquetas; 11 conservan el texto por duplicados o grupos singulares. Se mantienen el inventario de textos, longitudes, imágenes y etiquetas de desarrollo.

La [ejecución corregida 40540629476](https://github.com/MedinaParra/Voynich/actions/runs/40540629476), commit `cb97858416cd43cade752750956c4f13dc86f719`, terminó correctamente en ambas condiciones. Entrenamiento, conversión final y evaluación tardaron 298,39 segundos en la condición original y 293,23 en el control, además de instalación y preparación.

## Resultados de desarrollo con el mismo denominador

CER es la distancia de edición total dividida por 744 caracteres EVA de referencia. Se exportan todas las predicciones, incluidos los errores y los textos de entrenamiento asignados.

| Condición o comparador | Errores EVA / 744 | CER | Palabras exactas / 147 |
|---|---:|---:|---:|
| Kraken, parejas originales | 465 | **62,5000 %** | 2 |
| Kraken, etiquetas permutadas | 570 | 76,6129 % | 1 |
| Vecino por imagen y referencias originales | 509 | 68,4140 % | **14** |
| Palabra de entrenamiento más frecuente: `chor` | 530 | 71,2366 % | 4 |
| Carácter más frecuente repetido: `ooooo` | 720 | 96,7742 % | 0 |
| Salida vacía | 744 | 100,0000 % | 0 |

La ventaja descriptiva del modelo original es de 105 errores, o 14,1129 puntos porcentuales, respecto del control; frente al vecino por imagen son 44 errores, o 5,9140 puntos. Son diferencias observadas en una ejecución con una semilla. No se estimó su incertidumbre ni se declara significación estadística.

**Las dos coincidencias exactas de Kraken son etiquetas de un solo carácter, `s`, en f4v_w0069 y f4v_w0075. No acertó ninguna palabra de dos o más caracteres.** El control sólo acertó f4v_w0069, también `s`. El menor CER de Kraken frente al vecino por imagen no supone superioridad en reconocimiento de palabras completas.

| Subconjunto | Palabras | Caracteres EVA | Errores Kraken original | CER original | Exactas |
|---|---:|---:|---:|---:|---:|
| f4r | 64 | 324 | 203 | 62,6543 % | 0 |
| f4v | 83 | 420 | 262 | 62,3810 % | 2 |
| Referencia presente en vocabulario de entrenamiento | 52 | 212 | 121 | 57,0755 % | 2 |
| Referencia ausente de ese vocabulario | 95 | 532 | 344 | 64,6617 % | 0 |

Los dos últimos grupos particionan el mismo desarrollo que los dos primeros; no son otra muestra independiente.

## Diagnóstico crítico

En entrenamiento, Kraken original alcanza **8 errores / 944 caracteres, CER 0,8475 % y 191/197 palabras exactas**. La distancia hasta el 62,5 % de desarrollo y la ausencia de aciertos multicaracteres muestran una generalización muy pobre en esta prueba. El control también aprende gran parte de sus etiquetas artificiales: 41 errores / 944, CER 4,3432 % y 161/197 coincidencias con el texto asignado. Contra los textos originales de esas imágenes, el control tiene 683 errores / 944, CER 72,3517 %, y 10/197 exactas.

La ventaja respecto de la permutación es compatible con aprender asociaciones entre imágenes y referencias. Este único contraste no separa cuánto corresponde a signos, patrones de longitud o rasgos de las imágenes. La permutación, además, conserva 11 textos y parte de la estructura de entrenamiento. No valida por sí sola lectura paleográfica ni significado.

No conviene aumentar sólo las épocas sobre estas mismas 197 parejas: ya se aproximó a la memorización y el obstáculo observado está en transferir. El siguiente experimento útil requiere más ejemplos variados y un control independiente de la calidad de las parejas imagen/texto, con folios nuevos reservados antes de ajustar. Estos resultados permiten priorizar ese trabajo; no autorizan una transcripción automática fiable del manuscrito completo.

**El 73,8197 % del ensayo anterior usaba Boxer, filas y espacios. El nuevo 62,5 % usa caracteres EVA y recortes de palabra. No son una comparación directa antes/después.** El reajuste mezcla nueva referencia, unidades, recortes y adaptación del alfabeto; este diseño tampoco aísla el efecto de la corrección geométrica.

## Auditoría y conservación

La [auditoría independiente](results/kraken_eva_words/audit.json) pasó **16.382 comprobaciones sin discrepancias**. Usa una matriz completa de edición y un cálculo escalar de rasgos de imagen separado del driver. Comprueba píxeles conservados y enmascarados, geometría, hashes, parejas, separación física, permutación, los 344 textos por condición, predicciones, comparadores, sumas, desgloses, configuración, evidencia de época 200, checkpoints, codec EVA y prueba de preservación de pesos. No volvió a ejecutar inferencia ni revisó paleográficamente las referencias.

Se verificaron los SHA-256 de ambos ZIP contra la metadata de GitHub. La [procedencia](results/kraken_eva_words/provenance.json) conserva identificadores, fechas, tamaños y digests. Los dos contenedores de pesos convertidos tienen hashes distintos, pero cada uno conserva exactamente los 14 tensores y el codec originales: la equivalencia verificada es de los estados cargados.

| Modelo final | Tamaño | SHA-256 |
|---|---:|---|
| [Parejas originales](results/kraken_eva_words/runs/aligned_200/final_epoch.mlmodel) | 950.712 bytes | `c2b93256804d4697b56990e6bae0ae132942308ab9038b220a06352f8b013e8b` |
| [Etiquetas permutadas](results/kraken_eva_words/runs/permuted_200/final_epoch.mlmodel) | 950.712 bytes | `b2d033c01e2fcabfdd906e14f14906a708d22cc149190d78b83170b8ee4ec430` |

En `results/kraken_eva_words/runs/` se conservan ambos modelos finales, checkpoints de época 199, pesos convertidos de inicialización, pruebas tensoriales, codec, configuraciones, comandos, logs, datasets, resultados completos, inventarios y vistas de recortes. Los PNG, máscaras y parejas de texto se reconstruyen desde las fotografías y metadata conservadas. La [prueba de reconstrucción](results/kraken_eva_words/restoration_check.json) verifica 2.064 archivos regenerados contra sus hashes o textos originales. El artefacto completo también contiene los pesos safetensors marcados como `best`, que no se usaron para seleccionar el resultado; éstos quedan inventariados. Los artefactos de Actions tienen caducidad, por eso los modelos finales y checkpoints se guardan asimismo en Git.

Reproducción del reajuste con el entorno fijado en el workflow:

```bash
python research_gpt6/code/kraken_eva_word_training.py \
  --plan research_gpt6/data/kraken_eva_words_plan.json \
  --repo research_gpt6 --variant aligned_200 --out work/eva_words/aligned_200
```

Se repite con `--variant permuted_200` y otra salida. Auditoría de los archivos conservados, sin volver a entrenar ni inferir, con Pillow 12.3.0, numpy y scipy:

```bash
python research_gpt6/code/audit_kraken_eva_words.py \
  --bundles research_gpt6/results/kraken_eva_words/runs \
  --repo research_gpt6 --restore-crops --out work/eva_words_audit.json
```

### Primer intento conservado

La [ejecución inicial 40540130799](https://github.com/MedinaParra/Voynich/actions/runs/40540130799), commit `c261f8685de5e1b30cf4a5d6fd3d5b322f7f1851`, falló **antes de entrenar** en ambas condiciones. La instalación, los cinco controles de entrada y la preparación pasaron, pero el verificador usó el cargador CoreML heredado para leer safetensors. Se corrigió únicamente el cargador y el acceso al estado de tensores, manteniendo el plan experimental. Se conservan sus errores, logs, inventarios y procedencia en `initial_failed_attempt/`. Los cinco controles volvieron a pasar en la ejecución corregida.

Referencias EVA candidatas sin nueva revisión experta. Identificación de lengua y traducción: **NOT_RUN**. Este reajuste no descifra el Voynich.

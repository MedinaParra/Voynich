# 28. TimesFM 2.5 — experimento estructural ciego

Fecha: 2026-10-06

## Objetivo

Evaluar si un foundation model de series temporales detecta continuidad predictiva en rasgos estructurales del Voynich. No se interpreta el resultado como traducción ni semántica.

## Modelo fijado

- Google Research TimesFM 2.5, 200M, PyTorch (modelo realmente invocado por el harness).
- Checkpoint: `google/timesfm-2.5-200m-pytorch`.
- Uso: investigación no comercial.

## Prevención de leakage

El código no contiene el orden Layfield–Davis. La primera etapa pronostica rasgos de líneas en el orden del corpus congelado. La comparación de órdenes físicos se añadirá únicamente después de verificar externamente el mapeo de Q13/Q20.

## Rasgos iniciales por línea

Número de tokens, longitud media, razón de tipos únicos, entropía de caracteres, frecuencias q/o/y/d, fracción de palabras que comienzan en q y fracción que terminan en y.

## Controles siguientes

1. Baselines persistence/mean/AR/Markov.
2. Reverse-order control.
3. Character/token shuffle preserving marginal frequencies.
4. Leave-one-folio/quire-out.
5. Alternative feature families.
6. 9,999 physically valid permutations for Q13/Q20 once mapping is verified.
7. Compare TimesFM ranking against TF-IDF/cosine and held-out symbolic models.

## Decision rule

TimesFM is informative only if it beats simple baselines on held-out units and any physical-order advantage survives permutation controls. A lower forecast error alone is not evidence of language or decipherment.

## Execution status at commit

- Official TimesFM 3.0 availability/API documentation: PASS (verified externally).
- Isolated branch `experiment/timesfm-voynich`: PASS.
- Harness committed: PASS.
- Model weights downloaded in an execution runtime: NOT_RUN.
- TimesFM inference on Voynich corpus: NOT_RUN.
- Q13/Q20 physical-order tournament: NOT_RUN.

No numerical result is claimed until an actual runtime executes the checkpoint and records the output.


## Corrección de evaluación, 2026-10-06

El código anterior elegía `winner` comparando dos variantes en el test final y buscaba superar una mejora anterior del 63%. Ese máximo no constituye una estimación independiente del rendimiento primario. Se elimina la selección por test y ese umbral: contexto y variante primaria se eligen exclusivamente en validación por MSE estandarizado mediante varianzas del bloque de entrenamiento anterior a validación. Se informan ambas variantes, identificando la primaria sin mirar sus errores finales. Se añade baseline de media y manejo de denominadores nulos.

El horizonte final ya inspeccionado se etiqueta exploratorio; cambiar el código no vuelve nuevos esos datos. Un único horizonte de 16 líneas no demuestra robustez entre folios/cuadernos y ningún pronóstico de estos rasgos equivale a traducción.

Verificaciones locales: compilación Python y comprobaciones de selección individual/ensemble, empate determinista, baseline cero y parser: PASS. Inferencia del checkpoint con el código corregido: NOT_RUN al publicar la corrección; se verificará en GitHub Actions. El informe inicial arriba es histórico y no certifica el modelo ejecutado en una revisión posterior.

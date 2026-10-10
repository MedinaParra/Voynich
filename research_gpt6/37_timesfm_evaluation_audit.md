# 37. Corrección y trazabilidad del experimento TimesFM

Fecha: 2026-10-06. Rama: `experiment/timesfm-voynich`.

## Ejecución observada

La ejecución [37521095643](https://github.com/MedinaParra/Voynich/actions/runs/37521095643) sobre el commit `70a74bad40f0881921c47635f73566755c17fb0f` completó el trabajo TimesFM con éxito. Logs consultados: paquete timesfm 3.0.2, checkpoint `google/timesfm-2.5-200m-pytorch`, Python 3.11.16, 1.423 líneas admitidas, horizonte de 16 líneas. No confundir versión del paquete con versión del checkpoint.

El contexto 128 obtuvo reducción del MSE bruto frente a persistencia de 0,620507; el ensemble 128/1024 obtuvo 0,607483. Ambos mejoraron 9 de 10 rasgos. Son resultados de esa ejecución, no porcentajes de descifrado. El MSE sin normalizar combina conteos y proporciones, con predominio de rasgos de mayor escala.

## Problema corregido

El código seleccionaba `winner` mirando las dos variantes en el bloque final y buscaba superar un resultado previo de 63%. Se elimina esa selección por test y ese objetivo. Contexto y variante primaria se eligen por MSE estandarizado en validación, con varianzas calculadas exclusivamente antes de validación. Se conserva cada resultado final sin escoger un ganador posterior. Se añade baseline de media, se maneja baseline de error cero y se rechazan horizonte/contextos inválidos.

Corrección de código: `6c0d64cf697028a5dbd7c9ee420ca61e82ed09e1`. El workflow fija paquete timesfm 3.0.2, observado en la ejecución exitosa, y la documentación identifica el checkpoint 2.5. Otras dependencias y la revisión remota de pesos aún no están fijadas: reproducibilidad completa pendiente.

## Verificación

- Compilación local Python: PASS.
- Cuatro pruebas de regresión sobre selección y escalas: PASS. Comando: `python research_gpt6/code/test_timesfm_selection.py`. No cargan pesos.
- Parser local sobre corpus fijado: PASS.
- Ejecución real del modelo anterior: PASS_EXECUTED, con límites metodológicos arriba.
- Ejecución real corregida: iniciada en [37521477963](https://github.com/MedinaParra/Voynich/actions/runs/37521477963); aún no se disponía del resultado al redactar este registro. No asignar PASS anticipado.

La inferencia anterior se conserva en `results/timesfm_previous_run_audit.json` dentro de un envoltorio que identifica commit, run y limitaciones. No sustituye la inferencia corregida.

## Qué sigue sin resolverse

El último horizonte ya se había inspeccionado. Esta evaluación es exploratoria aunque se corrija la selección. Faltan ventanas reservadas por folio/cuaderno, baselines adicionales y controles de orden. TimesFM pronostica diez rasgos numéricos por línea; el script no asigna palabras a signos, no recupera claves y no traduce. Un mejor pronóstico no certifica significado ni identifica el mecanismo de escritura.

Nota de integración: se detectó el commit concurrente `df245e8920511c6d217eb5e0a6453c4ffe54d613`, que añade un test rolling-origin y conserva la corrección de selección. Este registro se añade sobre ese commit sin modificar su código; resultados de esa extensión no evaluados aquí.


## Resultado corregido verificado

Run [37521477963](https://github.com/MedinaParra/Voynich/actions/runs/37521477963), commit `6c0d64cf697028a5dbd7c9ee420ca61e82ed09e1`: el job TimesFM terminó con éxito y su log contiene la inferencia corregida. La validación eligió `top2_ensemble`, contextos 256/1024. En el test final: MSE estandarizado 0,675706; reducción frente a persistencia 42,8869%; baseline de media 0,770476, con reducción relativa del modelo frente a esa media de aproximadamente 12,30%. No comparar directamente ese 42,89% estandarizado con el 62,05% bruto de la ejecución anterior.

Resultado completo y procedencia en `results/timesfm_corrected_run_audit.json`. Esta ejecución certifica funcionamiento del harness corregido sobre ese horizonte, no robustez entre cuadernos, orden físico recuperado ni significado. El rolling-origin concurrente todavía no se evalúa en este registro.

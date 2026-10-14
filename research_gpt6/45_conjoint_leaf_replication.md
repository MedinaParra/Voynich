# 45. Réplica de pares físicos: Q1, Q3 y subconjunto de Q20

Fecha: 2026-10-07. Rama: `experiment/timesfm-voynich`.

**Resultado: `FAIL_REPLICATION_PANEL`.** El parecido léxico bruto de las hojas conjuntas se extiende descriptivamente a grupos de Q1, Q3 y Q20. La asociación conjunta no supera el control residual fijado, y algunas robusteces fallan. TimesFM no aporta una ventaja frente al promedio de la página fuente en el subconjunto admisible de Q20. Traducción: `NOT_RUN`.

## Qué se intentó replicar

El [control Q13](44_q13_matching_control.md) había distinguido una asociación bruta con el bifolio de una continuidad léxica adicional que sobreviviera a todos los controles. Este seguimiento conserva esa distinción y extiende el análisis a otros cuadernos. No busca un orden de lectura ni una interpretación de palabras.

Protocolo y selección publicados **antes** de calcular similitudes en [`315b9ca9`](https://github.com/MedinaParra/Voynich/commit/315b9ca991eef5f2931daf0eb5b0f8b7094037fe). Implementación inicial: `c64be0b8`. Versión autoritativa: [`6aefcf33`](https://github.com/MedinaParra/Voynich/commit/6aefcf33899ceb54b4f60836bf115c03b41fe7ca). El corpus ya había sido explorado en el proyecto; esta réplica no es una transcripción independiente ni una reserva de manuscrito nunca inspeccionada.

## Selección por metadatos y disponibilidad

Se buscaron pares de hojas ordinarias que compartieran `$Q` y `$B` en el corpus ZL EVA congelado. Cada par debía tener las cuatro caras con párrafos literales, la misma mano conocida y la misma variedad Currier conocida. Se agruparon por cuaderno/mano/Currier y se exigieron cuatro bifolios como mínimo. Q13 se excluyó de la réplica. Ninguna similitud ni salida de TimesFM intervino en esta selección.

| Grupo seleccionado | Mano / Currier | Pares físicos anotados | Alcance |
|---|---|---|---|
| Q1 | 1 / A | 1\|8, 2\|7, 3\|6, 4\|5 | Cuatro bifolios del cuaderno |
| Q3 | 1 / A | 17\|24, 18\|23, 19\|22, 20\|21 | Cuatro bifolios del cuaderno |
| Q20 | 3 / B | 105\|114, 106\|113, 107\|112, 108\|111 | Cuatro de los seis bifolios representados |

En Q20 se excluyó `103|116` porque f116v no tiene párrafos Voynich utilizables y falta su Currier; `104|115`, porque f115r tiene mano `@`. Las hojas 109 y 110 no están representadas en el corpus. Se conserva el registro de todos los grupos descartados y sus razones. El mapeo proviene de la anotación del corpus; no se realizó una nueva colación de imágenes del manuscrito.

Los requisitos de TimesFM se aplicaron **después y por separado**: si una cara tiene menos de cuatro filas limpias, se bloquea ese diagnóstico completo. Esto no elimina el análisis léxico del grupo ni permite acortar el horizonte para obtener un resultado.

## Análisis fijado

La representación, limpieza literal, políticas de coma y controles de Q13 se conservaron. TF–IDF se aprende únicamente en hojas fuera de **todo el cuaderno objetivo**, incluyendo la exclusión de pares de ese cuaderno que no entren en el test. El control residual usa trigramas de caracteres, diferencia de log-longitud y distancia foliar al cuadrado, sin etiquetas de pareja física en el ajuste.

Cada grupo tiene 105 emparejamientos perfectos y 24 que conectan una hoja de la mitad anterior con una de la posterior. Se enumeraron todos, incluyendo el observado. Se mantienen los criterios estrictos por grupo y se informan sus fallos.

Para el contraste conjunto se fijó una media con igual peso de las tres puntuaciones, estandarizadas por media y desviación poblacional de la referencia completa de cada grupo. La misma normalización se usa en la referencia restringida. Se enumeró el producto cartesiano exacto: **1.157.625** combinaciones completas y **13.824** restringidas. Las puntuaciones individuales y el algoritmo permiten reconstruir estos productos sin guardar un millón de números redundantes.

El panel sólo pasa si ambas políticas de coma tienen p≤0,05 en las dos referencias tanto para TF–IDF como para su residual, con efectos positivos en cada grupo y todas las comprobaciones por cara/retirada positivas. Las métricas secundarias no pueden rescatar un fallo.

## Resultado conjunto

| Política de coma | Métrica | p exacto completo, N=1.157.625 | p exacto restringido, N=13.824 | Decisión de estas puertas |
|---|---|---:|---:|---|
| Separar | TF–IDF bruto | 0,000140806 | 0,003110532 | Pasa |
| Separar | TF–IDF residual | 0,119933485 | 0,242766204 | Falla |
| Unir | TF–IDF bruto | 0,000308390 | 0,004412616 | Pasa |
| Unir | TF–IDF residual | 0,223183673 | 0,433087384 | Falla |

El patrón bruto es consistente en ambos tratamientos de la coma. El ajuste residual no confirma una componente adicional robusta. Los criterios no se modificaron después de observar estos valores.

## Diferencias entre cuadernos

Puntuaciones primarias para coma separada:

| Grupo | TF–IDF observado | Media de 105 | Rango bruto / 105 | p bruto restringido | p residual completo | p residual restringido |
|---|---:|---:|---:|---:|---:|---:|
| Q1 | 0,302330 | 0,259766 | 4 | 0,125000 | 0,600000 | 0,375000 |
| Q3 | 0,331617 | 0,239555 | 1 | 0,041667 | 0,047619 | 0,083333 |
| Q20, subconjunto | 0,576410 | 0,525655 | 9 | 0,250000 | 0,333333 | 0,666667 |

Ningún grupo pasa todas las puertas estrictas. Q3 obtiene el mejor emparejamiento bruto en las dos políticas de coma, pero falla el control residual restringido. Q1 tiene un residual inferior a la media completa y falla la vista de recto. Al unir comas, también fallan retiradas en Q1 y Q20 y la vista de verso restringida en Q20.

El resultado de Q20 corresponde a cuatro bifolios seleccionados por disponibilidad y metadatos. No se extrapola a sus seis bifolios representados ni al cuaderno completo.

## TimesFM y controles sencillos

Q1 y Q3 quedan `BLOCKED_INSUFFICIENT_CLEAN_ROWS` para TimesFM: varias caras no alcanzan el horizonte fijo de cuatro filas con la limpieza previa. Se registran las caras y conteos; no se les asignan valores predictivos. Sus análisis léxicos sí se ejecutaron.

En el subconjunto de Q20 se ejecutó `google/timesfm-2.5-200m-pytorch`, paquete `timesfm[torch]==3.0.2`, contexto máximo 64, horizonte 4, los diez rasgos anteriores y semilla 20261007. Se generó una predicción por página fuente antes de puntuar parejas. Cada pareja promedia ocho comparaciones dirigidas entre caras; se excluyen transiciones dentro de una misma hoja. Las escalas provienen de todas las filas externas a Q20.

| Predictor en Q20 | Error observado, menor mejor | Rango / 105 | p completo | Rango / 24 | p restringido |
|---|---:|---:|---:|---:|---:|
| TimesFM | 0,888650 | 7 | 0,066667 | 7 | 0,291667 |
| Última fila de la fuente | 1,558472 | 23 | 0,219048 | 11 | 0,458333 |
| Media de la página fuente | 0,808749 | 4 | 0,038095 | 4 | 0,166667 |

TimesFM obtiene **9,88% más error** que la media de la página fuente. Ninguno supera la referencia restringida al nivel fijado. La media también había superado TimesFM en Q13. Estos ensayos no justifican atribuir al modelo grande una capacidad adicional para recuperar emparejamientos físicos; no evalúan todas sus posibles aplicaciones.

## Alcance de la conclusión

La asociación bruta con los pares anotados se observa en secciones y estratos distintos de Q13. Esa extensión descriptiva es el avance. Bajo los controles fijados, la evidencia no respalda una componente léxica adicional uniforme que permita interpretar el contenido.

El ajuste por trigramas puede retirar contenido léxico real además de estilo o patrones de producción. Por eso el fallo residual no prueba ausencia de estructura, semántica o idioma. El tamaño de cuatro bifolios por grupo limita la potencia, especialmente la referencia restringida, cuyo menor p posible por grupo es 1/24.

Los productos exactos suponen asignaciones intercambiables e independientes de parejas entre grupos. La encuadernación histórica no fue aleatorizada. Q1 y Q3 comparten mano/Currier y no representan muestras independientes de producción. Las vistas de cara y las retiradas se solapan. Metadatos, selección de fragmentos e IDF son propios de esta transcripción.

Se mantienen `FAIL_STRICT_PAIR_COHERENCE` en Q13 y `FAIL_REPLICATION_PANEL` aquí. No se identifica una lengua, no se traduce una palabra, no se valida un orden único y la novedad frente al estado del arte no está establecida.

## Ejecución, corrección y auditoría

[GitHub Actions 37667152334](https://github.com/MedinaParra/Voynich/actions/runs/37667152334), job `112949189291`, completó `success` sobre `6aefcf33`. Pasaron **29 controles científicos**: 16 del harness Q13 y 13 de réplica. El éxito de ejecución es distinto del resultado científico negativo.

La primera implementación excluía de las escalas de TimesFM una fila externa de la roseta (`fRos.139,@Pb`), porque no tiene identificador de página ordinaria. La corrección la conserva, como exigía el protocolo. El run anterior `37666599995` sobre `c64be0b8` está superado para el diagnóstico TimesFM; sus valores no se usan en la conclusión. El cálculo léxico no cambió. Se añadió un control específico para esa fila.

Se descargó el artefacto completo `11503327766`, se verificaron su ZIP y la salida contra los digests de GitHub y del log. La comparación local/CI de todas las secciones léxicas y del panel comprobó **5.816 valores flotantes y 7.412 valores exactos**, con diferencia máxima cero.

El auditor reprodujo 735 registros de emparejamiento, 4.305 puntuaciones y 82 resúmenes de grupo. Reconstruyó las ocho referencias conjuntas (dos políticas × dos métricas × dos familias de referencia). Recalculó **7.200 errores por rasgo** de TimesFM y sus baselines desde entradas/predicciones guardadas, y 140 valores de arista; verificó también los dos diagnósticos bloqueados. No se afirma una segunda inferencia local del modelo.

- SHA256 original CI: `15d5802e50e1f68c7c0fe3e4d938f88c19b8f258732b4d34cb5ecc98d9058c3d`.
- SHA256 JSON compacto publicado: `510697e8d1b3c9150be86c72668050937883590a3a531d0992b86e40741d4020`; el contenido JSON es idéntico.
- Python local 3.12.14; CI 3.12.15; NumPy 2.3.5 en ambas.
- Identificador y paquete de TimesFM fijados, pero revisión/hash de pesos upstream no archivados. Las entradas y predicciones completas permiten reproducir las puntuaciones sin volver a descargar pesos.

## Reproducción

```bash
pip install 'numpy==2.3.5'
python research_gpt6/code/test_conjoint_replication.py
python research_gpt6/code/conjoint_replication.py \
  --corpus /ruta/voynich_eva.txt \
  --plan research_gpt6/data/conjoint_replication_plan.json \
  --metadata-audit research_gpt6/data/conjoint_replication_metadata.json \
  --out /tmp/conjoint_lexical.json
python research_gpt6/code/audit_conjoint_replication.py \
  --result research_gpt6/results/conjoint_replication_result.json
# Para repetir inferencia: instalar 'timesfm[torch]==3.0.2' y añadir --timesfm.
```

Archivos: [protocolo](data/conjoint_replication_plan.json), [selección y exclusiones](data/conjoint_replication_metadata.json), [análisis](code/conjoint_replication.py), [harness](code/test_conjoint_replication.py), [auditor sin pesos](code/audit_conjoint_replication.py), [salida completa](results/conjoint_replication_result.json), [auditoría CI](results/conjoint_replication_ci_audit.json) y [controles](results/conjoint_replication_checks.json).

Corpus: `cesarjz/Voynich`, commit `47e6a77dc9d5cd570c375f4aff710fa4a0567278`, blob `2a4533ab9bdfa85db9bad602d590978953055df1`, SHA256 `bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc`.

El siguiente contraste que puede reducir esta ambigüedad es una transcripción independiente con criterios de correspondencia fijados previamente. Elegir más órdenes, horizontes o umbrales sobre los mismos resultados no aporta esa independencia.

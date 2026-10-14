# 44. Q13: pares físicos frente a 945 emparejamientos

Fecha: 2026-10-07. Rama: `experiment/timesfm-voynich`.

**Resultado: `FAIL_STRICT_PAIR_COHERENCE`.** Existe una asociación descriptiva entre los pares de hojas físicamente conjuntas y sus rasgos textuales. La ventaja léxica no supera todos los controles fijados. TimesFM detecta una asociación semejante, pero la media de los rasgos de la página fuente obtiene menor error y mejor rango. Traducción: `NOT_RUN`.

## Pregunta y separación de afirmaciones

El [ensayo de orden anterior](28_resultado_singulion_q13.md) dio `FAIL_ORDER`: la secuencia atribuida a Layfield–Davis no fue excepcional entre las 120 permutaciones de los cinco bifolios. El presente seguimiento pregunta algo distinto: si las dos hojas de cada bifolio se parecen más que parejas alternativas. No optimiza un orden de lectura.

El protocolo se publicó antes del primer cálculo de este seguimiento en [`f7699ad8`](https://github.com/MedinaParra/Voynich/commit/f7699ad8be47917ddbf833e49a7eb46fefc1ec1f). Código de análisis y workflow: [`7d22db08`](https://github.com/MedinaParra/Voynich/commit/7d22db0830a51fc9b0452c070ac2f3e53f258684). Q13 y el corpus ya se habían inspeccionado; esto no es una reserva prospectiva de manuscrito desconocido.

## Diseño fijado

- Corpus ZL EVA v3b: commit externo `47e6a77dc9d5cd570c375f4aff710fa4a0567278`; blob `2a4533ab9bdfa85db9bad602d590978953055df1`; SHA256 `bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc`.
- Pares físicos: `75|84`, `76|83`, `77|82`, `78|81`, `79|80`. Se verificó que ambas caras de cada hoja comparten los metadatos de cuaderno y bifolio previstos. Las veinte páginas tienen `L=B`, `H=2` y `Q=M`; estos metadatos no entran como rasgos para puntuar parejas.
- Primaria: coseno TF–IDF de tokens, agregando recto y verso por hoja. IDF y vocabulario aprendidos en 89 hojas externas a Q13. Sólo fragmentos EVA literales de loci de párrafo; signos inciertos y anotaciones se descartan. Coma como separación es primaria; unirla es una sensibilidad fijada.
- Referencias exhaustivas: los 945 emparejamientos perfectos de diez hojas, y los 120 que conectan exclusivamente una hoja de 75–79 con otra de 80–84. Incluyen el observado. Se informa la cola inclusiva con tolerancia `1e-12`.
- Control residual: OLS sobre las 45 aristas posibles con intercepto, coseno de trigramas de caracteres, diferencia absoluta de log-longitud y cuadrado de distancia foliar. El ajuste no recibe etiquetas de pareja física.
- Robustez: vistas de recto y verso, y cinco análisis retirando un par físico. Se exigió ventaja positiva sobre ambas medias de referencia en todos esos casos.
- Regla estricta: ambas políticas de coma deben tener `p≤0,05` en las dos referencias, tanto en la primaria como en la residual, además de las robusteces positivas. Las métricas secundarias no pueden rescatar un fallo.

## Resultados léxicos

| Política de coma | Métrica | Observado | Media de 945 | Rango / 945 | p / 945 | Rango / 120 | p / 120 |
|---|---|---:|---:|---:|---:|---:|---:|
| Separar | TF–IDF | 0,743118 | 0,670632 | 3 | 0,003175 | 2 | 0,016667 |
| Separar | TF–IDF residual | 0,025398 | ≈0 | 58 | 0,061376 | 14 | 0,116667 |
| Unir | TF–IDF | 0,722239 | 0,644247 | 3 | 0,003175 | 1 | 0,008333 |
| Unir | TF–IDF residual | 0,031827 | ≈0 | 47 | 0,049735 | 7 | 0,058333 |

Ambas vistas de cara y los cinco análisis de retirada conservan ventajas positivas en las dos políticas. El criterio fracasa por los controles residuales: dos puertas en separar y una en unir. No se cambia el umbral para aceptar los valores cercanos a 0,05.

La señal de caracteres también es marcada: trigramas quedan terceros de 945 en ambas políticas; Jensen–Shannon de caracteres sitúa los pares físicos primeros de 945 y primeros de 120. Son diagnósticos secundarios, no otros intentos de obtener un resultado positivo.

La cobertura del vocabulario externo va aproximadamente de 86,6% a 91,8% de tokens por hoja en separar y de 83,0% a 88,2% en unir. Los tokens fuera de vocabulario se omiten de los vectores, por lo que el resultado no describe exhaustivamente todas las formas de Q13.

## TimesFM y los predictores sencillos

Se ejecutó `google/timesfm-2.5-200m-pytorch` con paquete `timesfm[torch]==3.0.2`, contexto máximo 64, horizonte 4 y semilla 20261007. Usa exactamente los diez rasgos y la limpieza del ensayo Q13 previo. Las varianzas se calculan fuera de Q13. Cada página fuente genera una predicción antes de puntuar emparejamientos. La puntuación de dos hojas promedia ocho comparaciones dirigidas entre sus caras; excluye transiciones dentro de una misma hoja.

| Predictor o diagnóstico | Error observado, menor mejor | Rango / 945 | p / 945 | Rango / 120 | p / 120 |
|---|---:|---:|---:|---:|---:|
| TimesFM, diez rasgos | 1,234100 | 5 | 0,005291 | 2 | 0,016667 |
| TimesFM, sin conteo de tokens | 1,231166 | 5 | 0,005291 | 2 | 0,016667 |
| Última fila de la fuente | 2,186653 | 240 | 0,253968 | 13 | 0,108333 |
| Media de filas de la fuente | 0,974975 | 3 | 0,003175 | 1 | 0,008333 |

TimesFM tiene **26,58% más error** que la media de la página fuente en los pares físicos, aunque mejora frente a repetir la última fila. La asociación sobrevive al retirar conteo de tokens. Esto favorece una interpretación de semejanza estadística entre hojas; esta ejecución no demuestra que el modelo grande añada capacidad de reconstrucción frente al promedio sencillo. Son diagnósticos sobre el mismo Q13, sin corrección para elegir retrospectivamente un ganador.

## Qué permiten y qué no permiten concluir los controles

Hay evidencia descriptiva de que la hoja conjunta aporta una asociación textual que la comparación exclusiva de órdenes había mezclado con otro efecto. No hay evidencia suficiente, bajo la regla fijada, para atribuirle una componente léxica adicional que sobreviva a todos los controles.

El coseno de trigramas puede recoger estilo, patrones de producción **y contenido léxico real**. Descontarlo puede retirar señal de interés; el fallo residual no prueba ausencia de contenido o estructura. El pequeño tamaño de Q13 también limita la potencia. La regresión no identifica causalmente una explicación.

Las referencias exactas representan asignaciones intercambiables de pares de hojas; la encuadernación histórica no fue un experimento aleatorizado. Restringir mitades, mano y Currier no elimina posibles diferencias de dibujos, distribución espacial, abreviación o sesiones de producción. Recto/verso y las retiradas comparten hojas: no son réplicas independientes.

La semejanza física es compatible con varias explicaciones, incluida producción por bloques sin semántica demostrada. No identifica una lengua, no traduce palabras, no recupera una secuencia única y no valida por sí sola la hipótesis histórica de lectura como singuliones. La novedad del enfoque no está establecida.

## Verificación y reproducción

[GitHub Actions 37657459441](https://github.com/MedinaParra/Voynich/actions/runs/37657459441), job `112916110413`, terminó `success` sobre el código `7d22db08`. Pasaron los 16 controles científicos. El estado científico negativo es distinto del éxito de ejecución.

Se descargó el artefacto completo `11499366721`; su ZIP coincide con el digest de GitHub. La salida original coincide con el SHA256 del log. La comparación local/CI de **toda** la sección léxica verificó 12.224 valores flotantes y 21.394 valores exactos; diferencia máxima `5,55e-16`. Se reprodujeron 11.400 errores por rasgo desde las predicciones archivadas, 2.835 registros de emparejamiento, 16.065 puntuaciones y 34 resúmenes exactos. No se afirma una segunda inferencia local de TimesFM.

- Original CI SHA256: `79e6cc2a7701455db0d7a7ee48fa79e3f942da4e38b50163c197861083ad798a`.
- JSON compacto publicado SHA256: `c28654c1b500d4bf665800e72cdd945dd8cacdee15760a4b1fe7c3f5aad13920`; mismo contenido JSON, distinto formato de espacios.
- Python local 3.12.14; CI 3.12.15; NumPy 2.3.5 en ambas ejecuciones.
- Se fijaron identificador de modelo y versión de TimesFM. No se archivó la revisión de Hugging Face ni el hash de cada archivo de pesos; una descarga futura puede diferir. Las predicciones y sus entradas completas quedan archivadas para reproducir las puntuaciones.

```bash
pip install 'numpy==2.3.5'
python research_gpt6/code/test_q13_matching_control.py
python research_gpt6/code/q13_matching_control.py \
  --corpus /ruta/voynich_eva.txt \
  --plan research_gpt6/data/q13_matching_plan.json \
  --out /tmp/q13_lexical.json
python research_gpt6/code/audit_q13_matching_result.py \
  --result research_gpt6/results/q13_matching_result.json
# Para repetir inferencia: instalar 'timesfm[torch]==3.0.2' y añadir --timesfm.
```

Archivos: [protocolo](data/q13_matching_plan.json), [análisis](code/q13_matching_control.py), [harness](code/test_q13_matching_control.py), [replay sin pesos](code/audit_q13_matching_result.py), [salida completa](results/q13_matching_result.json), [auditoría](results/q13_matching_ci_audit.json) y [controles](results/q13_matching_checks.json).

## Fuentes físicas y límite de verificación

Los pares se verifican contra `$B` del corpus congelado. La [explicación directa de Lisa Fagin Davis](https://www.voynich.ninja/thread-5186.html) confirma ejemplos `75|84` y `78|81` y distingue caras interiores/exteriores. El artículo *Singulion Structure and the Voynich Manuscript*, DOI [10.4000/16k0a](https://doi.org/10.4000/16k0a), está en [Digital Medievalist](https://journals.openedition.org/digitalmedievalist/2331); su página devolvió un control Anubis, por lo que no se presenta la tabla íntegra del artículo como verificada. La prueba aquí no depende de su secuencia hipotética.

El siguiente contraste útil requiere otra transcripción y otro cuaderno, con mapeo físico verificable y controles de rasgos fijados antes del cálculo. Buscar más órdenes óptimos en Q13 no resuelve la limitación principal.

## Réplica posterior fuera de Q13

El [experimento 45](45_conjoint_leaf_replication.md) aplicó los controles a grupos seleccionados por metadatos en Q1, Q3 y un subconjunto de Q20. El parecido bruto pasó el contraste conjunto exacto; la componente residual y varias robusteces no pasaron. En Q20 la media de la fuente volvió a superar TimesFM. Estado: `FAIL_REPLICATION_PANEL`; este seguimiento no modifica el resultado estricto de Q13 ni aporta una traducción.

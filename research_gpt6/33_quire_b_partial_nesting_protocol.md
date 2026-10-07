# 33. Protocolo congelado — Quire B parcial

Fecha: 2026-10-07

## Objetivo

Probar si el modelo de continuidad de borde congelado en Quire C y luego controlado por Currier/mano en Quire F recupera el **orden relativo de anidamiento de los tres bifolios supervivientes** del Quire B, que no fue incluido en los barridos de anidamiento A/C/D/E/F/G.

Este experimento no descifra el manuscrito, no estima semántica y no prueba por sí solo el orden histórico original.

## Estado previo y separación respecto de análisis anteriores

El Quire B apareció antes en el experimento de recuperación de **pares físicos** con los bifolios supervivientes `9|16`, `10|15`, `11|14`. Ese experimento no probó su orden outer→inner. Los barridos posteriores de anidamiento excluyeron B porque falta el bifolio central esperado `12|13`.

Por lo tanto, esta prueba usa texto ya perteneciente al programa general, pero evalúa un blanco distinto y hasta ahora no puntuado: el orden relativo entre los tres bifolios supervivientes. Se clasifica como **extensión predictiva preregistrada**, no como réplica independiente de manuscrito.

## Datos congelados

- ZL3b: misma fuente Voynich EVA fijada en el repositorio de investigación, commit fuente `47e6a77dc9d5cd570c375f4aff710fa4a0567278`.
- IT2a: misma transcripción Takahashi independiente ya fijada por SHA-256 en `order_quire_c_nesting.py`.
- Metadata de mano Davis-H y Currier-L: sólo de cabeceras ZL ya usadas por el control anterior; se reutilizan como etiquetas nuisance para ambas transcripciones.
- Bifolios físicos supervivientes, en orden encuadernado actual: `9|16`, `10|15`, `11|14`.
- El bifolio central `12|13` se trata como **ausente/no observado**. No se inventa su contenido.

## Espacio de hipótesis

Se enumeran exactamente los `3! = 6` órdenes outer→inner de los tres bifolios supervivientes.

Para un candidato `(a1|b1, a2|b2, a3|b3)` la secuencia completa habría contenido un bifolio central ausente entre `a3` y `b3`. Por ello sólo se puntúan las cuatro transiciones observables que no atraviesan el gap:

- `a1v → a2r`
- `a2v → a3r`
- `b3v → b2r`
- `b2v → b1r`

**Se prohíbe puntuar `a3v → b3r`**, porque en el cuaderno completo esa interfaz estaría interrumpida por el bifolio central ausente.

## Modelo congelado

Sin retuning:

- mismas tres componentes del modelo Quire C: TF-IDF de tokens, TF-IDF de caracteres 3–5 y Jaccard de tokens;
- z-normalización por componente y promedio simple;
- mismas ventanas de borde: 25, 50, 100, 200 tokens y página completa;
- misma orientación interna de cada bifolio;
- mismos tres niveles de control del barrido más reciente:
  1. `raw`;
  2. residual por clase ordenada Currier-L origen→destino;
  3. residual por clase ordenada exacta `(Davis-H, Currier-L)` origen→destino.

Ningún parámetro, peso, ventana ni metadata se escogerá a partir del resultado de B.

## Blanco primario

El blanco primario es el orden actual de supervivientes:

`9|16 → 10|15 → 11|14`

La evaluación primaria usa el control más exigente ya congelado: `hand_currier_residual`, por separado en ZL3b e IT2a, sobre las cinco ventanas.

## Regla de decisión congelada

Se define **PASS_PREDICTIVE_EXPLORATORY** sólo si se cumplen simultáneamente:

1. mediana del rango del orden actual `<= 2` en ZL3b bajo `hand_currier_residual`;
2. mediana del rango `<= 2` en IT2a bajo el mismo control;
3. el orden actual es top-1 en al menos `3/5` ventanas de ZL3b;
4. es top-1 en al menos `3/5` ventanas de IT2a;
5. el peor rango en cada transcripción es `<= 4`.

Se define **FAIL_PREDICTIVE** si ocurre cualquiera de estas condiciones fuertes:

- mediana de rango `>= 4` en cualquiera de las dos transcripciones; o
- cero ventanas top-1 en ambas transcripciones conjuntamente.

Cualquier otro patrón será **INCONCLUSIVE**.

Estas reglas son operacionales, no una prueba exacta a alfa 0,05. Con sólo seis órdenes posibles, incluso rango 1 tiene probabilidad exacta `1/6` bajo un nulo uniforme; las cinco ventanas están correlacionadas y no se contarán como réplicas independientes.

## Resultados secundarios obligatorios

Se reportarán, sin cambiar la decisión primaria:

- rangos bajo `raw`, `currier_residual` y `hand_currier_residual`;
- mejor orden por ventana y transcripción;
- score y margen respecto del segundo lugar;
- firmas metadata por folio;
- auditoría del parser;
- hashes/provenance del workflow y fuentes.

## Falsabilidad y techo de interpretación

Un FAIL_PREDICTIVE sería evidencia contra la generalización del modelo de continuidad de anidamiento a este quire parcial. Un PASS sólo apoyaría que el orden relativo actual de los tres bifolios supervivientes es compatible de forma robusta con el modelo textual congelado.

**Techo:** compatibilidad predictiva de orden físico relativo en un quire parcial. No significa traducción, significado recuperado, orden histórico demostrado ni descifrado.
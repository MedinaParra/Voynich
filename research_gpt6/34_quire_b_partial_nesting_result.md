# 34. Resultado — Quire B parcial

Fecha: 2026-10-07

## Estado

**PASS_PREDICTIVE_EXPLORATORY**, aplicando literalmente la regla congelada en `33_quire_b_partial_nesting_protocol.md`.

Workflow: `Voynich Quire B partial nesting`, run `37634555562`, conclusión mecánica `success`.

Commit de resultado: `2b2963fdeef968838ff7f02ed32900d005f8cc8e`.

## Resultado primario

Orden físico relativo evaluado:

`9|16 → 10|15 → 11|14`

El bifolio central `12|13` se dejó como gap y **no** se puntuó la interfaz `a3→b3`.

Bajo el control primario `hand_currier_residual`:

- ZL3b: rangos por ventana `[2, 3, 1, 1, 1]`, mediana `1`, top-1 `3/5`, peor rango `3`.
- IT2a: rangos `[3, 1, 1, 1, 1]`, mediana `1`, top-1 `4/5`, peor rango `3`.

Se cumplen los cinco criterios preregistrados de PASS.

## Observación importante sobre el control de metadata

Los seis folios observados de B tienen la misma firma disponible: Davis-H=`1`, Currier-L=`A`. Por ello sólo existe una clase de transición y los resultados `raw`, `currier_residual` y `hand_currier_residual` son numéricamente equivalentes.

Esto **no cambia la clasificación preregistrada**, pero sí limita su interpretación: en Quire B el control de metadata no tiene poder para separar continuidad textual de mano/Currier porque no hay variación interna de esas etiquetas.

## Qué sí muestra

El orden actual de los tres bifolios supervivientes es estable con ventanas medias/largas y se reproduce en dos transcripciones. En ZL3b es top-1 desde 100 tokens; en IT2a desde 50 tokens.

## Qué no muestra

Hay sólo `3! = 6` órdenes candidatos. Incluso rango 1 corresponde a `1/6` bajo un nulo uniforme de rango, de modo que este resultado no constituye por sí solo una prueba exacta a alfa 0,05. Las cinco ventanas son correlacionadas y ZL3b/IT2a son transcripciones del mismo manuscrito.

No demuestra significado, idioma, traducción, ni que la encuadernación actual sea necesariamente el orden histórico original.

## Próximo control adversarial recomendado

La señal debe demostrar **especificidad de interfaz de lectura**. El siguiente test debe comparar la interfaz físicamente correcta `cola(verso origen) → cabeza(recto destino)` contra interfaces deliberadamente incorrectas (`cabeza→cabeza`, `cola→cola`, `cabeza→cola`) sin retuning. Si las interfaces incorrectas recuperan los órdenes físicos igual de bien, la lectura de “continuidad de borde” se debilita sustancialmente.
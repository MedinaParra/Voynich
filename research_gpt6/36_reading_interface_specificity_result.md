# 36. Resultado — control de especificidad de interfaz

Fecha: 2026-10-07

## Estado

**FAIL_EDGE_SPECIFIC** según la regla congelada en `35_reading_interface_specificity_protocol.md`.

Workflow: `Voynich reading-interface specificity`, run `37635142234`, conclusión mecánica `success`.

Commit automático de resultados: `97328a47885b294594871c977a121e5cef887db5`.

## Resultado primario raw

La interfaz físicamente motivada TH = `tail(verso origen) → head(recto destino)` **no** fue específicamente superior a las tres interfaces incorrectas.

Mediana global del rango normalizado entre siete quires:

- TH correcto: `0.13043`;
- HH control: `0.13043`;
- TT control: `0.17391`;
- HT control: `0.28261`.

TH venció al **mejor** control incorrecto en sólo `1/7` quires. La condición preregistrada exigía `>=6/7`, por lo que el resultado es FAIL.

Contra el mejor control incorrecto: 1 victoria, 0 derrotas y 6 empates; test de signos unilateral secundario `p=0.5`.

## Resultado secundario con residual exacto Davis-H + Currier-L

También **FAIL_EDGE_SPECIFIC**.

Medianas globales:

- TH: `0.06522`;
- HH: `0.13043`;
- TT: `0.06522`;
- HT: `0.04348`.

TH volvió a vencer al mejor control incorrecto en sólo `1/7` quires. Contra el mejor control: 1 victoria, 2 derrotas y 4 empates; `p=0.875` unilateral secundario.

## Hallazgo central

En varios quires el ranking del orden físico es prácticamente idéntico para TH y los bordes incorrectos. Ejemplos raw:

- C: los cuatro modos tienen mediana normalizada `0.0`;
- D: los cuatro modos `0.56522`;
- G: los cuatro modos `0.78261`;
- B parcial: los cuatro modos `0.0`.

Por tanto, la señal que recuperaba algunos órdenes físicos **no está localizada de forma convincente en la interfaz verso→recto que motivó la hipótesis de continuidad de lectura**.

## Consecuencia científica

Esto obliga a rebajar la interpretación de los experimentos de anidamiento previos. El score puede estar capturando similitud textual más global entre folios, estructura de quire, sección, escriba o distribución léxica, en vez de continuidad específica de lectura en el borde correcto.

El PASS exploratorio de Quire B permanece como resultado operacional de su protocolo, pero **ya no puede presentarse como evidencia de continuidad de borde específica**. Lo mismo aplica a los buenos rangos de Quire C y otros quires hasta superar un control más discriminante.

Este FAIL no elimina la evidencia de que el texto posee estructura ni la recuperación previa de pares físicos; sí contradice la interpretación fuerte del modelo de orden como detector específico de transiciones `verso→recto`.

## Próxima bifurcación recomendada

No conviene seguir optimizando órdenes con este score. El siguiente paso debe separar explícitamente:

1. **similitud global de folio/quire**, que los controles incorrectos parecen conservar; y
2. **información local de borde**, que debería desaparecer al usar regiones internas o bordes equivocados.

Una prueba nueva debe residualizar primero la similitud global de página y recién después preguntar si queda exceso específico en TH. Si no queda, la rama de reconstrucción de orden por borde debe cerrarse como negativa.
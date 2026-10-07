# 38. Resultado — exceso local de borde tras retirar similitud global

Fecha: 2026-10-07

## Estado

**FAIL_LOCAL_EDGE_SPECIFIC**, aplicando literalmente el protocolo congelado `37_global_similarity_residual_protocol.md`.

Workflow: `Voynich global-similarity residual edge`, run `37636746484`, conclusión mecánica `success`.

Commit automático de resultados: `e631aa03265220d1df7903c3af274b59fd8f4774`.

## Resultado primario

Después de retirar por regresión lineal la similitud global `verso(origen) ↔ recto(destino)` para todos los pares dirigidos de cada quire, la interfaz físicamente motivada TH no supera a los controles incorrectos.

Medianas globales de rango normalizado:

- TH correcto: `0.28261`
- HH: `0.43478`
- TT: `0.28261`
- HT: `0.32609`

Pero el criterio preregistrado era por quire, contra el **mejor** control incorrecto. Resultado:

- TH gana: `0/7`
- TH pierde: `6/7`
- empate: `1/7`
- test de signos unilateral secundario contra `best_wrong`: `p = 1.0`

Por protocolo, esto es un FAIL inequívoco.

## Resultado secundario con metadata Davis-H + Currier-L

También **FAIL_LOCAL_EDGE_SPECIFIC**.

- TH gana al mejor control: `0/7`
- pierde `6/7`
- empata `1/7`
- `p = 1.0` contra `best_wrong`

Las medianas globales secundarias fueron TH `0.32609`, HH `0.32609`, TT `0.32609` y HT `0.26087`.

## Consecuencia metodológica

Se cierra para este programa la interpretación del score actual como detector específico de continuidad de lectura localizada en `tail(verso) → head(recto)`.

Los experimentos previos de ordenamiento y el PASS operacional de Quire B permanecen reproducibles como resultados de sus protocolos, pero **no deben interpretarse como evidencia de una señal local de borde**. El control de interfaz incorrecta ya había fallado y la residualización de similitud global no rescata la hipótesis; de hecho, TH no vence al mejor control incorrecto en ningún quire.

Lo que sí puede conservarse de esta rama es evidencia de estructura textual global y, por separado, la señal previa de emparejamiento físico de bifolios. No se seguirá optimizando órdenes con esta métrica de borde salvo aparición de evidencia independiente que justifique un mecanismo nuevo.

## Próximo frente de investigación

La ruta de mayor valor vuelve a las pruebas que pueden acercar el programa desde estructura hacia anclaje funcional/semántico sin depender de este score de orden: réplicas y controles de `lexical-anchor`, `label-object` y Ls/Lz con transcripción o evidencia independiente. Antes de abrir experimentos nuevos deben auditarse las ramas existentes para evitar duplicar trabajo y respetar preregistros previos.
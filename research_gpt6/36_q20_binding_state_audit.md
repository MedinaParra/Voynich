# 36. Q20 — auditoría exacta de estados de encuadernación

Fecha: 2026-10-07
Estado: **resultado ejecutado; distingue orden de producción de estado físico encuadernado**

## Objetivo

Separar dos preguntas que se estaban mezclando:

1. qué orden textual/de producción sugieren los datos de Voynichese;
2. qué anidamientos físicos históricos son compatibles con transferencias de pintura y wormholes.

Se enumeraron exhaustivamente los `6! = 720` anidamientos exterior→interior de los seis bifolios supervivientes de Q20, manteniendo fija la orientación interna de cada bifolio.

## Restricciones de pintura

Se trataron como contactos directos de páginas enfrentadas las tres transferencias publicadas más claras:

- `f104v → f105r`;
- `f114v → f115r`;
- `f115v → f116r`.

Sólo **24/720** anidamientos satisfacen las tres simultáneamente.

El anidamiento actual pertenece a ese conjunto y satisface 3/3.

## Restricción de wormholes antiguos

Siguiendo la interpretación publicada por Nick Pelling de las observaciones de Wladimir Dulov, el segundo patrón de wormholes se modeló como:

- `104|115` exterior;
- `105|114` inmediatamente dentro.

Hay **24/720** anidamientos compatibles con esa condición.

La intersección entre esos 24 estados y los 24 estados compatibles con las tres transferencias directas de pintura es:

**0/720**.

Por tanto, bajo esas interpretaciones, ninguna configuración física única puede explicar a la vez ambas clases de evidencia.

## Estado tardío / final

El patrón de agujeros que decrece desde `f116` hacia `f115` y `f114` se modeló como los tres bifolios exteriores:

`103|116 → 104|115 → 105|114`.

Eso deja **6/720** estados posibles, y los seis están dentro del conjunto compatible con las tres transferencias de pintura.

Así, pintura + wormholes tardíos son coherentes entre sí y con el estado actual; los wormholes antiguos exigen otro estado.

## Complejidad mínima de la transición

La distancia Kendall mínima entre un estado compatible con los wormholes antiguos y uno compatible con las transferencias es **2 inversiones**.

Ejemplo mínimo:

estado antiguo compatible con wormholes:

`104|115 → 105|114 → 103|116 → 106|113 → 107|112 → 108|111`

estado compatible con pintura / actual:

`103|116 → 104|115 → 105|114 → 106|113 → 107|112 → 108|111`

La diferencia puede explicarse simplemente trasladando `103|116` desde detrás de `104|115` + `105|114` hacia el exterior.

## Consecuencia para nuestra reconstrucción textual

Nuestro candidato textual/de producción, omitiendo el bifolio perdido, es:

`105|114 → 106|113 → 107|112 → 104|115 → 108|111 → 103|116`

Si se interpretara erróneamente como un anidamiento físico exterior→interior, satisfaría **0/3** transferencias directas de pintura.

Esto no lo refuta, porque nunca quedó demostrado que la señal textual reconstruya el estado de encuadernación. Al contrario, obliga a mantener una separación estricta:

- **orden textual / proximidad de producción**;
- **orden físico de un estado de encuadernación**;
- **orden de lectura histórico**.

## Conclusión

Bajo las restricciones publicadas utilizadas aquí, Q20 requiere **al menos dos estados físicos de encuadernación**. Por eso las transferencias de pintura no pueden usarse sin datación para refutar un orden textual anterior.

Este resultado fortalece la metodología, no el desciframiento: confirma que una única permutación no puede representar toda la historia codicológica de Q20.

## Archivos reproducibles

- `research_gpt6/code/q20_binding_state_audit.py`
- `research_gpt6/results/q20_binding_state_audit.json`

## Guardrails

- La interpretación de los wormholes es secundaria, tomada de Pelling/Dulov; no se hizo inspección física directa del manuscrito.
- Una transferencia de pintura sólo fecha una relación de contacto si se conoce cuándo se aplicó/se transfirió el pigmento.
- El bifolio perdido `109|110` se omite de esta enumeración de seis supervivientes.
- Este experimento no demuestra el orden original ni descifra el texto.

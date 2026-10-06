# 26. Experimento de orden singulion — protocolo congelado

Fecha: 2026-10-06

## Pregunta

¿La evidencia predictiva/estructural del texto aumenta cuando se usa una secuencia de bifolios/singuliones propuesta independientemente de la encuadernación actual?

## Corrección metodológica importante

El piloto `25_prediccion_controlada_piloto.md` mide dependencias **dentro de línea**. Reordenar folios no puede cambiar esa métrica. Por tanto, no es válido presentar una reejecución de `controlled_edge.py` con distinto orden como prueba de la hipótesis de Layfield–Fagin Davis.

El experimento de orden debe medir transiciones **entre páginas/bifolios**, manteniendo congelada la representación del texto y sin reajustar parámetros después de ver resultados.

## Hipótesis

- H0: la secuencia propuesta no mejora una métrica de continuidad fuera de muestra respecto del orden encuadernado ni respecto de permutaciones aleatorias compatibles.
- H1: la secuencia propuesta mejora la continuidad fuera de muestra y queda en la cola superior de una distribución nula por permutación.

## Fuentes fijadas

- Corpus primario: `cesarjz/Voynich`, commit `47e6a77dc9d5cd570c375f4aff710fa4a0567278`, `corpus/voynich_eva.txt`, blob `2a4533ab9bdfa85db9bad602d590978953055df1`.
- Propuesta codicológica: Colin Layfield y Lisa Fagin Davis, *Singulion Structure and the Voynich Manuscript*, Digital Medievalist 19 (2026), DOI 10.4000/16k0a.
- Recurso secundario de colación singulion: QuantumLynx Research, actualizado 2026-07-16. Se usará solo tras verificar su mapeo contra la fuente primaria; el propio recurso declara QA mínimo.

## Alcance pre-registrado

1. Separar análisis de Q13 y Q20, porque los autores solo proponen secuencias hipotéticas allí; no extrapolar una secuencia al Herbal.
2. Construir unidades página y bifolio a partir de metadatos codicológicos verificados.
3. Representación primaria: distribución de tokens EVA por página con vocabulario aprendido solo en train; variantes secundarias: bordes inicial/final y n-gramas de caracteres.
4. Comparar:
   - orden encuadernado actual;
   - orden singulion hipotético publicado para Q13/Q20;
   - 9.999 permutaciones de bifolios que preservan las páginas internas de cada bifolio;
   - control adicional: secuencia optimizada en train, evaluada sin reajuste en holdout.
5. Métricas primarias: log-probabilidad predictiva de la página siguiente y similitud coseno TF-IDF entre unidades adyacentes. Métricas secundarias: Jaccard de tipos, repetición/casi-repetición y transición de distribuciones de caracteres de borde.
6. Validación: ninguna secuencia se optimiza usando el holdout. Reportar efecto, intervalo bootstrap por unidad física y p Monte Carlo.
7. Ablaciones: Currier A/B, mano, longitud de página y quire. No interpretar una mejora como semántica hasta que sobreviva esos controles.

## Criterio de decisión

`PASS` para la afirmación estrecha “el orden propuesto contiene señal de continuidad adicional” solo si la secuencia publicada supera al orden actual y al 95% de permutaciones en la métrica primaria, y el signo se mantiene en el holdout. En otro caso: `FAIL` para esa afirmación. Datos/mapeo incompletos: `BLOCKED`.

## Estado de ejecución al congelar el protocolo

- Verificación del corpus y del blob usado por nuestros scripts previos: PASS.
- Verificación de que el piloto 25 es invariante al orden de folios por construcción: PASS (la función genera pares únicamente dentro de cada línea).
- Confirmación bibliográfica de que Layfield–Fagin Davis proponen secuencias hipotéticas solo para Q13 y Q20: PASS.
- Obtención automática del paquete QuantumLynx: BLOCKED, porque la página exige solicitud por email y entrega un enlace temporal.
- Extracción de la tabla/secuencia exacta Q13/Q20 desde una fuente primaria accesible a la ejecución: BLOCKED en esta sesión; no se inventa el orden.
- Comparación numérica current-vs-singulion: NOT_RUN hasta resolver el mapeo exacto publicado.

## Próximo paso ejecutable

Incorporar al repositorio la tabla exacta Q13/Q20 desde el artículo o desde el paquete singulion, verificarla contra los folios físicos (por ejemplo, Q13 contiene el bifolio 78|81 y el bifolio exterior 75|84), calcular los cuatro brazos del benchmark y registrar JSON con semillas, hashes y resultados.
# 27. Heurística adversarial para orden singulion

Fecha: 2026-10-06
Estado: diseño ampliado; no confundir con resultado numérico.

## Hallazgo que desbloquea Q13

Una reproducción independiente publicada en Voynich Ninja informa explícitamente la secuencia atribuida a Layfield–Davis para Q13:

1. 77|82
2. 78|81
3. 75|84
4. 76|83
5. 79|80

La misma reproducción, usando ZL3b y Held–Karp, obtiene:

1. 79|80
2. 78|81
3. 75|84
4. 76|83
5. 77|82

Esto es especialmente útil como prueba adversarial: las tres unidades centrales coinciden y solo cambian los extremos. No se debe interpretar como validación primaria hasta cotejar la tabla exacta del artículo.

## Nueva estrategia

En vez de preguntar únicamente «¿qué orden maximiza similitud?», separar cinco preguntas:

1. **Núcleo estable**: ¿qué adyacencias sobreviven a cambios de transcripción, métrica y algoritmo?
2. **Extremos**: ¿los bifolios candidatos a inicio/final muestran asimetría textual medible?
3. **Dirección**: ¿A→B predice mejor que B→A después de controlar frecuencia y longitud?
4. **Topología**: ¿los datos soportan realmente una cadena única o solo un pequeño grafo de vecindades?
5. **Generalización**: ¿las aristas elegidas en train conservan ventaja en holdout?

## Torneo heurístico preregistrado

Para cada bifolio construir vectores independientes de:
- frecuencia TF-IDF de tokens;
- n-gramas de caracteres EVA;
- prefijos y sufijos;
- distribución de token inicial/final de línea;
- posición de párrafo;
- entropía local y longitud.

Construir una matriz dirigida de compatibilidad A→B con componentes normalizados. No fijar pesos después de mirar Q13/Q20. Los pesos se aprenden exclusivamente en train o se exploran como análisis de sensibilidad.

Comparar:
- orden encuadernado;
- orden Layfield–Davis;
- solución Held–Karp independiente;
- beam search top-k;
- 9.999 permutaciones físicas válidas;
- controles con páginas barajadas dentro de restricciones equivalentes.

## Técnica especial: consenso de aristas

No exigir inicialmente una secuencia total. Ejecutar múltiples representaciones y construir un grafo de consenso. Una arista A→B se considera robusta si aparece repetidamente entre las mejores soluciones bajo perturbaciones bootstrap, transcripción alternativa y ablaciones de rasgos.

Esta formulación evita sobreinterpretar un único óptimo del TSP/Held–Karp y permite detectar un «núcleo» real aunque los extremos sean ambiguos.

## Técnica especial: prueba de flecha temporal

Para cada par candidato A,B medir score(A→B)-score(B→A). Evaluar contra nulls que preserven:
- frecuencia marginal;
- longitud de página;
- Currier A/B;
- sección/quire;
- estructura interna del bifolio.

Una dirección solo se acepta si mantiene signo en holdout y en la mayoría de bootstrap.

## Técnica especial: estabilidad leave-one-feature-out

Repetir el ranking eliminando de a una familia de rasgos. Si una arista desaparece al retirar un único rasgo, etiquetarla FRAGILE. Si sobrevive, STABLE. Esto permite distinguir continuidad genuinamente multicanal de un artefacto de vocabulario.

## Técnica especial: contraste con generadores

Aplicar el mismo torneo a controles sintéticos que preserven unigramas/bigramas y a un generador de autocopia local. El objetivo es medir si una supuesta reconstrucción de orden puede emerger artificialmente de mecanismos no semánticos.

## Criterios

- PASS_CORE: existe un subconjunto de aristas Q13/Q20 que supera 95% de nulls y sobrevive holdout + bootstrap + ablaciones.
- PASS_ORDER: además, una secuencia completa supera al orden encuadernado y al 95% de permutaciones sin ajuste post-hoc.
- FAIL_ORDER: no hay ventaja robusta de secuencia completa.
- FRAGILE: ventaja dependiente de una sola representación/transcripción.
- BLOCKED: falta mapeo físico o corpus verificable.

## Estado

- Q13: secuencia Layfield–Davis recuperada desde una fuente secundaria reproducible; VERIFICATION_PENDING contra artículo primario.
- Q13: existe una solución Held–Karp independiente que coincide en el núcleo central y cambia extremos; CANDIDATE_SIGNAL, no PASS.
- Q20: una reproducción independiente declara coincidencia con Layfield–Davis, pero la secuencia explícita aún no ha sido extraída; BLOCKED_PARTIAL.
- Benchmark numérico propio: NOT_RUN.

## Hipótesis nueva y falsable

La señal más robusta puede no ser «un orden único correcto», sino un **grafo parcial de adyacencias físicas/textuales**. Si las aristas 78|81 → 75|84 → 76|83 (o sus orientaciones verificadas) sobreviven representaciones, transcripciones y nulls mientras los extremos fluctúan, eso apoyaría continuidad local sin afirmar más de lo que permiten los datos.

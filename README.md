# Voynich Research

Repositorio de trabajo para análisis reproducibles y críticos del manuscrito Voynich.

El objetivo inmediato es auditar resultados publicados, fijar fuentes y versiones, y registrar código y evidencia reproducible. Las conclusiones descriptivas se mantienen separadas de cualquier afirmación de desciframiento o interpretación semántica.

## Fuente inicial

La primera auditoría examina el repositorio público [cesarjz/Voynich](https://github.com/cesarjz/Voynich), fijado en el commit `47e6a77dc9d5cd570c375f4aff710fa4a0567278`. El análisis y los resultados se organizan bajo `research_gpt6/` en una rama de trabajo. [Estado del arte y evaluación de propuestas](research_gpt6/11_estado_del_arte.md), con [actualización crítica de octubre de 2026](research_gpt6/13_actualizacion_2026.md).

## Estado

Repositorio inicializado. La rama `main` contiene solamente este archivo de orientación; el trabajo de investigación se desarrolla en ramas separadas.

## Investigación ampliada

[Catálogo bibliográfico y cobertura](research_gpt6/14_catalogo_bibliografico.md): actas VOY2022 completas y nuevas fuentes de 2024–2026. [Experimento reproducible de dependencias de borde](research_gpt6/15_dependencias_de_borde.md): código, resultados y limitaciones; no se ha obtenido una traducción validada.

[Plan de descifrado elegido](research_gpt6/16_plan_descifrado.md) y [primera fase ejecutada](research_gpt6/17_resultado_plan_descifrado.md): reglas de enlace EVA generalizan a hojas y cuadernos reservados. Identificación de idioma y traducción pendientes.

[Filtro de mecanismos ejecutado](research_gpt6/19_resultados_mecanismos.md): generadores sin semántica y controles latinos sobre hojas reservadas; la MI de borde puede reproducirse sin traducir. Ningún control explica conjuntamente las seis métricas.

## Avance del 7 de octubre de 2026

[Reglas de prefijos y sufijos](research_gpt6/42_transformation_probe.md): 35 correspondencias propuestas, diez pares utilizables y 0/10 rótulos generados; el contraste semántico raíz/hoja sigue bloqueado.

[Enlace de bordes y copia local](research_gpt6/43_local_copy_mechanism.md): evaluación de tres generadores en 89 grupos de hoja y cinco particiones, separando tres estratos de mano/Currier. La copia mejora la predicción solo 0,00335–0,00419 bits por token; el texto generado sigue fallando en repeticiones, variantes y formas únicas. No hay un mecanismo con adecuación conjunta ni una traducción.

El protocolo se fijó antes de ajustar el modelo nuevo y se conservan las salidas, hashes y controles de fallo. El corpus ya había sido explorado: estas reservas no son validación semántica externa.

[GitHub Actions](https://github.com/MedinaParra/Voynich/actions/runs/37596432044) pasó los catorce controles del canal de copia y reprodujo el resumen numérico y las ganancias por partición. La [auditoría](research_gpt6/results/local_copy_ci_audit.json) delimita qué se verificó.

[Control exhaustivo de pares físicos en Q13](research_gpt6/44_q13_matching_control.md): los bifolios quedan terceros entre 945 emparejamientos en similitud léxica, pero fallan los controles residuales fijados. TimesFM también detecta semejanza; la media de la página fuente obtiene menor error. Resultado estricto `FAIL_STRICT_PAIR_COHERENCE`, traducción `NOT_RUN`. Se conserva la salida completa y su [auditoría de CI](research_gpt6/results/q13_matching_ci_audit.json).

[Réplica en Q1, Q3 y cuatro bifolios de Q20](research_gpt6/45_conjoint_leaf_replication.md): la asociación léxica bruta pasa el contraste conjunto, pero el control residual y algunas robusteces fallan (`FAIL_REPLICATION_PANEL`). TimesFM queda bloqueado en Q1/Q3 por el horizonte fijo; en el subconjunto de Q20 obtiene un 9,88% más de error que la media de la página fuente. Pasaron 29 controles y se conserva la [auditoría de la salida completa](research_gpt6/results/conjoint_replication_ci_audit.json). Traducción: `NOT_RUN`.

## Estado del arte al 14 de octubre de 2026

[Revisión crítica y herramientas emergentes](research_gpt6/46_estado_del_arte_2026_10_14.md), con [registro de 76 referencias y recursos](research_gpt6/data/estado_arte_2026_10_14_sources.json). Se distinguen artículos, preprints, propuestas independientes, versiones y acceso a las fuentes; la cobertura es selectiva, no exhaustiva.

La prioridad propuesta es contrastar la transcripción ZL con una anotación independiente, medir signos y separadores desde imágenes y probar modelos de escritura/cifrado con reglas globales y evaluación reservada. DINOv3/FINO, SAM 3, Kraken y descifrado restringido son candidatos de evaluación. Sus nuevas aplicaciones a Voynich están `NOT_RUN`; no se presenta una traducción validada.

## Ruta Kraken - piloto del 14 de octubre de 2026

En la rama `experiment/kraken-voynich`: [protocolo fijado](research_gpt6/47_kraken_pilot_protocol.md) y [resultado ejecutado](research_gpt6/48_kraken_pilot_result.md). Kraken 7.1 comparó segmentación neuronal y clásica en cuatro imágenes de Yale y dos resoluciones, con una transcripción independiente de Boxer y controles positivo/negativo.

Pasaron 16 controles de ejecución. El modelo neuronal produjo 120 segmentos frente a 53 filas de transcripción y falló el criterio fijado (`FAIL_COUNT_PROXY`). En el control con escritura conocida obtuvo F1 geométrico 0,8632. Se conserva el resultado completo, su auditoría y vistas de f1r/f1v. Hacen falta regiones y recortes alineados/revisados antes de medir reconocimiento de glifos; entrenamiento y traducción siguen `NOT_RUN`.

## Ruta Kraken: recuperación del 26 de octubre de 2026

[Primer reconocimiento evaluado](research_gpt6/50_kraken_stage2_result.md): ejecución completa de 40 épocas sobre 34 filas y evaluación en 27 filas de otra hoja. El error de unidades es 95,5651%, peor que el comparador por imagen (93,2761%). El ensamblado recupera el conteo, pero falla el criterio espacial a 1200 px. Ambos criterios científicos quedan FAIL; traducción NOT_RUN. Se conservan el modelo final, las salidas, tres intentos fallidos y una auditoría numérica de 2.207 comprobaciones sin discrepancias.

[Protocolo de calidad de recortes](research_gpt6/51_crop_quality_protocol.md): diagnóstico de repetición literal de posiciones entre recortes del conjunto ya explorado, fijado antes de medirlo. No constituye una nueva reserva confirmatoria ni un entrenamiento.

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

[Calidad de recortes y fuentes espaciales: resultado del 26 de octubre](research_gpt6/52_crop_quality_and_spatial_sources.md): el 63,67% de las posiciones oscuras analizadas aparece en varios recortes; seis controles sintéticos y 475 verificaciones contra los PNG originales pasan. Una auditoría adicional del archivo Voynichese cuenta 37.886 palabras en 225 folios y 33 cajas de ancho no positivo. Hay diferencias de encuadre y segmentación de palabras respecto de Boxer. La prioridad es corregir y revisar los datos antes de entrenar de nuevo. Registro de imágenes, nuevo entrenamiento y traducción: NOT_RUN.

[Reordenación digital parcial Q13/Q20 y copia de lectura](research_gpt6/54_reordering_result.md): se seleccionaron órdenes por bifolios usando líneas alternas y se comprobaron en las restantes. Q13 queda 32/120 (cola 0,2667), sin apoyo; el núcleo Q20, 6/24 (0,2500), descriptivo. La copia de lectura conserva 213 posiciones, cambia 32 y contiene 211 fotografías y dos avisos de cantos no disponibles. Tiene 219 páginas, índice reversible y marcadores. Ocho controles y 2.133 comprobaciones pasan; el orden histórico sigue UNRESOLVED y traducción NOT_RUN.

[Primer inventario de números y contexto](research_gpt6/55_numeral_context_inventory.md): 20 casos dirigidos, con imágenes y coordenadas, distinguen foliación, marcas de cuaderno, cifras 1-5 junto a signos en f49v y posibles numerales. Se documentan dos recuentos de 15 figuras de Aries y se cuentan las etiquetas de los 12 diagramas zodiacales; se conservan las excepciones de Piscis y Géminis. Las cifras de f49v no coinciden en general con el número de palabras de sus renglones. Los resultados son descriptivos, con antecedentes explícitos y sin una clave numérica o traducción validada. Incluye código y atlas de ocho páginas.

[Pruebas de hipótesis numéricas simples](research_gpt6/57_numeral_hypothesis_result.md), con [reglas publicadas antes del conteo](research_gpt6/56_numeral_hypothesis_protocol.md): la asociación 1-5 de f49v obtiene 0/11 coincidencias con cantidades de palabras en otros renglones completos y 0/2 en f76r; las sensibilidades se conservan. En 259 etiquetas zodiacales admitidas de 299, aparecen seis formas duplicadas dentro de cuatro signos. Los límites de coincidencia bajo cualquier reordenación contradicen una lista canónica 1-30 repetida entre signos. La estructura de 30 unidades sigue abierta; no se descartan otros usos numéricos ni se valida una traducción.

[Kraken retomado el 27 de octubre: extracción provisional y tres entrenamientos](research_gpt6/59_kraken_crop_repair_result.md): el comparador reproduce 95,5651 % de error; con nuevos recortes baja a 82,1173 % a 40 épocas y 73,8197 % a 200. La exclusividad de posiciones oscuras se impone sin perder los candidatos medidos, pero 54/61 filas tienen componentes señalados para revisión. Es desarrollo sobre las hojas 3/4 ya exploradas, sin validación experta ni nueva reserva independiente. Se preservan los tres modelos, datos de entrada, logs y una auditoría de 1.302 comprobaciones sin discrepancias. Traducción NOT_RUN.

[Control de dependencia visual del modelo congelado](research_gpt6/61_kraken_visual_specificity_result.md), con [protocolo e incidencia de instrumentación](research_gpt6/60_kraken_visual_specificity_protocol.md): en desarrollo, el error intacto de 73,8197 % sube a 78,1116 % al reflejar o desordenar la imagen; en entrenamiento pasa de 24,8980 % a 68,2653 % o 62,8571 %. Se conserva el primer intento con contador inválido y la repetición corregida con control positivo. Las 27 predicciones previas se reproducen exactamente; una salida de entrenamiento varía entre intentos y queda registrada. La auditoría pasa 3.425 comprobaciones. Es un diagnóstico sobre las mismas páginas, sin nuevos modelos ni evidencia de traducción.

[Registro geométrico parcial Voynichese–Yale](research_gpt6/63_voynichese_registration_result.md), con [criterios fijados antes de estimar](research_gpt6/62_voynichese_registration_protocol.md): se calibran los dos encuadres de la misma secuencia EVA y se aceptan tres de cuatro registros de imagen. Se exportan 280 polígonos de palabra candidatos; f4r falla los criterios reservados y sus 64 palabras se excluyen, junto con una caja de ancho cero en f3r. Los doce pares de folios incorrectos se rechazan. El criterio global queda FAIL; la auditoría de archivos y geometría pasa 10.142 comprobaciones. No se entrenó otro OCR ni se obtuvo traducción.

[Corrección local y referencia candidata uniforme v2](research_gpt6/65_local_registration_result.md), [protocolos 64](research_gpt6/64_local_registration_protocol.md) y [66](research_gpt6/66_uniform_local_reference_protocol.md): el método local pasa 20/20 casos frente a 11/20 del global. En f4r, P90 agrupado baja de 7,19 a 3,25 píxeles; el control con residuos permutados queda en 7,16 y falla 5/5. Una construcción posterior conserva 344 polígonos candidatos en las cuatro páginas, excluye la caja original de ancho cero y mantiene las referencias históricas. Las auditorías de comparación y construcción no encuentran discrepancias. Son datos de desarrollo sin revisión experta nueva. No se entrenó otro OCR ni se obtuvo traducción.

[Kraken reentrenado con palabras EVA](research_gpt6/68_eva_word_retraining_result.md), con [protocolo 67](research_gpt6/67_eva_word_retraining_protocol.md): se completaron dos ajustes de 200 épocas desde los pesos conservados, con 197 palabras de entrenamiento y 147 de desarrollo. El modelo con parejas originales obtiene 62,5 % de error EVA; el control permutado, 76,6129 %, y el vecino por imagen, 68,4140 %. Sin embargo, Kraken sólo acierta dos etiquetas de un carácter y ninguna palabra multicaracteres, frente a 191/197 coincidencias en entrenamiento: generalización insuficiente. El resultado no es directamente comparable con el error Boxer anterior. Se conservan ambos modelos, checkpoints, predicciones y el primer intento fallido antes de entrenar; la auditoría pasa 16.382 comprobaciones sin discrepancias. Traducción NOT_RUN.

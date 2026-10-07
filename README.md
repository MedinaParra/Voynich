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

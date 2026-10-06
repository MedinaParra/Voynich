# Plan elegido: reglas de enlace, unidades y validación reservada
Fijado antes de ejecutar esta fase, 6 de octubre de 2026. No es una prerregistración externa ni un test ciego frente al investigador: ya se conoce la señal exploratoria anterior.

Hipótesis operativa: el último carácter EVA de un grupo aporta información transferible sobre el primero del siguiente, más allá de la composición del cuaderno y la posición en línea. Si falla fuera de muestra, se abandona este modelo mínimo como base suficiente para una clave contextual.

Prueba inmediata: comparación de log-loss de primer carácter. Base: distribución de primeros caracteres. Control contextual: quire y posición normalizada en cuatro bandas de línea. Modelo de enlace: ese contexto más último carácter anterior. Suavizado jerárquico fijado en 20 observaciones equivalentes; base con pseudoconteo 0,5 para las 26 letras ASCII, sin optimizar contra test. Cinco pliegues por hoja (r/v agrupados cuando el ID lo permite) y leave-one-quire-out. Se prueban ambas lecturas de comas; no se cruzan huecos o ilegibles. Intervalo bootstrap por grupos de test, 999 remuestras, semilla fija; no comparar como ocho confirmaciones independientes.

Umbral para continuar: ganancia positiva del enlace frente al control contextual y límite inferior bootstrap >0 en ambas segmentaciones y ambos particionados. No demostraría cifrado: un generador puede producir la misma dependencia.

Fases posteriores: exigir un mecanismo concreto que transforme unidades y comparar lenguas/cifrados/generadores con controles emparejados; solo entonces construir correspondencias semánticas con anclas de confianza, fijarlas y reservar pasajes. No asignar nombres a plantas retrospectivamente ni llenar huecos con traducciones plausibles. Traducir requiere que esas correspondencias predigan el contenido: log-loss de EVA por sí solo no lo prueba.

Estado al fijar el protocolo: fase predictiva NOT_RUN; identificación de idioma, mecanismo inverso y traducción NOT_RUN. Se actualizará mediante informe separado, sin modificar los criterios anteriores.

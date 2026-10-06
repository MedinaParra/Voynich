# Resultado de la primera fase del plan elegido
6 de octubre de 2026. [Plan fijado antes de ejecutar](16_plan_descifrado.md). Script [contextual_link.py](code/contextual_link.py), [JSON](results/contextual_link.json). Fuente y parser conservador del experimento anterior. Python 3.12.14; ejecución y compilación sintáctica: exit 0. No se ha traducido el texto.

## Resultado principal
| Comas | Reserva | Control contextual bits/inicio | Con enlace bits/inicio | Ganancia | IC bootstrap 95% |
|---|---|---:|---:|---:|---|
| Separadoras | Cinco pliegues por hoja | 3,04579 | 2,90506 | 0,14073 | 0,11031–0,16783 |
| Separadoras | Cuaderno completo | 3,14545 | 2,97299 | 0,17247 | 0,10329–0,20414 |
| Unidas | Cinco pliegues por hoja | 2,97245 | 2,86651 | 0,10595 | 0,07701–0,13246 |
| Unidas | Cuaderno completo | 3,07561 | 2,93503 | 0,14058 | 0,07587–0,17336 |

Criterio fijado: **PASS predictivo**. Ambas segmentaciones y reservas tienen ganancia con intervalo positivo. Se evaluaron 28432/26010 pares, 100 grupos de hoja y 16 grupos de metadata de cuaderno. El primer carácter de un grupo es parcialmente predecible a partir del último del anterior incluso después de controlar posición y composición de cuaderno. Esta afirmación se refiere a EVA, no a sonidos o letras identificadas.

## Implementación y alcance
El control usa cuaderno y cuatro bandas de posición dentro de cada tramo limpio; un hueco o token rechazado reinicia el tramo. «Posición en línea» en el protocolo es, por ello, una aproximación por tramo retenido, no coordenada paleográfica. Las dos caras se agrupan mediante ID de hoja (`f1r`/`f1v`→`f1`); la agrupación no reconstruye bifolios originales ni asegura independencia física de hojas del mismo bifolio. En cuadernos completamente nuevos, se usa una distribución de posición y enlace agrupada sobre entrenamiento, sin acceder a test. Para un contexto visto se usan conteos del cuaderno correspondiente. El código fija suavizado 20 y base uniforme ASCII de pseudoconteo 0,5. No se optimizaron estos valores contra test.

Los intervalos proceden de 999 remuestras de los grupos de test sobre predicciones ya obtenidas; no reentrenan modelos ni son una estimación completa de incertidumbre del mecanismo. Los cuatro resultados comparten datos y no son cuatro descubrimientos independientes. El estudio conoce la señal exploratoria anterior: validación reservada de predicción no equivale a descubrimiento ciego de semántica.

## Reproducción
El script importa el parser `boundary_dependence.py` de su mismo directorio. El corpus debe conservar el blob `2a4533ab9bdfa85db9bad602d590978953055df1`, comprobado automáticamente.

```bash
python research_gpt6/code/contextual_link.py --corpus corpus/voynich_eva.txt --out research_gpt6/results/contextual_link.json
```

## ¿Qué se puede traducir?
Ninguna palabra con justificación nueva en esta fase. La variable predicha es una letra de transliteración, no el contenido del manuscrito. Una tabla signo→letra podría convertir estos grupos en cadenas legibles sin recuperar su significado; no se presenta tal tabla como clave.

| Fase | Estado | Evidencia / obstáculo |
|---|---|---|
| Regla mínima de enlace generaliza | PASS predictivo | JSON, cuatro contrastes con ganancia positiva |
| Identificar que el mecanismo es cifrado y no generador | NOT_RUN | Faltan controles emparejados de ambos mecanismos |
| Identificar unidades, idioma y transformación inversa | NOT_RUN | El modelo de bordes no identifica ninguno |
| Traducción defendible | BLOCKED | No existe todavía una correspondencia semántica validada que invertir |

Elijo continuar esta vía porque produce predicciones comprobables, y el primer filtro pasó. El siguiente filtro tiene que comparar mecanismos concretos con lenguas/cifrados/generadores bajo la misma transcripción y métricas; la señal actual es compatible con todos ellos. No se puede seleccionar latín, hebreo o turco únicamente por esta ganancia. El resultado limita modelos independientes de contexto; no prueba una lengua histórica ni legitima completar una traducción por intuición.

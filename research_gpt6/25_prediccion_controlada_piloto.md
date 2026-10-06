# 25. Predicción de bordes con controles adicionales: piloto exploratorio

Fecha: 2026-10-06. Motivación: críticas del análisis externo y necesidad de pasar de preparación documental a una prueba falsable.

## Pregunta y alcance

¿Añadir el último carácter EVA del grupo anterior mejora la predicción del primero del siguiente en folios no usados para ajustar el modelo, después de controlar aproximadamente posición, longitudes y composición por cuaderno?

No es una prueba de significado ni identificación de lenguaje. El corpus ya fue explorado antes: este análisis no constituye un estudio confirmatorio independiente ni una reproducción exacta de los antecedentes citados. Se implementó un modelo de recuentos suavizados; no se ejecutó el pseudocódigo defectuoso de la respuesta externa.

## Implementación ejecutada

- Corpus fijado por el blob usado en informes anteriores; hash SHA-256 en JSON.
- Solo loci de texto de párrafo que quedan íntegramente legibles bajo el filtro aplicado. Se excluyen líneas con comas inciertas, huecos de dibujo o signos no admitidos; no se crean pares a través de cortes.
- Pares interiores: ambos grupos fuera de los extremos de línea.
- Cinco particiones por hoja física: recto y verso permanecen en el mismo grupo; la asignación completa se conserva en JSON. Modelos ajustados exclusivamente con los otros grupos.
- Modelo base: primer carácter condicionado a cuaderno, cuartil de posición, longitud anterior y siguiente (cada una limitada a categoría 8 o más), número de grupos de línea (categoría 15 o más). Distribución global de entrenamiento como respaldo; suavizado fijo 20.
- Modelo ampliado: mismas covariables más carácter final anterior, suavizado fijo 20 hacia el modelo base.
- Métrica: ganancia de log-probabilidad predictiva en bits por par. No AIC/BIC ni información mutua empírica.
- 199 permutaciones del carácter final en evaluación, dentro de hoja y celda de covariables. Se conserva la distribución local de esa variable; los modelos ya ajustados no se reentrenan.
- Intervalo exploratorio mediante 999 remuestreos de hojas, sin volver a entrenar.

No se introducen identificadores de folios desconocidos como covariables ficticiamente estimadas. No se dispone en este análisis de control por mano, Currier o representación grafémica alternativa.

## Resultados reales

| Medida | Resultado |
|---|---:|
| Pares evaluados | 7.127 |
| Hojas físicas | 97 |
| Ganancia del modelo ampliado | 0,008725 bits/par |
| Intervalo bootstrap exploratorio del 95% | 0,004589–0,012829 |
| Ganancia media tras permutar finales | 0,006114 bits/par |
| Diferencia observado menos media permutada | 0,002610 bits/par |
| Valor p de permutación | 0,005, mínimo posible con 199 permutaciones |
| Pares en celdas con más de un final distinto | 1.504 de 7.127 |
| Fracción media de finales efectivamente cambiados | 10,82% |

La ganancia positiva del nulo indica que la permutación conserva mucho de la estructura aprovechada por el modelo, no que haya quedado sin dependencia. Gran parte de las celdas son inmutables. No se presenta la significación nominal como prueba definitiva de independencia condicional rechazada.

La cifra es menor que en el informe 17, pero cambian tanto la selección de pares como las covariables: **no se puede atribuir toda la diferencia a los controles adicionales**. Para determinar cuánto explica cada control se necesita una ablación sobre exactamente los mismos pares, con criterios fijados antes de examinar sus resultados.

## Evaluación crítica

El resultado es compatible con una pequeña información predictiva residual bajo esta implementación. No demuestra que la dependencia sea lingüística, semántica o criptográfica; tampoco establece novedad frente a Parisel o Rozanova/Temerev. Las covariables son categorías gruesas, la permutación tiene movilidad limitada y los intervalos no incluyen incertidumbre del ajuste ni toda la dependencia entre hojas del mismo cuaderno.

Antes de elevarlo a afirmación publicable, se necesita: comparación de modelos sobre muestra idéntica; permutaciones con cobertura útil sin destruir las covariables relevantes; sensibilidad a cuadernos completamente reservados; controles Currier/mano y representaciones alternativas. Estas pruebas quedan NOT_RUN en este informe.

## Reproducción y verificaciones

```bash
python research_gpt6/code/controlled_edge.py --corpus voynich_eva.txt --out controlled_edge.json
```

Python/Linux; ejecución real, salida 0. Script y resultado completos incorporados. Comprobaciones ejecutadas: número de pares consistente, hojas disjuntas entre entrenamiento/evaluación y categorías de posición válidas: PASS. No certifican validez lingüística ni originalidad.

Antecedentes a contrastar: https://arxiv.org/abs/2604.19762 y https://arxiv.org/html/2608.17096v1. No se afirma haber reproducido sus experimentos en esta ejecución.

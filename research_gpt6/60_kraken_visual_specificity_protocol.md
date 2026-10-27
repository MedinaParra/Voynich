# 60 - ¿Depende Kraken de la imagen correcta?

Fecha: 27 de octubre de 2026. Base: `29c7fc54e7f21455faefe7abb238754da0f12dcf`, rama `experiment/kraken-voynich`.

El ensayo 59 redujo el error convencional a 516/699 unidades de desarrollo. Todavía no comprueba cuánto depende la salida de la imagen concreta frente a regularidades de la pequeña muestra de entrenamiento. Este protocolo fija un diagnóstico del modelo ya existente antes de ejecutar las nuevas intervenciones de entrada. La elección del modelo y las páginas ocurre después de conocer sus puntuaciones anteriores; esto no es una prerregistración confirmatoria ni un conjunto nuevo de evaluación.

## Entradas y condiciones fijadas

- Modelo `repaired_200`, SHA-256 `b5df9eef0a783bec696b33636fbfb8d4807bfaa256d74ad6b34df4c58db66acb`. No se vuelve a entrenar ni se seleccionan checkpoints.
- Los mismos 34 renglones de ajuste y 27 de desarrollo, referencias provisionales sin revisión independiente. Se regeneran los recortes y se verifican texto, tamaño y hashes contra los 122 registros originales/corregidos preservados.
- Cuatro condiciones sobre los 61 recortes corregidos: intacto, reflejo horizontal, ocho franjas verticales reordenadas de forma determinista y blanco. Reflejo y reordenamiento conservan todos los píxeles RGB y las dimensiones; blanco conserva las dimensiones.
- Se conservan los 244 registros de inferencia, sus entradas y los errores. Un fallo no se sustituye por una predicción vacía ni se excluye para mejorar una puntuación.
- Un hook de Torch cuenta las llamadas reales a la red. Si el preprocesador devuelve una cadena vacía sin llamar a la red, se informa como cortocircuito del preprocesador: no demuestra qué respondería la red a una entrada blanca.
- Las 27 predicciones intactas de desarrollo deben reproducir exactamente el resultado anterior. Una discrepancia invalida la comparación directa y se conserva.

## Medidas y controles de asociación

Se informa error micro de Levenshtein por unidades convencionales de Boxer y espacios, descomposición en sustituciones/eliminaciones/inserciones, número de salidas modificadas y cambio en puntos porcentuales respecto del intacto. La descomposición usa un desempate fijo; otras alineaciones mínimas pueden repartir de otra forma los tipos de error. Ninguna etiqueta de Boxer recibe un valor fonético o semántico.

Para cada rol y condición se compara el error observado con 9.999 asignaciones de referencias permutadas. Dentro de cada folio se ordenan las filas por relación ancho/alto y se dividen en dos mitades; las referencias solo se permutan dentro de cada mitad. Se preservan folio, rol y estrato geométrico, pero no se controla toda diferencia entre renglones. Semilla 20261027 para ajuste y 20261028 para desarrollo; se usan las mismas permutaciones entre condiciones. Se guardan todos los recuentos simulados y la fracción de cola inferior con corrección +1.

La permutación es un diagnóstico condicionado a estos grupos. La intercambiabilidad no está garantizada por las anotaciones; una fracción pequeña no se presenta como confirmación de lectura, desciframiento o significación lingüística. No se buscarán nuevos grupos, umbrales o transformaciones después de conocer el resultado.

Una degradación con imágenes alteradas puede mostrar sensibilidad visual, aunque también refleja entradas fuera de distribución. Una salida invariable o un error parecido bajo asignaciones incorrectas debilitaría el uso de la puntuación anterior como evidencia de reconocimiento específico. Sensibilidad a píxeles y lectura correcta son cuestiones distintas.

## Ejecución reproducible

```bash
python research_gpt6/code/test_kraken_visual_specificity.py
python research_gpt6/code/kraken_visual_specificity.py \
  --plan research_gpt6/data/kraken_visual_specificity_plan.json \
  --repo research_gpt6 --out work/kraken_visual_specificity
```

Entorno CPU y versiones fijados en `.github/workflows/kraken-visual-specificity.yml`. Se utilizan los modelos, imágenes Yale y etiquetas/mapeo Boxer ya preservados con atribución en el ensayo 59. El código del nuevo diagnóstico es propio. Traducción, revisión experta y evaluación en hojas nuevas: **NOT_RUN**.

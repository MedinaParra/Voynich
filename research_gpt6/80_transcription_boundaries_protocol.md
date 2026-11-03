# 80 — Contrastar lecturas y revisar límites sin fabricar una referencia

3 de noviembre de 2026. Continuación de 79, rama `experiment/kraken-voynich`.

Se fija este [plan](data/transcription_boundaries_plan.json) antes de calcular los desacuerdos. Es desarrollo descriptivo sobre once páginas ya utilizadas; ninguna se presenta como una nueva reserva. No habrá entrenamiento ni inferencia neuronal en este paso.

VT/Voynichese e IT pertenecen a la lectura de Takahashi: dos exportaciones no son dos lectores. El contraste principal será VT frente a ZL3b, una edición diferenciada, con influencias y convenciones compartidas. Boxer aporta otra lectura en notación propia, sin inventar una conversión a EVA. Se documentarán origen, espejo, versión, licencia y hashes.

Se emparejan identificadores externos de locus. Se guardan los textos originales, la coma incierta, separadores por dibujo, ligaduras, variantes e ilegibles. Las líneas con alternativas o símbolos que el comparador literal no representa se conservan, pero quedan fuera de su denominador. No se elige la primera alternativa como verdad.

El comparador separará letras y límites. Dentro de cada locus representable conservará todos los estados de alineación de edición con coste mínimo; una localización ambigua seguirá siéndolo. No se convertirán caminos de edición en probabilidades paleográficas. Una asociación textual con cajas sólo se admitirá si toda la secuencia de tokens del folio XML coincide exactamente con VT. La coincidencia de texto no verifica una ubicación física independiente.

Se medirán máscaras compartidas en los 989 candidatos congelados. La cola visual tomará hasta24 palabras de entrenamiento, con desacuerdos y controles de solapamiento alto/bajo, usando las reglas del plan y sin consultar errores de OCR. Mostrará recorte congelado, rectángulo sin máscara y contexto de la foto. El asistente registrará lo que puede observar; la revisión experta independiente seguirá explícitamente pendiente. No se cambiarán etiquetas, imágenes o particiones.

El resultado se publicará como inventario reproducible y material de revisión, con cobertura y exclusiones. No acredita mejora del OCR ni traducción. Un auditor separado recalculará alineaciones y comprobará el puente exacto de fuentes.

# Ensayo de un lector sin alfabeto: resultado negativo para este modelo

5 de noviembre de 2026.

Se implementó y ejecutó el método del [protocolo96](96_alien_protocol_protocol.md): conservar las igualdades entre signos de palabras vecinas, separar un efecto de posición y hacer competir explicaciones semánticas incompatibles. **Los controles básicos pasaron, pero ninguna de las ocho configuraciones del Voynich obtuvo una ventaja predictiva positiva frente al modelo nulo. No se obtuvo una traducción.** El modelo no se reajustó después de observar ese resultado.

«Alienígena» describe aquí a un lector que desconoce el alfabeto y el idioma. No afirma origen extraterrestre ni una metodología sin antecedentes.

## Qué se fijó y ejecutó

El protocolo, las dos implementaciones de datos/modelos y el plan con hashes de fuentes quedaron creados y verificados públicamente en el commit `cec2700e07b3e5a0a5649be0bdf077363737bae9` antes de ejecutar la primera métrica. La copia local completa, incluido el auditor, también estaba fijada antes de medir. Se ejecutaron las ocho proyecciones previstas y los cuatro controles; se conservaron resultados, conteos completos y testigos de todos los pares. No hubo selección posterior de parámetros o de una configuración ganadora.

Una sola tabla de renombrado por par preserva las coincidencias internas y entre palabras:

| Par observado | Código conjunto |
|---|---|
| `ab` / `ba` | `01` / `10` |
| `ab` / `cd` | `01` / `23` |

El diccionario inverso permite reconstruir las unidades originales. Se comprobaron reconstrucción e invariancia al renombrar las unidades ya fijadas; en la proyección agrupada esa prueba ocurre después de aplicar las seis agrupaciones operativas EVA. No se descubrió una segmentación histórica.

La medida puntuada fue C=min(3,signos distintos compartidos). MF predice sus cuatro valores condicionando en las longitudes, repeticiones internas y posición del par. M0 omite la posición. Un segundo MF usa conteos medios de ocho mezclas de palabras dentro de página × longitud exacta en unidades × posición inicial/intermedia/final. Todos son modelos normalizados con prior Dirichlet0,5. No predicen palabras latinas ni significados.

La prueba reservó por hash hojas físicas completas: recto, verso y paneles de una hoja no se separan entre ajuste y evaluación. Son hojas de un corpus ya explorado en este proyecto, no una reserva global nueva. No se incluyeron página, sección o mano como predictores; las mezclas sí conservan la composición de cada página. Conservar palabras mantiene marginalmente su repetición interna, pero puede cambiar qué clases de repetición quedan juntas.

## Resultados en las transcripciones

Ventaja = log2(MF_real/MF_nulo), promediada por par reservado. Formato = log2(MF_real/M0), también por par; puede ser negativo y no es una información mutua garantizada.

| Configuración | Pares reservados | Ventaja, bits/par | Formato, bits/par | Cola condicional |
|---|---:|---:|---:|---:|
| VT, separar comas, caracteres | 6.339 | −0,007297 | −0,007459 | 0,005 |
| VT, separar comas, grupos | 6.339 | −0,011297 | −0,009287 | 0,040 |
| VT, unir comas, caracteres | 6.339 | −0,008213 | −0,007459 | 0,005 |
| VT, unir comas, grupos | 6.339 | −0,012753 | −0,009287 | 0,065 |
| ZL, separar comas, caracteres | 4.464 | −0,005545 | −0,012590 | 0,005 |
| ZL, separar comas, grupos | 4.464 | −0,014986 | −0,011009 | 0,005 |
| ZL, unir comas, caracteres | 4.096 | −0,005840 | −0,013025 | 0,005 |
| ZL, unir comas, grupos | 4.096 | −0,009623 | −0,008574 | 0,005 |

La regla fijada exigía ventaja positiva **y** cola≤0,05. **0/8 configuraciones la cumplen.** Por tanto, este modelo aprendido sobre vecinos reales no mejora la predicción del diagnóstico respecto al ajustado con mezclas en las hojas reservadas.

Varias colas alcanzan0,005 pese a ventajas negativas. Eso significa que el score observado ocupa una posición extrema respecto a las mezclas bajo este estadístico; **no autoriza afirmar que el texto carezca de estructura**, ni que los datos sean equivalentes a un texto mezclado. El requisito de ganancia positiva evita llamar éxito a una diferencia que no produce la mejora predictiva buscada. La resolución mínima de la cola es1/200; no se reportan p=0.

Las proyecciones son dependientes. Además, los archivos de pares VT con comas separadas y unidas son idénticos en ambos modos de unidades: esa sensibilidad no produce otro corpus. Sus pequeñas diferencias en la ventaja proceden de los streams nulos distintos fijados por identificador de caso. No son otra réplica ni evidencia de un efecto de las comas.

## Cobertura y selección

| Fuente/proyección | Renglones completos aceptados | Palabras aceptadas | Hojas de ajuste / reservadas |
|---|---:|---:|---:|
| VT, separar o unir | 4.090 | 34.458 | 83 /16 |
| ZL, separar | 2.703 | 22.657 | 82 /16 |
| ZL, unir | 2.701 | 21.014 | 82 /16 |

En ZL se excluyeron616 renglones por lagunas de dibujo y777 por contenido no admitido, entre otros motivos registrados. Una palabra dudosa descarta su renglón entero; no se fabrican vecinos rescatando palabras. La selección es desigual entre ediciones. Una cadena literal en una transliteración tampoco certifica una lectura correcta de la tinta. [Inventario completo](results/alien_protocol/source_inventories.json).

## Controles y explicación rival

Los controles tienen60 hojas sintéticas de20 líneas y8 palabras;47 hojas ajustan y13 evalúan, con1.820 pares reservados por control. Son generadores conocidos y no pruebas históricas ciegas.

| Control | Ventaja, bits/par | Formato, bits/par | Cola | Criterio positivo |
|---|---:|---:|---:|---|
| Instrucciones independientes | +0,000706 | −0,000213 | 0,115 | No |
| Las mismas con marcadores de posición | +0,000460 | +0,755782 | 0,075 | No |
| Repetición Markov de instrucciones | +1,849737 | −0,000682 | 0,005 | Sí |
| Concordancia morfológica de juguete | +0,443137 | −0,000939 | 0,005 | Sí |

El gate previsto pasa: los dos controles independientes no activan el detector residual y la repetición sí. El modelo de posición detecta el formato añadido en el control correspondiente. A la vez, la concordancia artificial también activa el detector. Incluso una eventual ganancia positiva en Voynich no habría distinguido un protocolo cifrado de morfología, copia, repetición o composición temática. El control morfológico es deliberadamente elemental y no representa la diversidad de idiomas naturales.

## Dos mundos incompatibles con el mismo mensaje

El certificado usa ocho palabras sintéticas y dos codebooks biyectivos. En uno, `abcd` representa `HEAT`; en el otro, `COOL`. Las ocho instrucciones cambian de etiqueta y ambas secuencias vuelven a codificarse al mismo texto observado. No son propuestas de lectura del Voynich.

El texto, las igualdades y la entrada del detector son idénticos en ambos mundos. Un score que sólo recibe esa entrada no puede elegir la interpretación correcta. Este contraejemplo impide convertir una regularidad estadística en una traducción sin anclas externas que restrinjan los significados. No demuestra que el manuscrito use una sustitución simple: demuestra una ambigüedad que este método estructural no resuelve. [Certificado completo](results/alien_protocol/semantic_certificate.json).

## Comprobaciones y conclusión operativa

Un auditor separado, sin importar el código de producción, obtuvo **PASS:509.732 comprobaciones y cero discrepancias**. Reconstruyó231.606 pares, verificó6.912 celdas normalizadas con fracciones exactas y recalculó2.388 scores nulos. Verifica el manifiesto, los testigos, conteos, probabilidades, pérdidas, colas y certificado semántico. No valida la transliteración frente a fotos, la autenticidad histórica, el generador de mezclas como explicación del libro o el significado del texto. [Auditoría](results/alien_protocol/audit.json).

Los testigos incluyen tokens originales, unidades, códigos completos, inversos y posiciones. El escalar C sólo es la medida puntuada, no una representación suficiente para traducir. C es simétrico y tampoco identifica la dirección de lectura.

La [reproducción desde un checkout limpio en GitHub](https://github.com/MedinaParra/Voynich/actions/runs/42131129809) pasó al recuperar el paquete en el commit `0aac2971a73453fb8626d02b806c39ab871e47e4`: los ocho archivos congelados conservaron sus hashes, los 39 archivos de resultados coincidieron con el manifiesto y la auditoría regenerada fue idéntica (509.732 comprobaciones, cero discrepancias). Se conservan el [registro de recuperación](results/alien_protocol/recovery_replay.json) y el [log de ejecución](results/alien_protocol/recovery_replay.log). Es una repetición técnica del mismo ensayo y corpus; no añade una reserva científica nueva ni valida significados.

La consecuencia práctica es **no promover este detector a descifrador ni alimentarlo con una interpretación lingüística inventada**. El ensayo limita una medida concreta y documenta por qué el significado continúa sin identificar. No descarta que exista lenguaje, abreviaturas, un cifrado o instrucciones reales. No se reentrenó Kraken.

La revisión bibliográfica confirma antecedentes de variantes posicionales y unidades: Bowern y Lindemann(2021) y el preprint Rozanova/Temerev [arXiv:2608.17096](https://arxiv.org/abs/2608.17096). Esta combinación se implementó para este proyecto; no se afirma novedad global ni una solución publicable del manuscrito.

## Reproducir

Sólo Python3.12.14 y biblioteca estándar:

```bash
python research_gpt6/code/alien_protocol_probe.py --repo research_gpt6 --plan research_gpt6/data/alien_protocol_plan.json --out work/alien_protocol
python research_gpt6/code/audit_alien_protocol.py --bundle work/alien_protocol --out work/alien_protocol/audit.json
```

Las repeticiones técnicas deben conservar la configuración completa, incluidos resultados negativos y las ocho proyecciones dependientes. Una nueva hipótesis requeriría otro protocolo; no se modificó éste tras ver sus métricas.

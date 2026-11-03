# 85 — Dos cambios de frontera invierten un indicador local; no aparece una clave

**3 de noviembre de 2026. Rama `experiment/kraken-voynich`.**

Se implementó y ejecutó una prueba creativa concreta: un **adversario de fronteras** que busca las segmentaciones que más debilitan una regularidad, en lugar de elegir las que la favorecen. Se fijó el [protocolo 84](84_boundary_adversary_protocol.md) y el [plan](data/boundary_adversary_plan.json) en `bf89070b72e5ec71d6918df1ea713478a275adbc` antes de medir la señal.

El resultado principal es un certificado exacto: **dos decisiones de frontera bastan para invertir el signo del indicador elegido**. El indicador bajo VT ya era compatible con su control de orden aleatorio, por lo que no se ha destruido una evidencia estadística sólida previa. El experimento identifica fragilidad de una medida, no falsedad del texto o de todas las teorías de copia.

No se hizo nuevo OCR, entrenamiento, revisión experta o traducción. Las tres preferencias `m/g` del informe 83 siguen siendo propuestas no aprobadas y no entran en este experimento.

## Qué tiene de nuevo y qué ya estaba estudiado

Los informes 17/19 del repositorio ya estudiaron vecindad, comas y mecanismos de copia. Rozanova–Temerev 2026 también incluye borrado de separadores. No se reivindica que descubrir semejanza entre grupos vecinos sea nuevo ni que esta combinación no exista en la literatura mundial.

La incorporación nueva para este proyecto es **calcular extremos exactos para una familia completa de fronteras discutibles y conservar la perturbación mínima y sus testigos**. Eso sirve para decidir si una conclusión depende de una convención editorial antes de intentar atribuirle un mecanismo o un significado.

## Familia finita de anotaciones

De los 159 loci comparados en 81, se toman los 98 con letras proyectadas idénticas en VT y ZL. Se mantienen fijas esas letras. Los 40 loci con diferencias literales y 21 complejos quedan fuera. No es una prueba de todas las lecturas o todos los glifos posibles.

Una frontera presente y cierta en ambos archivos se mantiene. Una posición discrepante o incierta se puede activar/desactivar. La familia contiene 49 decisiones binarias: **562.949.953.421.312 combinaciones globales**, pero sólo 170 segmentaciones locales distribuidas entre 98 loci. El máximo local es 16. La programación dinámica combina las contribuciones sin recorrer el producto global.

Es una familia híbrida de estrés: que cada posición proceda de una anotación no certifica que cada combinación de decisiones sea paleográficamente correcta, ni que sean equiprobables. Las páginas ya se habían usado; no son una nueva reserva confirmatoria.

## Indicador fijado y significado limitado

Se retiran el primer y último token de cada segmentación. En los M tokens interiores se considera vecino semejante un par cuyas cadenas tengan longitud mínima 3 y distancia de Levenshtein≤1. Para M≥2:

\[
T_l=\frac{H_{adyacentes}}{M-1}-\frac{H_{pares\ ordenados,\ i\ne j}}{M(M-1)}.
\]

Los pares se cuentan por posición, incluyendo palabras iguales en posiciones diferentes; la diagonal se excluye. Para M<2 se define 0. La segunda fracción es la esperanza de la primera al permutar uniformemente esos mismos tokens interiores. El total es la suma por locus con igual peso; no es porcentaje de copia, de idioma o de desciframiento.

Con sólo dos tokens interiores, el indicador también vale 0 por simetría. En VT, 24/98 loci tienen cuatro tokens o menos y son estructuralmente nulos para esta medida. La mediana real es 6 tokens. Una frontera próxima al extremo puede cambiar qué texto se excluye como primer/último token: la fragilidad certificada es operacional y no sólo una modificación de vecindad a texto interior constante.

## Curva exacta de estrés

El presupuesto es un máximo de cambios respecto de VT, no un número obligatorio. Los valores son sumas de fracciones exactas; se muestran redondeados.

| Presupuesto máximo | Mínimo del indicador | Máximo |
|---|---:|---:|
|0|0,136508|0,136508|
|1|0,026984|0,255556|
|2|**−0,006349**|0,350794|
|4|−0,053968|0,479365|
|8|−0,102381|0,576984|
|Todos, hasta 49|−0,114286|0,596825|

Se examinaron todos los costes posibles, no sólo las filas mostradas. Ninguna elección de un único cambio lleva el total a 0; una combinación de dos sí. Por eso el radio exacto es **2 para el signo**, sin equivaler a un radio de significación estadística.

### Testigo explícito de dos cambios

| Locus | Segmentación VT | Cambio del testigo |
|---|---|---|
|f8r.4|`… shesed.chofchy.dam`|`… shesed.chof.chy.dam`|
|f8v.8|`okchol.ksh.chol.chol.chol.cthaiin.dain`|`okcholksh.chol.chol.chol.cthaiin.dain`|

Ambas decisiones aparecen en la edición ZL de esos loci. Los demás loci del testigo mantienen la opciónVT. Se conservan las letras y se cambian sólo dos posiciones. El total pasa de 43/315 a−2/315. La segunda fusión cambia también qué grupo queda excluido como primero, una limitación operativa registrada.

El [testigo completo](results/boundary_adversary/two_flip_witness.json) no aprueba estas divisiones como texto histórico. Demuestra que esa conclusión descriptiva no está protegida frente a la familia de anotación fijada.

## Control aleatorio y envolvente conservadora

Se generaron 999 permutaciones interiores que conservan, para cada segmentación, extremos y multiconjunto de tokens. Las prioridades pseudoaleatorias se comparten entre caminos por posición de inicio, con semilla y hash fijados. La corrección más-uno y los empates incluidos evitan colas de Monte Carlo iguales a 0.

| Registro condicional de Monte Carlo | Valor |
|---|---:|
|Cola de VT, con corrección más-uno|0,426|
|Cota superior de las colas de cualquier mundo fijo en la simulación acoplada|0,634|

La segunda cantidad usa, por réplica, el máximo de la diferencia permutado−observado en cada locus y suma esos máximos. Domina la diferencia de cualquier combinación fija. Es una derivación de este experimento, no un método atribuido al artículo de Phipson–Smyth que fundamenta la corrección más-uno.

Una cota alta **no demuestra ausencia de dependencia ni existencia de una segmentación con cola alta**: puede ser laxa porque el mundo que maximiza cambia por réplica. Aquí VT ya ofrece una cola grande, sin necesidad de esa cota. El nulo es intercambio interior condicionado a esta familia, no una teoría histórica completa. Las fronteras fueron construidas por transcriptores viendo el texto, por lo que tampoco se presenta como un p-valor universal que elimine ese sesgo.

## Controles sintéticos ejecutados

Se generaron 32 loci de 16 tokens por ejemplo. El positivo copia el grupo anterior con probabilidad 0,8 y lo modifica con probabilidad 0,35 si copia; su contraparte reordena sólo interiores, conservando exactamente multiconjunto y extremos. La condición ambigua añade una frontera interna opcional en cada segunda línea. Hay 199 permutaciones por ejemplo.

| Ejemplo | ColaVT | Envolvente |
|---|---:|---:|
|Copia/modificación, fronteras fijas|0,005|0,005|
|Mismo multiconjunto reordenado, fijas|0,250|0,250|
|Copia/modificación, fronteras ambiguas|0,005|0,005|
|Mismo multiconjunto reordenado, ambiguas|0,250|0,305|

Pasó el criterio de esos cuatro ejemplos fijados. No se estimó potencia o tasa de falsos positivos en una población. Sus líneas de 16 tokens son más largas que las reales; son controles positivos de funcionamiento, no calibración emparejada que garantice sensibilidad para Voynich.

## Qué no puede identificar esta prueba

Se verificó sobre los 170 caminos que una sustitución biyectiva de caracteres conserva el indicador; invertir el orden de los tokens también lo conserva. Por construcción, la medida no puede recuperar una clave monoalfabética ni determinar la dirección de lectura. Un resultado grande tampoco distinguiría lengua, cifrado, autocopia y otros generadores con dependencia.

Este resultado aconseja usar el adversario como **filtro de robustez**, no como descifrador. Las futuras propiedades propuestas como pistas tendrán que conservar sus conclusiones bajo la incertidumbre declarada y, además, discriminar mecanismos recuperables conocidos. Esta prueba no se ha convertido en una traducción ni descarta las familias generales de copia o lenguaje.

## Evidencia y reproducción

El [auditor separado](code/audit_boundary_adversary.py) recalculó las fuentes, todos los caminos, puntuaciones racionales, costes, extremos, testigos y radio sin importar el código principal: PASS 1674 comprobaciones. No audita independientemente las colas de permutación. Cuatro controles matemáticos adicionales verifican centrado, degeneración de dos interiores, presupuestos y dominación de la envolvente. Esos controles son software/matemática, no iteraciones de desciframiento.

El prototipo construyó las tablas reales antes de los ejemplos sintéticos. Se reordenó el pipeline para ejecutar primero la calibración, sin cambiar parámetros; los tres archivos de resultados quedaron idénticos por hash. Se preserva [el registro de esa reproducción](results/boundary_adversary/execution_order_replay.json).

[Resumen](results/boundary_adversary/summary.json), resultados/caminos y simulaciones completas se conservan sin pérdida, con hashes. La [reproducción desde un checkout limpio en GitHub](https://github.com/MedinaParra/Voynich/actions/runs/41670013108), commit `970715288dd289ee7e2a645c5c2ef5fe037bd6b8`, pasó: se reconstruyeron idénticos todos los registros de calibración, caminos, certificados y simulaciones, y el auditor exacto reprodujo su resultado. Se descargó y verificó el digest del ZIP; se conservan [el recibo](results/boundary_adversary/ci_receipt.json), el log y los registros de resumen/auditoría. La reproducción no añade validación de un mecanismo histórico.

```bash
python research_gpt6/code/boundary_adversary.py --repo research_gpt6 \
  --out work/boundary_adversary --plan research_gpt6/data/boundary_adversary_plan.json
python research_gpt6/code/audit_boundary_adversary.py --repo research_gpt6 \
  --out work/boundary_adversary/audit.json
```

Fuentes primarias de contexto: [Rozanova–Temerev 2026](https://arxiv.org/html/2608.17096v1), [Reddy–Knight 2011](https://aclanthology.org/W11-1511/), [Phipson–Smyth 2010, corregido 2011](https://gksmyth.github.io/pubs/PermPValuesPreprint.pdf). Antecedentes locales: [17](17_resultado_plan_descifrado.md) y [19](19_resultados_mecanismos.md).

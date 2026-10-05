# 01 — Validación del corpus

**Estado: PASS parcial** para inspección y conteo del STA1 incluido en el commit fijado; **NOT_RUN** para comparación independiente STA1/EVA y paleografía.

- Fuente: `corpus/voynich_sta.txt`
- SHA-256: `81c331b7d8e76761e27d350c3b37ccfbe192848e6c8a227bcb5d40fb29259b17`
- Parser tipo notebook 03 (regex `[A-Z][0-9a-z]`, segmentos separados por punto): 194,341 tokens incluyendo separadores, 157,254 glifos, 37,087 palabras, vocabulario de 166 glifos.
- Commit GitHub: `47e6a77dc9d5cd570c375f4aff710fa4a0567278`.

El notebook 74 usa otra expresión (`[A-Z][a-z0-9]*`) y parser de líneas que no incorpora los folios `fRos`. Por ello cuenta 154,973 átomos, 5,225 líneas y 226 folios; f57v tiene 428 átomos. Los conteos de símbolos exclusivos se reprodujeron con este parser. Un contraste con el parser general que sí admite `fRos` mantiene X2=10, Xd=5, Xf=4, Pc=5 y Ea=1 exclusivamente en f57v; el denominador global sí aumenta. Esta discrepancia de universo importa para cualquier cálculo de significancia.

**No comprobado:** diferencias frente a otra transcripción EVA/STA1; ambigüedades paleográficas; límites dudosos; cotejo con imágenes; robustez de métricas ante distintas políticas de parsing.

El entorno carece de dependencias para correr los notebooks completos. Consulte `results/` y `code/` para los puertos focalizados y su definición exacta.

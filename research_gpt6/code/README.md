# Código y reproducibilidad

Estos scripts ejecutan reproducciones acotadas del corpus incluido en el commit fijado, sin depender de Jupyter. Son puertos explícitos de celdas de notebooks; consulte cada docstring y el JSON de salida. No ejecutan el análisis integral del proyecto ni prueban hipótesis semánticas.

## Fuente y entorno

- Repo: `https://github.com/cesarjz/Voynich`, commit `47e6a77dc9d5cd570c375f4aff710fa4a0567278`.
- Python 3.12.14; NumPy instalado para el script de permutaciones.
- SHA-256 STA1: `81c331b7d8e76761e27d350c3b37ccfbe192848e6c8a227bcb5d40fb29259b17`.

## Ejecución desde la raíz del repo de auditoría

Este repositorio no duplica el corpus fuente. Obtén el archivo STA1 fijado en la auditoría desde el proyecto original y pásalo explícitamente:

```bash
git clone https://github.com/cesarjz/Voynich.git /tmp/Voynich-source
python research_gpt6/code/reproduce_core.py --corpus /tmp/Voynich-source/corpus/voynich_sta.txt
python research_gpt6/code/reproduce_position.py --corpus /tmp/Voynich-source/corpus/voynich_sta.txt
python research_gpt6/code/reproduce_f57v.py --corpus /tmp/Voynich-source/corpus/voynich_sta.txt
python research_gpt6/code/heldout_prediction.py --corpus /tmp/Voynich-source/corpus/voynich_sta.txt
python research_gpt6/code/leave_one_quire_out.py --corpus /tmp/Voynich-source/corpus/voynich_sta.txt
python research_gpt6/code/audit_zodiac_crib.py --notebook /tmp/Voynich-source/28_zodiac_cribs.ipynb
python research_gpt6/code/zodiac_crib_holdout.py --corpus /tmp/Voynich-source/corpus/voynich_sta.txt
```

También se puede definir `VOYNICH_CORPUS` en el entorno y omitir `--corpus` en los tres scripts de reproducción. `heldout_prediction.py` y `leave_one_quire_out.py` requieren `--corpus`; comparan unigramas, posición y n-gramas de orden 1–4 con validación agrupada por folio y por quire, respectivamente. `audit_zodiac_crib.py` verifica hash, resultados guardados y un cálculo del notebook 28; no vuelve a ejecutar la comparación hebrea. `zodiac_crib_holdout.py` prueba si un mapa glifo→letra aprendido en nueve signos permite leer el nombre del décimo, reservando cada signo por turno y usando un nulo por permutación. Semillas, suavizado y unidades de aleatorización están en los JSON. No implican significado ni desciframiento. El valor predeterminado de los scripts de reproducción solo funciona si el corpus existe en `corpus/voynich_sta.txt` bajo este repo. Las salidas están en `research_gpt6/results/`. `reproduce_position.py` utiliza semilla fija 20261005 y 999 permutaciones.


## Adquisición de comparadores históricos

`python research_gpt6/code/acquire_historical_sources.py --out historical_sources`

Recupera el TEI de Penn LJS 419 y el manifiesto IIIF del Codex Bellunensis; produce inventario con URL, hashes, licencias e imágenes. Es metadato, no transcripción. Ejecución registrada en el informe 21 sobre caché de adquisiciones HTTP: 0 elementos text, 615 graphic y 331 lienzos. `--refresh` fuerza descarga; no requiere dependencias externas.

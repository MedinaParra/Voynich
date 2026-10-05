# Código y reproducibilidad

Estos scripts ejecutan reproducciones acotadas del corpus incluido en el commit fijado, sin depender de Jupyter. Son puertos explícitos de celdas de notebooks; consulte cada docstring y el JSON de salida. No ejecutan el análisis integral del proyecto ni prueban hipótesis semánticas.

## Fuente y entorno

- Repo: `https://github.com/cesarjz/Voynich`, commit `47e6a77dc9d5cd570c375f4aff710fa4a0567278`.
- Python 3.12.14; NumPy instalado para el script de permutaciones.
- SHA-256 STA1: `81c331b7d8e76761e27d350c3b37ccfbe192848e6c8a227bcb5d40fb29259b17`.

## Ejecución desde la raíz del repo

```bash
python research_gpt6/code/reproduce_core.py
python research_gpt6/code/reproduce_position.py
python research_gpt6/code/reproduce_f57v.py
```

Las ejecuciones finalizaron con código 0. Las salidas están en `research_gpt6/results/`. `reproduce_position.py` utiliza semilla fija 20261005 y 999 permutaciones.

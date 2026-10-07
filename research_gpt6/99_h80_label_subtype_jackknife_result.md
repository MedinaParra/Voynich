# H80 — Label-subtype jackknife robustness — Result

Status: **PASS**

- Actions run: `37649999102`
- Job: `112890523197`
- Artifact: `h80-label-subtype-jackknife-results`
- Artifact ID: `11495493392`
- Artifact ZIP SHA256: `41e5d179e3512f9cd093a683b4dbd77e49b165a87d33aceb403ee4cdd097f906`
- aligned exact-prefix events: 122
- represented folios: 27
- 999/999 randomizations per source

## Label-subtype audit
- `L0`: 7 events / 3 folios
- `Lc`: 8 / 7
- `Lf`: 52 / 12
- `Ln`: 22 / 6
- `Ls`: 11 / 3
- `Lt`: 22 / 9

Major preregistered subtypes: `Lf`, `Ln`, `Lt`.

## Source A
- omit `Lf`: `+0.1262855831`
- omit `Ln`: `+0.1151616902`
- omit `Lt`: `+0.0797289667`
- worst-case residual: `+0.0797289667`
- worst-case p: `0.029`

## Source B
- omit `Lf`: `+0.1173094582`
- omit `Ln`: `+0.1075202575`
- omit `Lt`: `+0.0793839011`
- worst-case residual: `+0.0793839011`
- worst-case p: `0.035`

## Interpretation
The H72 fifth-character EVA-`a` residual remains positive and significant when each major IVTFF label subtype (`Lf`, `Ln`, `Lt`) is removed in turn. The signal is therefore not attributable to any one of these major label classes in the locally matched sample.

This remains a token-form result. Language identification, semantics, translation, and decipherment are **NOT_RUN**.

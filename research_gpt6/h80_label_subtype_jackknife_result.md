# H80 — Label-subtype jackknife robustness — Result

Status: **PASS**

## Frozen execution
- Actions run: `37649999102`
- Job: `112890523197`
- Head commit: `2237bb34db5bb78b73adeb18732ab05edb96ffd6`
- Artifact: `h80-label-subtype-jackknife-results`
- Artifact ID: `11495493392`
- Artifact ZIP SHA-256: `41e5d179e3512f9cd093a683b4dbd77e49b165a87d33aceb403ee4cdd097f906`
- Source A blob: `2a4533ab9bdfa85db9bad602d590978953055df1`
- Source B blob: `7f491b574b65e5fba6b553e57372c3fa50e10fec`
- Randomizations: `999/999` for each source

## Parent sample
- aligned exact-prefix events: **122**
- represented folios: **27**

Label-subtype audit:
- `L0`: 7 events / 3 folios
- `Lc`: 8 / 7
- `Lf`: 52 / 12 — major
- `Ln`: 22 / 6 — major
- `Ls`: 11 / 3
- `Lt`: 22 / 9 — major

Frozen major-subtype rule therefore selected exactly `Lf`, `Ln`, and `Lt`.

All three leave-one-major-subtype-out scenarios satisfied the preregistered support gate:
- omit `Lf`: 70 events / 22 folios
- omit `Ln`: 100 / 26
- omit `Lt`: 100 / 23

## Source A
- omit `Lf`: equal-folio residual `+0.1262855831`
- omit `Ln`: `+0.1151616902`
- omit `Lt`: `+0.0797289667`
- worst-case residual: **+0.0797289667**
- worst-case one-sided p: **0.029**

## Source B
- omit `Lf`: equal-folio residual `+0.1173094582`
- omit `Ln`: `+0.1075202575`
- omit `Lt`: `+0.0793839011`
- worst-case residual: **+0.0793839011**
- worst-case one-sided p: **0.035**

## Frozen decision
H80 is **PASS** because both frozen transcriptions have more than one major subtype, every scenario satisfies support, both worst-case residuals remain strictly positive, both worst-case p-values are `<= 0.05`, and all `999/999` randomizations completed.

## Interpretation
The H72 fifth-character EVA-`a` residual is not attributable to any single major IVTFF label subtype represented in the frozen matched sample. Together with prior robustness checks, this strengthens a claim about reproducible token-form structure in this controlled label-versus-running-text comparison.

This result does **not** identify a morpheme, word meaning, phonetic value, language, plaintext, cipher mechanism, visual object, translation, or decipherment. Those claims remain **NOT_RUN**.

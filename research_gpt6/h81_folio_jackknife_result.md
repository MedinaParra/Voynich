# H81 — Leave-one-folio-out robustness — Result

Status: **PASS**

## Frozen execution
- Actions run: `37650959176`
- Job: `112893846609`
- Head commit: `5bb8581e24ffe708342b8f5ad0e391e8b83f9310`
- Artifact: `h81-folio-jackknife-results`
- Artifact ID: `11495389089`
- Artifact ZIP SHA-256: `7bfec248ad4e662c733edc4beaefd9201c137b8fbcf47d9b411b229abc55c232`
- Source A blob: `2a4533ab9bdfa85db9bad602d590978953055df1`
- Source B blob: `7f491b574b65e5fba6b553e57372c3fa50e10fec`
- Randomizations: `999/999` for each source

## Parent-sample and support gates
The frozen H72 parent sample reproduced exactly:
- **122 aligned exact-prefix events**
- **27 represented folios**

All 27 leave-one-folio-out scenarios retained 26 folios. The smallest retained event count was 111, so every scenario exceeded the preregistered support floor of 90 events / 25 folios.

Therefore neither `BLOCKED_SAMPLE_DRIFT` nor `BLOCKED_CONCENTRATION` applies.

## Source A
- worst-case omitted folio: `f89v2`
- worst-case equal-folio residual: **+0.0825147075**
- joint minimum-statistic one-sided p: **0.016**
- null minimum mean: `-0.0317963901`
- 999/999 randomizations completed

## Source B
- worst-case omitted folio: `f89v2`
- worst-case equal-folio residual: **+0.0746142746**
- joint minimum-statistic one-sided p: **0.044**
- null minimum mean: `-0.0283176644`
- 999/999 randomizations completed

## Frozen decision
H81 is **PASS**. In both frozen transcriptions, every individual-folio omission leaves a positive worst-case residual and the jointly corrected minimum statistic remains within the preregistered `p <= 0.05` gate.

The same folio, `f89v2`, is the worst omission in both sources. This is useful diagnostically: the effect is not caused by that folio, but its removal produces the smallest retained effect. Source B is close to the preregistered significance boundary (`p = 0.044`), so the robustness result should be described as positive but not overwhelming.

## Interpretation
H81 strengthens the narrow structural claim that the H72 fifth-character EVA-`a` excess in labels versus tightly matched running-text controls is not attributable to any single represented folio and reproduces across both frozen transcriptions.

It does **not** establish a morpheme, lexical meaning, phonetic value, language, plaintext, cipher mechanism, visual-object mapping, translation, or decipherment. Those claims remain **NOT_RUN**.

# H72 — Internal EVA `a` position localization result

Status: **PASS**

## Frozen execution
- Run: `37645697033`
- Job: `112875754025`
- Head commit: `f6dde7a098b1e31f209d42247ceafa4a19c2d5f1`
- Artifact: `11493383181` (`h72-internal-a-position-results`)
- Artifact SHA-256: `81ead33b1543f12dca031cd8402a696542465136a88b4337238825951a53b436`
- Source A blob: `2a4533ab9bdfa85db9bad602d590978953055df1`
- Source B blob: `7f491b574b65e5fba6b553e57372c3fa50e10fec`

## Count-only position audit
The aligned exact-prefix H71 sample contained 122 events across 27 folios.

Body-position eligibility (body = `t[2:-1]`):
- position 1: 122 events / 27 folios — eligible
- position 2: 122 / 27 — eligible
- position 3: 67 / 25 — eligible
- position 4: 27 / 14 — ineligible
- position 5: 9 / 8 — ineligible

Thus positions 1–3 formed the confirmatory family before inspecting their `a` outcomes.

## Source A
999/999 folio-level joint sign-flip permutations completed.

- body position 1: equal-folio residual **+0.0741656678**, event-weighted +0.0573652213, `p_FWER=0.231`
- body position 2: **+0.0091091117**, event-weighted +0.0267421910, `p_FWER=0.830`
- body position 3: **+0.1488989899**, event-weighted +0.1959897482, `p_FWER=0.037`

## Source B
999/999 folio-level joint sign-flip permutations completed.

- body position 1: equal-folio residual **+0.0902251795**, event-weighted +0.0654868356, `p_FWER=0.165`
- body position 2: **+0.0084033679**, event-weighted +0.0275045537, `p_FWER=0.840`
- body position 3: **+0.1414545455**, event-weighted +0.1904341927, `p_FWER=0.040`

## Replicated confirmatory position
**Body position 3** is the sole preregistered position satisfying positive effect plus max-stat FWER <=0.05 in both sources.

Because `body position 3 = t[4]`, this is the **fifth EVA character of the full token**. It is present in 67 aligned label events spanning 25 folios.

## Interpretation
H72 supports a reproducible localization of the H71 internal-`a` excess at the fifth EVA character / third character after the frozen two-character prefix. Positions 1 and 2 were positive descriptively but did not survive familywise correction.

This does not yet prove that the effect is truly left-anchored: for different token lengths, the fifth character occupies different positions relative to the token ending. A length-stratified follow-up is needed to distinguish absolute-left position from suffix-relative structure.

No morpheme, phonetic value, semantics, language, plaintext, cipher mechanism, translation or decipherment is established. These remain **NOT_RUN**.

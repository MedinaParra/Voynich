# H66 — Aligned cross-transcription consensus-label test — Result

Scientific status: **PASS**

Infrastructure status: **SUCCESS**

GitHub Actions:
- run: `37638993483`
- job: `112852629523`
- artifact: `11491800454`
- artifact SHA-256: `06888c99086bbe5be17a389d087964e2f36acbbb73f396334bfb8b9cedb09121`

## Aligned sample
- Source A label candidates: 780
- Source B label candidates: 669
- exact shared IVTFF label loci with identical token reading, matching Currier/hand, and eligible strict P controls in both sources: **286**
- represented folios: **30**
- aligned locus lists identical: true
- preregistered minimum: 100 events / 8 folios

## Source A
- full five-feature BA: `0.6748251748`
- full p: `0.001` (999/999)
- reduced `{frac_o, frac_a, starts_q}` BA: `0.6765734266`
- reduced p: `0.001` (999/999)
- retention of excess over chance: `1.0100000000`
- status: **PASS**

## Source B
- full five-feature BA: `0.6573426573`
- full p: `0.001` (999/999)
- reduced `{frac_o, frac_a, starts_q}` BA: `0.6520979021`
- reduced p: `0.001` (999/999)
- retention of excess over chance: `0.9666666667`
- status: **PASS**

## Interpretation
H65's reduced-model retention failure in Source B does **not** persist when the two transcriptions are forced onto the same physical label loci with identical EVA readings. On the consensus sample, the three-component signature retains essentially all of the five-feature classifier signal in both sources.

This supports the explanation that the H65 discrepancy was driven primarily by effective-sample/transcription differences rather than by a reproducible need for `frac_y` or `ends_y`.

The current minimal replicated signature is therefore:
- more EVA `o` in labels;
- more EVA `a` in labels;
- strong suppression of initial EVA `q` in labels relative to strict paragraph text.

This remains a token-form/context result. Language identification, semantic identification, translation and decipherment are **NOT_RUN**.

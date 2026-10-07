# H74 — Suffix-conditioned fifth-character `a` result

Status: **FAIL**

## Frozen execution
- Run: `37646486578`
- Job: `112878478827`
- Head commit: `4e58a41ce5cd38eeb5619ef4cc697be57df249c0`
- Artifact: `11494847263`
- Artifact SHA-256: `60e516484d56e3ae81ab834bd7e3ee69509dda8b280e974c3951161355c43758`

## Sample
- conditioned events: **30**
- represented folios: **17**
- preregistered minimum: >=25 events / >=10 folios — met.
- both frozen source blobs verified.

## Source A
- equal-folio residual at `t[4]`: **+0.1519607843**
- event-weighted residual: **+0.1333333333**
- null mean: **-0.0000637893**
- p(one-sided): **0.075**
- permutations: **999/999**

Length descriptives:
- length 6: n=18, mean residual +0.1111111111
- length 7: n=9, mean residual +0.2222222222

## Source B
- equal-folio residual at `t[4]`: **+0.1519607843**
- event-weighted residual: **+0.1333333333**
- null mean: **+0.0033317631**
- p(one-sided): **0.061**
- permutations: **999/999**

Length descriptives:
- length 6: n=18, mean residual +0.1111111111
- length 7: n=9, mean residual +0.2222222222

## Interpretation
The fifth-character `a` residual remains positive and numerically identical in both frozen transcriptions after conditioning on folio, Currier/hand, exact length, exact first-two-character prefix and exact final character. However, neither source meets the preregistered p<=0.05 criterion, so H74 is **FAIL**.

This valid failure means the stronger claim that the H72/H73 fifth-character effect survives exact suffix conditioning is not established. The positive point estimate motivates an explicitly new interaction/heterogeneity test, but H74 itself must not be reclassified or rescued by lowering thresholds.

No morphology, phonetics, semantics, language, plaintext, cipher mechanism, translation or decipherment is established.

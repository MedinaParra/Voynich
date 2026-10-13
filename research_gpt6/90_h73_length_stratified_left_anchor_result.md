# H73 — Length-stratified left-anchor result

Status: **PASS**

## Frozen execution
- Run: `37646130077`
- Job: `112877249422`
- Head commit: `24f4f8920d153f75d736b3c384499a194299f7a4`
- Artifact: `11493348662`
- Artifact SHA-256: `1101f0a538ad323cc140cddebe07dd60e04d9a9fbfac8a6322ee5170d22d9ec0`

## Sample audit
- exact length 6: **40 events / 22 folios** (threshold 30 / 8)
- exact length 7: **18 events / 11 folios** (threshold 15 / 8)

Both frozen source blobs verified.

## Source A
- length 6, index `t[4]`: equal-folio residual **+0.1698232323**; event-weighted +0.2493055556
- length 7, index `t[4]`: equal-folio residual **+0.2548209366**; event-weighted +0.2171717172
- equal-stratum combined statistic: **+0.2123220845**
- null mean: -0.0026394910
- p(one-sided): **0.007**
- permutations: **999/999**

## Source B
- length 6: equal-folio residual **+0.1613636364**; event-weighted +0.2400000000
- length 7: equal-folio residual **+0.2548209366**; event-weighted +0.2171717172
- equal-stratum combined statistic: **+0.2080922865**
- null mean: -0.0005515502
- p(one-sided): **0.009**
- permutations: **999/999**

## Interpretation
The fifth EVA character (`t[4]`) shows a positive label-vs-paragraph `a` residual in both exact-length strata and in both frozen transcriptions. At length 6 this character is penultimate; at length 7 it is antepenultimate. This favors an absolute-left positional constraint over a single fixed suffix-relative explanation.

It does not prove that the position is a morpheme boundary or identify phonetics, semantics, language, plaintext, cipher mechanism, translation or decipherment. Those remain **NOT_RUN**.

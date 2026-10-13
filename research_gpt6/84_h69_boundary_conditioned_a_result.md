# H69 — Boundary-conditioned internal EVA a enrichment — Result

Scientific status: **FAIL**

Infrastructure status: **SUCCESS**

GitHub Actions:
- run: `37640811477`
- job: `112858960338`
- artifact: `11492665739`
- artifact SHA-256: `3ddacb5639473189c1dc2bc8a37d0530e9908f588d45636f89069fcb945ed584`

## Common sample
- exact-agreement consensus labels, original length >=5
- strict-P controls matched on folio, Currier, hand, exact token length, exact first two EVA characters and exact final EVA character
- common retained pairs: **54**
- represented folios: **19**
- preregistered minimum: 50 pairs / 8 folios

## Source A
- residual EVA `a` mean difference L-P: `+0.0373456790`
- null mean: `-0.0004056526`
- one-sided Monte Carlo p: `0.099`
- permutations: `999/999`
- status: **FAIL**

## Source B
- residual EVA `a` mean difference L-P: `+0.0256172840`
- null mean: `+0.0016420742`
- one-sided Monte Carlo p: `0.207`
- permutations: `999/999`
- status: **FAIL**

## Interpretation
The H68 residual-`a` enrichment remains directionally positive after extremely strict boundary matching, but it does not meet the preregistered significance criterion in either frozen transcription.

Therefore we cannot claim that internal EVA `a` enrichment is independent of the first-two/final-character families. The current evidence is more consistent with a coupled morphological/compositional regime in which boundary patterns and internal `a` usage covary.

The test is also much smaller (54 pairs) than H68 (230 pairs), so the result does not prove absence of an independent internal effect; it shows that the stronger independence claim was not established by this preregistered test.

Semantic identity, phonetic value, language identification, translation and decipherment remain **NOT_RUN**.

# H68 — Internal o/a enrichment after boundary ablation — Result

Scientific status: **PASS**

Infrastructure status: **SUCCESS**

GitHub Actions:
- run: `37640316941`
- job: `112857206416`
- artifact: `11492245287`
- artifact SHA-256: `89fc27db42009506ea427ecfa9d6849f717bbb01388d3967e984c7b921684e6f`

## Sample
Both frozen transcriptions yielded the same H66 aligned-consensus event set after requiring original token length >=5:
- retained pairs: **230**
- represented folios: **30**
- residual body: exactly `token[2:-1]`
- permutations: **999/999 per source**
- multiplicity: max-stat FWER across residual `o` and `a`

## Source A
- residual `a` mean difference L-P: `+0.0781832298`
- residual `a` t: `4.9989516278`
- residual `a` p_FWER: `0.001`
- residual `o` mean difference L-P: `+0.0382660455`
- residual `o` t: `2.2916530851`
- residual `o` p_FWER: `0.051`

## Source B
- residual `a` mean difference L-P: `+0.0731107660`
- residual `a` t: `4.5845008086`
- residual `a` p_FWER: `0.001`
- residual `o` mean difference L-P: `+0.0314958592`
- residual `o` t: `1.9402161664`
- residual `o` p_FWER: `0.083`

## Replicated component
- `residual_frac_a`: **PASS**
- `residual_frac_o`: **does not replicate under the preregistered familywise threshold**

## Interpretation
The label-vs-paragraph compositional difference is not solely a word-boundary effect. Even after removing the first two and final EVA characters, labels contain substantially more internal EVA `a` than their exact-matched strict paragraph controls, and this effect replicates in both frozen transcriptions with familywise-corrected p=0.001.

The analogous residual `o` enrichment is positive in both sources but does not meet the preregistered replicated significance threshold.

This supports a more specific current model: initial `q` suppression is a boundary/context signature, whereas EVA `a` enrichment extends into the internal token body. It does not identify what EVA `a` or `q` mean.

Language identification, semantic identification, translation and decipherment remain **NOT_RUN**.

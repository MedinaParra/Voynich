# H65 — Exact-consensus locus replication result

Status: **FAIL**.

Frozen execution evidence:
- GitHub Actions run: `37614094070`
- workflow head SHA: `3f0077a1d92975308c8f051458b0bf9410e37b75`
- artifact: `consensus-locus-h65-results`, ID `11478712588`
- artifact SHA-256: `7c61087dfe981ac4bcda40d18a9ea217ad9652bffbfec2a0b83ad08c7610c8c6`
- primary IVTFF blob: `2a4533ab9bdfa85db9bad602d590978953055df1`
- independent Takahashi blob: `7f491b574b65e5fba6b553e57372c3fa50e10fec`

## Frozen support
- common loci: 5,213
- exact-consensus loci: 2,283
- metadata disagreements: 0
- consensus positive label loci: 482
- matched/evaluable pairs: 246
- evaluable quires: H, I, M, O, S (5)
- consensus-label survival vs primary candidate labels: 0.6179487
- 999/999 permutations completed

## Primary result
- observed balanced accuracy: **0.5345528455**
- null mean BA: **0.4999186178**
- null max BA: **0.5711382114**
- Monte Carlo p: **0.112**
- quires above chance: **4/5**
- per-quire BA: H 0.5000, I 0.5091, M 0.5128, O 0.6724, S 0.5274

The preregistered gate required BA > 0.55 and p <= 0.01 in addition to the support criteria. H65 therefore **FAILS**. The gate is not relaxed post hoc.

## Interpretation
H65 does not replicate the edge-ablated functional label-vs-running-text signal when restricted to exact transcription consensus loci. This does **not** invalidate H60-H62; it narrows their interpretation. The difference may depend on information removed by the exact-consensus restriction, on transcription-specific token choices, on token-edge information in this stricter subset, or on sampling/support changes.

This result does not support semantics, language identification, plaintext, translation, or decipherment.

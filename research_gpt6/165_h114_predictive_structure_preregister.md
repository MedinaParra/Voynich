# H114 — Held-out predictive structure beyond frozen generative controls: preregistration

## Purpose
Test whether the Voynich transcription contains out-of-sample sequential information not captured by the strongest already-frozen H96 synthetic generator family. This is a structural test only. It does not test semantics, language identity, plaintext, translation, or decipherment.

## Frozen starting evidence
H96 is the immediate predecessor and is not to be retuned. Its verified run on the current experimental head is run `38717159875`, job `116362543811`, with 200 eligible folios, 200 replicas per family, partition hash `50c82d6b48da54c3e2a1b70f14743f4c41bb2112ba74976de7185147d9d1766c`, statistics hash `36949af6b6738b29bbf5a261508a1b6f8d7deb8258b62f7534a32e0c45b5a070`, and overall H96 status **FAIL**. The strongest H96 family by frozen holdout endpoint count is `token_markov1` (4/8 endpoints); it is therefore the primary null for H114. No H96 family is to be altered after this preregistration.

## Frozen corpus and partition
Use the same Takahashi source and exact H96 development/holdout folio partition. Verify the source SHA-256 equals `32b11a0b584a75bbe9817c96a316a246f82d02d69996d789bc2cb908190bab77` and the partition hash equals the H96 value above. Any mismatch => **BLOCKED**.

## Primary representation
Token sequence exactly as parsed by the existing H96 code path. Folio boundaries are hard boundaries; no context may cross a folio boundary. No illustrations, labels, geometry, folio subject labels, EVA semantic guesses, or manually selected lexical anchors may enter the model.

## Primary prediction task
For every token position in the held-out folios with at least two preceding tokens inside the same folio, predict the next token distribution from models fitted only on development folios.

Compare three frozen predictors:
1. `UNIGRAM`: development-token unigram with additive alpha=0.5.
2. `TOKEN_M1`: first-order token Markov model with additive alpha=0.5.
3. `TOKEN_M2`: second-order token Markov model with hierarchical backoff M2 -> M1 -> unigram and additive alpha=0.5 at each observed context.

Vocabulary is frozen from development folios plus one `<UNK>` symbol. Held-out unseen tokens map to `<UNK>`; no held-out vocabulary information may be used in fitting.

## Primary endpoint
Mean held-out token negative log likelihood (NLL, natural-log nats/token), pooled over all eligible held-out positions.

Define:
- `D10 = NLL_UNIGRAM - NLL_TOKEN_M1`
- `D21 = NLL_TOKEN_M1 - NLL_TOKEN_M2`

Positive values mean added sequential context improves prediction.

## Frozen synthetic null
Generate 200 synthetic corpora from the already-frozen H96 `token_markov1` family using its frozen seed/rules, preserving the H96 development/holdout firewall and token counts. For every replica, refit UNIGRAM/TOKEN_M1/TOKEN_M2 only on that replica's development partition and evaluate its held-out partition identically. This produces null distributions for D10 and D21.

No generator parameters may be retuned from H96. If exact H96 token_markov1 replay cannot be reproduced from repository code, H114 = **BLOCKED**, not substituted with a new null.

## Decision rule
Infrastructure **PASS** requires source hash, partition hash, non-empty train/test positions, deterministic replay, and exactly 200 valid null replicas.

Scientific H114 **PASS** requires BOTH:
- observed `D10 > 0` and exceeds the 99th percentile of synthetic-null D10; and
- observed `D21 > 0` and exceeds the 99th percentile of synthetic-null D21.

Otherwise H114 = **FAIL**. A missing required computation = **NOT_RUN**. Infrastructure preventing the frozen computation = **BLOCKED**.

The 99th-percentile rule is one-sided and frozen before execution. No alternative context length, smoothing constant, subset, token normalization, or favorable folio selection may be substituted after observing the result.

## Secondary diagnostics (non-decisional)
Report per-held-out-folio NLL for all three predictors; fraction of folios with D10>0 and D21>0; `<UNK>` rate; vocabulary size; eligible prediction count. These diagnostics cannot turn a FAIL into PASS.

## Interpretation ceiling
Even H114 PASS would mean only that the frozen Voynich transcription contains held-out sequential predictive structure not reproduced by the frozen H96 token-Markov-1 generator. It would not establish natural language, semantics, plaintext, translation, or decipherment.

Semantics: **NOT_RUN**
Language identification: **NOT_RUN**
Translation: **NOT_RUN**
Decipherment: **NOT_RUN**

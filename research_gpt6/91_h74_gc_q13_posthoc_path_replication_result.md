# H74 — GC/v101 replication of the H73 post-hoc Q13 optimum result

Status: **FAIL**.

This records the completed execution of the preregistered protocol in `90_h74_gc_q13_posthoc_path_replication_preregistration.md`. It does not alter H73 and makes no reading-order, semantic, language, translation, or decipherment claim.

## Execution evidence

- Branch: `experiment/h58-strict-l-vs-p`.
- Workflow: `H74 GC v101 Q13 path replication`.
- Run: `37626248148`, conclusion `success`.
- Job: `112808636765` (`h74-gc-q13-posthoc-path-replication`), conclusion `success`.
- Experimental head executed: `28c1318d2917e29d78c3add04e049acde822ec0a` (PR merge checkout `0d1dc922468bb75eb9968e4346163aebf0a5a7ce`).
- GC/v101 source SHA-256: `b09570cb6c993bc2d87134d115e60a978650a8a6495483ddbb1f6005a586096f`, matching the frozen expected hash.
- Artifact: `h74-gc-q13-posthoc-path-replication-results`, ID `11483329467`.
- Artifact SHA256: `9d10a71a8ec22fb68f6029244c92928a0a41cbac176b4ec69933e9c5e73b773d`.
- Exact orders scored: **120/120**.

## Frozen candidate

`77|82 -> 76|83 -> 75|84 -> 78|81 -> 79|80`

Current physical nesting order:

`75|84 -> 76|83 -> 77|82 -> 78|81 -> 79|80`

## Result

- candidate score: **0.7182146753922127**;
- current nested score: **0.6734273220203645**;
- candidate minus current: **+0.04478735337184825**;
- exact null mean: **0.6678786280557669**;
- maximum score among all orders: **0.732315348126516**;
- candidate exact rank: **9/120**;
- exact one-sided p: **0.08333333333333333**;
- percentile at or below candidate: **0.9333333333333333**;
- GC/v101 Q13 vocabulary: **1689** types.

All frozen validity gates passed. The candidate scored above the current nested sequence, satisfying the first scientific criterion, but the exact permutation p-value was greater than the preregistered `0.05` threshold. Therefore H74 is **FAIL**.

## Conservative interpretation

The Q13 path discovered post hoc in ZL/Takahashi is relatively high-scoring in the previously unused GC/v101 transcription, but not unusually high enough under the exact 120-order null to satisfy the frozen confirmation rule. It therefore remains a discovery-set candidate and is not promoted as evidence of historical reading order or semantic continuity.

H73 remains **FAIL**.
H74: **FAIL**.
Q20: **NOT_RUN/BLOCKED_FOR_EXACT_SEQUENCE**.
Semantic identification: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

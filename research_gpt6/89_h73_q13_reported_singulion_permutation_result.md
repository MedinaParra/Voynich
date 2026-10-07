# H73 — Q13 reported-singulion exact permutation falsification result

Status: **FAIL**.

This records execution of the preregistered protocol in `88_h73_q13_reported_singulion_permutation_preregistration.md`. The workflow completed successfully and all 120 exact permutations were scored in both frozen transcriptions.

## Execution evidence

- Workflow: `H73 Q13 reported singulion permutation`.
- Run: `37617236165` (run number 1), conclusion `success`.
- Job: `112778425012` (`h73-q13-reported-singulion-permutation`), conclusion `success`.
- Experimental branch head executed: `8bc776dc601a76fb9a848c43f720381c66aa9f60` (PR merge checkout `05178ec3b5c7dd20adf8a153b363e59d1273087f`).
- Artifact: `h73-q13-reported-singulion-permutation-results`, ID `11481026335`.
- Artifact SHA256: `9521b412fecb66faa3d7611d0aee23f17bdb94f7a739c765263d3e56f71bb9d0`.

## Frozen sequences

Current physical nesting order, outer-to-inner:

`75|84 -> 76|83 -> 77|82 -> 78|81 -> 79|80`

Secondary-reported Layfield–Davis Q13 sequence:

`77|82 -> 78|81 -> 75|84 -> 76|83 -> 79|80`

## Zandbergen–Landini

Validity gates all passed:
- all folios 75–84 contained P text;
- bifolio P-token counts ranged from **1,022** to **1,527**;
- vocabulary: **1,460** types;
- exact permutations scored: **120/120**.

Scores:
- reported sequence: **0.7330207126226126**;
- current nested sequence: **0.749444508657555**;
- reported minus current: **-0.016423796034942373**;
- exact null mean: **0.7412388349386262**;
- exact permutation p: **0.6666666666666666**;
- exact rank: **79/120**;
- percentile at or below reported: **0.35**;
- maximum score: **0.7873437783269416**.

Source status: **FAIL**.

## Takahashi IT2a

Validity gates all passed:
- all folios 75–84 contained P text;
- bifolio P-token counts ranged from **1,030** to **1,535**;
- vocabulary: **1,487** types;
- exact permutations scored: **120/120**.

Scores:
- reported sequence: **0.7247845865041738**;
- current nested sequence: **0.7424439616571716**;
- reported minus current: **-0.01765937515299787**;
- exact null mean: **0.7335352403857053**;
- exact permutation p: **0.65**;
- exact rank: **77/120**;
- percentile at or below reported: **0.36666666666666664**;
- maximum score: **0.7830132651656831**.

Source status: **FAIL**.

## Decision

The preregistration required the reported sequence to score strictly above the current nested sequence and to fall in the upper 5% of all 120 permutations in **both** frozen transcriptions. It satisfies neither condition in either source.

H73: **FAIL**.

Q20 remains `NOT_RUN_BLOCKED_FOR_EXACT_SEQUENCE`.

## Post-hoc observation — not part of the H73 claim

Both ZL and Takahashi independently produced the same maximizing undirected path (the reverse is score-equivalent because adjacency cosine is symmetric):

`77|82 -> 76|83 -> 75|84 -> 78|81 -> 79|80`

Maximum scores:
- ZL: **0.7873437783269416**;
- Takahashi: **0.7830132651656831**.

This path was discovered **after** H73 execution and therefore cannot be promoted using ZL or Takahashi as confirmatory evidence. It may only be used as a prospectively frozen hypothesis in a genuinely unconsulted representation/transcription, such as GC/v101.

## Conservative interpretation

Under a simple preregistered P-text TF-IDF adjacency metric and an exact all-orders permutation null, the Q13 sequence attributed to Layfield–Davis by the frozen secondary report is not unusually continuous and is less continuous than the current outer-to-inner physical nesting order in both admitted EVA-family transcriptions.

This weakens that specific Q13 ordering under this metric. It does **not** refute the broader physical singulion hypothesis, does not reproduce the primary article's exact LSA pipeline, and does not address visual/codicological evidence.

Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

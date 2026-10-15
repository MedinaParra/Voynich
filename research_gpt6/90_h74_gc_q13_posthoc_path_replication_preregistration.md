# H74 — GC/v101 replication of the H73 post-hoc Q13 optimum

Status before execution: **NOT_RUN**.

## Rationale and strict discovery/confirmation split

H73 prospectively tested the secondary-reported Layfield–Davis Q13 sequence and returned **FAIL** in both ZL and Takahashi. After scoring all 120 physical-bifolio permutations, both discovery transcriptions happened to return the same maximizing undirected path:

`77|82 -> 76|83 -> 75|84 -> 78|81 -> 79|80`

Because this path was discovered after inspecting ZL and Takahashi, neither source can provide confirmatory evidence for it. H74 therefore freezes that path **before any Q13 order score is inspected in GC/v101** and tests it only in the previously unused-for-order Glen Claston transcription.

H74 does not change H73 from FAIL and does not redefine the Layfield–Davis sequence.

## Frozen source

Repository: `noah-chelednik/voynich-data`

Commit: `472ef7366606a799fc8f1044c037e06b413f6ddd`

File: `data_sources/cache/GC2a-n.txt`

Required SHA-256: `b09570cb6c993bc2d87134d115e60a978650a8a6495483ddbb1f6005a586096f`

Any hash mismatch is **BLOCKED**.

## Frozen Q13 units and candidate

Physical bifolia:

- `75|84`
- `76|83`
- `77|82`
- `78|81`
- `79|80`

Current physical nesting order, outer-to-inner:

`75|84 -> 76|83 -> 77|82 -> 78|81 -> 79|80`

H73 post-hoc candidate frozen for independent GC testing:

`77|82 -> 76|83 -> 75|84 -> 78|81 -> 79|80`

Its reverse is treated as score-equivalent because the frozen adjacency metric is symmetric.

No candidate edge/order may be altered after H74 execution.

## Frozen GC text selection

1. retain only `P*` paragraph loci from folios 75 through 84;
2. remove IVTFF markup conservatively;
3. split away unresolved `?` material;
4. retain standalone alphanumeric GC/v101 transcription tokens of length >=2;
5. preserve GC/v101 symbols exactly as represented; do not map or transliterate them to EVA;
6. aggregate P tokens from both folios belonging to each physical bifolio.

No IT/ZL/Takahashi token or token identity is used anywhere in the H74 score.

## Frozen validity gates

- all ten folio numbers 75–84 must contain at least one GC P token;
- each bifolium aggregate must contain >=50 GC P tokens;
- Q13 GC vocabulary must contain >=100 distinct token types;
- exactly all 120 physical-bifolio permutations must be scored.

Failure of a gate is **BLOCKED**.

## Frozen representation and score

Use the exact H73 TF-IDF formulation, applied solely to GC/v101:

- five bifolio documents;
- raw term frequency;
- `idf(t) = log((1 + 5)/(1 + df_t)) + 1`;
- TF*IDF vectors;
- L2 normalization;
- cosine similarity between bifolio vectors;
- sequence score = mean cosine across the four adjacent transitions.

No dimensionality reduction, embeddings, learned weights, sequence search, fuzzy transliteration, or visual information is used.

## Exact null

Enumerate all `5! = 120` Q13 bifolio orders.

Report:

- frozen candidate score;
- current nested score;
- exact null mean;
- candidate rank;
- exact one-sided `p = count(score >= candidate_score)/120`;
- maximum score and all tied maximizers;
- candidate-minus-current difference.

## Decision rule

H74 = **PASS** only if all validity gates pass and:

1. the frozen H73-derived candidate scores strictly above current nested order; and
2. exact permutation `p <= 0.05` in GC/v101.

H74 = **FAIL** if the test is valid but either scientific criterion fails.

H74 = **BLOCKED** if source/sample/execution gates fail.

Before execution H74 is **NOT_RUN**.

## Interpretation boundary

A PASS would establish a prospectively confirmed **cross-transcription/alphabet Q13 lexical-adjacency candidate**: an order selected post-hoc in ZL/Takahashi but found independently unusual under the same frozen metric in GC/v101.

It would still not prove historical reading order, semantic continuity, or the physical singulion hypothesis. GC describes the same manuscript, and the candidate was selected from the manuscript itself. A deliberately shuffled-known-text calibration remains required before interpreting adjacency maximization as evidence of meaningful reading sequence.

A FAIL would mean the H73 optimum does not generalize prospectively to GC/v101 and should remain a discovery-set artifact/candidate only.

Q20: **NOT_RUN/BLOCKED_FOR_EXACT_SEQUENCE**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

# Holistic topology H1 result

Status: **PASS**.

This records the frozen experiment preregistered in `42_holistic_outside_box_pivot_preregistration.md`.

## Execution evidence

- Branch: `experiment/lexical-anchor-replication`
- Experimental head tested: `8f2b3be91e90c28627f83fa4651edc5e180c6b9b`
- Pull-request merge checkout: `4d7443a9f776f91e47a24dd3f9f03c933de2a320`
- GitHub Actions run: `37546798669` (`Voynich frozen experiments`, run 35)
- Job: `112552628856` (`holistic-topology`)
- Job conclusion: `success`
- Artifact: `holistic-topology-results`, ID `11451212068`
- Artifact SHA256: `a5d428bb2a9d013a0b8889f9d39d0ae57c6ea6bc7b1ef43088406595b0abd60f`
- Frozen corpus blob: `2a4533ab9bdfa85db9bad602d590978953055df1`
- Eligible folios: 205
- Confound-controlled evaluable queries: 146 per family
- Permutations: 999/999 per family

## Family A — glyph/character structure

- status: **PASS**
- MRR: `0.3700198681677867`
- Recall@1: `0.1917808219178082`
- Recall@3: `0.4794520547945205`
- mean true-neighbor cosine distance: `0.08695805421153799`
- mean non-neighbor cosine distance: `0.14623471253940254`
- Monte Carlo p: `0.001`

## Family B — token morphology

- status: **PASS**
- MRR: `0.4025030075160065`
- Recall@1: `0.23972602739726026`
- Recall@3: `0.4931506849315068`
- mean true-neighbor cosine distance: `0.08374477256445569`
- mean non-neighbor cosine distance: `0.13169784556447234`
- Monte Carlo p: `0.001`

## Frozen decision

Both independent feature families beat their matched null at p <= .05, both effects point in the preregistered direction, and the confound-controlled evaluation remained executable. Therefore H1 is **PASS** under the frozen cross-view criterion.

## Scientific interpretation

This supports a reproducible local-topology signal in the manuscript under two independent textual views after the implemented matching controls. Immediate physical neighbors are, on average, more similar than matched non-neighbors in both feature families.

This result does **not** show that the surviving folio order is the original generating order. It does **not** identify a language, plaintext, cipher, semantic label, author, or translation. It also does not rescue the earlier Lc/Lf lexical-anchor interpretation, which remains weakened by the exact-length control.

The justified next step is a separately preregistered H2 that reconstructs a candidate topology/order without semantic or illustration leakage and tests it out-of-view/out-of-sample rather than optimizing and evaluating on the same representation.

Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

# H65 — Bidirectional zero-shot leave-one-feature-out robustness preregistration

Status: **NOT_RUN**.

## Motivation
H63 and H64 established bidirectional zero-shot transfer of the strict L* label-locus versus P* paragraph-text distinction between the frozen Zandbergen-Landini (ZL) and Takahashi transcriptions using five frozen token-form predictors. H65 asks whether that bidirectional transfer collapses when any one predictor is removed.

This is a mechanism/robustness falsification. It does not search for new features and does not assign semantics.

## Frozen sources and samples
Use exactly the immutable sources already admitted by H63/H64:
- ZL Git blob `2a4533ab9bdfa85db9bad602d590978953055df1`;
- Takahashi Git blob `7f491b574b65e5fba6b553e57372c3fa50e10fec`.

Use the same H60-H64 extraction and matching rules independently in each transcription:
- certain single-token generic `L` positive;
- generic `P` controls only;
- exact folio + exact token length + Currier/hand metadata when present;
- deterministic control selection, seed `20261007`;
- no manual recoding or token edits.

Require >=60 test pairs and >=8 represented test folios in each transfer direction, otherwise **BLOCKED**.

## Frozen feature set
The full H60-H64 vector is:
1. fraction `o`;
2. fraction `a`;
3. fraction `y`;
4. starts `q`;
5. ends `y`.

H65 contains exactly five preregistered ablations. Each model removes one and only one feature:
- `minus_frac_o`;
- `minus_frac_a`;
- `minus_frac_y`;
- `minus_starts_q`;
- `minus_ends_y`.

No replacement feature is allowed.

## Bidirectional zero-shot evaluation
Evaluate both directions separately:
- ZL -> Takahashi;
- Takahashi -> ZL.

For each test folio and each ablation:
1. exclude training-source pairs from the same folio;
2. fit standardization only on remaining training-source tokens and only on retained features;
3. fit the same nearest-class-mean classifier family;
4. classify the held-out target-source matched pairs with no target-source fitting.

No test-source token may contribute to standardization, class means, model choice, or feature choice.

Primary statistic for every direction x ablation cell is aggregate balanced accuracy.

## Null
For each transfer direction, use exactly **999** deterministic within-pair identity-swap permutations, seed `20261007`. Predictions for all five ablations are frozen before the null. The same permutation identity vector is applied across the five ablations within a direction.

For each cell: `p = (1 + count(null_BA >= observed_BA))/1000`.

No post-hoc ablation selection is permitted.

## Decision
H65 is **PASS** only if **all 10** preregistered direction x ablation cells satisfy:
1. valid frozen sample;
2. 999/999 permutations complete;
3. observed BA > 0.5;
4. Monte Carlo p <= 0.05.

This conjunction is intentionally strict. No averaging across ablations or directions can rescue a failed cell.

H65 is **FAIL** if execution is valid and at least one of the 10 cells misses BA > 0.5 or p <= 0.05.

H65 is **BLOCKED** only for source verification, frozen extraction, or sample/infrastructure failure that prevents valid execution without protocol modification.

Before execution: **NOT_RUN**.

## Interpretation boundary
PASS would show that bidirectional zero-shot transfer does not require any single one of the five frozen EVA token-form predictors by itself. It would not show invariance to arbitrary feature changes and would not rule out a distributed EVA-representation effect.

FAIL would identify that the current robust transfer claim depends materially on at least one specific frozen feature; H63/H64 would remain valid full-model PASS results, but the stronger no-single-feature-necessity claim would be rejected.

Regardless of outcome, this experiment does not identify label semantics, language, plaintext, cipher, or translation. Historical Lc-vs-Lf and subtype/semantic-anchor tests remain **FAIL**.

Semantic identification: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

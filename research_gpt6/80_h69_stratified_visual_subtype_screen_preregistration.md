# H69 — Documentary-stratified visual-subtype morphology screen

Status before execution: **NOT_RUN**.

## Question

Within the exact documentary strata admitted by H68, does token-internal symbol-repetition structure predict either of two frozen visual-referent subtype contrasts out of folio?

This is a **candidate visual-subtype morphology screen**. It is not a translation or semantic-identification test.

## Frozen source

Exactly the H67/H68 source:

- `noah-chelednik/voynich-data`
- commit `472ef7366606a799fc8f1044c037e06b413f6ddd`
- path `data_sources/cache/IT_ivtff_1a.txt`
- Git blob SHA-1 `4201d762a4bd6e9014e0e796d72dd5c3efb597da`
- SHA-256 `db624a731114f26854bbfe3a59d40827fa8911be46d086b6c558d99e557241ee`

Hash mismatch is **BLOCKED**.

## Frozen contrast family

Exactly two contrasts are tested:

A. `Lc` vs `Lf`, restricted to exact strata `O|A|1` and `S|A|1`.

B. `Ln` vs `Lt`, restricted to exact stratum `M|B|2`.

`Ls` and `Lz` are excluded because H68 showed zero exchangeable tokens under the preregistered documentary control. No additional pairwise contrast may be added after results.

## Frozen sample construction

For each contrast independently:

1. parse known alphabetic tokens exactly as H67/H68;
2. restrict to the frozen class pair and frozen exact `(Q,L,H)` strata;
3. construct deterministic one-to-one matched pairs **within exact `(Q,L,H,folio,token_length)` cells**;
4. within each cell, sort tokens lexicographically and use seed `20261007` only to break deterministic equal-token multiplicity ordering if needed;
5. take `min(n_class0,n_class1)` pairs in that cell; unmatched excess tokens are excluded;
6. no pair may cross folio, quire, Currier, hand, or token length.

This removes token length and local documentary position as direct class predictors.

## Frozen validity gates

Each of the two contrasts must independently yield:

- >=20 matched pairs;
- >=5 distinct represented folios;
- both classes present in every matched pair by construction;
- at least one training folio remains for every held-out folio.

If either frozen contrast fails a validity gate, H69 = **BLOCKED**. We do not drop the blocked contrast and continue with the other one.

## Frozen representation

Reuse the H66 symbol-renaming-invariant representation only:

1. `unique_fraction`;
2. `singleton_type_fraction`;
3. `max_frequency_fraction`;
4. `adjacent_equal_fraction`;
5. `first_last_equal`.

Token length is not a predictor and is exactly matched. No EVA symbol identity, prefix/suffix identity, character n-gram, full-token identity, or manually selected lexical form is used.

## Frozen classifier and holdout

For each contrast:

- leave one **folio** out;
- z-standardize features on training folios only;
- fit nearest class centroid on training folios only;
- classify all matched tokens in the held-out folio;
- aggregate predictions over all held-out folios;
- primary score = balanced accuracy.

No parameter may be learned from the held-out folio.

## Permutation test

Use exactly **9,999** paired permutations with seed `20261007`.

For each permutation and each contrast:

1. independently swap the two class labels inside every matched pair with probability 0.5;
2. rerun the entire leave-one-folio-out training and prediction procedure under those permuted labels;
3. compute the permuted balanced accuracy.

This retrains the classifier under each null permutation; predictions are not frozen from the observed labels.

## Familywise correction

The two contrasts form one frozen family. For every permutation compute the maximum excess above chance across the two contrasts:

`max(BA_A - 0.5, BA_B - 0.5)`.

For each observed contrast, familywise Monte Carlo p is:

`(1 + count(null_max >= observed_BA - 0.5)) / 10000`.

The original stringent lexical-anchor discovery threshold is retained: familywise `p <= 0.001`.

## Decision rule

H69 = **PASS** only if:

- both contrasts pass all validity gates and complete 9,999/9,999 permutations; and
- at least one of the two frozen contrasts has observed BA > 0.5 and familywise p <= 0.001.

H69 = **FAIL** if both contrasts are valid but neither reaches the frozen familywise criterion.

H69 = **BLOCKED** if either contrast cannot satisfy the frozen validity gates or execution cannot complete as preregistered.

Before execution H69 is **NOT_RUN**.

## Interpretation boundary

A PASS would permit only the phrase **`visual-subtype morphology candidate`** for the specific passing frozen contrast(s). It would show out-of-folio discrimination inside matched documentary/length cells using alphabet-renaming-invariant morphology.

It would **not** satisfy the full historical `PASS_LEXICAL_ANCHOR` gate, because running-text recurrence and an independent transcription replication would still be required. It would not license natural-language glosses, object names, language identification, translation, or decipherment.

The historical `Lc`-vs-`Lf` FAIL remains a valid prior negative; H69 is a new source/sample/representation test and must be reported alongside, not used to erase it.

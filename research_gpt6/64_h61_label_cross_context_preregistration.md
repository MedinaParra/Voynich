# H61 — Strict label-vs-paragraph cross-context generalization preregistration

Status: **NOT_RUN**.

## Motivation

H60 and the broader label-locus-vs-running-text test both produced **PASS** under leave-one-folio-out evaluation, while `Lc` versus `Lf`, topology-conditioned lexical anchoring, and exact-length subtype tests are **FAIL**. A remaining non-semantic alternative is that the L-vs-P signal is specific to shared scribal or physical-document contexts rather than a portable label-register distinction.

H61 therefore asks whether the already observed strict L-vs-P token-form distinction generalizes when complete scribal hands and complete quires are held out. This is a falsification of context-specificity, not a search for new features.

## Frozen corpus and pairs

Use corpus blob `2a4533ab9bdfa85db9bad602d590978953055df1` and seed `20261007`.

Pair construction is inherited unchanged from H60:
- positives: certain single-token `L*` loci;
- controls: tokens only from generic `P*` paragraph loci; `L*`, `C*`, `R*`, and unknown generic locus types are excluded;
- exact match on folio, token length, Currier state, and hand state;
- deterministic control draw using seed `20261007`;
- no manual recoding and no illustration or semantic information.

The pair set is frozen before either cross-context view is scored.

## Frozen predictors

Exactly the H60 five token-form predictors:
- fraction `o`;
- fraction `a`;
- fraction `y`;
- starts `q`;
- ends `y`.

Absolute length, folio identity, hand, quire, Currier state, section, locus subtype, illustration class, topology, proposed plaintext and semantics are prohibited predictors.

## Cross-context views

### View A — leave-one-hand-out

Use the IVTFF page `$H` field only as the grouping variable. Unknown hand `?` is excluded from this view. A hand is eligible only if it contains at least **10 matched pairs**. Require at least **2 eligible hands** and at least **60 pairs** across eligible hands; otherwise this view is **BLOCKED**.

For each eligible hand, train on every other eligible hand and test on the held-out hand. Standardization is fitted only on the training fold. Classifier remains nearest-class-mean.

### View B — leave-one-quire-out

Use the IVTFF page `$Q` field only as the grouping variable. Unknown quire `?` is excluded. A quire is eligible only if it contains at least **10 matched pairs**. Require at least **2 eligible quires** and at least **60 pairs** across eligible quires; otherwise this view is **BLOCKED**.

For each eligible quire, train on every other eligible quire and test on the held-out quire, with training-fold-only standardization and the same nearest-class-mean classifier.

## Primary statistic

For each view, aggregate balanced accuracy over all held-out observations from eligible groups. Group identities are never predictors.

## Null

Exactly **999** deterministic randomizations with seed `20261007`. For each permutation, independently swap L/P identity within each frozen matched pair with probability 0.5 and rerun the complete grouped holdout pipeline for both views.

For each view:
`p = (1 + count(null_BA >= observed_BA)) / 1000`.

## Decision

H61 **PASS** requires the conjunction of both views:
1. View A is valid (>=2 eligible hands, >=60 eligible pairs);
2. View B is valid (>=2 eligible quires, >=60 eligible pairs);
3. 999/999 permutations complete;
4. hand-out BA > 0.5 and p <= 0.05;
5. quire-out BA > 0.5 and p <= 0.05.

H61 **FAIL** if both views execute validly but either inferential criterion fails.

H61 **BLOCKED** if either required view cannot meet its frozen sample/group threshold or the frozen metadata/pair construction cannot be implemented without changing the protocol.

Before execution: **NOT_RUN**.

## Interpretation boundary

**PASS** would show that the H60 label-vs-paragraph token-form signal generalizes across the eligible scribal-hand and physical-quire contexts represented in this frozen corpus. It would weaken a simple explanation based solely on shared hand or quire context.

**FAIL** would show that the previously observed signal does not survive this stronger cross-context requirement and should not be treated as globally portable.

Neither outcome identifies label meanings, object names, language, plaintext, cipher, author, translation, or decipherment.

Semantic identification: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

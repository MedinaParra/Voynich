# H61 — Residual transition grammar after boundary ablation

Status: **NOT_RUN**.

## Motivation
H60 found a reproducible distinction between certain single-token L* loci and strictly P* paragraph text under same-folio, exact-length, Currier/hand matching (BA 0.6585858586; p=0.001). Prior work has already noted that Voynich labels differ strongly from running text in word-initial character pairs such as EVA `ok` and `ot`. H61 asks a narrower question: **does a label-vs-paragraph distinction remain in the internal character transition order after removing the two leading characters and the final character?**

This experiment is intended to separate a residual transition-grammar signal from the already-known label boundary/prefix effect. It makes no semantic assumption about labels.

## Frozen data
Use the same frozen corpus/blob as H60:
`2a4533ab9bdfa85db9bad602d590978953055df1`

Seed: `20261007`.

Recreate the H60 sample exactly:
- positive: certain single-token `L*` loci;
- control: tokens from generic IVTFF `P*` loci only;
- match same folio, exact token length, Currier state and hand;
- deterministic one-control selection with seed `20261007`.

Then retain only matched pairs with token length >=5. No rematching after this filter.

Require >=100 retained pairs and >=8 represented folios; otherwise H61 is **BLOCKED**.

## Boundary ablation
For each token `t`, define the residual body as `t[2:-1]`:
- first two EVA characters removed;
- final EVA character removed;
- because retained tokens have length >=5, residual body length is >=2.

The removed characters may not be used by the predictive model.

## Predictive model — residual bigram grammar
Use leave-one-folio-out evaluation.

Within every training fold, fit two add-one-smoothed first-order character-transition models on residual bodies, one for class L and one for class P.

Alphabet is frozen to lowercase ASCII EVA transcription symbols `a`–`z`; smoothing alpha = 1.0. Only adjacent character transitions **inside the residual body** are scored. Do not use BOS/EOS transitions, token length, raw character counts, folio, Currier, hand, section, locus subtype, or illustration metadata as predictors.

For a held-out token, compute mean log transition likelihood under each class model and predict the class with higher mean log likelihood. Ties are predicted as P (class 0), frozen before execution.

Primary observed statistic: aggregate balanced accuracy across held-out folios.

## Null A — class identity
Exactly 999 deterministic within-pair identity swaps, seed `20261007`. For each permutation, refit the complete leave-one-folio-out transition model and recompute balanced accuracy.

`p_identity = (1 + count(null_BA >= observed_BA)) / 1000`.

## Null B — sequence order conditional on composition
Exactly 999 deterministic sequence-order randomizations, seed `20261008`.

For every randomization, independently shuffle the characters **within each residual body** while preserving:
- its exact character multiset;
- residual-body length;
- pair membership;
- folio;
- class identity.

Refit the complete leave-one-folio-out transition model to the shuffled bodies and recompute balanced accuracy.

This null preserves residual-body unigram composition but destroys observed internal order.

`p_order = (1 + count(shuffled_BA >= observed_BA)) / 1000`.

## Decision
Scientific **PASS** requires all of:
1. >=100 retained matched pairs;
2. >=8 represented folios;
3. 999/999 class-identity permutations;
4. 999/999 sequence-order randomizations;
5. observed balanced accuracy > 0.5;
6. `p_identity <= 0.05`;
7. `p_order <= 0.05`;
8. observed BA > mean sequence-order-null BA.

**FAIL**: valid execution satisfying sample/randomization requirements but missing any inferential criterion.

**BLOCKED**: frozen sample thresholds cannot be met or the exact H60 sample cannot be recreated.

## Descriptive decomposition
Report, without affecting PASS:
- number of retained pairs and folios;
- observed BA;
- mean/median of both nulls;
- per-folio balanced accuracy where both classes occur;
- fraction of residual bodies whose internal order actually changes under a random shuffle (diagnostic only).

No post-hoc feature selection is allowed.

## Interpretation boundary
PASS would show that the L-vs-P distinction is not confined to the first two and final EVA characters and that observed **internal character order** contributes information beyond the residual character multiset. It would support a reproducible difference in token-internal transition grammar between L and P loci.

PASS would **not** identify the meaning of labels, a language, plaintext, cipher, author, translation, or decipherment.

FAIL would indicate that H60 can be explained largely by boundary/prefix and/or character-composition effects under this model; it would not imply meaningless text.

Language identification: **NOT_RUN**.
Semantic identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

# H66 — Exact-consensus edge-only functional test preregistration

Status: **NOT_RUN**.

## Why this test exists
H65 failed after restricting to exact transcription-consensus loci and removing the first and last glyph from the predictor representation. H66 is an explicitly adaptive, post-H65 **mechanism test**, not a rescue or a new semantic claim.

It asks one narrow question: on the same strict exact-consensus construction, do the two token-edge indicators already frozen in the earlier functional program carry a reproducible label-vs-running-text distinction by themselves?

## Frozen sources and construction
Use exactly the two frozen sources and exact-consensus locus construction from H65:
- IVTFF blob `2a4533ab9bdfa85db9bad602d590978953055df1`;
- Takahashi blob `7f491b574b65e5fba6b553e57372c3fa50e10fec`;
- exact same locus agreement rule, metadata agreement rule, same-folio/Currier/hand/exact-length running-text matching, deterministic seed `20261007`;
- same quire eligibility rule: >=10 matched pairs per held-out quire;
- require >=4 evaluable quires and >=80 evaluable pairs.

No fuzzy matching, manual harmonization, glyph repair, feature search, or threshold tuning is permitted.

## Frozen predictors
Use **only** these two binary edge features, both already present in the pre-H65 functional program:
1. token starts with `q`;
2. token ends with `y`.

No interior glyph frequencies, token length, folio, quire, Currier, hand, locus subtype, section, topology, illustration class, or semantic annotation may enter the classifier.

## Evaluation
Use exactly the H65 leave-one-quire-out nearest-class-mean pipeline. Standardization is fit on training quires only. Aggregate balanced accuracy over all held-out predictions is the primary statistic. Also report per-quire BA and the number of held-out quires above 0.5.

## Null
Exactly 999 deterministic within-pair label swaps using seed `20261007`, refitting the complete leave-one-quire-out pipeline for every permutation.

Monte Carlo p = `(1 + count(null_BA >= observed_BA))/1000`.

## Frozen decision
**PASS_EDGE_ONLY_CONSENSUS_SIGNAL** iff all hold:
1. >=4 evaluable quires;
2. >=80 evaluable exact-consensus matched pairs;
3. 999/999 permutations complete;
4. observed BA > 0.55;
5. Monte Carlo p <= 0.01;
6. >=3 evaluable quires have BA > 0.5.

**FAIL** if execution is valid but any inferential criterion fails.

**BLOCKED** if the exact-consensus support criteria cannot be met without changing the frozen construction.

## Interpretation ceiling
PASS would show that a strict cross-transcription-consensus subset retains a functional label-vs-running-text difference using only the frozen `q`-initial / `y`-final edge indicators. Combined with H65 FAIL, that would localize part of the robust functional signal toward token edges on the strict-consensus subset.

FAIL would mean those two frozen edge indicators do not by themselves explain the H60-H62 functional effect under exact consensus.

Neither outcome identifies semantics, language, plaintext, cipher, glosses, translation, or decipherment.

Semantic gloss: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

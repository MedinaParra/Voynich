# Familywise label-object / lexical-anchor screen preregistration

Status: **NOT_RUN**.

## Motivation
The specific Lc/Lf hypothesis failed both exact-length replication and topology-conditioned testing. It must remain FAIL. A scientifically valid next lexical step is not to retune Lc/Lf, but to test whether *any* label-object contrast in the frozen annotation vocabulary carries reproducible token-form information after the same confound controls, with multiplicity handled prospectively.

## Frozen corpus and eligibility
Use the same frozen discovery EVA corpus/blob and parser used by the previous lexical-anchor experiments. Labels/objects are taken only from the corpus's existing annotation codes; no illustration interpretation or manual semantic recoding is permitted.

For each annotation code, collect its associated label token under the same extraction rules used by the prior lexical-anchor pipeline. Restrict to Currier/hand `A|1` where that metadata exists, matching the earlier lexical experiment. Codes with fewer than 20 usable tokens are ineligible.

## Candidate contrasts
Enumerate all unordered pairs of eligible annotation codes *before looking at classifier performance*. A pair is evaluable only if exact token-length matching can retain at least 10 examples per class in aggregate and at least two leave-one-quire-out folds contain both classes after matching.

Lc/Lf is included if evaluable, but its prior FAIL remains historical regardless of this familywise screen.

## Predictors
Use only the length-ablated lexical features frozen previously:
- fraction `o`
- fraction `a`
- fraction `y`
- starts `q`
- ends `y`

Absolute token length is prohibited as a predictor. Exact token length is a matching/permutation stratum.

## Evaluation
For each candidate pair, use leave-one-quire-out evaluation. Within held-out data, exact-match classes by token length and balance classes deterministically. Train the nearest-class-mean classifier on all other eligible data, standardized using training statistics only. Report aggregate balanced accuracy and per-fold BA.

## Null and familywise correction
Use exactly 999 deterministic permutations with seed `20261006`.

For each permutation, shuffle annotation-code labels within exact `(quire, token_length)` strata before evaluating every candidate pair. Record the maximum improvement over chance, `max(BA - 0.5)`, across all evaluable pairs in that permutation.

For each observed pair, familywise Monte Carlo p is:
`(1 + count(null_max >= observed_BA - 0.5)) / 1000`.

This max-statistic controls the familywise error rate across the complete screened contrast family.

## Decision
A pair is **PASS** only if:
1. >=2 evaluable held-out quires;
2. >=10 matched examples per class aggregate;
3. 999/999 permutations complete;
4. aggregate BA > 0.5;
5. familywise p <= 0.05.

A valid evaluable pair missing either inferential criterion is **FAIL**. A pair missing sample/fold requirements is **BLOCKED**. The experiment-level screen is **PASS** if at least one pair passes familywise correction; otherwise **FAIL** if at least one pair is evaluable and all evaluable pairs fail. If no pair is evaluable, experiment status is **BLOCKED**.

Before execution: **NOT_RUN**.

## Interpretation boundary
A PASS would establish only that an annotation-code contrast predicts token-form features beyond exact length under out-of-quire evaluation and familywise correction. It would not establish what either annotation code means, identify an illustrated object, identify a language/plaintext/cipher, or constitute translation. Any semantic interpretation of a passing pair requires a new preregistered experiment.

Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

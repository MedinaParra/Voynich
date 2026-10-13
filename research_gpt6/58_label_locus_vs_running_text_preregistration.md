# Label-locus vs running-text falsification preregistration

Status: **NOT_RUN**.

## Motivation
The original `Lc/Lf` lexical-anchor pilot was confounded by token length; exact-length, topology-conditioned, and familywise between-code tests are all **FAIL**. Those routes remain closed. The next safe label-object question is broader and does not assign semantics: do tokens explicitly annotated as label/object loci differ reproducibly from running-text tokens after exact length and manuscript-location controls?

## Frozen data
Use the same frozen discovery corpus/blob `2a4533ab9bdfa85db9bad602d590978953055df1` and existing parser. Do not manually recode illustrations or labels. Positive items are tokens attached to existing label/object annotation codes under the frozen extraction rules. Controls are running-text tokens from the same folio and Currier/hand state, excluding annotated label/object tokens.

## Matching
For every positive token, construct eligible controls with identical:
- folio;
- exact token length;
- Currier/hand metadata when present.

Select one control deterministically from eligible controls using seed `20261007`. A positive with no eligible control is excluded before evaluation. Require >=60 matched pairs and >=8 folios containing matched pairs; otherwise **BLOCKED**.

## Predictors
Use only the previously frozen length-ablated token-form features:
- fraction `o`;
- fraction `a`;
- fraction `y`;
- starts `q`;
- ends `y`.

Absolute token length, folio, Currier, hand, section, illustration class, annotation subtype, topology features, and proposed semantics are prohibited predictors.

## Evaluation
Leave-one-folio-out classification. Standardize predictor columns from training folds only. Use the same nearest-class-mean classifier family as prior lexical tests. Primary statistic is aggregate balanced accuracy across held-out matched pairs.

## Null
Exactly 999 deterministic permutations, seed `20261007`. Within each matched pair, independently swap label-locus/running-text identities with probability 0.5. Refit the complete leave-one-folio-out pipeline for every permutation.

Monte Carlo p = `(1 + count(null_BA >= observed_BA))/1000`.

## Negative control
Repeat descriptively after replacing each positive token with a second independently selected running-text token from the same folio and exact-length stratum. This negative control must not replace the primary paired null and is not part of the PASS criterion.

## Decision
**PASS** iff:
1. >=60 matched pairs;
2. >=8 represented folios;
3. 999/999 permutations complete;
4. observed aggregate BA > 0.5;
5. p <= 0.05.

**FAIL** if execution is valid but either inferential criterion fails.

**BLOCKED** if matching/sample requirements or frozen extraction cannot be implemented without changing the protocol.

Before execution: **NOT_RUN**.

## Interpretation boundary
PASS would show a reproducible token-form distinction between annotated label/object loci and matched running text. It would not identify what any label means, validate `Lc` versus `Lf`, identify a language, plaintext or cipher, or constitute translation. FAIL would further weaken token-form lexical-anchor approaches under strict local controls.

The historical `Lc/Lf` results remain **FAIL** regardless of this experiment.
Semantic identity: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

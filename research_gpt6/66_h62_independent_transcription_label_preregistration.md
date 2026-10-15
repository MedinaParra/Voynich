# H62 — Independent-transcription strict label-vs-paragraph replication preregistration

Status: **NOT_RUN**.

## Motivation
H60 found a strict L* label-locus vs P* paragraph-text token-form distinction in the frozen Zandbergen-Landini discovery transcription, and H61 showed that the same distinction generalizes when eligible scribal hands and physical quires are held out. H62 asks whether the same frozen token-form distinction replicates in an independently sourced transliteration tradition rather than only within the discovery transcription.

This is a transcription-robustness test, not a semantic or translation test.

## Frozen replication source
Use only the immutable Takahashi IT2a-n source already admitted by the independent-transcription provenance gate:

- repository: `oklo/voynich_gpt`
- commit: `2d7c61c387ad6962de730caf73c48612bc8f6957`
- path: `IT2a-n.txt`
- Git blob SHA-1: `7f491b574b65e5fba6b553e57372c3fa50e10fec`
- IVTFF header: `#=IVTFF EvaT 2.0 M 3`

No other transcription, manual correction, manual relabeling, or visual recoding may be introduced after this preregistration.

## Frozen extraction
Apply the H60 extraction logic to IT2a-n without tuning:

- positive items: certain single-token loci whose IVTFF generic locus type is `L`;
- controls: tokens only from loci whose IVTFF generic locus type is `P`;
- exclude C*, R*, L* from the control pool;
- remove uncertain tokens/markup using the same cleaning policy used by H60;
- no manual token edits.

## Matching
For every positive token, select one eligible P-only control with identical:

- folio;
- exact token length;
- Currier/hand metadata when present in the frozen source.

Selection is deterministic with seed `20261007`.

Require at least **60 matched pairs** and at least **8 represented folios**, otherwise H62 is **BLOCKED**.

## Predictors
Exactly the five H60/H61 frozen token-form predictors:

1. fraction `o`;
2. fraction `a`;
3. fraction `y`;
4. starts `q`;
5. ends `y`.

Absolute length, folio, hand, Currier state, section, illustration class, locus subtype, proposed semantics, and discovery-transcription token identity are prohibited predictors.

## Evaluation
Use leave-one-folio-out classification inside the Takahashi replication transcription.

- training-fold-only standardization;
- same nearest-class-mean classifier family as H60;
- primary statistic: aggregate balanced accuracy over held-out matched pairs.

No hyperparameter selection is allowed.

## Null
Exactly **999** deterministic within-pair label swaps with seed `20261007`. Refit the entire leave-one-folio-out pipeline for every permutation.

Monte Carlo p = `(1 + count(null_BA >= observed_BA))/1000`.

## Negative control
Descriptive only: P-vs-P comparison using a second independently selected P-only token from the same folio/exact-length/metadata stratum where available. It is not part of PASS.

## Decision
H62 is **PASS** iff all conditions hold:

1. >=60 matched pairs;
2. >=8 represented folios;
3. 999/999 permutations complete;
4. observed balanced accuracy > 0.5;
5. Monte Carlo p <= 0.05.

H62 is **FAIL** if a valid execution meets sample/permutation requirements but misses either inferential threshold.

H62 is **BLOCKED** if the immutable Takahashi source cannot support the frozen extraction/matching thresholds without protocol modification.

Before execution: **NOT_RUN**.

## Interpretation boundary
PASS would show that the strict label-vs-paragraph token-form distinction is reproducible in a second transliteration tradition frozen independently of the discovery file. Because both sources represent the same manuscript and both use EVA-family transcription conventions, PASS would still not exclude all shared transcription-convention effects.

PASS would **not** establish that labels are nouns, names, object identifiers, semantic anchors, plaintext, or a cipher key. The prior Lc-vs-Lf, exact-length subtype, topology-conditioned lexical-anchor, and familywise subtype tests remain **FAIL** regardless of H62.

Semantic identification: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

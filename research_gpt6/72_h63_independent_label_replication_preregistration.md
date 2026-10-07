# H63 — Independent-transcription strict label-vs-paragraph replication

Status: **NOT_RUN**.

## Motivation
H60 found a strict L-vs-P token-form distinction in the frozen Zandbergen/Landini-derived corpus (BA 0.6585858586; p=0.001). Because transliteration choices can induce or amplify token-form effects, H63 asks whether the same preregistered H60 classifier replicates on an independently sourced IVTFF transcription that was not used to obtain the H60 result.

This is a replication test, not a search for a translation.

## Frozen independent source
Repository: `oklo/voynich_gpt`
Commit: `2d7c61c387ad6962de730caf73c48612bc8f6957`
Path: `IT2a-n.txt`
Git blob SHA-1: `7f491b574b65e5fba6b553e57372c3fa50e10fec`
Header: `IVTFF EvaT 2.0 M 3`, extracted from `LSI_ivtff_0d.txt`, version 2a dated 02/02/2023.

The workflow MUST verify the Git blob hash before analysis. Any mismatch => **BLOCKED**.

Seed: `20261007`.

## Sample definition
Use the same structural rules as H60, applied independently to IT2a-n:
- positive tokens: certain single-token loci whose generic locus is `L*`;
- controls: tokens from generic IVTFF `P*` loci only;
- exclude C*, R*, L* from control pool;
- require no `?` uncertainty in positive source text;
- exact match on same folio, token length, Currier state and hand;
- deterministic one-control draw per positive using seed `20261007`.

No counts from the discovery corpus are imposed on the replication source.

Require >=60 matched pairs and >=8 represented folios; otherwise **BLOCKED**. The threshold may not be lowered after execution.

## Predictors
Exactly the H60 frozen predictors:
1. fraction of EVA `o` characters;
2. fraction of EVA `a` characters;
3. fraction of EVA `y` characters;
4. starts with EVA `q`;
5. ends with EVA `y`.

Absolute token length and manuscript metadata are prohibited predictors.

## Evaluation
Leave-one-folio-out evaluation.

Within each training fold:
- standardize predictors using training data only;
- fit nearest-class-mean classifier in the five-dimensional frozen predictor space;
- predict all tokens from the held-out folio.

Primary statistic: aggregate balanced accuracy.

## Null
Exactly 999 deterministic within-pair identity swaps, seed `20261007`, refitting the full LOFO pipeline for every permutation.

Monte Carlo p-value:
`p = (1 + count(null_BA >= observed_BA)) / 1000`.

## Negative control
Descriptive only: construct independent P-vs-P matched pairs from the same folio/exact-length/Currier/hand strata where possible. This does not affect PASS.

## Decision
Scientific **PASS** requires all of:
1. frozen independent source blob verified;
2. >=60 matched pairs;
3. >=8 represented folios;
4. 999/999 permutations;
5. observed balanced accuracy > 0.5;
6. Monte Carlo p <= 0.05.

**FAIL**: valid replication satisfying sample/permutation requirements but missing inferential criteria.

**BLOCKED**: immutable source mismatch or sample threshold not met.

## Interpretation boundary
PASS would replicate the strict L-vs-P token-form distinction on an independently sourced transcription, reducing the likelihood that H60 is an artifact of one transliteration file or one transcription tradition.

It would not establish label semantics, a language, plaintext, cipher, author, translation, or decipherment.

FAIL would weaken the claim that the H60 token-form distinction is transcription-robust; it would not imply meaningless text.

Language identification: **NOT_RUN**.
Semantic identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

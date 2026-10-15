# H66 — Symbol-renaming-invariant bidirectional zero-shot label-vs-paragraph test

Status before execution: **NOT_RUN**.

## Question

Does the strict L* label-locus versus P* paragraph-text distinction found in H60–H65 survive when **all predictor features are invariant to arbitrary one-to-one renaming of transcription symbols**?

This test is designed to attack the explanation that H63–H65 transfer only because both admitted transcriptions share EVA-family symbol identities such as `o`, `a`, `y`, or `q`.

## Frozen corpora

Exactly the two already admitted frozen sources are used; no corpus substitution is allowed after seeing results.

- Zandbergen–Landini discovery corpus Git blob: `2a4533ab9bdfa85db9bad602d590978953055df1`.
- Takahashi IT2a replication corpus Git blob: `7f491b574b65e5fba6b553e57372c3fa50e10fec`.

Any blob mismatch is **BLOCKED**.

## Frozen sample construction

Reuse the H63/H64 parser and matching rules without modification:

1. positive = certain single-token `L*` locus;
2. exclude uncertain text containing `?`;
3. control = token from `P*` locus only;
4. exact matching on folio, Currier metadata, hand metadata, and token length;
5. one control sampled with frozen seed `20261007`;
6. `C*` and `R*` loci are excluded from controls;
7. tokenizer remains lowercase alphabetic token length >=2 after the same IVTFF markup cleaning.

No rematching is permitted after seeing H66 scores.

## Frozen representation

Token length is already exactly matched and is **not** itself a predictor.

For token `t` of length `n>=2`, use exactly these five features:

1. `unique_fraction` = number of distinct symbols / `n`;
2. `singleton_type_fraction` = number of distinct symbols occurring exactly once / number of distinct symbols;
3. `max_frequency_fraction` = maximum symbol count / `n`;
4. `adjacent_equal_fraction` = number of adjacent equal-symbol pairs / (`n-1`);
5. `first_last_equal` = 1 if first and last symbol are identical, else 0.

These features depend only on the token's equality/repetition pattern. Under any arbitrary bijective renaming of the transcription alphabet they remain exactly unchanged.

No symbol identity, prefix identity, suffix identity, EVA glyph name, character n-gram, lexical identity, or manually chosen object meaning is admitted.

## Frozen classifier

Use the same transparent model family as H63/H64:

- z-standardize features using **training-source data only**;
- compute class centroids on training-source data only;
- classify by nearest squared-Euclidean centroid;
- for every test folio, exclude that folio from the training-source matched pairs before fitting;
- no parameter may be fitted on the target transcription.

## Two preregistered directions

A. ZL -> Takahashi zero-shot.

B. Takahashi -> ZL zero-shot.

Both must pass. A one-way effect is **FAIL** for H66.

## Null and statistics

For each direction:

- freeze model predictions first;
- perform exactly **999** paired label-swap permutations using seed `20261007`;
- balanced accuracy is the primary statistic;
- Monte Carlo p = `(1 + count(null >= observed)) / (1 + permutations)`.

Familywise error across the two directional primary tests is controlled by Bonferroni: each direction must satisfy `p <= 0.025`.

A P-vs-P pseudo-label negative control using the already frozen target P pools may be reported descriptively, but it is not a PASS gate and must not be used to alter the model.

## Sample-validity gates

Each direction requires:

- >=60 matched training-source pairs;
- >=60 matched target pairs;
- >=8 represented target folios;
- exactly 999/999 completed permutations.

Failure of a validity gate for reasons that prevent the scientific test is **BLOCKED**, not FAIL.

## Decision rule

H66 = **PASS** only if both directions independently satisfy all validity gates and:

- observed balanced accuracy > 0.5; and
- Monte Carlo `p <= 0.025`.

H66 = **FAIL** if the test is valid but either direction fails either scientific criterion.

H66 = **BLOCKED** if a preregistered validity requirement cannot be met.

Before execution H66 remains **NOT_RUN**.

## Interpretation boundary

A PASS would show that the bidirectional strict label-versus-paragraph transfer contains information in symbol-repetition/equality structure that is invariant to alphabet renaming. It would materially weaken a simple EVA-character-identity explanation.

A PASS would **not** establish object semantics, lexical meaning, language, plaintext, cipher mechanism, translation, or decipherment. It would also not eliminate a shared locus-annotation convention, because both transcriptions still describe the same manuscript and use related structural markup.

Historical `Lc`-vs-`Lf`, exact-length subtype, topology-conditioned lexical-anchor, and familywise subtype failures remain failures regardless of H66.

Semantic identification: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

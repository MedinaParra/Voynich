# H62 — Residual character signature after boundary ablation

Status: **NOT_RUN**.

## Motivation
H61 showed that, after removing the first two and final EVA characters, L and P tokens remain highly distinguishable, but composition-preserving shuffling destroys little of that discrimination (`p_order = 0.251`). The next falsifiable question is therefore compositional rather than sequential: **are there specific residual EVA characters whose enrichment/depletion in L versus P survives familywise correction and is stable across independent quires?**

This is a decomposition of the H61 residual signal, not a translation attempt.

## Frozen data
Use corpus Git blob:
`2a4533ab9bdfa85db9bad602d590978953055df1`

Seed: `20261007`.

Recreate the strict H60 matched sample exactly:
- certain single-token `L*` positives;
- generic IVTFF `P*` controls only;
- same folio, exact token length, Currier state and hand;
- deterministic one-control selection with seed `20261007`.

Expected H60 recreation: 780 positives, 495 matched pairs, 34 represented folios, 285 unmatched positives.

Apply the same H61 filter without rematching:
- retain pairs with original token length >=5;
- residual body = `token[2:-1]`.

Require >=100 retained pairs and >=8 represented folios; otherwise **BLOCKED**.

## Character statistics
Alphabet is frozen to lowercase EVA/ASCII transcription symbols `a`–`z`.

For each retained pair and each character `c`, compute:

`d_pair(c) = freq_L_body(c) - freq_P_body(c)`

where frequency is count divided by residual-body length. Because the original pair has equal token length, the two residual bodies also have equal length.

Observed statistic for each character is the mean paired difference across all retained pairs.

No characters may be selected or excluded after seeing the result. All 26 are tested.

## Familywise null
Exactly 999 deterministic within-pair identity swaps, seed `20261007`.

For every permutation:
1. independently swap or retain L/P identity within every pair;
2. recompute all 26 mean paired differences;
3. record `max_abs = max_c(abs(mean_difference(c)))`.

For each character:

`p_FWER(c) = (1 + count(max_abs_null >= abs(observed(c)))) / 1000`.

This single max-stat null controls familywise error over all 26 characters.

## Quire stability gate
Quire is taken only from frozen manuscript metadata (`$Q`) and is not a predictor.

A quire is evaluable for stability if it contains >=5 retained matched pairs. For every character with `p_FWER <= 0.05`, compute the mean paired difference independently inside every evaluable quire.

Define sign stability as the fraction of evaluable quires whose nonzero quire-level difference has the same sign as the global observed difference. Zero quire-level differences count as not supporting the sign.

Require >=8 evaluable quires for the confirmatory stability gate.

## Decision
Scientific **PASS** requires all of:
1. exact H60 sample recreated;
2. >=100 retained pairs and >=8 represented folios;
3. >=8 evaluable quires (>=5 pairs each);
4. 999/999 max-stat permutations;
5. at least one character with `p_FWER <= 0.05`;
6. at least one familywise-significant character has sign stability >=0.75 across evaluable quires.

**FAIL**: valid execution satisfies sample/permutation requirements but no character meets the familywise + stability rule.

**BLOCKED**: sample, H60 recreation, quire, or permutation requirements cannot be met.

## Descriptive outputs
Report without affecting PASS:
- all 26 observed differences and FWER p-values;
- significant character set;
- per-quire differences for significant characters;
- number of evaluable quires and retained pairs;
- largest positive and negative observed residual-character shifts.

## Interpretation boundary
PASS would establish a specific, manuscript-wide **residual compositional signature** distinguishing L from P loci after removing the two leading and final EVA characters, with familywise correction and cross-quire sign stability.

It would not establish the semantics of any character, the meaning of labels, a language, plaintext, cipher, translation, or decipherment.

FAIL would mean the H61 residual composition signal is diffuse/multivariate or quire-specific rather than attributable to a stable individually significant character under this test.

Language identification: **NOT_RUN**.
Semantic identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

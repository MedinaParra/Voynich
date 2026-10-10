# H84 — IT↔GC structural transcription-disagreement challenge

Status before execution: **NOT_RUN**.

## Purpose

H60/H61/H62/H65/H66 establish that strict label loci (`L*`) differ in token form from paragraph loci (`P*`) and that this distinction transfers across manuscript context and transcription traditions. A remaining adversarial explanation is that isolated labels are simply harder or more ambiguous to transcribe, so the positive label-vs-paragraph signal could partly reflect locus-dependent transcription instability rather than a distinct manuscript mechanism.

H84 tests one falsifiable prediction of that explanation:

> At exact manuscript loci, do `L*` tokens disagree more strongly between the frozen Takahashi/IT EVA transcription and the frozen Glen Claston/v101 (`GC`) transcription than length-matched `P*` controls from the same folio?

This is a transcription-stability test, not a semantic, language, plaintext, cipher, translation, or decipherment test.

## Frozen sources

Use only `noah-chelednik/voynich-data` at commit:

`472ef7366606a799fc8f1044c037e06b413f6ddd`

Files and required SHA-256 values:

- `data_sources/cache/IT_ivtff_1a.txt` — `db624a731114f26854bbfe3a59d40827fa8911be46d086b6c558d99e557241ee`
- `data_sources/cache/GC2a-n.txt` — `b09570cb6c993bc2d87134d115e60a978650a8a6495483ddbb1f6005a586096f`

Any hash mismatch is **BLOCKED**.

## Frozen parsing and exact-locus alignment

Reuse the H70 record convention:

- record key = exact `(folio, locus_number)`;
- parse page metadata from IVTFF headers;
- remove IVTFF markup, bracketed/unresolved spans and `?` material conservatively;
- retain a locus only when IT and GC each yield exactly **one known token** at that exact locus;
- no fuzzy matching, nearest-neighbour locus substitution, manual repair or manual token editing.

The IT locus code defines the class:

- positive candidate: generic locus begins with `L`;
- control candidate: generic locus begins with `P`;
- `C*`, `R*`, and all non-`P*` records are forbidden controls.

No `L*` subtype is used as a predictor or selection variable beyond the generic `L` status.

## Symbol-renaming-invariant disagreement score

Literal alphabet symbols are not compared across IT and GC.

For each token independently, convert its encoded character sequence into a canonical equality pattern by assigning integers in first-occurrence order. Examples:

- `abba` → `(0,1,1,0)`
- `xyyx` → `(0,1,1,0)`
- `abcd` → `(0,1,2,3)`

For an exact locus `i`, define:

`D_i = normalized_Levenshtein(pattern_IT_i, pattern_GC_i)`

where the Levenshtein distance is divided by the maximum of the two pattern lengths.

Thus `D_i=0` means the two transcription strings have the same equality/repetition structure up to arbitrary symbol renaming. The score can increase because of segmentation/length disagreement or because repeated-symbol structure differs. This is intentional: H84 asks whether label loci are structurally less stable across the two frozen transcription systems.

## Frozen matching

Construct one `L*`–`P*` pair only when both loci are exact-locus single-token-mappable in IT and GC and share exactly:

1. folio;
2. IT token length.

Controls are used without replacement.

Deterministic pairing algorithm:

1. sort all eligible L loci by `(folio, locus_number)`;
2. group eligible P controls by `(folio, IT_token_length)`;
3. sort each P pool by locus number, then shuffle each pool once using `random.Random(20261016)` in deterministic sorted-stratum order;
4. iterate the sorted L loci and assign the next unused P control from its exact stratum;
5. exclude an L locus if no unused exact-stratum P control remains.

No GC token length, disagreement score, token content, illustration subtype, or result may influence matching.

## Sample-validity gate

H84 requires:

- at least **60 matched L–P pairs**;
- at least **8 represented folios**;
- all paired loci exact-locus single-token-mappable in both frozen sources.

Otherwise H84 = **BLOCKED**. The thresholds may not be lowered after execution.

## Primary statistic

For matched pair `j`, define:

`delta_j = D_label_j - D_paragraph_j`

Primary statistic:

`Delta = mean(delta_j)`

Prediction of the transcription-ambiguity explanation: `Delta > 0`.

Report:

- matched-pair and folio counts;
- mean/median `D` for L and P;
- `Delta`;
- exact-pattern-agreement fraction (`D=0`) for L and P;
- by-folio mean deltas.

## Frozen null

Exactly **9,999** paired sign-flip permutations with seed `20261017`.

For each permutation independently multiply every `delta_j` by `+1` or `-1` with probability 0.5 and recompute the mean. This preserves each pair and its documentary/length matching while breaking only the L-vs-P direction.

One-sided Monte Carlo p-value:

`p_upper = (1 + count(null_Delta >= observed_Delta)) / 10000`.

All 9,999 permutations must complete or H84 = **BLOCKED**.

## Diagnostics fixed before execution

These diagnostics do **not** create alternate PASS routes:

1. IT↔GC absolute token-length difference for L and P on the same matched set;
2. fraction of loci with identical IT and GC encoded token length;
3. equality-pattern disagreement restricted to pairs where both the L locus and its P control each have equal IT/GC token lengths. Report this sensitivity only if it retains >=30 pairs over >=6 folios; otherwise mark it `NOT_RUN_INSUFFICIENT_SAMPLE`.
4. a descriptive P-vs-P negative-control pairing using a second unused P locus from the same `(folio, IT length)` stratum where available. It is not part of the decision.

No diagnostic may replace the primary statistic after results are known.

## Decision

H84 = **PASS** iff all conditions hold:

1. source hashes and parsing/alignment valid;
2. >=60 matched pairs and >=8 folios;
3. 9,999/9,999 paired permutations complete;
4. `Delta > 0`;
5. `p_upper <= 0.05`.

H84 = **FAIL** if execution is valid and adequately powered by the frozen sample gate but misses either inferential condition.

H84 = **BLOCKED** for source/hash/parsing/sample/permutation failure.

## Interpretation boundary

A **PASS** would support a specific nuisance explanation: exact label loci are structurally less stable between IT and GC than matched paragraph loci. It would require reinterpreting part of the label-vs-paragraph classifier evidence with greater caution; it would not prove that the manuscript has no label register or no semantics.

A **FAIL** would weaken this specific explanation because label loci would not show the predicted excess cross-transcription structural disagreement under the frozen exact-locus, same-folio, same-IT-length comparison. It would not prove that the transcriptions are independent observations or that all paleographic confounds are absent.

Regardless of outcome:

- semantic identification: **NOT_RUN**;
- language identification: **NOT_RUN**;
- translation: **NOT_RUN**;
- decipherment: **NOT_RUN**.

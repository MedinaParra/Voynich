# H85 — IT↔GC exact-record ordinal-token transcription-disagreement challenge

Status before execution: **NOT_RUN**.

## Motivation

H84 was BLOCKED before inference because it required an entire paragraph (`P*`) record to contain exactly one known token in both IT and GC. The frozen files contain thousands of exact P records, but paragraph records normally contain multiple tokens; only 24 whole P records passed that record-level single-token rule.

H85 does **not** lower H84's sample or significance thresholds. It separately preregisters a token-level documentary unit that is available without fuzzy text matching:

> Within an exact P record, align IT and GC tokens by ordinal position **only when the two frozen transcriptions contain the same number of known tokens after the frozen cleaning rule**.

No content-based token alignment is permitted.

The scientific question and primary disagreement statistic remain the same as H84: are label loci structurally less stable across IT↔GC than matched paragraph controls?

## Frozen sources

Use only `noah-chelednik/voynich-data` at commit:

`472ef7366606a799fc8f1044c037e06b413f6ddd`

Required SHA-256 values:

- `data_sources/cache/IT_ivtff_1a.txt`: `db624a731114f26854bbfe3a59d40827fa8911be46d086b6c558d99e557241ee`
- `data_sources/cache/GC2a-n.txt`: `b09570cb6c993bc2d87134d115e60a978650a8a6495483ddbb1f6005a586096f`

Any mismatch is **BLOCKED**.

## Frozen parsing

Reuse the H84/H70 parser and conservative known-token cleaning exactly:

- exact record key `(folio, locus_number)`;
- remove IVTFF markup, bracketed/unresolved spans and `?` material;
- no manual repair;
- no fuzzy record or token matching.

### Label candidates

An IT record is an L candidate only if:

1. its generic IT locus begins `L`;
2. the exact record exists in GC;
3. IT yields exactly one known token;
4. GC yields exactly one known token.

Each retained L record contributes exactly one candidate token pair.

### Paragraph-control candidates

An IT record is a P source only if:

1. its generic IT locus begins `P`;
2. the exact record exists in GC;
3. IT yields at least one known token;
4. GC yields at least one known token;
5. the cleaned known-token counts are **exactly equal** between IT and GC.

If a qualifying P record has `k` known tokens, it yields `k` candidate ordinal token pairs `(IT_j, GC_j)` for `j=1..k`.

If token counts differ, the entire P record is excluded. Sequence alignment, edit-distance realignment, token merging/splitting, lexical matching, and hand correction are forbidden.

## Frozen structural disagreement score

Use exactly H84's symbol-renaming-invariant score.

Canonicalize each token by first-occurrence equality pattern, e.g. `abba -> (0,1,1,0)` and `xyyx -> (0,1,1,0)`.

For token pair `i`:

`D_i = normalized_Levenshtein(pattern_IT_i, pattern_GC_i)`.

Literal alphabet identities are never compared.

## Frozen control matching

Match each L candidate to one ordinal P token candidate sharing exactly:

1. folio;
2. IT token length.

Controls are used without replacement, and **a P record may supply at most one matched control in the entire primary sample**, regardless of how many ordinal token candidates it contains.

Deterministic algorithm:

1. sort L candidates by `(folio, locus_number)`;
2. construct P-token candidates identified by `(folio, P_locus_number, ordinal)`;
3. group P-token candidates by `(folio, IT_token_length)`;
4. sort candidates within every stratum by `(P_locus_number, ordinal)`, then shuffle each stratum once using `random.Random(20261018)` in sorted-stratum order;
5. iterate sorted L candidates and select the first candidate in the exact stratum whose P record has not already been used;
6. mark that P record used globally and never use another token from it;
7. exclude the L candidate if no unused P record remains in the exact stratum.

No GC length, token content, D score, illustration subtype, or result may influence matching.

## Sample-validity gate

Unchanged from H84:

- >= **60 matched L–P pairs**;
- >= **8 represented folios**.

Otherwise H85 = **BLOCKED**. These thresholds may not be lowered.

Report also:

- number of exact P records present in both sources;
- number with equal cleaned known-token counts;
- number of ordinal P token candidates before matching;
- number of distinct P records used in the final sample.

## Primary statistic

For matched pair `j`:

`delta_j = D_label_j - D_paragraph_j`.

Primary statistic:

`Delta = mean(delta_j)`.

Prediction of the transcription-ambiguity explanation: `Delta > 0`.

Report label/P mean and median D, exact-pattern-agreement fractions, Delta, and by-folio mean deltas.

## Frozen null

Exactly **9,999** paired sign-flip permutations with seed `20261019`.

For each permutation independently multiply each frozen `delta_j` by +1 or -1 with probability 0.5 and recompute the mean.

One-sided Monte Carlo p:

`p_upper = (1 + count(null_Delta >= observed_Delta)) / 10000`.

All 9,999 permutations must complete or H85 = **BLOCKED**.

## Frozen diagnostics

Descriptive only; none can create a second PASS route:

1. absolute IT↔GC encoded token-length difference for L and P on the matched sample;
2. fraction with equal IT/GC encoded token length;
3. sensitivity restricted to pairs where both L and P each have equal IT/GC encoded lengths, only if >=30 pairs across >=6 folios; otherwise `NOT_RUN_INSUFFICIENT_SAMPLE`;
4. distribution of qualifying P-record token counts before matching.

## Decision

H85 = **PASS** iff all hold:

1. source hashes/parsing valid;
2. >=60 matched pairs and >=8 folios;
3. 9,999/9,999 permutations complete;
4. `Delta > 0`;
5. `p_upper <= 0.05`.

H85 = **FAIL** if execution and sample are valid but the inferential prediction fails.

H85 = **BLOCKED** for source/hash/parsing/sample/permutation failure.

## Interpretation boundary

PASS would support the specific nuisance hypothesis that exact label loci are structurally less stable between IT and GC than same-folio/same-IT-length paragraph tokens under a non-fuzzy ordinal alignment rule.

FAIL would weaken that specific explanation of the established label-vs-paragraph signal. It would not prove transcription independence, semantics, language, plaintext, or decipherment.

Regardless of outcome:

- semantic identification: **NOT_RUN**;
- language identification: **NOT_RUN**;
- translation: **NOT_RUN**;
- decipherment: **NOT_RUN**.

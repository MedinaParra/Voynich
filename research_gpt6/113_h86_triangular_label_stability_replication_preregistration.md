# H86 — Triangular replication of the H85 inverse label-stability observation

Status before execution: **NOT_RUN**.

## Motivation

H85 preregistered the nuisance prediction that exact label loci should be *more* structurally unstable across Takahashi/IT and Glen Claston/GC than same-folio, same-length paragraph controls. That prediction failed. The observed direction was instead strongly negative:

`Delta = mean(D_label - D_paragraph) = -0.0875375`

with labels showing greater IT↔GC equality-pattern agreement than paragraph controls.

Because the negative direction was not H85's preregistered alternative, it is not promoted post hoc to a discovery PASS. H86 prospectively freezes that **inverse direction** before evaluating a new transcription source, Zandbergen-Landini (ZL).

H86 is a triangular cross-transcription replication, not a fully source-disjoint replication: it adds ZL and compares it independently to each of the two frozen H85 traditions (IT and GC). The conjunction asks whether the inverse stability ordering survives when either side of the original IT↔GC edge is replaced by ZL.

This is a transcription-stability test, not a semantic, language, plaintext, translation, or decipherment test.

## Frozen sources

### Zandbergen-Landini (new source for H86)

- repository: `cesarjz/Voynich`
- commit: `47e6a77dc9d5cd570c375f4aff710fa4a0567278`
- path: `corpus/voynich_eva.txt`
- Git blob SHA-1: `2a4533ab9bdfa85db9bad602d590978953055df1`

### Takahashi/IT

Use the exact H85/H70 frozen source:

- repository: `noah-chelednik/voynich-data`
- commit: `472ef7366606a799fc8f1044c037e06b413f6ddd`
- path: `data_sources/cache/IT_ivtff_1a.txt`
- SHA-256: `db624a731114f26854bbfe3a59d40827fa8911be46d086b6c558d99e557241ee`

### Glen Claston/GC

Use the exact H85/H70 frozen source:

- repository: `noah-chelednik/voynich-data`
- commit: `472ef7366606a799fc8f1044c037e06b413f6ddd`
- path: `data_sources/cache/GC2a-n.txt`
- SHA-256: `b09570cb6c993bc2d87134d115e60a978650a8a6495483ddbb1f6005a586096f`

Any frozen-source hash mismatch is **BLOCKED**.

## Frozen documentary alignment

All three sources visibly use IVTFF-style manuscript record identifiers of the form `<folio.record_number,locus>`.

For both H86 arms, align records only by the exact key:

`(folio, record_number)`.

The **ZL locus code** defines generic class membership:

- label candidate: ZL generic locus begins `L`;
- paragraph-control source: ZL generic locus begins `P`;
- `C*`, `R*`, and all other generic locus types are excluded from controls.

The corresponding IT/GC locus subtype is not used to rescue, remap, or reclassify records.

No fuzzy matching, lexical matching, edit-distance alignment, nearest-record substitution, manual remapping, or token-content-assisted alignment is permitted.

## Frozen token cleaning

Apply the same conservative token policy to each source independently:

1. remove inline IVTFF `<...>` markup;
2. remove square-bracketed uncertain/alternative spans `[...]` as unresolved rather than selecting one side;
3. remove brace annotations `{...}`;
4. remove numeric `@...;` annotations;
5. split on IVTFF token separators (periods, commas, whitespace, and explicit `<->` layout breaks after markup removal);
6. any piece containing `?` is excluded;
7. retain only standalone ASCII alphabetic runs of length >=2 and lowercase them;
8. no manual spelling repair or token merge/split.

This cleaning rule is frozen before execution and must be applied identically within each arm.

## Frozen label candidates

For a ZL exact record classified `L`:

- ZL must yield exactly one known token;
- the comparison source (IT for arm A, GC for arm B) at the same exact record key must yield exactly one known token.

Each qualifying exact L record contributes one candidate token pair.

## Frozen paragraph-control candidates

For a ZL exact record classified `P`:

- the same exact record key must exist in the comparison source;
- both records must yield at least one known token;
- the cleaned known-token counts must be exactly equal between ZL and the comparison source.

If both records yield `k` known tokens, align token `j` only with token `j`, for `j=1..k`.

If token counts differ, exclude the entire P record. Sequence alignment, lexical matching, token merging/splitting, and hand correction are forbidden.

## Structural disagreement score

Use exactly H85's symbol-renaming-invariant endpoint.

For each token independently, convert its encoded character sequence to a first-occurrence equality pattern. Examples:

- `abba -> (0,1,1,0)`
- `xyyx -> (0,1,1,0)`
- `abcd -> (0,1,2,3)`

For a token pair:

`D = normalized_Levenshtein(pattern_ZL, pattern_other)`

where distance is divided by the maximum pattern length.

Literal symbol identities are therefore not compared.

## Frozen control matching

Within each arm separately, match every eligible ZL label candidate to one ordinal P-token candidate sharing exactly:

1. folio;
2. ZL token length.

Controls are used without replacement and **a P record may supply at most one matched control per arm**.

### Arm A — ZL↔IT

Pairing seed: `20261020`.

### Arm B — ZL↔GC

Pairing seed: `20261022`.

For each arm:

1. sort L candidates by `(folio, ZL_record_number)`;
2. group P ordinal candidates by `(folio, ZL_token_length)`;
3. sort each P pool by `(P_record_number, ordinal)` and shuffle it once using the arm seed in deterministic sorted-stratum order;
4. iterate sorted labels and select the first candidate whose P record has not been used;
5. mark the chosen P record globally used within that arm;
6. exclude a label if no unused exact-stratum P record remains.

No comparison-source token length, token content, D score, illustration subtype, or outcome may influence matching.

## Arm-level sample gates

Each arm independently requires:

- >= **60 matched L–P pairs**;
- >= **8 represented folios**;
- number of distinct P records used equals the pair count.

If either arm fails its frozen sample gate, that arm is **BLOCKED** and the H86 conjunction cannot PASS.

## Primary statistic

For matched pair `j` in an arm:

`delta_j = D_label_j - D_paragraph_j`

and

`Delta = mean(delta_j)`.

**Prospectively frozen H86 prediction:** `Delta < 0` in both arms.

Report for each arm:

- matched pairs and folios;
- label/P mean and median D;
- exact-pattern-agreement fractions;
- Delta;
- by-folio mean deltas.

## Frozen nulls and multiplicity

Two arm-level tests are performed, so use a Bonferroni familywise alpha of **0.05 / 2 = 0.025 per arm**.

Each arm uses exactly **9,999 paired sign-flip permutations**.

- Arm A null seed: `20261021`.
- Arm B null seed: `20261023`.

For every permutation, independently multiply each frozen `delta_j` by +1 or -1 with probability 0.5 and recompute the mean.

Lower-tail Monte Carlo p:

`p_lower = (1 + count(null_Delta <= observed_Delta)) / 10000`.

All 9,999 permutations must complete for an arm to be inferentially valid.

## Frozen diagnostics

Descriptive only; they do not create alternate PASS routes:

1. absolute encoded token-length difference for labels and P controls;
2. equal encoded-length fraction for labels and P controls;
3. sensitivity restricted to matched pairs where both the L and P token pair each have equal source lengths, only if >=30 pairs across >=6 folios; otherwise `NOT_RUN_INSUFFICIENT_SAMPLE`;
4. qualifying P-record token-count distribution.

## Decision

### Arm status

An arm = **PASS** iff:

1. source verification and exact-record parsing are valid;
2. >=60 pairs and >=8 folios;
3. 9,999/9,999 permutations complete;
4. `Delta < 0`;
5. `p_lower <= 0.025`.

An adequately sampled valid arm missing either inferential condition = **FAIL**.

An arm failing source/parsing/sample/permutation validity = **BLOCKED**.

### H86 conjunction

H86 = **PASS** only if **both ZL↔IT and ZL↔GC arms PASS**.

H86 = **FAIL** if both arms are valid/inferentially executable but at least one fails the preregistered negative-direction criterion.

H86 = **BLOCKED** if either arm is BLOCKED; any valid other-arm result is reported descriptively but cannot rescue the conjunction.

## Interpretation boundary

A PASS would replicate H85's previously unregistered inverse observation after prospectively fixing the direction, using a new ZL source against both H85 transcription traditions. It would materially weaken the simple claim that label-vs-paragraph differences arise because labels are transcriptionally less stable. It would also provide positive evidence that isolated label tokens preserve equality/repetition structure unusually well across these transcription traditions.

A PASS would still **not** establish semantics, object names, plaintext, language, or decipherment. The three pairwise comparisons would also not be statistically independent because they share source traditions and the same manuscript.

A FAIL would mean the H85 inverse direction does not robustly transfer to both new ZL edges under the frozen protocol.

A BLOCKED result would be a data/alignment limitation, not evidence for or against label stability.

Regardless of outcome:

- semantic identification: **NOT_RUN**;
- language identification: **NOT_RUN**;
- translation: **NOT_RUN**;
- decipherment: **NOT_RUN**.

# H87 — Leave-one-folio-out equality-pattern codebook recurrence

Status before execution: **NOT_RUN**.

## Question

H66 established that strict `L*` label loci differ from matched `P*` paragraph tokens using five low-dimensional features invariant to arbitrary symbol renaming. H87 asks a different generative question:

> After exact confound matching and removal of symbol identities, do label tokens reuse **exact equality/repetition templates** outside their own folio more strongly than paragraph controls of the same length?

Examples of canonical equality templates:

- `abba -> (0,1,1,0)`
- `xyyx -> (0,1,1,0)`
- `abcd -> (0,1,2,3)`

A positive result would support a restricted structural-template/codebook account of the label register. It would not identify meanings or a cipher.

## Frozen corpora

Use exactly the two H66 sources:

### Zandbergen-Landini
- repository: `cesarjz/Voynich`
- commit: `47e6a77dc9d5cd570c375f4aff710fa4a0567278`
- path: `corpus/voynich_eva.txt`
- Git blob SHA-1: `2a4533ab9bdfa85db9bad602d590978953055df1`

### Takahashi
- repository: `oklo/voynich_gpt`
- commit: `2d7c61c387ad6962de730caf73c48612bc8f6957`
- path: `IT2a-n.txt`
- Git blob SHA-1: `7f491b574b65e5fba6b553e57372c3fa50e10fec`

Any blob mismatch is **BLOCKED**.

## Frozen parsing and eligible tokens

Reuse the H66/H60 conventions:

1. page metadata are read from IVTFF headers; retain Currier (`$L`) and hand (`$H`);
2. remove IVTFF markup, bracketed spans, brace annotations and numeric `@...;` annotations;
3. replace `?` with a separator and retain lowercase alphabetic tokens of length >=2;
4. positive candidate = generic `L*` locus with exactly one cleaned token and no `?` in the original record;
5. control candidates come only from generic `P*` loci;
6. `C*`, `R*`, unknown loci and non-P running text are forbidden controls.

No label subtype (`Lc/Lf/Ln/...`) is used.

## Frozen matching — without replacement

H60/H66 sampled a P control with replacement. That is inappropriate for a recurrence test because reusing the same P occurrence could artificially inflate control recurrence. H87 therefore preregisters a new **without-replacement** matching rule before execution.

For each corpus separately:

- exact matching stratum = `(folio, Currier, hand, token_length)`;
- each eligible label may receive at most one P-token occurrence from the exact stratum;
- each P-token occurrence may be used at most once;
- labels are sorted by `(folio, token, Currier, hand)`;
- P occurrences are retained in deterministic parse order inside each stratum, shuffled once with the corpus-specific seed, and consumed sequentially.

Seeds:

- ZL pairing seed: `20261024`;
- Takahashi pairing seed: `20261025`.

No token content, equality pattern, result, visual subtype, or downstream score may influence control selection.

## Canonical equality pattern

For every matched token, replace symbols by first-occurrence IDs. Only the resulting integer tuple is retained for H87 scoring.

Token length is exactly matched within each pair and is not itself evidence.

## Leave-one-folio-out pooled codebook

For each held-out folio `f` independently:

1. remove **all** matched pairs from folio `f`;
2. pool both members (`L` and matched `P`) of every remaining training pair into a single **unlabelled** training multiset;
3. within each token length, count exact canonical equality patterns in that pooled multiset;
4. never build separate L and P training codebooks.

Thus the training codebook contains no class labels. A held-out label and its matched P control of the same length are scored against the identical training distribution.

For held-out token `t`, let `c_f(pattern(t))` be the count of that exact canonical pattern in the pooled same-length training multiset excluding folio `f`.

Frozen token recurrence score:

`R_f(t) = log(1 + c_f(pattern(t)))`.

For matched held-out pair `i`:

`delta_i = R_f(label_i) - R_f(paragraph_i)`.

Within held-out folio `f`:

`Delta_f = mean(delta_i)`.

Primary corpus statistic:

`Delta = equal-folio mean(Delta_f)`.

Every represented folio therefore has equal weight regardless of label count.

## Frozen prediction

For each corpus independently:

`Delta > 0`.

That is, labels should reuse out-of-folio canonical templates more strongly than exact-length matched P controls if a restricted structural codebook contributes to the H66 signal.

## Sample validity

Each corpus requires:

- >= **60 matched pairs** after without-replacement matching;
- >= **8 represented folios**;
- every held-out folio must have at least one matched pair and a nonempty pooled same-length training codebook for every evaluated pair.

Pairs whose token length has no training tokens after removing their folio are excluded **before scoring** and counted. If the remaining evaluable sample drops below 60 pairs or 8 folios, the corpus arm is **BLOCKED**.

## Frozen null and familywise control

There are two confirmatory corpus arms, so familywise alpha 0.05 is Bonferroni-controlled at **0.025 per arm**.

For each arm perform exactly **9,999 folio-block sign-flip permutations**:

- freeze the observed `Delta_f` values;
- for each permutation independently multiply each folio's entire `Delta_f` by +1 or -1 with probability 0.5;
- recompute the equal-folio mean.

This preserves all within-folio dependence.

Seeds:

- ZL null seed: `20261026`;
- Takahashi null seed: `20261027`.

One-sided Monte Carlo p:

`p_upper = (1 + count(null_Delta >= observed_Delta)) / 10000`.

All 9,999 permutations must complete.

## Frozen diagnostics

Descriptive only; none creates an alternative PASS route:

1. held-out exact-pattern-seen fraction (`training count > 0`) for labels and P controls;
2. median recurrence score for labels and P;
3. by-folio `Delta_f` distribution and fraction of folios with `Delta_f > 0`;
4. results by token length for lengths with >=20 evaluable pairs, without inferential p-values;
5. number of unique equality patterns observed in labels and P in the matched sample.

## Decision

A corpus arm = **PASS** iff:

1. source/parsing/matching validity passes;
2. >=60 evaluable pairs and >=8 folios;
3. 9,999/9,999 folio-block permutations complete;
4. `Delta > 0`;
5. `p_upper <= 0.025`.

A valid adequately sampled arm missing either inferential condition = **FAIL**.

An arm with source/sample/permutation failure = **BLOCKED**.

H87 overall = **PASS** only if **both ZL and Takahashi arms PASS**.

H87 overall = **FAIL** if both arms are valid but at least one fails.

H87 overall = **BLOCKED** if either arm is blocked; a valid other-arm result is still reported but cannot rescue the conjunction.

## Interpretation boundary

A PASS would show that the symbol-renaming-invariant label-vs-paragraph distinction includes a stronger property than the five H66 summary features: label tokens would preferentially occupy a reusable out-of-folio codebook of exact repetition templates under an unlabelled pooled reference distribution.

This could be consistent with a restricted morphological register, identifier grammar, templated nomenclature, or structured generator. It would not distinguish those mechanisms and would not establish object semantics, natural language, plaintext, translation, or decipherment.

A FAIL would show that H66's transferable structural signal does not reduce to greater exact-template recurrence.

Regardless of outcome:

- semantic identification: **NOT_RUN**;
- language identification: **NOT_RUN**;
- translation: **NOT_RUN**;
- decipherment: **NOT_RUN**.

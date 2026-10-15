# H93 visual-equivalence → lexical-similarity test — preregistration

## Status

**PASS** (preregistration only). Execution: **NOT_RUN**.

## Rationale

H92 cleanly falsified the preregistered geometry → label-length endpoint. H93 is a distinct prospective hypothesis and MUST NOT be interpreted as a rescue of H90/H92. It asks whether visually similar objects carry more similar associated label strings than visually dissimilar objects.

## Frozen population

Use only the 153 object–label pairs in the 9 independent folios that passed the H91 blind Stage-B geometry gate. Pair membership, object geometry, label-box ordinal, and folio membership are frozen before lexical exposure. No pair or folio may be removed after token strings are read except for a deterministic missing/empty-token provenance failure, which must be reported and makes the confirmatory execution **BLOCKED** unless the missingness rule can be applied without lexical-value selection.

## Primary visual predictor

For every unordered pair of the 153 frozen objects, define a geometry-only feature vector from the already frozen H91g/H91 Stage-B object record:

`[log(area), log(width/height), overlap_fraction]`

Standardize each feature globally using means and standard deviations computed from the 153 frozen objects only. Define visual distance as Euclidean distance in this standardized 3-D feature space. No lexical value may be used to construct, tune, weight, or select these features.

## Primary lexical endpoint

After the visual-distance matrix is completely frozen and hashed, expose only the token strings attached to the already frozen label-box ordinals. Define lexical distance as normalized Levenshtein distance:

`edit_distance(token_i, token_j) / max(len(token_i), len(token_j))`.

No transliteration normalization, glyph-class collapsing, semantic grouping, language assumption, or manual token correction is allowed beyond the frozen source representation.

## Test statistic

Primary statistic: Spearman correlation `rho` between visual distance and lexical distance across all unordered object pairs.

Directional alternative frozen prospectively: visually closer objects should have lexically closer labels, therefore the expected association is **rho > 0** between visual distance and lexical distance.

Because object-pair observations are dependent, significance MUST NOT use the ordinary Spearman asymptotic p-value.

## Null and permutation test

Use 19,999 permutations. On each permutation, shuffle complete token identities among the 153 frozen object slots **within folio only**, preserving each folio's token multiset and all geometry. Recompute lexical pair distances and Spearman rho. Seed: `20261010` using NumPy `default_rng`.

One-sided permutation p-value: `(1 + count(null_rho >= observed_rho)) / (1 + 19999)`.

## Decision rule

Familywise caution is required because H93 follows a failed H92 in the same research program. Freeze alpha = **0.001**.

- **PASS** iff observed `rho > 0` AND permutation `p <= 0.001`.
- **FAIL** iff execution is complete and the PASS rule is not met.
- **BLOCKED** iff provenance, token resolution, frozen-pair reconstruction, or infrastructure prevents a complete protocol-faithful execution.
- **NOT_RUN** until an actual execution exists.

No secondary endpoint, alternate distance metric, subset, folio deletion, glyph normalization, two-sided reinterpretation, or threshold change may rescue a primary **FAIL**.

## Mandatory controls

1. **Pairing scramble negative control:** deterministically scramble label assignments within folio before computing the observed statistic; seed `93001`. It is descriptive only and cannot rescue the primary endpoint.
2. **Cross-folio-only sensitivity:** recompute rho using only object pairs from different folios. This is descriptive only and cannot rescue the primary endpoint.
3. Report the number of frozen objects, resolved tokens, unordered pairs, per-folio counts, observed rho, null median rho, p-value, and all hashes needed for replay.

## Interpretation ceiling

A **PASS** would establish only a reproducible statistical association between coarse visual similarity and lexical string similarity in the frozen H91 family. It would NOT identify meanings, language, plaintext, cipher mechanism, translation, or decipherment. A **FAIL** falsifies this specific visual-equivalence/lexical-similarity hypothesis under the frozen representation.

## Strict downstream state at preregistration

- H91 geometry family gate: **PASS**
- H92 geometry → label length: **FAIL**
- H93 preregistration: **PASS**
- H93 execution: **NOT_RUN**
- Semantics: **NOT_RUN**
- Language: **NOT_RUN**
- Translation: **NOT_RUN**
- Decipherment: **NOT_RUN**

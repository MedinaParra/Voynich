# H82 — f68r2 centre-mark ↔ label-morphology test

Status before execution: **NOT_RUN_EXPLORATORY**.

## Evidential tier and contamination disclosure

H82 is prospectively frozen before computing its statistic or permutation p-values, but it is **not confirmatory**.

The external f68r2 CSV was inspected during hypothesis selection after H79–H81. Its rows contain both the visual centre classification and the associated label readings. Therefore H82 is discovery-contaminated at the dataset-inspection level even though the exact test below is frozen before calculation.

A PASS may only be described as **PASS_EXPLORATORY** and must be replicated on an untouched visual/object-labelled panel or independent annotation before any confirmatory claim.

## Purpose

H79 established a strong f68r1 object↔label positional association. H80 rejected a locally smooth topology→label-form prediction, and H81 did not support a special paragraph-rarity prediction in its valid ZL arm.

H82 tests a different discrete-object hypothesis on a different panel:

> Do f68r2 stars with an ink-marked centre (`ring` or `dot`) carry label forms that are more morphologically separated from labels on visually `plain` stars than expected by chance, after preserving exact token length?

This is a visual-class ↔ character-form association test. It does not assign a meaning to either visual class.

## Frozen external source

Repository: `RN-Top/Voynich`

Revision: `1eb6c0d1e98fb56acaadc0095c4d88a4a1c5bed0`

Path: `analyses/star_centres_f68r2_r3.csv`

Required Git blob SHA-1:

`b19bbeae51334ab124f05f081b5dc6e07ef2ae42`

The file was created independently of this H82 protocol and reports f68r2 star coordinates, centre class, hand reading, ZL label locator/string, and a separate `plant_match` field.

H82 MUST ignore `plant_match` completely.

The source's own preregistration/report discloses that centre classification was intended to precede label placement but was not fully blind because some labels were visible during gridded-tile inspection. This limitation is part of the reason H82 remains exploratory regardless of p-value.

## Frozen row selection

Use only rows with `panel == f68r2`.

Required raw cardinality: exactly **23** rows.

Required `centre` values: only `plain`, `ring`, or `dot`.

Visual binary class:

- `marked` = `ring` or `dot`;
- `plain` = `plain`.

For the label form, read only the `zl_label` field. It must contain a locator followed by whitespace and then the transcription string. Extract the substring after the first whitespace.

A row is label-valid iff the extracted string matches exactly:

`^[a-z]{2,}$`

No bracket expansion, punctuation removal, `@number` decoding, fuzzy repair, spelling correction, stemming, EVA equivalence classes, or hand-reading substitution is permitted.

Rows failing this exact label-validity rule are excluded and reported.

Frozen sample-validity gates after this mechanical filtering:

- >= **18** valid rows total;
- >= **5** valid `marked` rows;
- >= **12** valid `plain` rows;
- >= **4** distinct exact token lengths;
- every valid row has a unique star ID.

Failure is **BLOCKED**.

## Frozen morphology distance

For every unordered pair of valid label strings compute ordinary character-level Levenshtein distance and normalize by the longer token:

`d(i,j) = levenshtein(token_i, token_j) / max(len(token_i), len(token_j))`

No learned model, n-gram tuning, glyph substitution matrix, reversal, stem extraction, or semantic dictionary is allowed.

Define:

- `D_between` = mean distance over all marked–plain pairs;
- `D_marked` = mean distance over all marked–marked pairs;
- `D_plain` = mean distance over all plain–plain pairs;
- `D_within = 0.5 * (D_marked + D_plain)`;
- primary statistic `S = D_between - D_within`.

The preregistered direction is **positive**: if the visible centre class corresponds to a discrete label-form class, between-class labels should be more dissimilar than labels within the same visual class.

Also report mean token length separately by visual class as a descriptive diagnostic only.

## Frozen null A — unrestricted visual-class assignment

Use exactly **19,999** permutations with seed `20261014`.

For each draw:

1. hold the complete valid token inventory fixed;
2. hold the number of `marked` and `plain` positions fixed;
3. uniformly permute the binary visual-class labels over all valid tokens;
4. recompute `S`.

Upper-tail Monte Carlo p:

`p_unrestricted = (1 + count(null_S >= observed_S)) / 20000`.

## Frozen null B — exact-length-preserving visual-class assignment

This is the primary confound control.

Partition valid positions by exact token length. Within each exact-length stratum, permute the observed `marked`/`plain` class labels among the tokens in that stratum. Singleton or single-class strata remain fixed.

Use exactly **19,999** permutations with seed `20261015`.

Exchangeability gates:

- >= **10** valid positions belong to exact-length strata containing both visual classes;
- >= **3** exact-length strata contain both visual classes;
- at least **4** marked positions are movable under the exact-length-preserving null;
- 19,999/19,999 permutations complete.

Failure of any exchangeability gate is **BLOCKED**.

Upper-tail Monte Carlo p:

`p_length_preserving = (1 + count(null_S >= observed_S)) / 20000`.

## Frozen decision

The two nulls form a conjunction. Bonferroni family alpha 0.05 gives `alpha = 0.025` for each.

H82 = **PASS_EXPLORATORY** only if all source/sample/exchangeability gates pass and:

1. `S > 0`;
2. `p_unrestricted <= 0.025`;
3. `p_length_preserving <= 0.025`.

H82 = **FAIL_EXPLORATORY** if all validity gates pass but any scientific criterion fails.

H82 = **BLOCKED** for source-integrity, sample, exchangeability, or execution failure.

No row-repair rule, visual-class definition, distance metric, weighting, length stratum, seed, permutation count, or alpha may be altered after viewing H82 output.

## Frozen outputs

Record:

- source revision/path/blob SHA-1 and integrity result;
- raw f68r2 row count;
- every excluded row with star ID and exact exclusion reason;
- valid sample size and marked/plain counts;
- exact token-length inventory by class;
- movable positions/marked positions and mixed-length strata for null B;
- `D_between`, `D_marked`, `D_plain`, `D_within`, observed `S`;
- descriptive mean length by class;
- both null means/SDs, p-values, seeds, and completed permutation counts;
- overall status.

## Interpretation boundary

A PASS_EXPLORATORY would support only this narrow statement:

> In the externally annotated f68r2 sample, visible marked-centre versus plain-centre stars are associated with a difference in their attached ZL label character forms that survives exact token-length-preserving permutation.

It would not establish what `ring`/`dot` means, identify a celestial catalogue, show that the labels are star names, identify a language, recover plaintext, translate any label, or decipher the manuscript.

Because the source table was inspected before H82 preregistration and the external annotation was not perfectly blind, a positive result MUST be followed by an untouched independent replication before promotion beyond exploratory status.

A FAIL_EXPLORATORY would narrow the visual-class route: the external centre marking would not show the frozen label-morphology separation prediction.

H79 geometric star↔label pairing (A0): **PASS**.
H80 local star-topology label morphology: **FAIL**.
H81 star-label paragraph rarity: **BLOCKED** (valid ZL arm **FAIL**).
H82 centre-mark ↔ label morphology: **NOT_RUN_EXPLORATORY**.
Semantic identification A1+: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

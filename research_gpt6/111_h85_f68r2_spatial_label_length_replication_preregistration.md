# H85 — f68r2 spatial ↔ label-length replication challenge

Status before execution: **NOT_RUN_EXPLORATORY**.

## Evidential role and contamination disclosure

H80 on f68r1 prospectively tested character-form similarity on robust local star edges. Its confirmatory character-form hypothesis failed, but its frozen descriptive length diagnostic showed smaller absolute label-length differences on neighboring than on non-neighboring stars (`1.4783` versus `1.8101`).

H85 treats that **length-only pattern as discovery** and asks whether a simpler global spatial-length relation replicates on the different f68r2 panel.

The f68r2 external table was already inspected for H82, including its coordinates and label strings. Therefore f68r2 is not a pristine unseen dataset. H85 is prospectively frozen before calculating the spatial-length statistic, but any positive result is capped at **PASS_EXPLORATORY**, not confirmation.

## Primary question

> On f68r2, are stars that are farther apart spatially also more different in attached label length than expected under random reassignment of the same label inventory?

This tests only a possible coarse positional/organizational code in **token length**. It does not test meaning.

## Frozen primary source — f68r2

Repository: `RN-Top/Voynich`

Revision: `1eb6c0d1e98fb56acaadc0095c4d88a4a1c5bed0`

Path: `analyses/star_centres_f68r2_r3.csv`

Required Git blob SHA-1:

`b19bbeae51334ab124f05f081b5dc6e07ef2ae42`

Use only rows with `panel == f68r2`.

Required raw cardinality: exactly **23** rows.

For each row:

- coordinates = numeric `(x,y)` from the table;
- label source = `zl_label` only;
- extract the substring after the first whitespace in `zl_label`;
- retain the row only if the extracted label matches exactly `^[a-z]{2,}$`;
- define `token_length = len(extracted_label)`.

No special-marker decoding, punctuation removal, bracket expansion, hand-reading substitution, stemming, EVA equivalence, spelling correction or fuzzy repair is permitted.

This deliberately reuses the exact mechanical H82 label-validity rule.

Required primary sample gates:

- >=18 valid rows;
- >=5 distinct token lengths;
- unique star IDs;
- nonzero variance in pairwise spatial distances and pairwise absolute length differences.

Failure is **BLOCKED**.

## Frozen primary statistic

For every unordered pair of valid f68r2 stars `(i,j)` compute:

- `G_ij = sqrt((x_i-x_j)^2 + (y_i-y_j)^2)`;
- `L_ij = abs(token_length_i - token_length_j)`.

Primary statistic:

`rho_obs = SpearmanCorrelation({G_ij}, {L_ij})`

over all unordered pairs.

Average ranks are used for ties. The preregistered direction is **positive**: greater spatial separation should correspond to greater label-length difference if length participates in a coarse spatial organization.

Pairwise dependence is handled by permuting complete labels among fixed star positions, not by using an asymptotic correlation p-value.

## Frozen primary null

Use exactly **19,999** label-assignment permutations, seed `20261018`.

For every draw:

1. keep all f68r2 star coordinates fixed;
2. uniformly permute the complete valid token-length vector among the fixed star IDs;
3. recompute all pairwise absolute length differences;
4. recompute the same Spearman `rho`.

Upper-tail Monte Carlo p:

`p_f68r2 = (1 + count(null_rho >= rho_obs)) / 20000`.

Use a repository-local SplitMix64 PRNG with deterministic rejection-sampled `randbelow` and Fisher-Yates shuffling.

## Frozen primary decision

H85 = **PASS_EXPLORATORY** iff all primary validity/execution gates pass and:

1. `rho_obs > 0`;
2. `p_f68r2 <= 0.05`;
3. 19,999/19,999 permutations complete.

H85 = **FAIL_EXPLORATORY** if the primary f68r2 test is valid but either scientific criterion fails.

H85 = **BLOCKED** for source-integrity, sample, variance or execution failure.

No coordinate transform, distance metric, label cleaning, token-length definition, p-value direction, seed or threshold may be changed after output is viewed.

## Frozen f68r1 discovery diagnostic

To quantify the observation that motivated H85, run the same global statistic on the already-used f68r1 H79/H80 inventory. This arm is **diagnostic only** and cannot alter the H85 decision.

Sources:

### Independent f68r1 star centres

Repository: `seeton/Voynich-public`

Revision: `8920f2e506fce4c2c5a1245fb21a312f25655f1b`

Path: `analysis/annotations/f68r_star_centres.csv`

Required downloaded-file SHA-256:

`e7cb7787118aa71f440fbf544da5b327a6afd8eba8b2989d6e5ca71d40629d04`

### Yale label source

Repository: `YaleDHLab/voynich`

Revision: `c4d36f4595292c92da8c7428e30cb23b700a019b`

Path: `utils/voynichese/coords/f68r1.json`

Required Git blob SHA-1:

`12c4230fdefc8c566e9bdb3626fc6009c70a7533`

Use exactly the frozen H79 star→Yale-occurrence mapping:

`{1:50, 2:38, 3:37, 4:43, 5:31, 6:36, 7:48, 8:53, 9:54, 10:41, 11:32, 12:55, 13:56, 14:46, 15:34, 16:39, 17:59, 18:51, 19:52, 20:40, 21:44, 22:58, 23:57, 24:35, 25:45, 26:47, 27:49, 28:42, 29:33}`.

Resolve each mapped Yale occurrence to its vocabulary token exactly as in H80. Require 29 unique star IDs, 29 unique occurrence indices, and all 29 token strings to match `^[a-z]{2,}$`.

Compute the same pairwise spatial-distance versus absolute-token-length-difference Spearman correlation and an unrestricted 19,999-permutation upper-tail null with seed `20261019`.

Report this f68r1 result only as **discovery diagnostic** because H80 already exposed the local length contrast before H85 was designed. It has no PASS/FAIL gate for H85.

## Frozen outputs

Record:

- all source hashes/integrity checks;
- f68r2 raw and valid row counts plus exact exclusions;
- f68r2 token-length inventory;
- number of unordered pairs;
- primary f68r2 `rho_obs`, null mean/SD/min/max, p-value, seed and completed draws;
- H85 status;
- f68r1 diagnostic `rho`, null summary and p-value;
- explicit interpretation ceiling.

## Interpretation boundary

A `PASS_EXPLORATORY` would support only that the f68r2 labels show a coarse **spatial organization of token length** consistent with the length-only clue first seen descriptively on f68r1. It would not show that length encodes coordinates, distances, star identity, catalogue number, celestial meaning, language, or plaintext.

A `FAIL_EXPLORATORY` would mean the f68r1 descriptive local-length pattern does not replicate as the preregistered global spatial-length association on f68r2, arguing against pursuing token length as a general astronomical spatial code.

H79 geometric f68r1 star↔label pairing (A0): **PASS**.
H80 local f68r1 star-topology character morphology: **FAIL**; local length contrast descriptive only.
H81 f68r1 paragraph rarity: **BLOCKED** (valid ZL arm **FAIL**).
H82 f68r2 centre-mark character morphology: **FAIL_EXPLORATORY**.
H83 f68r2 exact-36 external geometry: **BLOCKED_DATA / BLOCKED_SELECTION**.
H84 hapax exact-length robustness: **FAIL_ROBUSTNESS**.
H85 f68r2 spatial ↔ label length replication: **NOT_RUN_EXPLORATORY**.
Semantic identification A1+: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

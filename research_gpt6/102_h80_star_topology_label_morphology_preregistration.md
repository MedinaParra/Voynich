# H80 — f68r1 robust star-topology ↔ label-morphology test

Status before execution: **NOT_RUN**.

## Purpose

H79 established a strong, token-blind 29/29 spatial pairing between independently annotated f68r1 star centres and the frozen Yale stellar-label position block. H80 is the first textual test permitted to use those admitted pairs.

H80 asks a deliberately narrower question than semantic identification:

> Do labels attached to **robustly adjacent stars** have more similar internal character forms than labels on non-adjacent star pairs, beyond what is expected from the fixed label inventory and beyond exact token-length structure?

This is a spatial-organization / morphology test. It does not identify what any label means.

## Frozen independent star-centre source

Repository: `seeton/Voynich-public`

Revision: `8920f2e506fce4c2c5a1245fb21a312f25655f1b`

Path: `analysis/annotations/f68r_star_centres.csv`

Required downloaded-file SHA-256:

`e7cb7787118aa71f440fbf544da5b327a6afd8eba8b2989d6e5ca71d40629d04`

Required f68r1 properties:

- exactly 29 rows;
- unique `star_id` exactly 1..29;
- `coordinate_frame == crop_x0_0_y0_550` for every row;
- `annotation_method == star-outline Harris-density refinement` for every row.

Any mismatch is **BLOCKED**.

## Frozen Yale source

Repository: `YaleDHLab/voynich`

Revision: `c4d36f4595292c92da8c7428e30cb23b700a019b`

Path: `utils/voynichese/coords/f68r1.json`

Required Git blob SHA-1:

`12c4230fdefc8c566e9bdb3626fc6009c70a7533`

H80 may read the Yale vocabulary **only after** the star graph and H79 mapping are frozen as specified below. No label string is used to define geometry, edge stability, pair inclusion, or graph thresholds.

## Frozen H79 mapping

Use exactly the canonical H79 primary top-left mapping, recorded before H80:

`{1:50, 2:38, 3:37, 4:43, 5:31, 6:36, 7:48, 8:53, 9:54, 10:41, 11:32, 12:55, 13:56, 14:46, 15:34, 16:39, 17:59, 18:51, 19:52, 20:40, 21:44, 22:58, 23:57, 24:35, 25:45, 26:47, 27:49, 28:42, 29:33}`.

The Yale occurrence indices are zero-based positions in the coordinate array.

For each mapped occurrence, read its vocabulary index from the coordinate row and then its token string from the corresponding vocabulary entry.

Token validity gate:

- all 29 mapped labels must resolve to exactly one lowercase ASCII alphabetic string matching `^[a-z]{2,}$`;
- all 29 occurrences and all 29 star IDs must be unique.

Failure is **BLOCKED**.

## Frozen robust star graph

No token string may be consulted while constructing the graph.

### Base graph

Construct an ordinary 2D Delaunay triangulation from the 29 published `(x,y)` star centres using `scipy.spatial.Delaunay` with default options.

The base undirected edge set is the union of all triangle sides, stored as sorted `(min_star_id,max_star_id)` pairs.

A Delaunay/Qhull failure is **BLOCKED**.

### Annotation-jitter stability

Reuse the external/H79 annotation uncertainty without tuning: independently jitter every star x and y coordinate by `Uniform(-35,+35)` pixels.

Use exactly **1,000** jitter draws with seed `20261009`.

For each draw:

1. jitter all 29 star centres;
2. rebuild the Delaunay triangulation;
3. record which **base** Delaunay edges remain present.

A base edge is `stable_edge` iff it is present in at least **0.80** of the 1,000 jitter graphs.

Frozen graph-validity gates:

- 1,000/1,000 jitter graphs complete;
- >= **25** stable edges;
- stable edges touch >= **24** of the 29 star IDs;
- >= **200** unordered non-edge pairs remain after stable-edge selection.

Failure of a graph-validity gate is **BLOCKED**, not FAIL.

## Frozen label-distance metric

For every unordered pair of labels define ordinary character-level Levenshtein distance and normalize as:

`normalized_edit = levenshtein(token_i, token_j) / max(len(token_i), len(token_j))`.

No stemming, EVA-specific equivalence classes, glyph substitution costs, fuzzy normalization, learned embedding, token reversal, or semantic dictionary is allowed.

Primary observed statistic:

`delta_edit = mean(normalized_edit over stable_edges) - mean(normalized_edit over all non_edges)`.

The preregistered direction is **negative**: neighboring stars should have more similar labels if local star topology organizes label morphology.

Also report the raw edge/non-edge means and the analogous absolute token-length-difference contrast as a diagnostic only. The length diagnostic is not a PASS criterion because an exact-length-preserving confirmatory null is specified below.

## Frozen null A — unrestricted label assignment

Use exactly **9,999** permutations with seed `20261010`.

For each draw:

1. keep star centres, stable graph, and star IDs fixed;
2. uniformly permute the complete 29-token label inventory among the 29 star IDs;
3. recompute `delta_edit`.

Lower-tail Monte Carlo p:

`p_unrestricted = (1 + count(null_delta <= observed_delta)) / 10000`.

This null preserves the exact complete label inventory and graph but destroys the admitted star↔label assignment.

## Frozen null B — exact-length-preserving character-form test

This is the confound control required for H80.

Partition the 29 observed star-assigned labels by their **exact token length**. Within each exact-length stratum independently, permute the complete token strings among the star IDs occupying that length stratum. Singletons remain fixed.

Use exactly **9,999** permutations with seed `20261011`.

This null preserves the exact token length at every individual star and tests whether any local similarity depends on character composition rather than merely local length structure.

Validity gates for null B:

- >= **10** of the 29 star positions belong to length strata containing at least two labels;
- >= **2** exact-length strata contain at least two labels;
- 9,999/9,999 permutations complete.

If these exchangeability gates fail, H80 = **BLOCKED**.

Lower-tail Monte Carlo p:

`p_length_preserving = (1 + count(null_delta <= observed_delta)) / 10000`.

## Frozen decision

The two confirmatory nulls form one conjunction and are each tested at Bonferroni `alpha = 0.025`.

H80 = **PASS** only if all validity gates pass and:

1. `delta_edit < 0`;
2. `p_unrestricted <= 0.025`;
3. `p_length_preserving <= 0.025`.

H80 = **FAIL** if execution/sample validity passes but any scientific criterion above fails.

H80 = **BLOCKED** for source-integrity, mapping/token, graph, exchangeability, or execution failure.

No threshold, Delaunay rule, jitter threshold, edit metric, length stratum, or alpha may be changed after viewing the result.

## Frozen outputs

Record:

- source hashes and integrity checks;
- frozen H79 star→occurrence mapping;
- the 29 resolved token strings and lengths;
- base Delaunay edge count;
- edge-preservation fraction for every base edge;
- stable-edge list/count and covered-star count;
- non-edge count;
- observed edge and non-edge normalized-edit means and `delta_edit`;
- edge/non-edge absolute-length-difference means and contrast;
- exact-length stratum inventory and movable-position count;
- both null means/SDs, p-values, seeds and completed permutation counts;
- overall status.

## Interpretation boundary

A PASS would support **local topological organization of label morphology around actual f68r1 stars**, surviving exact token-length control. It would elevate the H79 A0 spatial pairing into a stronger structural relation, but still would not establish a specific meaning, identify a language, prove proper names, identify a celestial catalogue, or translate text.

A FAIL would be equally informative: despite H79's very strong object↔label spatial pairing, the assigned label strings would not show the preregistered local-topology morphology relation. That pattern would be compatible with individual names/identifiers or other non-smooth coding systems and would narrow the class of spatially organized encoding hypotheses.

H78 local visual-context stability: **BLOCKED**.
H79 geometric star↔label pairing (A0): **PASS**.
Semantic identification A1+: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

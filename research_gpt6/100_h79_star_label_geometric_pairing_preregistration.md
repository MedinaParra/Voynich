# H79 — f68r1 star↔label geometric pairing gate

Status before execution: **NOT_RUN**.

## Renumbering provenance

This protocol was first frozen, before any execution result was inspected, as `98_h78_star_label_geometric_pairing_preregistration.md` in commit `34a299f48a3a4c1fdd902084e86ff80d52266a2e`.

A repository audit then found that identifier **H78 was already occupied** by the earlier, distinct `98_h78_local_visual_context_stability_preregistration.md`. To avoid two different experiments sharing one identifier, the present protocol is canonically renumbered **H79**.

**No source, algorithm, seed, threshold, null, sensitivity, stability criterion, PASS/FAIL/BLOCKED rule, or interpretation boundary is changed by the renumbering.** The duplicate-H78 execution, if GitHub Actions starts it from an earlier queued commit, is superseded for scientific reporting and must not be used as an additional replication.

## Purpose

H77 showed that a global-Otsu connected-component decomposition is not stable enough to define manuscript objects. H79 therefore changes the measurement basis rather than relaxing H77.

H79 asks whether an **independently published, label-blind set of 29 f68r1 star centres** can be put into a statistically non-random and annotation-jitter-stable one-to-one spatial correspondence with the **29 Yale text boxes previously frozen as the f68r1 stellar-label block**, without using any EVA/Voynich token string in the scoring path.

H79 is a geometric pairing/admissibility gate. It does not identify the meaning of any label.

## Frozen independent star-centre source

Repository: `seeton/Voynich-public`

Revision: `8920f2e506fce4c2c5a1245fb21a312f25655f1b`

Path:

`analysis/annotations/f68r_star_centres.csv`

Required source properties:

- exactly 29 rows with `page == f68r1`;
- `star_id` exactly `1..29`, unique;
- every row `coordinate_frame == crop_x0_0_y0_550`;
- every row `annotation_method == star-outline Harris-density refinement`;
- downloaded CSV SHA-256 exactly `e7cb7787118aa71f440fbf544da5b327a6afd8eba8b2989d6e5ca71d40629d04`, as recorded in the frozen external `stellar_catalogue_match` manifest.

Any source-integrity mismatch is **BLOCKED**.

The external preregistered contract states that these centres were annotated from star outlines on a high-resolution image without consulting label transcription content. H79 treats that provenance as frozen external input and does not modify the centres.

## Frozen Yale label-position source

Repository: `YaleDHLab/voynich`

Revision: `c4d36f4595292c92da8c7428e30cb23b700a019b`

Path:

`utils/voynichese/coords/f68r1.json`

Required Git blob SHA-1: `12c4230fdefc8c566e9bdb3626fc6009c70a7533`.

The Yale JSON contains a vocabulary and a coordinate-box array. H79 MUST NOT read or score vocabulary/token strings. It uses only the second JSON array of coordinate boxes.

The frozen f68r1 stellar-label block is zero-based Yale occurrence indices **31 through 59 inclusive**, exactly 29 boxes. This block was previously established by the independent external contiguous-alignment audit and is frozen here before execution.

No alternative start/end index may be searched in H79.

## Coordinate invariance

The external star centres and Yale text boxes are in different pixel scales/crops but share the conventional page orientation. H79 therefore does not fit a pixel transform from correspondences.

For each point set separately, convert x and y coordinates to normalized average ranks:

`rank01 = (average_rank - 1) / (n - 1)`

with ranks computed independently for x and y. This makes the comparison invariant to translation and monotonic axis-wise scale changes and avoids estimating a transform using any proposed star↔label pairs.

Star points use their published `(x,y)` centres.

### Primary label anchor

Use each Yale label box **top-left `(x,y)`**. This matches the primary position anchor used in the frozen external Yale-label geometry audit and avoids token-width displacement.

### Sensitivity label anchor

Repeat with bbox centre `(x + width/2, y + height/2)`.

The primary assignment itself remains the top-left-anchor assignment.

## Frozen one-to-one assignment

For a star-rank point `s_i` and label-rank point `l_j`, cost is ordinary Euclidean distance in normalized rank space.

Use the Hungarian / linear-sum assignment minimizing total cost over all 29×29 possible pairs.

Primary statistic:

`mean_assigned_rank_distance`

= mean Euclidean cost of the 29 pairs in the optimal assignment.

Lower is more concordant.

Also report median and maximum assigned distance, but they are not primary decision statistics.

## Frozen geometric null

Use exactly **9,999** permutations with seed `20261007`, independently for primary and sensitivity anchors.

For each null draw:

1. keep the 29 label x-ranks fixed;
2. uniformly randomly permute the complete 29 label y-ranks among those x-ranks;
3. keep the 29 star-rank points fixed;
4. rerun the full Hungarian assignment;
5. record mean assigned rank distance.

This null preserves exactly:

- the number of stars and labels;
- every label x rank;
- every label y rank as a marginal distribution;
- every star coordinate;
- the assignment optimizer itself.

It destroys only the observed 2D coupling of label x and y positions.

Monte Carlo lower-tail p:

`p = (1 + count(null_cost <= observed_cost)) / 10000`.

Primary concordance criterion: `p_top_left <= 0.01` and observed cost < null mean.

Sensitivity criterion: bbox-centre `p <= 0.05` and observed cost < its null mean.

## Frozen annotation-jitter pairing stability

The external catalogue-match contract already froze ±35 high-resolution image pixels per coordinate axis as an annotation-error sensitivity. H79 reuses that value without tuning.

Use exactly **1,000** jitter draws with seed `20261008`.

For every draw:

1. independently add `Uniform(-35,+35)` to x and y of every one of the 29 star centres;
2. recompute star x/y normalized ranks from the jittered coordinates;
3. keep primary top-left label rank points fixed;
4. rerun Hungarian assignment;
5. compare each `star_id -> Yale occurrence index` pair to the unjittered primary assignment.

For each of the 29 base pairs, report the fraction of jitter draws preserving that exact pair.

A pair is `jitter_stable` iff preservation fraction >= **0.80**.

Pairing-stability gate: at least **20 of 29** base pairs must be jitter_stable.

Also report the median pair-preservation fraction across all 29 pairs.

## Frozen decision

H79 = **PASS** only if all are true:

1. both source-integrity gates pass;
2. exactly 29 star centres and exactly 29 frozen Yale label boxes are loaded;
3. primary top-left geometric concordance has observed cost < null mean and `p <= 0.01`;
4. bbox-centre sensitivity has observed cost < null mean and `p <= 0.05`;
5. at least 20/29 base primary pairs preserve the exact assignment in >=80% of the 1,000 ±35 px jitter draws;
6. all 9,999/9,999 primary and sensitivity null draws and all 1,000/1,000 jitter draws complete.

H79 = **BLOCKED** for source-integrity, cardinality, or execution failure.

H79 = **FAIL** if execution is valid but either geometric-concordance criterion or the frozen pairing-stability criterion is not met.

The thresholds and frozen Yale occurrence block must not be modified after viewing output.

## Frozen outputs

Record:

- source hashes/provenance checks;
- the 29 star IDs and coordinates;
- the 29 Yale occurrence indices and bbox coordinates, **without vocabulary strings**;
- primary and sensitivity observed/null metrics and p-values;
- primary unjittered optimal mapping `star_id -> Yale occurrence index` with distances;
- preservation fraction for every base pair over 1,000 jitters;
- jitter-stable pair count;
- overall status.

## Interpretation boundary

A PASS would support a reproducible **A0 spatial association / object-indexed pairing** between the independently annotated f68r1 star centres and the frozen Yale stellar-label position block, and would yield a prospectively admitted set of spatial star↔label-position pairs for a later morphology-vs-object-descriptor test.

A PASS would not show that any label is a proper star name, coordinate, decan, constellation member, natural-language word, or cipher plaintext. Token strings are not used by H79.

A FAIL would mean this cross-source geometric operationalization does not recover a sufficiently strong and jitter-stable object↔label pairing; no pair table from H79 may then be promoted to semantic analysis.

H76 visual-candidate admissibility: **PASS**.
H77 connected-component stability: **BLOCKED**.
H78 local visual-context stability: **separate pre-existing protocol**.
Semantic identification beyond A0: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

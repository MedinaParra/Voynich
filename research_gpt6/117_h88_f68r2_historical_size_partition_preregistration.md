# H88 — f68r2 historical 36+23 size-partition admissibility audit

Status before execution: **NOT_RUN**.

## Purpose

H83 found that the exact 36-object external-geometry route was blocked because the modern assisted-human reference contains 59 confirmed f68r2 stars but did not itself label which 36 belong to the interior system.

A historical source independent of the current decan/catalogue hypothesis supplies a stronger prospective constraint: Jorge Stolfi's late-1990s VIB description of f68r2 states that the diagram contains a ring of **23 small stars** and an interior filled with **36 stars**, with the interior stars described as larger than the border stars. The contemporaneous `f68r2.S` unit additionally records labels on the interior-star sequence and predates the present research program.

H88 asks only whether the frozen 59-object human reference contains an **unsupervised, reproducible two-size partition** that recovers the historical 23-small / 36-large split without choosing a threshold to force the count.

This is a data/admissibility audit. It is not a semantic, decan, catalogue, language, translation, or decipherment test.

## Historical constraint frozen before execution

Historical VIB material used only to define the prediction:

- source family: Jorge Stolfi / VIB Voynich notes;
- f68r2 description: 23 small border/ring stars and 36 larger interior stars;
- `f68r2.S`: labels on the interior stars, edited 1999-01-28, with the reading-order inventory predating this experiment.

The historical source is **not** used to tune any numeric threshold in the modern coordinate data.

## Frozen modern sources

Repository: `brigadire/voinich`

Revision: `2bb4437906b714c1fba26f9897f8df3e7660a0b0`

### Confirmed object endpoints

Path:

`research/astro_spatial_human_completeness/job_18_object_freeze_c1_0/CONFIRMED_ENDPOINTS.tsv`

Expected Git blob SHA-1:

`e9733f16dc18b32ab5643c6d08a11f395c49a9c1`

Use only rows satisfying all of:

- panel = `f68r2`;
- object class = `STAR`;
- geometry = `BOX`;
- reference role = `STAR_REFERENCE`;
- canonical ID begins `HOBJ_f68r2_` or `HNEW_STAR_f68r2_`.

Require exactly **59** unique f68r2 stars. Any other count is **BLOCKED**.

### Frozen human label↔star groups

Path:

`research/astro_hapax_star_label/f68r2_astronomical_name_search_v1/F68R2_GROUP_SCOPE.tsv`

Expected Git blob SHA-1:

`5bcab575377d59147f313acc5929804f84bf02ab`

Use only rows with:

- panel = `f68r2`;
- relation semantics = `VISUAL_ASSOCIATION_GROUP`;
- human confidence = `HIGH`;
- exactly one `star_ids` value.

Require exactly **24** such groups and 24 unique associated star IDs. Otherwise **BLOCKED**.

The transcription crosswalk field is deliberately ignored. H88 must not use Voynich token content, locus identity, Stolfi label identity, or proposed astronomical names.

## Frozen size measurements

For each star bounding box `(x1,y1,x2,y2)` define:

- width `w = x2 - x1`;
- height `h = y2 - y1`;
- primary size scalar `A = w*h` (bounding-box area);
- robustness size scalar `D = sqrt(w^2+h^2)` (bounding-box diagonal).

Require `w>0`, `h>0` for every star. Any invalid box is **BLOCKED**.

The analysis uses `log(A)` and `log(D)` separately. No other size feature may create an alternative PASS route.

## Frozen unsupervised partition

For each of `log(A)` and `log(D)` independently:

1. sort the 59 scalar values ascending;
2. consider every possible contiguous split after ranks `1..58`;
3. for each split compute the total within-cluster sum of squared deviations from the two cluster means;
4. choose the split with the unique minimum total SSE;
5. label the lower-mean cluster `small` and the higher-mean cluster `large`.

This is the exact global optimum of one-dimensional `k=2` clustering. The algorithm is forbidden from targeting a 23/36 count, changing `k`, choosing a manual threshold, removing outliers, or tuning the size metric after seeing the split.

If the minimum-SSE split is tied exactly, that metric is **BLOCKED** for non-unique partitioning.

## Frozen historical prediction

The historical 23-small / 36-large description predicts, without threshold tuning, that BOTH frozen size metrics recover:

- small cluster size = **23**;
- large cluster size = **36**.

Additionally, because the frozen human groups represent visually associated labels on stars, all **24** group-associated star IDs must lie in the `large` cluster under BOTH metrics.

The two metrics must produce the **same 59-object membership partition** exactly. This robustness conjunction prevents promotion of a count recovered only by one convenient size proxy.

## Decision

H88 = **PASS_ADMISSIBILITY** iff all conditions hold:

1. both frozen source hashes match;
2. exactly 59 valid unique f68r2 star boxes are present;
3. exactly 24 unique HIGH-confidence human label↔star groups are present;
4. both `log(A)` and `log(D)` have unique global two-cluster optima;
5. both independently yield exactly 23 small + 36 large;
6. the two metrics yield identical object membership;
7. all 24 grouped stars are in the common 36-object large cluster.

H88 = **FAIL_ADMISSIBILITY** if source/data validity passes but any of conditions 5–7 fails.

H88 = **BLOCKED** for source-hash, parsing, object-count, invalid-box, group-count, or non-unique-optimum failure.

## Mandatory diagnostics

Report, without changing the decision:

- optimal split rank for each metric;
- best and second-best total SSE for each metric;
- `max(small)` and `min(large)` in raw area/diagonal units;
- boundary ratio `min(large)/max(small)`;
- number and IDs of grouped stars falling in the small cluster, if any;
- exact 23 small IDs and exact 36 large IDs if a partition is obtained;
- agreement count between the area and diagonal partitions.

## Interpretation boundary

A PASS would **not** prove a decan interpretation. It would materially change only the H83 data status: the modern 59-star reference would contain a reproducible exact 36-object large-star subset consistent with an independent historical 36-interior / 23-border description, without selecting 36 objects by a tuned radius or hand-picked threshold.

Only after a PASS may a separately preregistered external-geometry test freeze those exact 36 IDs and compare them with a historical 36-item candidate family.

A FAIL means the currently frozen bounding-box geometry does not objectively recover the historical split under this preregistered size route; no alternate threshold may be tuned post hoc to rescue it.

Semantic identification: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

# H89 — f68r2 border-ring geometry admissibility test

Status before execution: **NOT_RUN**.

## Purpose

H88 froze an unsupervised and perfectly metric-consistent partition of the 59 human-confirmed f68r2 stars into **24 small + 35 large**. All 24 HIGH-confidence label-associated stars fall in the 35-large set, but the historical Stolfi/VIB description predicts 23 small border/ring stars and 36 interior stars.

H89 tests one and only one follow-up explanation permitted by that historical description:

> Are the 24 H88-small objects geometrically decomposable, without any tuned distance threshold, into exactly 23 stars surrounding the interior plus exactly one spatially interior small star?

This is a geometric data-admissibility test. It does not test decans, astronomical identities, label meaning, language, translation, or decipherment.

## Frozen sources

Use exactly the H88 human-reference source:

- repository: `brigadire/voinich`;
- revision: `2bb4437906b714c1fba26f9897f8df3e7660a0b0`;
- path: `research/astro_spatial_human_completeness/job_18_object_freeze_c1_0/CONFIRMED_ENDPOINTS.tsv`;
- expected Git blob SHA-1: `e9733f16dc18b32ab5643c6d08a11f395c49a9c1`.

Use the same f68r2 `STAR` / `BOX` / `STAR_REFERENCE` extraction as H88 and require exactly 59 valid unique stars.

No transcription file, label string, locus ID, proposed star name, historical catalogue, or decan assignment may be read by H89.

## Frozen H88 partition

The H88 common area+diagonal small set is frozen exactly as these 24 IDs:

- `HOBJ_f68r2_9B165406AD77`
- `HOBJ_f68r2_EBC81EC14071`
- `HOBJ_f68r2_222319BDB3B7`
- `HOBJ_f68r2_3A47CFE17F40`
- `HOBJ_f68r2_1CF5F57F6301`
- `HOBJ_f68r2_11B515BAA47C`
- `HOBJ_f68r2_F78E01F368AC`
- `HOBJ_f68r2_665E5F11C7FC`
- `HOBJ_f68r2_FDEE7796EE6E`
- `HOBJ_f68r2_07C6E78D42DD`
- `HOBJ_f68r2_FD6FEE3E56A4`
- `HOBJ_f68r2_65E2D78262E2`
- `HOBJ_f68r2_50D2198107DB`
- `HOBJ_f68r2_A4F4A1C7116A`
- `HOBJ_f68r2_9C5B596B5265`
- `HOBJ_f68r2_6D595B71AAAC`
- `HOBJ_f68r2_34D8D73B52BB`
- `HOBJ_f68r2_4C62BFF7A717`
- `HOBJ_f68r2_0BCC383185CE`
- `HOBJ_f68r2_90CEDA9618ED`
- `HOBJ_f68r2_7437D0A5A09A`
- `HOBJ_f68r2_7A528C1AAC25`
- `HOBJ_f68r2_CA59FCCC6F79`
- `HOBJ_f68r2_25982A4DBF9C`.

The frozen large set is the exact complement of these 24 IDs within the validated 59-star inventory, hence exactly **35** IDs.

H89 may not change this partition, recompute a different size threshold, remove an outlier, or substitute another modern object inventory.

## Frozen coordinates

For every star box `(x1,y1,x2,y2)`, use only the bounding-box center:

`cx = (x1+x2)/2`, `cy = (y1+y2)/2`.

No box size enters H89.

## Frozen geometry algorithm

### Step A — large-set convex hull

Compute the convex hull of the 35 frozen large-star centers with the deterministic Andrew monotonic-chain algorithm, sorting points lexicographically by `(x,y,canonical_id)`.

Collinear boundary points are permitted. Boundary membership counts as `inside`.

The only numerical tolerance is `1e-9` in cross-product comparisons to protect exact decimal-coordinate arithmetic; this is not a fitted spatial threshold.

Classify each of the 24 frozen small-star centers as inside/on or outside the convex hull of the 35 large-star centers.

### Step B — candidate interior small star

H89 requires **exactly one** of the 24 small stars to be inside/on the large-star convex hull.

If zero or more than one qualify, H89 = **FAIL_ADMISSIBILITY**. No nearest-to-centre or residual ranking may be used to select one.

If exactly one qualifies, call it `small_interior_candidate` and define prospectively:

- proposed interior set = 35 frozen large stars + this one candidate = **36**;
- proposed border set = the remaining **23** frozen small stars.

### Step C — enclosing-ring check

Compute the convex hull of the 23 proposed border-star centers with the same algorithm.

Require every one of the 36 proposed interior-star centers to lie inside/on this 23-star border hull.

This is a threshold-free operationalization of the historical claim that the small stars form a surrounding border/ring around the interior population.

## Decision

H89 = **PASS_ADMISSIBILITY** iff all conditions hold:

1. frozen source blob matches;
2. exactly 59 valid unique f68r2 star centers are recovered;
3. all 24 frozen H88-small IDs exist and the complement contains exactly 35 stars;
4. the 35-large convex hull is valid;
5. exactly **one** H88-small center lies inside/on the 35-large convex hull;
6. the other exactly **23** H88-small centers form a valid convex hull;
7. all exactly **36** proposed interior centers lie inside/on that 23-small border hull.

H89 = **FAIL_ADMISSIBILITY** when source/data gates pass but conditions 5–7 fail.

H89 = **BLOCKED** for source mismatch, parsing/inventory failure, missing frozen IDs, or invalid convex-hull geometry.

## Mandatory report

Report without changing the decision:

- number and IDs of H88-small stars inside/on the 35-large hull;
- exact `small_interior_candidate` if unique;
- exact 23 proposed border IDs if candidate is unique;
- number of proposed interior centers contained by the border hull;
- IDs of any proposed interior centers outside the border hull;
- vertex IDs of both convex hulls;
- hull polygon areas as descriptive diagnostics only.

## Interpretation boundary

A PASS would not establish a decan interpretation or any semantic identity. It would establish a reproducible, text-blind exact 36-object interior subset and exact 23-object border subset from the frozen 59-star human reference, using a historical two-class constraint plus preregistered geometry rather than a tuned radial or size threshold.

Only after PASS may a separate preregistered external 36-item geometric/catalogue hypothesis be tested using the exact frozen 36 IDs.

A FAIL leaves H83's exact-36 external-geometry route blocked; the small/large threshold may not be altered post hoc to rescue it.

Semantic identification: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

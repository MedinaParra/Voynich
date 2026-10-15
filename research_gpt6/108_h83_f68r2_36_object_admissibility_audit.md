# H83 — f68r2 36-object geometric-route admissibility audit

Status: **BLOCKED_DATA / BLOCKED_SELECTION**.

This is a source/admissibility audit, not an executed semantic test and not a post-hoc geometry search.

## Question

Can the currently public object-annotation sources support a defensible, prospectively fixed set of exactly **36 f68r2 interior star objects** for a future label-blind test of a 36-item historical system (for example the decan count-level candidate), without choosing the 36 objects after seeing geometry or labels?

The required standard is intentionally stricter than merely finding 36 plausible stars on the page. A candidate 36-point set must be defined independently of the intended external match and must not be selected post hoc from a larger ambiguous star inventory.

## Source A — seeton/Voynich-public

Frozen revision used in the existing external-catalogue work:

`8920f2e506fce4c2c5a1245fb21a312f25655f1b`

The public stellar-catalogue report states that f68r2 visually contains **36 larger interior stars plus 23 smaller border stars**, but also states that the preregistered automatic/manual segmentation could not reliably separate the two classes. The attempted 36-coordinate layer was therefore discarded rather than retained as a potentially wrong object set.

The same report consequently treated `36` only as a **count-level candidate** for decans and did not open a label-level or point-correspondence test.

Admissibility for exact 36-point geometry: **BLOCKED**.

Reason: the source itself explicitly declines to freeze a reliable 36-coordinate subset.

## Source B — RN-Top/Voynich

Frozen revision inspected:

`1eb6c0d1e98fb56acaadc0095c4d88a4a1c5bed0`

The file `analyses/star_centres_f68r2_r3.csv` provides only **23 confidently label-associated f68r2 stars** for its specific centre-mark experiment. It is not a complete 36-interior-star inventory.

Admissibility for exact 36-point geometry: **BLOCKED**.

Reason: incomplete for the 36-object question.

## Source C — DireLabs/ms408

Frozen revision inspected:

`ff3b282c9eb1c19962429f323f67f3a8ce7d5280`

The coarse f68r2 annotation in `results/annotations/archive/t13_annotations_v0.1-coarse.jsonl` was produced by a model (`claude-sonnet-4-6`), has `qa.reviewed=false`, and supplies only the page-level category `star_count_band = 31+`. It does not provide an exact 36-object coordinate inventory.

Admissibility for exact 36-point geometry: **BLOCKED**.

## Source D — brigadire/voinich AI annotation layers

Frozen revision inspected:

`2bb4437906b714c1fba26f9897f8df3e7660a0b0`

The first AI pass contains **47** f68r2 STAR candidates. A later clean-room AI2 pass contains **59** f68r2 STAR candidates, with 43 matched between AI1 and AI2. The repository's own agreement report explicitly states that off f68r1 the star counts are annotator-sensitive and that human adjudication is required.

These AI counts are useful evidence that a 36-object split is nontrivial; neither pass supplies a frozen interior/border classification yielding 36.

Admissibility for exact 36-point geometry: **BLOCKED**.

## Source E — brigadire augmented human reference

The later assisted human-reference layer is materially stronger than the raw AI layers and must be distinguished from them.

`research/astro_spatial_augmented_human_reference/AUGMENTED_REFERENCE_REPORT.md` records an augmented human-confirmed object reference. However, the reviewer was **assisted by an existing overlay**, so this is not an independent blind gold standard.

Crucially, the panel-level recall summary gives the final human-confirmed f68r2 STAR denominator as:

**59 stars**.

The human-completeness protocol defines neutral visible-object classes (`STAR` and `LABEL`), explicitly permits weak and partially clipped edge stars, and forbids transcription/semantics. It does **not** define a frozen `interior-large` versus `border-small` star subtype that would select exactly 36 of the 59 confirmed f68r2 stars.

Therefore the human reference confirms that the page contains a larger star inventory, but it does not prospectively identify which exact 36 objects form the hypothesized interior system.

Admissibility for exact 36-point geometry: **BLOCKED_SELECTION**.

## Why a post-hoc 36-of-59 selection is not allowed

At this point we know the target count `36` and have already seen multiple f68r2 object inventories. Choosing a size threshold, radial cutoff, connected component rule, or hand-selected subset now and then comparing that chosen 36-point set with an external 36-item system would create a substantial researcher-degree-of-freedom / selection bias.

The following are therefore forbidden as confirmatory rescue steps on these same data:

- choose the 36 stars nearest the diagram centre;
- choose the 36 largest bounding boxes;
- tune a size or radius threshold until 36 remain;
- manually classify 36 as 'interior' after inspecting the geometry;
- select the 36 that optimize an external catalogue/decan score;
- use label strings to decide which stars belong to the 36-set.

Any such analysis could be exploratory only and could not establish a label-blind external referent.

## What would unblock the route

The 36-object route becomes testable only if at least one of the following appears **before** the external geometric score is inspected:

1. an independent image annotation that prospectively defines an operational interior/border rule and yields exactly 36 interior stars;
2. a historically independent source whose diagram itself fixes a one-to-one 36-object correspondence without using Voynich labels;
3. a pre-existing published 36-coordinate f68r2 inventory created for reasons independent of a decan/catalogue hypothesis, with adequate provenance and reproducible object inclusion.

If such a source becomes available, the next test must freeze its exact 36 coordinates, allowed transformations, candidate family, null, multiplicity correction, and label-opening rule **before** computing the external match.

## Frozen audit decision

- f68r2 full assisted-human STAR inventory: **59**.
- prospectively defined exact interior 36 subset in inspected sources: **NOT FOUND**.
- independent blind 36-coordinate reference: **NOT FOUND**.
- exact 36-object geometric decan/catalogue test: **BLOCKED_DATA / BLOCKED_SELECTION**.
- external semantic identification: **NOT_RUN**.
- label opening based on a 36-object external match: **NOT_RUN**.

This does not reject a 36-item historical interpretation. It rejects the evidential admissibility of testing that interpretation by selecting 36 objects post hoc from the currently available f68r2 star inventories.

## Current ladder

H79 geometric f68r1 star↔label pairing (A0): **PASS**.

H80 local f68r1 star-topology label morphology: **FAIL**.

H81 f68r1 star-label paragraph rarity: **BLOCKED** (valid ZL arm **FAIL**).

H82 f68r2 centre-mark ↔ label morphology: **FAIL_EXPLORATORY**.

H83 f68r2 exact-36 external-geometry route: **BLOCKED_DATA / BLOCKED_SELECTION**.

Semantic identification A1+: **NOT_RUN**.

Language identification: **NOT_RUN**.

Translation: **NOT_RUN**.

Decipherment: **NOT_RUN**.

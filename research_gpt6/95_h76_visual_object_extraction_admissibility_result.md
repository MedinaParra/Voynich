# H76 — Blind visual-object extraction admissibility result

Status: **PASS**.

This records the completed execution of the preregistered measurement/admissibility protocol in `94_h76_visual_object_extraction_admissibility_preregistration.md`. H76 is a data-quality gate only; it does not test semantics, language, plaintext, translation, or decipherment.

## Execution evidence

- Branch: `experiment/h58-strict-l-vs-p`.
- Workflow: `H76 visual-object extraction admissibility`.
- Run: `37636896748` (run number 2), conclusion `success`.
- Job: `112845380340` (`h76-visual-object-extraction-admissibility`), conclusion `success`.
- Experimental head executed: `be3d6cedac4eb4da3d6b52beb62f9e53c839c3c4`.
- PR merge checkout: `cecb6e8c4807584b8baa0a93f4e6ac85fe02ef59`.
- Artifact: `h76-visual-object-extraction-admissibility-results`, ID `11491240756`.
- Artifact SHA256: `42492d4091f00fac76f6bcdb5a2bf73605fb99cb5b74a2bf9b30999d88c4a0ca`.
- Artifact size: 6,578 bytes.
- Frozen Yale coordinate revision: `c4d36f4595292c92da8c7428e30cb23b700a019b`.

The workflow successfully fetched the frozen Yale coordinate files, downloaded and decoded the frozen page-image endpoints, ran the preregistered text-masking/Otsu/component pipeline, and uploaded the JSON result.

## f68r1

- image dimensions: **636 × 900**;
- image SHA256: `a7da74a67a4411dc95e650c270c76ffd1a323dc20f55dc9ab718e6344c263d11`;
- Yale coordinate boxes: **65**;
- boxes fully inside image: **65/65 = 1.000**;
- Otsu threshold: **191**;
- foreground pixels after expanded text masking: **125,181**;
- all connected components: **989**;
- admissible components under the frozen area/bbox/border criteria: **57**;
- admissible low-text-overlap components: **57**;
- low-text-overlap fraction: **1.000**;
- median low-text-overlap component area: **138 px**.

Frozen gates:

- >=15 low-text-overlap candidates: **PASS**;
- >=80% low-text-overlap fraction: **PASS**;
- median low-text-overlap area >=60 px: **PASS**.

Page status: **PASS**.

## f68r2

- image dimensions: **636 × 900**;
- image SHA256: `c8ac7f381499fca09cd5c5dd83dd26a0e07d66752d2a0390fb25878ddc1aee60`;
- Yale coordinate boxes: **81**;
- boxes fully inside image: **81/81 = 1.000**;
- Otsu threshold: **182**;
- foreground pixels after expanded text masking: **20,795**;
- all connected components: **506**;
- admissible components: **90**;
- admissible low-text-overlap components: **89**;
- low-text-overlap fraction: **0.9888888888888889**;
- median low-text-overlap component area: **176 px**.

Frozen gates:

- >=15 low-text-overlap candidates: **PASS**;
- >=80% low-text-overlap fraction: **PASS**;
- median low-text-overlap area >=60 px: **PASS**.

Page status: **PASS**.

## Frozen decision

Both frozen pages satisfy every preregistered acquisition, coordinate-compatibility, candidate-count, text-leakage, and median-area gate.

H76: **PASS**.

## Conservative interpretation

H76 establishes a reproducible, text-blinded pool of non-text visual connected-component candidates on `f68r1` and `f68r2` using frozen public page images and Yale text coordinates. This is the first admissibility gate needed by the multimodal E3 route.

It does **not** show that the 57/90 admissible connected components are correctly segmented manuscript objects. A connected component may be a complete object, a fragment of an object, decorative ink, or another non-text visual element. Therefore H76 does not justify label↔object semantics yet.

The next defensible step is a preregistered robustness gate testing whether a substantial subset of the H76 candidates remains geometrically stable under small, prospective perturbations of binarization threshold and text-mask margin. Only a stable subset should be admitted to later spatial label↔candidate pairing.

Infrastructure: **PASS**.
H76 visual-candidate admissibility: **PASS**.
Semantic identification: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

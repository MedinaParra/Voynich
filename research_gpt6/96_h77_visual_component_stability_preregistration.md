# H77 — Visual-component perturbation stability gate

Status before execution: **NOT_RUN**.

## Purpose

H76 established that frozen public images and Yale text coordinates yield enough non-text connected-component candidates on `f68r1` and `f68r2`. H77 asks a narrower measurement question before any label↔object pairing:

> Does a substantial subset of the H76 low-text-overlap candidates remain geometrically recoverable under small, prospectively fixed perturbations of binarization threshold and text-mask margin?

H77 is an **admissibility/robustness gate**, not a semantic hypothesis test. It has only `PASS` or `BLOCKED` scientific status.

## Frozen inputs

Use exactly the same two pages and frozen sources as H76.

### Pages

- `f68r1`
- `f68r2`

### Yale coordinate source

Repository: `YaleDHLab/voynich`

Revision: `c4d36f4595292c92da8c7428e30cb23b700a019b`

Paths:

- `utils/voynichese/coords/f68r1.json`
- `utils/voynichese/coords/f68r2.json`

### Page-image source and frozen H76 hashes

Image endpoint:

`http://www.voynichese.com/2/data/folio/image/glance/color/large/{PAGE}.jpg`

Required **downloaded JPEG-byte SHA-256** values established prospectively for H77 from the completed H76 acquisition record:

- `f68r1`: `a7da74a67a4411dc95e650c270c76ffd1a323dc20f55dc9ab718e6344c263d11`
- `f68r2`: `c8ac7f381499fca09cd5c5dd83dd26a0e07d66752d2a0390fb25878ddc1aee60`

These hashes are over the downloaded JPEG bytes before decoding, exactly as implemented and recorded by H76. A hash mismatch is **BLOCKED**.

## Frozen base extraction

Reproduce the H76 extraction exactly:

- grayscale: `Y = 0.299 R + 0.587 G + 0.114 B`, rounded to uint8;
- global 256-bin Otsu threshold;
- foreground: grayscale strictly below threshold;
- Yale text mask expanded by **3 px**;
- 8-neighbour connected components;
- admissible component iff:
  - area >=40 px;
  - bbox width >=5 and <=160 px;
  - bbox height >=5 and <=160 px;
  - component does not touch image border;
- `low_text_overlap` iff <=10% of component-bbox area is covered by union of original unexpanded Yale text boxes.

Only base components satisfying both `admissible` and `low_text_overlap` enter the H77 stability denominator.

No token string is used in extraction, matching, or decision.

## Frozen perturbation grid

For each page calculate its Otsu threshold once from the unmasked grayscale image. Run the complete extraction under all 9 combinations:

- threshold delta: `{-10, 0, +10}` grayscale levels relative to that frozen Otsu value;
- text-mask expansion margin: `{2, 3, 4}` pixels.

Threshold is clipped to `[0,255]` before applying `gray < threshold`.

The H76-compatible base setting is `(delta=0, margin=3)`. The other **8** settings are robustness challenges.

All component admissibility and low-text-overlap rules remain exactly unchanged across settings.

## Frozen geometric matching

Match base low-text components independently to the low-text components in each alternative setting.

For every possible base↔alternative pair compute:

1. axis-aligned bounding-box intersection-over-union (`IoU`);
2. Euclidean centroid distance in image pixels.

A pair is eligible only if:

- `IoU >= 0.50`; and
- centroid distance `<= 12 px`.

Enforce **one-to-one** matching within each alternative setting by greedily accepting eligible pairs sorted by:

1. descending IoU;
2. ascending centroid distance;
3. ascending base component ID;
4. ascending alternative component ID.

Once either member is assigned it cannot be reused in that setting.

This prevents many H76 fragments from being credited for the same perturbed component.

## Frozen per-component stability definition

For each base low-text component count in how many of the 8 alternative settings it obtains an eligible one-to-one match.

A base component is `stable` iff it is recovered in at least **6 of 8** alternative settings.

For every stable base component also report:

- number of recovered alternatives;
- median IoU across its successful alternative matches;
- median centroid distance across its successful alternative matches.

## Frozen page-level gates

Each page independently must satisfy all of:

1. frozen image SHA-256 matches H76;
2. base setting reproduces H76 exactly for:
   - image dimensions;
   - Otsu threshold;
   - admissible component count;
   - low-text-overlap component count;
3. every one of the 8 alternative settings produces at least **10** low-text-overlap admissible candidates;
4. at least **15** base candidates are `stable`;
5. stable fraction among base low-text candidates is at least **0.50**;
6. median, across stable components, of each component's median successful-match IoU is at least **0.60**.

Frozen H76 reproduction targets:

### f68r1
- dimensions: `636 × 900`;
- Otsu threshold: `191`;
- admissible components: `57`;
- low-text-overlap components: `57`.

### f68r2
- dimensions: `636 × 900`;
- Otsu threshold: `182`;
- admissible components: `90`;
- low-text-overlap components: `89`.

H77 = **PASS** only if both pages satisfy every frozen gate.

H77 = **BLOCKED** if either page fails source integrity, H76 reproduction, perturbation adequacy, stable-count, stable-fraction, or stable-IoU gate.

The thresholds must not be relaxed after viewing H77 output.

## Frozen outputs

For each page emit:

- source hashes and dimensions;
- reproduced base metrics;
- candidate counts for all 9 perturbation settings;
- one-to-one match counts for each of the 8 alternatives;
- for every base low-text component: bbox, centroid, area, successful-setting count, stable flag, median successful IoU, median successful centroid distance;
- stable count and stable fraction;
- page-level median of stable-component median IoU;
- gate booleans and status.

## Interpretation boundary

A PASS means that a substantial subset of the H76 visual-candidate substrate is not an artifact of one exact Otsu threshold or one exact text-mask margin. That stable subset may then be admitted to a separately preregistered spatial label↔candidate pairing gate.

A PASS does **not** establish that stable connected components are complete manuscript objects, stars, plants, containers, nymphs, or semantic entities.

A BLOCKED result means the current connected-component substrate is too parameter-sensitive for downstream semantic use under this protocol; no spatial label↔object semantics should be inferred from it.

H76 visual-candidate admissibility: **PASS**.
Semantic identification: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

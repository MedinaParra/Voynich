# H76 — Blind visual-object extraction admissibility gate

Status before execution: **NOT_RUN**.

## Purpose

Before any new label↔object semantic test, determine whether a frozen public image/coordinate source supports a reproducible **text-blind visual-object candidate extraction** on two object-rich Voynich pages.

H76 is a data/measurement gate only. It does not test semantics, language, plaintext, translation, or decipherment.

## Frozen pages

Use exactly:

- `f68r1`
- `f68r2`

These pages are frozen because the project already treats them as dense stellar/object-label layouts. Page choice is fixed before execution and is not based on any H76 output.

## Frozen coordinate source

Repository: `YaleDHLab/voynich`

Revision: `c4d36f4595292c92da8c7428e30cb23b700a019b`

Coordinate paths:

- `utils/voynichese/coords/f68r1.json`
- `utils/voynichese/coords/f68r2.json`

The coordinate JSON contains word occurrences and text bounding boxes. These boxes are used only to mask text pixels and to audit page-coordinate compatibility. Token strings must **not** be used to select, retain, reject, merge, or classify visual components.

## Frozen image source

Use the image endpoint documented by the frozen YaleDHLab `download-images.ipynb`:

`http://www.voynichese.com/2/data/folio/image/glance/color/large/{PAGE}.jpg`

for the two frozen pages only.

Record SHA-256 and decoded pixel dimensions for each downloaded JPEG. H76 is the acquisition/measurement gate that establishes those image hashes for downstream experiments; no image hash is selected after seeing H76 component counts.

If either image cannot be downloaded and decoded from this frozen endpoint, H76 = **BLOCKED**.

## Frozen extraction algorithm

Run independently on each page.

### 1. Coordinate compatibility

Parse every occurrence box `[vocab_index, x, y, width, height]` from the Yale coordinate file.

Require:

- decoded image width >= 500 and height >= 700;
- >= 95% of coordinate boxes lie fully inside the decoded image rectangle before clipping.

If either requirement fails on either page, H76 = **BLOCKED**.

### 2. Text mask

Create a boolean text mask from **all** coordinate boxes, irrespective of token identity or locus type.

Expand each box by exactly **3 pixels** on every side and clip to image bounds.

No EVA strings are consulted during masking.

### 3. Binarization

Convert RGB to grayscale using the fixed luminance formula

`Y = 0.299 R + 0.587 G + 0.114 B`.

Compute a single global Otsu threshold from the 256-bin grayscale histogram.

Define foreground as pixels with grayscale strictly below the Otsu threshold, then set every text-mask pixel to background.

### 4. Connected components

Use 8-neighbour connectivity.

A component is an admissible visual-object **candidate** iff all frozen conditions hold:

- area >= 40 foreground pixels;
- bounding-box width >= 5 pixels;
- bounding-box height >= 5 pixels;
- bounding-box width <= 160 pixels;
- bounding-box height <= 160 pixels;
- component does not touch the outer image border.

Do not classify candidates as stars, plants, nymphs, containers, letters, or any semantic type in H76.

### 5. Text-leakage audit

For every admissible component, take its component bounding rectangle. Compute the fraction of that rectangle's pixel area covered by the union of the **unexpanded original** Yale text boxes.

A component is `low_text_overlap` iff this bounding-box overlap fraction is <= **10%**.

This quantity is deliberately geometric rather than foreground-pixel overlap, because foreground pixels inside the expanded text mask have already been removed by design.

The primary count is the number of admissible `low_text_overlap` components.

## Frozen admissibility gates

Each page independently must satisfy all of:

1. image acquisition/decoding succeeds;
2. coordinate compatibility passes;
3. >= **15** admissible `low_text_overlap` components;
4. >= **80%** of admissible components are `low_text_overlap`;
5. median area of `low_text_overlap` components is >= **60** pixels.

H76 = **PASS** only if **both** frozen pages satisfy every gate.

H76 = **BLOCKED** if either page fails any acquisition, coordinate-compatibility, or visual-candidate adequacy gate.

There is no scientific `FAIL` state for H76 because this is an admissibility/measurement gate, not a hypothesis test.

## Frozen outputs

Record per page:

- image URL;
- image SHA-256;
- width and height;
- coordinate box count;
- fraction fully inside image bounds;
- Otsu threshold;
- total foreground pixels after text masking;
- all connected-component count;
- admissible component count;
- low-text-overlap component count and fraction;
- median low-text-overlap component area;
- frozen gate status.

Also emit the bounding box, area, centroid, and text-overlap fraction for every admissible component. Do **not** emit or use token strings in the component table.

## Interpretation boundary

A PASS means only that public frozen page images plus Yale text coordinates admit a reproducible pool of visual candidates after text masking, sufficient to preregister a later spatial label↔object pairing test.

A PASS does not establish that any candidate is correctly segmented as a manuscript object and does not establish any label meaning.

A BLOCKED result means the present frozen extraction/measurement route is inadequate and must not be silently relaxed after inspecting results.

H72 exact label→paragraph recurrence: **FAIL**.
H75 one-edit label→paragraph recurrence: **FAIL**.
Semantic identification: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

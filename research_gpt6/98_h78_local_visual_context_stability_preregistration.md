# H78 — Label-centered local visual-context stability gate

Status before execution: **NOT_RUN**.

## Motivation

H76 established that the frozen public images and Yale text coordinates are technically usable. H77 then returned **BLOCKED** because the connected-component decomposition was strongly sensitive to small changes in the global intensity threshold. The H77 thresholds are not relaxed.

H78 therefore changes the measurement basis rather than tuning the failed segmentation. It asks whether a **continuous, segmentation-free local visual-context descriptor** around frozen text-coordinate anchors is geometrically stable under small, prospectively fixed changes in context radius and text-mask margin.

H78 is a measurement/admissibility gate only. It does not test whether an anchor is a semantic label, whether nearby ink is an object, or whether any Voynich token has a meaning.

## Frozen sources

Use exactly the H76/H77 sources.

Pages:
- `f68r1`
- `f68r2`

Yale coordinate source:
- repository `YaleDHLab/voynich`
- revision `c4d36f4595292c92da8c7428e30cb23b700a019b`
- `utils/voynichese/coords/f68r1.json`
- `utils/voynichese/coords/f68r2.json`

Image endpoint:
`http://www.voynichese.com/2/data/folio/image/glance/color/large/{PAGE}.jpg`

Required downloaded JPEG SHA-256:
- `f68r1`: `a7da74a67a4411dc95e650c270c76ffd1a323dc20f55dc9ab718e6344c263d11`
- `f68r2`: `c8ac7f381499fca09cd5c5dd83dd26a0e07d66752d2a0390fb25878ddc1aee60`

A source-hash mismatch is **BLOCKED**.

## Frozen anchors

Every Yale coordinate box fully contained in the image is an anchor. H78 does not use the token string, token frequency, label subtype, EVA morphology, or any semantic information in extraction, stability scoring, or the decision.

Expected coordinate inventories inherited from H76:
- `f68r1`: 65 boxes, all inside;
- `f68r2`: 81 boxes, all inside.

Any mismatch in dimensions or coordinate count relative to H76 is **BLOCKED**.

## Continuous image representation

Decode RGB and compute grayscale exactly as H76:

`Y = round(0.299 R + 0.587 G + 0.114 B)`.

Compute continuous Sobel gradients on the grayscale image:
- horizontal `Gx` using `scipy.ndimage.sobel(..., axis=1, mode='reflect')`;
- vertical `Gy` using `scipy.ndimage.sobel(..., axis=0, mode='reflect')`;
- magnitude `M = hypot(Gx,Gy) / 8.0` to keep the approximate scale in 8-bit intensity units;
- orientation `theta = atan2(Gy,Gx)` folded modulo pi, so opposite contrast polarity has the same edge orientation.

No binarization, Otsu threshold, connected-component labeling, watershed, contour tracing, or object detector is used in H78.

## Frozen local region

For an anchor box `(x,y,w,h)`, define an outer rectangle by expanding the box by radius `R` in all directions and clipping to the image.

Before measuring the region, mask the union of **all** Yale text boxes expanded by text-mask margin `m`. Thus the descriptor is built only from non-text pixels near the anchor; the anchor's own glyph pixels are excluded as part of the same global text mask.

A setting is valid for an anchor only if at least **600 unmasked pixels** remain in its outer rectangle.

## Frozen descriptor

From the valid non-text pixels in the local rectangle compute a 24-dimensional descriptor:

1. grayscale histogram: 8 equal-width bins on `[0,256)`, normalized to sum 1;
2. gradient-magnitude histogram: 8 bins with fixed edges `[0,2,4,8,16,32,64,128,inf)`, normalized to sum 1;
3. gradient-orientation histogram: 8 equal bins on `[0,pi)`, weighted by gradient magnitude, normalized to sum 1.

Concatenate the three normalized histograms. If an orientation histogram has zero total weight, use eight zeros.

The descriptor is not standardized or fitted from outcomes.

## Frozen visual-signal gate

A valid anchor enters the H78 base denominator only if, at the base setting, its mean continuous Sobel magnitude over unmasked pixels is at least **4.0 intensity units**.

This prevents a stable but nearly blank parchment neighborhood from being counted as an informative visual context.

No thresholded component or object identity is inferred from this gate.

## Frozen perturbation grid

Run all 9 combinations:
- context radius `R ∈ {24, 32, 40}` pixels;
- text-mask margin `m ∈ {2, 3, 4}` pixels.

Base setting: `(R=32, m=3)`.
The other 8 settings are robustness challenges.

The same source image, coordinate boxes, grayscale conversion, Sobel representation and descriptor definition are used in every setting.

## Frozen per-anchor stability

For each base anchor in the denominator, compare its base descriptor with the descriptor of the **same frozen coordinate anchor** under each alternative setting using cosine similarity.

An alternative counts as recovered iff:
- it remains valid with >=600 unmasked pixels; and
- cosine similarity to the base descriptor is >= **0.90**.

A base anchor is `stable` iff it is recovered in at least **6/8** alternative settings.

Report for each base anchor:
- box index and geometry;
- base valid-pixel count;
- base mean gradient magnitude;
- successful-setting count;
- stable flag;
- median cosine similarity across successful settings.

## Frozen page-level gates

Each page independently must satisfy all of:

1. source image SHA-256 matches H76/H77;
2. dimensions and coordinate count reproduce H76;
3. at least **15** base anchors pass the valid-pixel + visual-signal gate;
4. at least **10** base anchors are stable;
5. stable fraction among base admitted anchors is at least **0.50**;
6. median, over stable anchors, of each anchor's median successful cosine is at least **0.93**.

H78 = **PASS** only if both pages satisfy every gate.

H78 = **BLOCKED** if either page fails any frozen gate.

The thresholds must not be relaxed after inspecting H78 output.

## Interpretation ceiling

A PASS would establish only that a segmentation-free, text-masked **local visual-context representation** can be measured reproducibly around a substantial subset of frozen coordinate anchors. It would justify a separately preregistered spatial/visual association experiment.

It would **not** establish that an anchor is a semantic label, that the nearby visual context is one complete manuscript object, or that any visual class corresponds to a word meaning.

A BLOCKED result would mean that this patch-based representation is also too unstable or too visually sparse on these pages; no semantic association test should be built on it without another independently justified measurement basis.

H76 visual-candidate acquisition/admissibility: **PASS**.
H77 connected-component stability: **BLOCKED**.
H78 local visual-context stability: **NOT_RUN**.
Semantic identification: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.
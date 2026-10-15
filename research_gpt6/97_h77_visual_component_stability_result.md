# H77 — Visual-component perturbation stability result

Status: **BLOCKED**.

This records the completed execution of the preregistered robustness/admissibility protocol in `96_h77_visual_component_stability_preregistration.md`. The GitHub workflow completed successfully; the preregistered measurement gates did not.

## Execution evidence

- Branch: `experiment/h58-strict-l-vs-p`.
- Workflow: `H77 visual component stability`.
- Run: `37637686396` (run number 2), conclusion `success`.
- Job: `112848101274` (`h77-visual-component-stability`), conclusion `success`.
- Experimental head executed: `3a2ae078037f8a88dd223bc35518a53fee63bb15`.
- PR merge checkout: `0bc428c761a1d8bb88eb71f9ac3bed1ad4725cea`.
- Artifact: `h77-visual-component-stability-results`, ID `11491161849`.
- Artifact SHA256: `da9d1c134f535d11c7479234bf87ad610a098bf338824baa65935870af183745`.
- Artifact size: 10,106 bytes.
- Runtime dependencies: `numpy==2.4.6`, `pillow==12.3.0`, `scipy==1.17.1`.

Both frozen JPEG-byte hashes matched H76, both Yale coordinate files were fetched successfully, and the base `(Otsu+0, text-mask margin 3)` setting reproduced the H76 dimensions, Otsu thresholds, admissible-component counts, and low-text-overlap counts exactly on both pages.

Infrastructure: **PASS**.
H76 reproduction: **PASS** on both pages.

## Frozen robustness challenge

The complete extraction was rerun over the preregistered 3×3 perturbation grid:

- threshold delta: `-10, 0, +10` grayscale levels relative to page Otsu;
- text-mask margin: `2, 3, 4` px.

The H76 base was `(0,3)` and the other 8 settings were challenges. A base component counted as stable only if it obtained an eligible one-to-one match in at least 6/8 alternatives with pairwise `IoU >= 0.50` and centroid distance <=12 px.

## f68r1

Source/base reproduction:

- image SHA256: `a7da74a67a4411dc95e650c270c76ffd1a323dc20f55dc9ab718e6344c263d11` — matched;
- dimensions: `636 × 900` — matched H76;
- Otsu threshold: **191** — matched H76;
- base admissible components: **57** — matched H76;
- base low-text-overlap components: **57** — matched H76.

All 8 alternative settings retained >=10 low-text candidates: **PASS**.

One-to-one matches from the 57 base components:

- `(delta=0, margin=2)`: **56**;
- `(delta=0, margin=4)`: **57**;
- `(delta=+10, margin=2/3/4)`: **14 / 14 / 15**;
- `(delta=-10, margin=2/3/4)`: **20 / 18 / 18**.

Stable base components: **8/57 = 0.1403508772**.

- preregistered minimum stable count 15: **FAIL gate**;
- preregistered stable fraction >=0.50: **FAIL gate**;
- median of stable-component median IoUs: **0.8264233890**, threshold >=0.60: **PASS gate**.

Page status: **BLOCKED**.

The key pattern is that changing only the text-mask margin at the original Otsu threshold preserves almost all base components, while ±10 grayscale-level changes sharply alter the one-to-one component inventory.

## f68r2

Source/base reproduction:

- image SHA256: `c8ac7f381499fca09cd5c5dd83dd26a0e07d66752d2a0390fb25878ddc1aee60` — matched;
- dimensions: `636 × 900` — matched H76;
- Otsu threshold: **182** — matched H76;
- base admissible components: **90** — matched H76;
- base low-text-overlap components: **89** — matched H76.

All 8 alternative settings retained >=10 low-text candidates: **PASS**.

One-to-one matches from the 89 base low-text components:

- `(delta=0, margin=2)`: **88**;
- `(delta=0, margin=4)`: **89**;
- `(delta=+10, margin=2/3/4)`: **51 / 54 / 55**;
- `(delta=-10, margin=2/3/4)`: **44 / 44 / 42**.

Stable base components: **35/89 = 0.3932584270**.

- preregistered minimum stable count 15: **PASS gate**;
- preregistered stable fraction >=0.50: **FAIL gate**;
- median of stable-component median IoUs: **0.8948863636**, threshold >=0.60: **PASS gate**.

Page status: **BLOCKED**.

## Frozen decision

H77 required **both** pages to satisfy every stability gate. `f68r1` fails both stable-count and stable-fraction requirements, while `f68r2` fails the stable-fraction requirement.

H77: **BLOCKED**.

The thresholds are not relaxed after seeing the result. The 8 stable `f68r1` components and 35 stable `f68r2` components are reported descriptively but are not silently promoted into an admitted semantic-object dataset under H77.

## Conservative interpretation

H76 showed that a single frozen segmentation setting yields many non-text visual connected components. H77 now shows that the **component decomposition itself is strongly threshold-sensitive**, especially on `f68r1`. Therefore the current simple global-Otsu connected-component pipeline is not sufficiently robust to support a downstream claim that its components are stable manuscript objects.

This does not show that the drawings lack object structure. It shows that this particular low-level segmentation operationalization is inadequate for semantic use under the preregistered perturbation challenge.

A defensible next step must change the measurement basis rather than weaken H77. Examples include an independently sourced/manual object annotation with frozen provenance, or a separately preregistered object-specific detector whose object units are not defined by one global intensity threshold.

Infrastructure: **PASS**.
H76 visual-candidate admissibility: **PASS**.
H77 component stability: **BLOCKED**.
Semantic identification: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

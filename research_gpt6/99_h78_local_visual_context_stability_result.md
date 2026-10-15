# H78 — Local visual-context stability result

Status: **BLOCKED**.

This records execution of the preregistered protocol in `98_h78_local_visual_context_stability_preregistration.md`. The workflow completed successfully, but f68r1 failed the preregistered minimum-anchor adequacy gates. No semantic inference is licensed.

## Execution evidence

- Branch: `experiment/h58-strict-l-vs-p`.
- Workflow: `H78 local visual context stability`.
- Run: `37639612169`, conclusion `success`.
- Job: `112854756076` (`h78-local-visual-context-stability`), conclusion `success`.
- Experimental head executed: `9f1ec6750e0dab4818100df39e30b56dfc4d50ea`.
- PR merge checkout: `94c090324e7c24c72ef7e08a18c498e5b9ad5318`.
- Artifact: `h78-local-visual-context-stability-results`, ID `11490519312`.
- Artifact SHA256: `34d7c4663658552abf6baf6ab10dc6e1e11e0f48b9219b15ce1518e65cd854b1`.
- Artifact size: 7,592 bytes.
- Runtime dependencies: `numpy==2.4.6`, `pillow==12.3.0`, `scipy==1.17.1`.

Infrastructure: **PASS**.

## Frozen measurement design

Base setting:

- patch radius: **32 px**;
- text-mask margin: **3 px**.

Robustness alternatives combined radii `{24,32,40}` with margins `{2,3,4}`, excluding the base setting, for **8** alternatives per admitted anchor.

Frozen thresholds included:

- minimum valid pixels: **600**;
- minimum base mean gradient: **4.0**;
- minimum cosine to base: **0.90**;
- minimum successful alternatives for a stable anchor: **6/8**;
- minimum base admitted anchors per page: **15**;
- minimum stable anchors: **10**;
- minimum stable fraction: **0.50**;
- minimum page median stable-anchor median cosine: **0.93**.

## f68r1

Source integrity:

- image SHA256: `a7da74a67a4411dc95e650c270c76ffd1a323dc20f55dc9ab718e6344c263d11` — matched;
- dimensions: `636 × 900` — matched;
- Yale coordinate boxes: **65/65 inside image**.

Base measurement:

- base admitted visual-signal anchors: **9**;
- stable anchors: **9**;
- stable fraction among admitted anchors: **1.000**;
- page median of stable-anchor median cosine: **0.9983944248407135**.

Frozen gates:

- base admitted anchors >=15: **FAIL**;
- stable anchors >=10: **FAIL**;
- stable fraction >=0.50: **PASS**;
- median stable cosine >=0.93: **PASS**.

Page status: **BLOCKED**.

The important measurement pattern is that the nine f68r1 anchors that contain enough non-text local gradient signal are extremely robust to the frozen radius/mask perturbations, but the preregistered sample is too small to admit the page for downstream use.

## f68r2

Source integrity:

- image SHA256: `c8ac7f381499fca09cd5c5dd83dd26a0e07d66752d2a0390fb25878ddc1aee60` — matched;
- dimensions: `636 × 900` — matched;
- Yale coordinate boxes: **81/81 inside image**.

Base measurement:

- base admitted visual-signal anchors: **25**;
- stable anchors: **25**;
- stable fraction: **1.000**;
- page median of stable-anchor median cosine: **0.9993487214466523**.

Frozen gates:

- base admitted anchors >=15: **PASS**;
- stable anchors >=10: **PASS**;
- stable fraction >=0.50: **PASS**;
- median stable cosine >=0.93: **PASS**.

Page status: **PASS**.

## Frozen decision

The family-level H78 protocol required both pages to satisfy all frozen adequacy/stability gates. f68r1 fails the minimum base-anchor and stable-anchor counts.

H78: **BLOCKED**.

The threshold is not lowered and the nine stable f68r1 anchors are not silently promoted into an admitted general visual-context dataset.

## Conservative interpretation

H78 shows that the continuous local Sobel-context descriptor is highly perturbation-stable **where sufficient non-text gradient signal exists**. It is therefore a more robust measurement unit than H77's global connected-component decomposition. However, under the frozen thresholds it has inadequate coverage on f68r1, the page for which H79 now supplies a 29/29 stable star↔label-position pairing.

Consequently H78 does not yet provide enough independent visual descriptors to test whether the 29 H79 star-associated labels encode object properties. A defensible next step should seek independent star-specific descriptors (for example size, ray count, colour/state, or local grouping) or a separately preregistered descriptor-extraction method centred on independently annotated star centres rather than label boxes.

Infrastructure: **PASS**.
H78 local visual-context stability: **BLOCKED**.
H79 geometric star↔label pairing (A0): **PASS**.
Semantic identification A1+: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

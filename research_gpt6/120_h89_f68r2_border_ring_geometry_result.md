# H89 — f68r2 border-ring geometry admissibility result

Status: **FAIL_ADMISSIBILITY**.

This records execution of the frozen protocol in `119_h89_f68r2_border_ring_geometry_preregistration.md`. Infrastructure, source-integrity, and inventory gates all passed. The preregistered unique-small-interior condition failed because four, not one, of the 24 H88-small stars lie inside/on the convex hull of the 35 H88-large stars.

## Execution evidence

- Workflow: `H89 f68r2 border-ring geometry`.
- Run: **37653107604** (run number 2).
- Job: **112901268723** (`h89-f68r2-border-ring-geometry`).
- Experimental branch head executed: `2243fddde2d4a8fa78b48ff3fd11679389a277d7`.
- PR merge checkout: `025c5f2f39f50dcec3fb8a4fd5c6500b8bad2c5e`.
- Artifact: `h89-f68r2-border-ring-geometry-results`, ID **11497986056**.
- Artifact ZIP SHA-256: `0c0e0219ad2205d8190a8fb822aed09f020288cfae60095afaa425db2a901594`.

Infrastructure: **PASS**.

## Frozen source and inventory

- `CONFIRMED_ENDPOINTS.tsv` Git blob SHA-1 observed/expected: `e9733f16dc18b32ab5643c6d08a11f395c49a9c1`.
- valid unique f68r2 stars: **59**;
- frozen H88-small IDs present: **24 / 24**;
- complement H88-large stars: **35**;
- parse errors: **0**.

All inventory gates: **PASS**.

## Large-set convex hull

The convex hull of the frozen 35-large star centers has:

- vertex count: **11**;
- polygon area: **1,875,010.2398**.

Hull vertex IDs:

- `HNEW_STAR_f68r2_6E493FF400D59178`
- `HOBJ_f68r2_ADBB083AC840`
- `HNEW_STAR_f68r2_3F4A557977173F29`
- `HOBJ_f68r2_FBCDB6FC478C`
- `HOBJ_f68r2_3235BA541B1F`
- `HOBJ_f68r2_D660FAABD911`
- `HOBJ_f68r2_209959BE0C31`
- `HOBJ_f68r2_63F4864C6AFB`
- `HOBJ_f68r2_39476885B40C`
- `HOBJ_f68r2_741BC5BEBE14`
- `HNEW_STAR_f68r2_CE325F0FE67F3E21`.

## Frozen unique-candidate test

The protocol required exactly **one** of the 24 H88-small centers to lie inside/on the 35-large convex hull.

Observed count: **4**.

Observed IDs:

- `HOBJ_f68r2_0BCC383185CE`
- `HOBJ_f68r2_50D2198107DB`
- `HOBJ_f68r2_7A528C1AAC25`
- `HOBJ_f68r2_CA59FCCC6F79`.

Therefore the unique small-interior candidate condition fails. The protocol stops here; no one of these four may be selected by distance-to-centre, visual preference, or another post-hoc ranking.

The Step-C 23-border hull is consequently **NOT_RUN**.

## Decision

H89: **FAIL_ADMISSIBILITY**.

No 36-object set is promoted from this convex-hull route.

## Conservative interpretation

H88 showed a robust 24-small / 35-large size partition consistent across area and diagonal, with all 24 label-associated stars in the large population. H89 shows that simple convex containment is too coarse to identify the one additional small unlabeled star that would be needed to reconcile that partition with the historical 23-border / 36-interior description: four small stars occupy the large-set convex region.

This does **not** refute the historical 23+36 structural description. It rejects this preregistered convex-hull operationalization as a unique selector. Any continuation must use an independently frozen ring/boundary or a separately preregistered non-convex/order-based model; it may not choose one of the four candidates after seeing this result.

Semantic identification: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

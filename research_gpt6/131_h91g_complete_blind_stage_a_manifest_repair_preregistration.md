# H91g — complete blind Stage-A manifest repair preregistration

Status: **PASS (preregistration only)**

## Purpose
Prospectively repair only the H91f manifest-compliance failure before any lexical Stage B. H91g is infrastructure/provenance repair, not a rescue or reinterpretation of H90.

## Lexical firewall
During H91g implementation and execution, token strings, token lengths, glyph identities, lexical classes, meanings and semantic annotations MUST NOT be read, retained, printed, hashed as values, or used for selection. Label boxes may be represented only by deterministic ordinal identifiers derived from their frozen coordinate-file order plus their numeric geometry.

## Frozen inputs and unchanged gates
- Yale coordinate source revision: `c4d36f4595292c92da8c7428e30cb23b700a019b`.
- Exclude `f68r1` and `f68r2` mechanically from the independent inventory.
- Visual extractor: unchanged H76/H91c algorithm and thresholds.
- Stage-A candidate rule remains low-text-overlap component count >=15.
- Stage-B folio stability threshold remains >=80% under ±5 px x/y jitter.
- Family gate remains >=2 independent admissible folios and >=40 stable pairs.
- No threshold lowering, folio dropping after inspection, secondary rescue, or semantic claim is allowed.

## Required complete Stage-A manifest schema
Before any lexical exposure, the H91g artifact MUST serialize and hash:
1. Yale source revision and per-folio coordinate blob SHA / SHA-256 plus image SHA-256.
2. Complete canonically ordered folio inventory, exclusions and reasons.
3. For every successful folio, every frozen low-text-overlap visual object with deterministic object ID, bbox, centroid, area, and text-overlap fraction.
4. Label-coordinate boxes as deterministic ordinal IDs with numeric x/y/w/h only; token text is forbidden.
5. Frozen pairing rule identifier/version: nearest eligible label-box centroid to object centroid, Euclidean image coordinates, deterministic tie break by lowest label ordinal; one-to-one assignment resolved globally by sorted `(distance, object_id, label_ordinal)` greedy acceptance. This rule is frozen before lexical exposure and may not change in Stage B.
6. Jitter schedule/version: deterministic Cartesian offsets `(-5,-5),(-5,0),(-5,5),(0,-5),(0,0),(0,5),(5,-5),(5,0),(5,5)` pixels applied to object centroids; no RNG is used, so jitter seed is explicitly `NONE_DETERMINISTIC_GRID_V1`.
7. Executing repository commit SHA supplied by the workflow environment and the SHA-256 of the Stage-A runner source bytes.
8. Candidate folio list/count and SHA-256 of canonical JSON before adding the manifest hash field.

## Falsifiable controls
H91g = **PASS** only if all required fields above are present for the complete inventory, lexical strings remain absent, the H76/H91c positive controls remain exactly f68r1=57 and f68r2=89 low-text-overlap components when checked by the unchanged extractor, and the repaired independent inventory reproduces the previously observed Stage-A candidate count of 168 under the unchanged >=15 rule.

H91g = **FAIL** if the schema is incomplete, lexical values leak, positive controls differ from 57/89, or candidate count differs from 168 without an independently demonstrated source/infrastructure change.

H91g = **BLOCKED** if source acquisition, provenance, or infrastructure prevents complete evaluation. H91g = **NOT_RUN** until an actual execution exists.

## Consequence
Only an H91g PASS may authorize H91b Stage B. Stage B must use the frozen pairing rule and jitter schedule above, still without using lexical values for pairing or folio selection. H92 remains NOT_RUN until the original H91b family gate passes.

No semantic, language, translation, or decipherment claim is made.

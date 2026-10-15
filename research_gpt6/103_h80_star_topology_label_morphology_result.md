# H80 — f68r1 robust star-topology ↔ label-morphology result

Status: **FAIL**.

This records the completed execution of the preregistered protocol in `102_h80_star_topology_label_morphology_preregistration.md`. The workflow and every source/sample/exchangeability gate completed successfully; the preregistered scientific criteria did not.

H80 is a morphology/organization test only. It does not identify label meaning, language, cipher, plaintext, translation, or decipherment.

## Execution evidence

- Branch: `experiment/h58-strict-l-vs-p`.
- Workflow: `H80 star-topology label morphology`.
- Run: `37640978029` (run number 1), conclusion `success`.
- Job: `112859539294` (`h80-star-topology-label-morphology`), conclusion `success`.
- Experimental head executed: `5cb3b1a84dd30993e1285fc4603e729e90286fe7`.
- PR merge checkout: `ff76a81dbcc01276860ad6e8fe1ffc0e280aee08`.
- Artifact: `h80-star-topology-label-morphology-results`, ID `11492660972`.
- Artifact SHA256: `5de9232894152fd363c8ad178dcf993f1fcdf171c1977583f955f1085bd14548`.
- Artifact size: 2,588 bytes.
- Runtime dependencies: `numpy==2.4.6`, `scipy==1.17.1`.

Infrastructure: **PASS**.

## Source integrity and H79 mapping

### Independent f68r1 star centres

- frozen CSV SHA256: `e7cb7787118aa71f440fbf544da5b327a6afd8eba8b2989d6e5ca71d40629d04` — matched;
- f68r1 rows: **29**;
- star IDs: exactly **1..29**, unique;
- coordinate frame and annotation-method checks: **PASS**.

### Yale f68r1 coordinate/vocabulary source

- frozen Git blob SHA-1: `12c4230fdefc8c566e9bdb3626fc6009c70a7533` — matched;
- all 29 canonical H79 occurrence mappings resolved uniquely;
- all 29 resolved tokens matched the frozen lowercase ASCII length>=2 validity rule.

Source/mapping gates: **PASS**.

## Robust star graph

The base graph used ordinary 2D Delaunay adjacency on the 29 independent star centres. Edge robustness was measured over 1,000 independent ±35 px coordinate-jitter graphs, seed `20261009`.

- base Delaunay edges: **74**;
- jitter graphs completed: **1,000/1,000**;
- stable edges at preservation >=0.80: **69**;
- stable edges cover: **29/29 stars**;
- stable-graph non-edge pairs: **337**.

Frozen graph gates required >=25 stable edges, >=24 covered stars and >=200 non-edges. All passed.

Only five base Delaunay edges fell below the 0.80 stability threshold; therefore the tested graph itself is highly robust to the inherited annotation uncertainty.

## Resolved exact-length structure

Exact token-length strata among the 29 star-assigned labels:

- length 4: **4**;
- length 5: **4**;
- length 6: **8**;
- length 7: **6**;
- length 8: **5**;
- length 9: **1**;
- length 10: **1**.

Exact-length-preserving exchangeability:

- movable positions: **27**;
- swappable exact-length strata: **5**.

Frozen requirements were >=10 movable positions and >=2 swappable strata. Both passed.

## Observed topology–morphology contrast

Normalized character-level Levenshtein distance was defined prospectively as edit distance divided by the longer token length.

- mean normalized edit on stable star edges: **0.6854669887278583**;
- mean normalized edit on non-edges: **0.7006912062550045**;
- observed `delta_edit = edge - nonedge`: **-0.0152242175271462**.

The descriptive effect is therefore in the preregistered negative direction: neighboring stars have labels that are very slightly more similar on average. Statistical controls determine whether that difference is stronger than expected from the fixed label inventory and length structure.

## Null A — unrestricted token assignment

Frozen seed: `20261010`.

- permutations: **9,999/9,999**;
- null mean delta: **-0.00037316295156051486**;
- null SD: **0.019777076161518605**;
- observed delta: **-0.0152242175271462**;
- lower-tail Monte Carlo p: **0.2263**.

Preregistered criterion: `p <= 0.025`.

Unrestricted-assignment criterion: **FAIL**.

## Null B — exact-length-preserving token assignment

Frozen seed: `20261011`.

Every individual star retains its observed label length while complete token strings are permuted only among labels of exactly equal length.

- permutations: **9,999/9,999**;
- null mean delta: **-0.016022556390930733**;
- null SD: **0.020067773366921806**;
- observed delta: **-0.0152242175271462**;
- lower-tail Monte Carlo p: **0.5082**.

Preregistered criterion: `p <= 0.025`.

Exact-length-preserving criterion: **FAIL**.

## Length diagnostic

This diagnostic was frozen as descriptive rather than confirmatory:

- stable-edge mean absolute token-length difference: **1.4782608695652173**;
- non-edge mean absolute token-length difference: **1.8100890207715135**;
- edge minus non-edge length contrast: **-0.33182815120629616**.

Thus neighboring stars do tend descriptively to carry labels of more similar length. However, once exact token length at every star is held fixed in the confirmatory null, the observed character-form similarity is essentially null (`p=0.5082`).

## Frozen decision

H80 required all three scientific conditions:

1. `delta_edit < 0` — **PASS**;
2. unrestricted `p <= 0.025` — **FAIL**;
3. exact-length-preserving `p <= 0.025` — **FAIL**.

H80: **FAIL**.

## Conservative interpretation

H79 remains a strong A0 result: the 29 f68r1 star centres and the 29 stellar-label positions form a highly recoverable one-to-one spatial relation.

H80 shows that this spatial relation does **not** extend to the preregistered prediction that adjacent stars carry unusually similar label character forms. The small negative raw edit contrast is compatible with chance, and after preserving exact token length it is centered almost exactly on the controlled null.

Therefore the current evidence disfavors a **locally smooth star-topology code expressed through label character morphology**. It does not reject individual proper names, arbitrary object identifiers, discrete categories, nonlocal catalogue codes, or other systems in which nearby objects need not have similar written forms.

No alternate graph neighbourhood, edit metric, stem definition, glyph-equivalence table, or significance threshold should now be tuned on the same 29 labels to rescue this topology-morphology route.

Infrastructure: **PASS**.
H79 geometric star↔label pairing (A0): **PASS**.
H80 local star-topology label morphology: **FAIL**.
Semantic identification A1+: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

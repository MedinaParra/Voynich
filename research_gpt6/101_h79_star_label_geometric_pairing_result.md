# H79 — f68r1 star↔label geometric pairing result

Status: **PASS**.

This records the canonical execution of the preregistered protocol in `100_h79_star_label_geometric_pairing_preregistration.md`. H79 was renumbered from a duplicate H78 identifier before interpreting any execution result; the scientific protocol itself was unchanged.

H79 is a geometric A0 association / pairing result only. It does not identify label meaning, language, cipher, plaintext, translation, or decipherment.

## Execution evidence

- Branch: `experiment/h58-strict-l-vs-p`.
- Workflow: `H79 star-label geometric pairing`.
- Run: `37639612181` (run number 2), conclusion `success`.
- Job: `112854755453` (`h79-star-label-geometric-pairing`), conclusion `success`.
- Experimental head executed: `9f1ec6750e0dab4818100df39e30b56dfc4d50ea`.
- PR merge checkout: `94c090324e7c24c72ef7e08a18c498e5b9ad5318`.
- Artifact: `h79-star-label-geometric-pairing-results`, ID `11490989214`.
- Artifact SHA256: `838ac743bd68a31b274b42125b74eb2f1dd5a33dbf310dfa29c20560fde8fa17`.
- Artifact size: 2,730 bytes.
- Primary/sensitivity null permutations: **9,999/9,999 each**.
- Annotation-jitter draws: **1,000/1,000**.

Infrastructure: **PASS**.

## Frozen source-integrity gates

### Independent f68r1 star centres

Source: `seeton/Voynich-public`, frozen revision `8920f2e506fce4c2c5a1245fb21a312f25655f1b`, `analysis/annotations/f68r_star_centres.csv`.

- SHA256: `e7cb7787118aa71f440fbf544da5b327a6afd8eba8b2989d6e5ca71d40629d04` — matched expected value;
- f68r1 rows: **29**;
- `star_id`: exactly **1..29**, unique;
- coordinate frame: `crop_x0_0_y0_550` — matched for every row;
- annotation method: `star-outline Harris-density refinement` — matched for every row.

Source-integrity gate: **PASS**.

### Yale label-position boxes

Source: `YaleDHLab/voynich`, frozen revision `c4d36f4595292c92da8c7428e30cb23b700a019b`, `utils/voynichese/coords/f68r1.json`.

- Git blob SHA-1: `12c4230fdefc8c566e9bdb3626fc6009c70a7533` — matched expected value;
- total Yale coordinate boxes: **65**;
- frozen zero-based stellar-label block: occurrence **31..59** inclusive;
- frozen block size: **29**.

The H79 implementation deliberately ignored Yale vocabulary/token strings and decoded only the coordinate-box array for scoring.

Source-integrity/cardinality gate: **PASS**.

## Primary geometric concordance — bbox top-left

Coordinates for the two point sets were independently converted to normalized average x/y ranks. A 29×29 Hungarian assignment minimized total Euclidean distance in this rank space. The null preserved all x and y rank marginals but randomly reassigned label y ranks among fixed x ranks.

Observed assignment:

- mean assigned rank distance: **0.032222772820549986**;
- median assigned rank distance: **0.0357142857142857**;
- maximum assigned rank distance: **0.14285714285714285**.

Frozen null:

- null mean: **0.11468139212648099**;
- null SD: **0.012340279995639426**;
- observed minus null mean: **-0.082458619305931**;
- lower-tail Monte Carlo p: **0.0001**;
- permutations: **9,999/9,999**.

Preregistered criterion: observed < null mean and `p <= 0.01`.

Primary geometric-concordance gate: **PASS**.

## Sensitivity — bbox centre

Repeating the complete test using Yale bbox centres rather than top-left anchors:

- observed mean assigned rank distance: **0.032828638238291116**;
- observed median: **0.03571428571428571**;
- observed maximum: **0.14285714285714285**;
- null mean: **0.11462409378095148**;
- null SD: **0.012387658294002317**;
- observed minus null mean: **-0.08179545554266036**;
- lower-tail Monte Carlo p: **0.0001**;
- permutations: **9,999/9,999**.

Preregistered sensitivity criterion: observed < null mean and `p <= 0.05`.

BBox-centre sensitivity gate: **PASS**.

## Annotation-jitter pairing stability

The external catalogue-match contract had prospectively used ±35 high-resolution-image pixels per coordinate axis as its annotation-error sensitivity. H79 reused that uncertainty unchanged.

- jitter draws: **1,000/1,000**;
- exact-pair preservation criterion: >=0.80;
- stable pair minimum: >=20/29;
- observed stable pairs: **29/29**;
- stable-pair fraction: **1.000**;
- median exact-pair preservation fraction: **1.000**.

All 29 mappings satisfy the frozen stability criterion. Pair-preservation was 1.000 for 27 mappings and 0.999 for the remaining two, still well above the preregistered 0.80 threshold.

Pairing-jitter-stability gate: **PASS**.

## Frozen primary star → Yale occurrence mapping

The admitted primary top-left Hungarian mapping is:

| star_id | Yale occurrence |
|---:|---:|
| 1 | 50 |
| 2 | 38 |
| 3 | 37 |
| 4 | 43 |
| 5 | 31 |
| 6 | 36 |
| 7 | 48 |
| 8 | 53 |
| 9 | 54 |
| 10 | 41 |
| 11 | 32 |
| 12 | 55 |
| 13 | 56 |
| 14 | 46 |
| 15 | 34 |
| 16 | 39 |
| 17 | 59 |
| 18 | 51 |
| 19 | 52 |
| 20 | 40 |
| 21 | 44 |
| 22 | 58 |
| 23 | 57 |
| 24 | 35 |
| 25 | 45 |
| 26 | 47 |
| 27 | 49 |
| 28 | 42 |
| 29 | 33 |

These occurrence indices are positions only. H79 did not use the token strings occupying them.

## Frozen decision

All preregistered source-integrity, cardinality, primary-concordance, sensitivity-concordance, execution-completeness, and annotation-jitter stability gates passed.

H79: **PASS**.

## Conservative interpretation

H79 provides strong evidence that the independently annotated 29 f68r1 star centres and the independently frozen 29-position Yale stellar-label block describe essentially the same page-level two-dimensional object/label layout. The result survives a stringent x/y-marginal-preserving null and is exceptionally stable under the prospectively inherited ±35 px star-centre jitter.

This promotes the f68r1 relation to a reproducible **A0 spatial object↔label-position association** and admits the 29-pair table for a separately preregistered next-stage experiment.

It does **not** identify any label as a star name, celestial coordinate, decan name, catalogue identifier, natural-language word, cipher plaintext, or semantic gloss. The external centres and Yale boxes come from the same manuscript page, so this is not independent-manuscript replication.

The next defensible semantic step requires visual/object descriptors independent of the label strings (for example star size, ray count, colour/state or independently defined local object class) and a prospectively frozen test of whether those descriptors predict label morphology. H79 alone is insufficient for such a claim.

Infrastructure: **PASS**.
H76 visual-candidate admissibility: **PASS**.
H77 connected-component stability: **BLOCKED**.
H79 geometric star↔label pairing (A0): **PASS**.
Semantic identification A1+: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

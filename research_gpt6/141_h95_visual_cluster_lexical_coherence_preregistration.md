# H95 — Visual-cluster lexical-coherence test — preregistration

Status: **PASS** (preregistration only; scientific execution **NOT_RUN**)

## Motivation and separation from H92–H94
H92 (geometry→length), H93 (continuous visual-distance→edit-distance), and H94 (geometry→initial glyph) are closed confirmatory FAILs and will not be rescued. H95 asks a distinct categorical question: whether clusters defined from object geometry alone exhibit greater within-cluster lexical coherence than expected under labels permuted within folio.

## Frozen population and gate
Reproduce H91 exactly. Required gate: 168 Stage-A candidates, 9 admissible folios, 153 stable object-label pairs. Any provenance/reproduction failure is **BLOCKED**; a numerical mismatch without infrastructure error is **FAIL** for the gate and the lexical endpoint is **NOT_RUN**.

## Blind ordering
1. Reconstruct the 153 frozen objects and their geometry without reading token strings.
2. Build the visual representation and cluster assignments; serialize and SHA-256 hash them.
3. Only after the cluster hash is frozen, resolve the paired token strings.

## Visual representation
Per object: `[log(area), log(width/height), x_norm, y_norm]`, globally standardized with population SD (`ddof=0`). Exactly-zero-SD coordinates are deterministically set to standardized 0.0. No token-derived feature may enter clustering.

## Clustering
Deterministic k-means with `k=4`, `random_state=95001`, `n_init=100`. Cluster IDs are canonicalized by lexicographically sorting centroid coordinates. If any cluster has fewer than 10 objects, H95 is **BLOCKED** before lexical inspection because the preregistered categorical endpoint is inadequately supported.

## Primary lexical endpoint
For every unordered pair of objects in the same visual cluster, compute normalized Levenshtein distance `d_lev/max(len(a),len(b))`. Primary statistic is the mean within-cluster lexical distance. Lower values indicate greater lexical coherence.

Null distribution: 19,999 permutations of token assignments **within folio**, preserving geometry, clusters, folio counts, token inventory, and cluster sizes. Seed `20261010`. One-sided p-value `(1 + # null_mean <= observed_mean) / 20000`. Confirmatory PASS requires observed mean < null median and `p <= 0.001`. Otherwise **FAIL**.

## Preregistered controls
- Negative control: one deterministic within-folio token scramble, seed `95002`; report its within-cluster mean distance only.
- Structural sensitivity: report the same-cluster pair count and cluster sizes. These cannot rescue the primary endpoint.
- No alternative k, clustering algorithm, distance metric, folio exclusion, glyph subset, or alpha may rescue H95 after execution.

## Interpretation ceiling
A PASS would establish only a reproducible association between blind visual categories and string-form coherence in this frozen label set. It would **not** establish semantics, identify a language, translate any token, or decipher the manuscript. A FAIL closes this preregistered visual-cluster lexical-coherence hypothesis.

## Decision-state fields
- H95 preregistration: PASS
- H95 execution: NOT_RUN
- Semantics: NOT_RUN
- Language identification: NOT_RUN
- Translation: NOT_RUN
- Decipherment: NOT_RUN

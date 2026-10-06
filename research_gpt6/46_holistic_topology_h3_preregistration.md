# Holistic topology H3 preregistration: held-out line grammar

Status: **NOT_RUN**.

H1 and H2 both returned PASS. H3 tests whether the cross-view topology predicts a third textual representation that was not used to construct either H1 feature family.

## Hypothesis

Edges supported by both discovery views should connect folios with more similar line-position grammar than matched random edges, and should do so at least as strongly as surviving immediate physical adjacency under the same eligible universe.

## Frozen corpus and eligibility
Use the same frozen EVA corpus blob and the same running-text/folio eligibility rules as H1/H2. Labels remain excluded. No illustration semantics, proposed translations, or modern-language hypotheses are used.

## Frozen consensus graph
Construct A-nearest-neighbor and B-nearest-neighbor directed selections exactly as in H2. Convert each to an undirected edge set. The H3 **consensus edge set** is their intersection. No H3 feature may influence edge construction.

If the intersection has fewer than 30 unique edges, H3 is **BLOCKED**.

## Independent Family C — line-position grammar
Family C deliberately excludes H1/H2 feature blocks as primary features. For each folio, derive distributions from running-text lines:
- normalized token-count-per-line histogram, capped at 20;
- normalized first-token-length histogram, capped at 15;
- normalized last-token-length histogram, capped at 15;
- normalized within-line token position of repeated token types, binned into quintiles;
- fraction of lines whose first token repeats elsewhere on the folio;
- fraction of lines whose last token repeats elsewhere on the folio.

Do not use character n-grams, prefix/suffix identity, vocabulary identity, Currier labels, hand labels, section labels, illustration labels, or physical adjacency in Family C.

Compute cosine distance between Family C folio vectors.

## Primary statistic
Mean Family C cosine distance over consensus graph edges. Lower is favorable.

## Matched null
Exactly 999 deterministic null edge sets, seed `20261006`.

For every observed consensus edge `(u,v)`, sample a replacement partner for `u` from the same H1 confound stratum as `v`, excluding self and excluding an observed consensus partner where possible. Deduplicate to an undirected set and resample until the null edge count equals the observed consensus edge count; if this cannot be achieved for a permutation, report it rather than silently changing the design.

Monte Carlo p = `(1 + count(null_mean_distance <= observed_mean_distance)) / 1000`.

## Physical-order comparator
Using the same eligible folios, compute mean Family C distance over surviving immediate physical-neighbor edges. This is a preregistered comparator, not used to construct the consensus graph.

Report `delta_vs_physical = consensus_mean_distance - physical_mean_distance`; negative means learned consensus topology is closer under held-out Family C than surviving physical adjacency.

## Decision
**PASS** iff:
1. consensus graph has at least 30 unique edges;
2. all 999 nulls complete;
3. Monte Carlo p <= 0.05;
4. consensus mean Family C distance is lower than null expectation.

The physical comparator is descriptive and does not determine PASS/FAIL, to avoid requiring the learned graph to outperform a topology that may itself contain genuine production locality.

**FAIL** if execution is valid but the inferential criterion is missed.

**BLOCKED** if consensus graph has <30 edges or matched null construction cannot complete 999 permutations.

Before execution: **NOT_RUN**.

## Interpretation boundary
PASS would show that the topology independently discovered in Families A and B predicts a third, held-out line-grammar representation. This would materially strengthen the case for a shared latent production/document structure and reduce the likelihood that H2 is merely cross-feature redundancy.

It would still not establish original folio order, language, plaintext, cipher mechanism, semantic identity, author, or translation.

Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

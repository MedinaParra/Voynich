# Holistic topology H2 preregistration: cross-view reconstruction

Status: **NOT_RUN**.

Frozen only after H1 returned PASS. H2 asks whether the topology signal can do more than recognize the surviving physical neighbors.

## Hypothesis

A candidate folio graph inferred from one textual view should predict proximity in an independent textual view better than a matched random graph if it captures a genuine latent production/document topology rather than representation-specific noise.

## Discovery and validation separation

Use the same frozen EVA corpus and the same eligibility/parser rules as H1. Labels and illustration semantics remain excluded.

Two reciprocal tests are frozen:

1. **A -> B:** infer a candidate graph using Family A distances only; evaluate its edges using Family B distances.
2. **B -> A:** infer a candidate graph using Family B distances only; evaluate its edges using Family A distances.

Family definitions are exactly those in H1. No feature tuning is permitted.

## Candidate graph

Within each H1 confound-matched candidate universe, each eligible folio selects its nearest other folio in the discovery family. Convert directed selections to a unique undirected edge set. Do not use physical adjacency to select or tune candidate edges.

Report number of eligible nodes, directed selections, unique candidate edges, connected components, and degree distribution summary.

## Primary validation statistic

For each reciprocal test, compute the mean validation-family cosine distance over candidate graph edges. Lower is better.

Secondary descriptive statistics:
- median validation distance on candidate edges;
- fraction of candidate edges that are surviving physical immediate neighbors;
- graph component count and largest-component size.

Physical-neighbor overlap is descriptive only and is not a PASS criterion.

## Null

Exactly 999 deterministic null graphs per reciprocal test, seed `20261006`.

For each folio, replace its discovery-selected partner by a uniformly sampled alternative from the same confound-matched candidate universe, excluding self. Convert selections to an undirected graph exactly as for the observed candidate graph. This preserves the number of node-level selections and available confound strata while destroying the discovery-family nearest-neighbor relation.

Monte Carlo p is `(1 + count(null_mean_distance <= observed_mean_distance)) / 1000` because lower validation distance is the preregistered favorable direction.

## Decision

**PASS** only if both reciprocal tests independently have Monte Carlo p <= 0.05 and both observed validation-family mean distances are lower than their null expectation.

**FAIL** if execution is valid but either reciprocal test misses the frozen criterion.

**BLOCKED** if the H1 eligible/matched universe cannot produce at least 50 unique candidate edges in either reciprocal direction or 999 matched null graphs cannot be completed.

Before execution: **NOT_RUN**.

## Anti-leakage

- Physical adjacency is never used to construct candidate edges.
- Illustration classes or proposed meanings are never used to construct candidate edges.
- No modern-language hypothesis or proposed decipherment is used.
- Discovery-family distances are not used as the primary validation statistic.
- No threshold, k, feature family, or confound stratum may be changed after seeing H2 results.

## Interpretation boundary

PASS would support cross-view generalization of a text-internal folio topology: edges selected because folios are close in one representation are independently close in another representation beyond matched random graphs. It would justify a later H3 comparing this learned graph with codicological/physical order and testing held-out metadata or image structure.

PASS would still not prove that the graph is the original folio order, nor identify language, plaintext, cipher, semantics, author, or translation.

Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

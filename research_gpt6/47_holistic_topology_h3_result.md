# Holistic topology H3 result

Status: **PASS**.

Frozen preregistration: `46_holistic_topology_h3_preregistration.md`.

## Execution evidence
- Branch: `experiment/lexical-anchor-replication`
- Experimental head tested: `06be350623a699e18e9e5c5843843a27ea4c5107`
- PR merge checkout: `63cd492aa63e4442a2cc0a99851b496b45e85692`
- GitHub Actions run: `37548446216` (run 43), conclusion `success`
- Job: `112557983414` (`holistic-topology-h3`), conclusion `success`
- Artifact: `holistic-topology-h3-results`, ID `11451612275`
- Artifact SHA256: `f90d3f433467cabf61e775bfb291509cd7da20cf64b2d07b35f51983dae0608b`
- Frozen corpus blob: `2a4533ab9bdfa85db9bad602d590978953055df1`
- Eligible folios: 205
- Consensus A∩B edges: 96
- Permutations: 999/999

## Held-out Family C result
- observed consensus mean cosine distance: `0.2250253242368878`
- matched-null mean distance: `0.24771460712539195`
- Monte Carlo p: `0.002`
- status: **PASS**

## Physical-order comparator (descriptive, not decision criterion)
- surviving physical immediate-neighbor edges: 189
- physical mean Family C distance: `0.2608629030909592`
- `delta_vs_physical = consensus - physical`: `-0.035837578854071406`

The learned A∩B consensus graph is therefore closer under the independently held-out line-grammar representation than the matched-null expectation. Descriptively, it is also closer under Family C than surviving immediate physical adjacency; this comparison was preregistered as descriptive and does not determine PASS/FAIL.

## Frozen decision
The consensus graph has >=30 edges, all 999 nulls completed, p <= .05, and the observed Family C distance is below the null expectation. H3 therefore **PASS**.

## Conservative interpretation
H1 detected local topology in two independent textual views. H2 showed reciprocal cross-view generalization. H3 now shows that their consensus topology predicts a third representation based on line-position grammar that was held out from graph construction. This materially strengthens evidence for a shared latent production/document structure rather than a signal confined to one feature family.

It does not establish that the consensus graph is the original folio order. It does not identify language, plaintext, cipher mechanism, semantics, author, or translation. A subsequent test should challenge the result with stronger out-of-sample partitioning (e.g. held-out quires/folios or independent transcription) and explicit anti-confound ablations before any semantic use of the topology.

Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

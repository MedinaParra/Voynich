# Holistic topology H2 result

Status: **PASS**.

Frozen preregistration: `44_holistic_topology_h2_preregistration.md`.

## Execution evidence
- Branch: `experiment/lexical-anchor-replication`
- Experimental head tested: `b008bd453fa79f36a4a8d7c5802df6f98b6e1d33`
- PR merge checkout: `84a43894eae87565431424361c9b4966bfa84775`
- GitHub Actions run: `37548152077` (run 39)
- Job: `112557048979` (`holistic-topology-h2`), conclusion `success`
- Artifact: `holistic-topology-h2-results`, ID `11451531995`
- Artifact SHA256: `c7ee457e547f809375f04f1e693221bc1471dddeede807932531240992cd6994`
- Frozen corpus blob: `2a4533ab9bdfa85db9bad602d590978953055df1`
- Eligible folios: 205
- 999/999 null graphs completed in each reciprocal direction

## A -> B
- **PASS**
- unique edges: 141
- directed selections: 194
- validation-family mean distance: `0.05877022628717713`
- null mean validation distance: `0.10472110568040713`
- median validation distance: `0.055538082606597095`
- Monte Carlo p: `0.001`
- physical-neighbor fraction (descriptive only): `0.15602836879432624`
- components: 64; largest component: 14
- degree min/mean/max: 0 / `1.3756097560975609` / 6

## B -> A
- **PASS**
- unique edges: 145
- directed selections: 194
- validation-family mean distance: `0.052731040643267696`
- null mean validation distance: `0.1149507265919795`
- median validation distance: `0.0456907061316526`
- Monte Carlo p: `0.001`
- physical-neighbor fraction (descriptive only): `0.1793103448275862`
- components: 60; largest component: 12
- degree min/mean/max: 0 / `1.4146341463414633` / 5

## Frozen decision
Both reciprocal tests independently satisfy p <= .05 and have observed validation-family mean distances below their matched null expectations. H2 therefore **PASS**.

## Conservative interpretation
A graph selected solely from one text representation generalizes strongly to the independent representation in both directions. This is evidence for a shared text-internal latent structure rather than a signal confined to one feature family. The learned nearest-neighbor graph overlaps surviving physical immediate neighbors only about 15.6% to 17.9%; that overlap is descriptive and was not a decision criterion.

This does not establish that the learned graph is the original manuscript order. It does not identify language, plaintext, cipher, semantic meaning, author, or translation. The next justified test must be preregistered and should determine whether the cross-view graph predicts information not used to build it, ideally with a held-out representation/metadata family and explicit comparison to surviving physical topology.

Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

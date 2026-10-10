# H92 independent geometry–lexical anchor replication — result

## Status

**FAIL** (scientific). Infrastructure: **PASS**.

This result is the preregistered independent replication following the H91 blind Stage-B geometry gate. It does not support a geometry-to-label-length association in the held-out family.

## Frozen execution

- Branch: `experiment/h58-strict-l-vs-p`
- Head commit tested: `c375ef17939f28b25d05224bdd31818266b938c2`
- GitHub Actions run: `38014630896`
- Workflow: `H92 independent geometry lexical-anchor replication`
- Infrastructure conclusion: `success` / **PASS**
- Artifact: `11654639106` (`h92-independent-geometry-lexical-anchor`)
- Artifact size: 3,426 bytes
- Artifact ZIP SHA-256: `aa233a3c76ddc2166235a05e80b7c6b9331518d072b61ca3355582eb2ab159c4`
- Independent family: 9 folios, 153 frozen object-label pairs

## Preregistered primary endpoint

Label length predicted from the frozen H90 geometry predictor family, evaluated with LOOCV and 9,999 folio-stratified token-identity permutations at alpha = 0.01.

Observed results:

- observed MAE: `1.3346098339232229`
- permutation-null median MAE: `1.3165720838722246`
- p-value: `0.897`
- primary status: **FAIL**

The observed error is slightly worse than the permutation-null median and is nowhere near the preregistered significance threshold. H90's suggestive in-sample direction therefore does **not** replicate in this independent held-out family.

## Frozen controls

### Pair-scramble negative control

- observed MAE: `1.354129728642799`
- null median MAE: `1.3164100341192189`
- p-value: `0.9925`

Control status: **PASS as a negative control**; it provides no positive lexical signal and cannot rescue the primary endpoint.

### x/y ablation

- observed MAE: `1.303081681095994`
- null median MAE: `1.284138303277701`
- p-value: `0.8986`

Ablation status: **FAIL as evidence for association**; it cannot rescue the primary endpoint.

## Interpretation

H91 established that a geometry-only object-label pairing family can be selected reproducibly without lexical exposure. H92 now shows that, for the preregistered primary lexical property (label length) and frozen H90 predictor family, those stable geometric pairings do not carry a replicating predictive signal.

This is a clean confirmatory non-replication, not evidence that the Voynich Manuscript has no visual–lexical structure in general. It specifically falsifies the tested H90 geometry-to-label-length anchor as an independently replicating effect under this protocol. No threshold is lowered, no folio is dropped post hoc, and no secondary endpoint rescues the primary failure.

## Strict downstream state

- H91 geometry family gate: **PASS**
- H92 independent geometry → label-length replication: **FAIL**
- semantic interpretation: **NOT_RUN**
- language identification from this branch: **NOT_RUN**
- translation: **NOT_RUN**
- decipherment: **NOT_RUN**

No semantic, language, translation, or decipherment claim follows from this result.

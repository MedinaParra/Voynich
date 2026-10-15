# Independent-transcription topology replication result

Status: **PASS**.

## Execution evidence
- Branch: `experiment/lexical-anchor-replication`
- Experimental head tested: `6a7087af7f6abeff90a51d515514c09d4713f3b9`
- PR merge checkout: `c0c593bb93798b0d764070f5a7a3b866536c2cee`
- GitHub Actions run: `37578255569` (run 62), conclusion `success`
- Job: `112651896887` (`independent-transcription-topology`), conclusion `success`
- Artifact: `independent-transcription-topology-results`, ID `11463572000`
- Artifact SHA256: `7036d27c9f27a1748beebcfbc4cb31f33fbb937207b4c6af8371bd6899e35173`
- Discovery blob: `2a4533ab9bdfa85db9bad602d590978953055df1`
- Independent replication Git blob: `7f491b574b65e5fba6b553e57372c3fa50e10fec`
- Discovery eligible folios: 205
- Aligned eligible folios: 205
- Frozen consensus edges: 96
- Surviving consensus edges: 96
- Permutations: 999/999
- Negative-control permutations: 999/999

## Result
- observed replication distance: `0.2826349474795637`
- matched-null mean distance: `0.31822819065059155`
- negative-control mean distance: `0.41252653272038237`
- Monte Carlo p: `0.004`
- status: **PASS**

## Conservative interpretation
The previously frozen 96-edge A/B consensus topology, discovered on the primary transcription, remains significantly locally coherent when evaluated on the independently sourced Takahashi IT2a-n transcription. The observed distance is lower than the matched-null expectation and substantially lower than the preregistered negative-control distance. This materially strengthens the claim that the topology signal is not merely an idiosyncrasy of one transcription file.

This does not establish original folio order, language, plaintext, cipher mechanism, semantics, author, or translation. The independent transcription uses the same manuscript and EVA-family representation, so shared manuscript-level structure and transcription conventions remain possible explanations. Further replication with another transcription tradition/encoding or image-derived measurements would be stronger.

The lexical-anchor conclusions are unchanged: exact-length Lc/Lf is **FAIL**, and topology-conditioned Lc/Lf is **FAIL**. The structural PASS must not be used to revive those semantic claims.

Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

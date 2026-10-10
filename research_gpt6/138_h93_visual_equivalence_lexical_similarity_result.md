# H93 visual-equivalence → lexical-similarity — result

## Status

**FAIL** (scientific). Infrastructure: **PASS**.

## Frozen execution evidence

- Branch: `experiment/h58-strict-l-vs-p`
- Head tested: `09a41b3f9599d3f9c3886b9ad2cfa408a7d17975`
- GitHub Actions run: `38030981462`
- Job: `114151687279` (`h93`), conclusion `success`
- Artifact: `11662335265` (`h93-visual-equivalence-lexical-similarity`)
- Artifact size: 2,067 bytes
- Artifact ZIP SHA-256: `fa84cd863a5649d92c89405050015314414e9b4e3636caf45736198ea7fb1304`
- Objects: 153
- Unordered object pairs: 11,628
- Constant geometry feature indices: `[2]`, handled exactly under preregistered H93a
- Frozen visual hash: `2c91b5180a545af9d5cfdb53f37242cac5fa49b64d19484b0dc28f4491920ea8`

## Primary endpoint

- observed Spearman rho: `-0.016010678989776265`
- permutation-null median rho: `-0.0006949853854786273`
- one-sided permutation p: `0.8927`
- preregistered alpha: `0.001`
- primary status: **FAIL**

The preregistered directional hypothesis required positive association and p <= 0.001. Neither condition is met.

## Mandatory controls

- within-folio pairing-scramble rho: `0.02770782101047367`
- cross-folio-only sensitivity rho: `-0.013097856471697134`

These controls are descriptive and do not rescue the primary endpoint.

## Interpretation

Under the frozen H91 family and H93 representation, coarse visual similarity does not predict normalized lexical-string similarity. Together with H92, this is a second prospective non-replication within the label-object lexical-anchor program: H92 rejected geometry → label length, while H93 rejects visual-distance → edit-distance association.

This does **not** establish absence of all visual–lexical structure in the Voynich Manuscript and does not support any semantic, language, plaintext, translation, or decipherment claim. No threshold, subset, distance metric, or folio selection is changed post hoc.

## Strict downstream state

- H91 geometry family gate: **PASS**
- H92 geometry → label length: **FAIL**
- H93 visual equivalence → lexical similarity: **FAIL**
- Semantics: **NOT_RUN**
- Language: **NOT_RUN**
- Translation: **NOT_RUN**
- Decipherment: **NOT_RUN**

# H97 — hierarchical folio-state generator result

Status: **FAIL**

## Execution evidence
- Branch: `experiment/h58-strict-l-vs-p`
- Workflow head SHA: `34e319fb80d0f804872bd97f8c0a20880b07f394`
- GitHub Actions run: `38112184808`
- Job: `114389854915`
- Actions conclusion: **PASS** (infrastructure only)
- Artifact: `11693316460` (`h97-hierarchical-folio-state`)
- Artifact size: 2012 bytes
- Artifact SHA-256: `572862fab54d9d615fe98c51ce011a144b4e51e1011e78458f9817bdef2d6625`
- Source SHA-256: `32b11a0b584a75bbe9817c96a316a246f82d02d69996d789bc2cb908190bab77`
- Partition hash: `50c82d6b48da54c3e2a1b70f14743f4c41bb2112ba74976de7185147d9d1766c`
- Eligible folios: 200; development: 160; holdout: 40
- Synthetic replicas: 999

Note: because the workflow was observed through PR context, Actions checked out merge SHA `d6161e81eca79efc2ad7f2b9c678cd246131d0b3`; the artifact provenance nevertheless identifies workflow head SHA `34e319fb80d0f804872bd97f8c0a20880b07f394`. No scientific criterion is changed by this record.

## Mandatory controls
All preregistered controls = **PASS**:
- source SHA: PASS
- partition hash: PASS
- holdout-fit firewall: PASS
- cluster occupancy: PASS
- token-count preservation: PASS
- degeneracy: PASS
- determinism: PASS

Development-state occupancies were **24 / 53 / 32 / 51**, all above the preregistered minimum.

## Confirmatory result
H97 passed **5/8** frozen holdout endpoints, therefore overall **H97 = FAIL** under the preregistered mandatory 8/8 intersection rule.

Endpoint pass mask in frozen order:
`[PASS, PASS, FAIL, PASS, FAIL, PASS, PASS, FAIL]`

The three failed endpoints were:
1. token type/token ratio: real `0.3309131`; synthetic 99% interval `[0.2648253, 0.3209476]`;
2. character bigram conditional entropy: real `2.1006613`; synthetic 99% interval `[2.1151683, 2.1992303]`;
3. consecutive-folio Jensen-Shannon divergence: real `0.0439020`; synthetic 99% interval `[0.0118773, 0.0204252]`.

The within-folio first-half/second-half divergence did pass: real `0.0277658`; synthetic 99% interval `[0.0152312, 0.0287496]`.

## Conservative interpretation
Adding four development-derived folio states materially improves the frozen H96-style signature from the best H96 partial family (4/8) to 5/8, but **does not satisfy the confirmatory criterion**. In particular, the model still generates far too little discontinuity between consecutive folios. This does not identify a cipher, language, scribal state, section state, or physical ordering mechanism. It falsifies only this exact preregistered hierarchical implementation.

The label-object family remains unchanged: H91 geometric pairing = PASS; H92–H95 tested lexical-anchor mappings = FAIL. H97 does not rescue those lexical hypotheses.

Semantics = **NOT_RUN**. Language = **NOT_RUN**. Translation = **NOT_RUN**. Decipherment = **NOT_RUN**.

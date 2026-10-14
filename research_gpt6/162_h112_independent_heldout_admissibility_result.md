# H112 — Independent held-out visual–lexical admissibility: result

## Status

- Infrastructure: **PASS**
- H112 source-admissibility gate: **FAIL**
- Held-out lexical replication: **NOT_RUN**
- Semantics: **NOT_RUN**
- Language identification: **NOT_RUN**
- Translation: **NOT_RUN**
- Decipherment: **NOT_RUN**

## Frozen execution evidence

- Workflow run: `38575708202`
- Job: `115892113494`
- Experimental branch: `experiment/h58-strict-l-vs-p`
- Head SHA: `a23c8cce1a297bff7e7400989b04be8790d89455`
- Artifact ID: `11899318303`
- Artifact name: `h112-independent-heldout-admissibility`
- Artifact size: `848` bytes
- Artifact digest: `sha256:7605a8eceb24441352e3c79325ebe1ff9726ffe0c35363c5bcab4181f7a9f1ac`

GitHub Actions completed successfully, so infrastructure is PASS. The frozen H112 structural audit classified the candidate held-out sources as inadmissible under the preregistered gate: both candidate sources were reachable but did not parse as valid JSON in the frozen audit. Consequently `source_access_parse=false`, no admissible explicit object↔label pairs entered the confirmatory dataset, and the lexical stage was not executed.

## Interpretation

This is a **FAIL of candidate-source admissibility**, not evidence against or for a visual–lexical relationship in the Voynich manuscript. No spelling, token length, token frequency, semantic interpretation, language identification, translation, or decipherment was used to rescue the candidates. Manually repairing the external sources or inferring correspondences after inspecting lexical content would violate the purpose of the held-out gate and is therefore outside H112.

## Stopping rule

Do not reinterpret H112 as a lexical FAIL. Do not repair these candidate source files post hoc for H112. A future confirmatory lexical-anchor test requires a genuinely independent source that passes a separately frozen structural admissibility gate before lexical content is inspected.

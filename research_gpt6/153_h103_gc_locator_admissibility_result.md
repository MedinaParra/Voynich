# H103 — GC locator admissibility result

Status: **FAIL**

## Execution evidence
- Workflow run: `38253474809`
- Job: `114825415948`
- Infrastructure: **PASS** (`completed/success`)
- Executing PR merge commit: `3b17d008df00f6644301f1a5d8e558b59317ef48`, containing experimental head `9548783a873badf0db0da55de4d0a49fc079f166`.
- Frozen GC v101 SHA256: `b09570cb6c993bc2d87134d115e60a978650a8a6495483ddbb1f6005a586096f` — identity control **PASS**.
- Artifact: `h103-gc-locator-admissibility`, ID `11748593676`, ZIP SHA256 `b99898ac54da00336bf532b0074c9e3bd249f6b919d6bbd26b6a805c4c954c09`, 647 bytes.

## Preregistered controls
- `source_sha_identity`: **PASS**
- `all_9_folios_parseable`: **PASS**
- `shared_prefix_all_9`: **PASS**
- `shared_prefix_single_token_all_9`: **FAIL**

The only locator prefix shared across all nine H91 folios was `P`. Parseable record counts were f14v=9, f25v=7, f39r=16, f40r=11, f50v=11, f87r=16, f8v=17, f90r1=9, f95r2=9. However, no locator prefix supplied at least one single-token record on every folio; only f8v had one single-token `P` record.

## Scientific interpretation
H103 therefore **FAILS** its prospectively frozen admissibility criterion. GC v101 does not expose a shared locator class with single-token records across all nine H91 folios under the preregistered parser. This independently explains why the strict H98 visual-label ordinal transfer cannot be repaired simply by replacing the assumed `L` locator with a discovered common prefix.

No post-hoc relaxation to multi-token `P` records, nearest loci, token selection within a record, or folio-specific locator classes is permitted as a rescue of H98/H103. Any future visual→locus bridge must be independently defined and frozen before lexical outcomes are opened, preferably from externally annotated coordinates or an independently auditable visual/transcription alignment.

Semantics = **NOT_RUN** · Language = **NOT_RUN** · Translation = **NOT_RUN** · Decipherment = **NOT_RUN**.

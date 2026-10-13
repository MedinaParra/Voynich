# Independent-transcription topology replication — provenance audit

Status: **BLOCKED**.

Preregistration: `52_independent_transcription_topology_preregistration.md`.

## Audit performed before analysis

The preregistration requires the replication transcription to come from a versioned public source with an immutable commit/blob identifier and requires provenance to be established before any replication statistic is computed.

Public documentation at `voynich.nu` identifies several genuinely distinct transliteration traditions, including Takeshi Takahashi (TT/IT), Zandbergen-Landini (ZL), and Glen Claston (GC/v101). The legacy data directory currently exposes versioned Takeshi files including `TT_ivtff_v0a.txt`, `IT_ivtff_0b.txt`, and `IT_ivtff_1a.txt`. The site's transliteration documentation explicitly describes Takahashi as one of the independent/main transliterations and distinguishes it from ZL and GC.

However, the audited public legacy files are served as mutable web paths rather than from a source-control commit/blob or other immutable content-addressed identifier. The legacy index provides filename/version and modification date, but not an upstream immutable revision identifier. Web/GitHub search in this audit did not establish a trustworthy public Git commit/blob containing the exact candidate Takahashi file.

A copy made now inside this repository would freeze the bytes prospectively, but it would not retroactively satisfy the preregistered requirement that the candidate be fetched from a public source whose exact upstream version is immutably identifiable. Relaxing that requirement after preregistration would weaken the provenance test and is not allowed.

## Decision

**BLOCKED** before statistical execution.

Reason: source independence is historically/documentarily plausible, but the stricter preregistered immutable-upstream provenance criterion has not been satisfied. No topology replication statistic, p-value, PASS, or FAIL was computed.

This is a provenance/infrastructure block, not evidence against the H1-H4 topology result.

## Safe next route

The experiment may be unblocked only by locating a public source-control commit/blob (or equivalently immutable content-addressed archive) for a Takahashi/IT transcription whose lineage is independent of the discovery transcription. The exact bytes and SHA256 must then be frozen before parsing or analysis. Alternatively, a new experiment may be separately preregistered around a different independently authored transcription such as GC/v101, but it must not be called execution of this frozen protocol unless all current criteria are met.

Lexical-anchor exact-length result remains **FAIL**.
Topology-conditioned lexical-anchor result remains **FAIL**.
H1-H4 remain **PASS** under their respective frozen protocols.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

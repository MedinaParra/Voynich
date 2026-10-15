# Independent-transcription provenance audit — immutable source found

Status: **PASS (provenance gate only)**.

This supersedes only the infrastructure/provenance blockage recorded in `53_independent_transcription_provenance_audit.md`; it does not change any scientific result.

## Immutable replication source
A public GitHub copy of the Takahashi IT2a transcription was located and verified before computing replication statistics:

- repository: `oklo/voynich_gpt`
- commit: `2d7c61c387ad6962de730caf73c48612bc8f6957`
- path: `IT2a-n.txt`
- Git blob SHA-1: `7f491b574b65e5fba6b553e57372c3fa50e10fec`
- IVTFF header: `#=IVTFF EvaT 2.0 M 3`
- embedded provenance: `Extracted from LSI_ivtff_0d.txt`, version 2a dated 02/02/2023

The frozen discovery corpus is a different transcription tradition: Zandbergen-Landini, IVTFF Eva- 2.0, version 3b dated 13/05/2025, frozen at `cesarjz/Voynich` commit `47e6a77dc9d5cd570c375f4aff710fa4a0567278`.

The Takahashi and ZL sources are therefore non-identical transcription traditions and are independently frozen at immutable Git commits/blobs. This satisfies the preregistered provenance gate in `52_independent_transcription_topology_preregistration.md`.

The replication itself remains **NOT_RUN** until its preregistered statistic is executed. No result is inferred from source discovery alone.

Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

# Independent-transcription topology replication preregistration

Status: **NOT_RUN**.

## Motivation
H1-H4 support a latent text-internal topology in the frozen EVA corpus, while both exact-length lexical-anchor tests failed. Before any renewed semantic experiment, the structural result should be challenged against transcription dependence. Community resources document multiple partially independent Voynich transcriptions, including Takeshi Takahashi and the Zandbergen/Landini interlinear tradition. This experiment asks whether the H1-H4 topology phenomenon survives a transcription source not identical to the frozen discovery text.

## Primary hypothesis
A/B topology discovered from the frozen discovery transcription predicts held-out structural similarity in an independently sourced EVA transcription better than matched random graphs.

## Data freeze rule
The replication transcription must be fetched from a versioned public source with an immutable commit/blob identifier and its SHA256 recorded before analysis. Prefer a Takahashi line-level transcription when its provenance can be established independently of the discovery file. If the candidate source is merely a reformatted copy of the same underlying ZL/Takahashi text used by discovery, classify the experiment **BLOCKED** rather than claiming independent replication.

No result may be computed until provenance is audited and frozen.

## Folio alignment
Align by canonical folio ID only. Do not use token similarity to repair or infer folio mappings. Require at least 150 folios shared with the 205 discovery-eligible folios; otherwise **BLOCKED**.

## Discovery graph
Use the already-frozen H2 A/B consensus graph from the discovery transcription. No replication-transcription feature may influence graph construction.

## Replication representation R
From the independent transcription, construct only transcription-robust line-level features:
- token-count-per-line histogram (cap 20);
- first-token-length histogram (cap 15);
- last-token-length histogram (cap 15);
- line character-count histogram after EVA normalization (cap 120, bins of 10);
- fraction of repeated token types per folio;
- fraction of lines beginning with a token type seen elsewhere on that folio;
- fraction of lines ending with a token type seen elsewhere on that folio.

No Currier, hand, section, illustration, label-object class, proposed language, semantic class, or translation is a predictor.

Compute cosine distance between replication folio vectors.

## Primary statistic
Mean replication distance over frozen discovery-consensus edges whose endpoints both exist in the replication transcription.

Require at least 60 surviving consensus edges; otherwise **BLOCKED**.

## Matched null
Exactly 999 deterministic null graphs, seed `20261007`. For each observed edge, replace the partner with a folio drawn from the same discovery confound stratum, restricted to replication-available folios. Preserve observed edge count; if 999 nulls cannot be generated without relaxing this rule, **BLOCKED**.

Monte Carlo p = `(1 + count(null_mean_distance <= observed_mean_distance))/1000`.

## Negative control
Also evaluate 999 degree/edge-count-matched random graphs without discovery-stratum matching. This is descriptive and must not replace the primary matched null.

## Decision
**PASS** iff:
1. provenance audit establishes a genuinely non-identical transcription source;
2. >=150 aligned eligible folios;
3. >=60 surviving frozen consensus edges;
4. 999/999 matched nulls complete;
5. observed replication distance < matched-null mean;
6. p <= 0.05.

**FAIL** if the experiment is valid but inferential criteria fail.

**BLOCKED** if source independence/provenance, alignment, edge-count, or null-generation requirements fail.

Before execution: **NOT_RUN**.

## Interpretation boundary
PASS would replicate the structural topology across transcription sources and reduce the likelihood that H1-H4 are artifacts of one transcription/editorial representation. FAIL would materially weaken the topology program. BLOCKED on provenance is preferable to falsely labeling a reformatted copy as independent.

This experiment does not test the meaning of Lc/Lf and does not reopen the failed lexical-anchor hypothesis. Translation, language identification, semantic identity, plaintext and decipherment remain **NOT_RUN**.

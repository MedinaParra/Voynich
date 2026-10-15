# H97 — hierarchical folio-state generator preregistration

Status: **PASS (preregistration only)**

## Rationale
H96 confirmatory FAIL showed that all six frozen simple generators failed the 8/8 holdout intersection rule. The strongest partial family, token Markov-1, passed 4/8 endpoints, while real between-folio Jensen-Shannon divergence (JSD) was 0.043902 versus synthetic median 0.010955 and real within-folio half-vs-half JSD was 0.027766 versus synthetic median 0.020320. H97 prospectively tests the single hypothesis suggested by that frozen discrepancy: explicit folio-level heterogeneity improves out-of-sample reproduction without changing H96 endpoints.

This is a new confirmatory experiment. H96 remains FAIL and is not re-scored.

## Frozen source and partition
Reuse exactly H96 Takahashi source SHA-256 `32b11a0b584a75bbe9817c96a316a246f82d02d69996d789bc2cb908190bab77`, eligibility (200 folios), and deterministic 160-development / 40-holdout partition hash `50c82d6b48da54c3e2a1b70f14743f4c41bb2112ba74976de7185147d9d1766c`. Any mismatch => H97 = **BLOCKED**.

Holdout lexical content MUST NOT be used to fit state centroids, transition distributions, smoothing, or hyperparameters. Holdout folio IDs/token counts may be used only to preserve sample sizes.

## Frozen model
Fit a hierarchical token Markov-1 generator on development folios only.

For each development folio compute exactly four nonsemantic statistics: mean token length, token-length SD, character unigram entropy, adjacent-token repeat fraction. Standardize each coordinate using development mean/SD. If any SD is zero => **BLOCKED**.

Cluster development folios with deterministic k-means k=4, `random_state=97001`, `n_init=100`. No alternate k may be tested. Fit one token Markov-1 transition model per cluster with additive smoothing `1e-6` over the development vocabulary.

To preserve the lexical firewall, holdout folios are NOT assigned a state from their lexical statistics. Instead, for each synthetic replica draw a state independently for each holdout folio from the empirical development cluster proportions, seed-controlled below. Generate exactly the observed token count for each holdout folio. Initial token is drawn from that state's development unigram distribution.

This deliberately tests whether latent folio heterogeneity alone can reproduce H96's multiscale signature; it does not claim the states correspond to Currier, scribes, topics, keys, or sections.

## Frozen replicas/seeds
Generate exactly 999 synthetic holdout replicas. Base seed `20261010`; replica seed `97001 + replica_index`. No tuning after execution.

## Frozen endpoints
Reuse exactly the eight H96 holdout statistics, unchanged and in the same order:
1. mean token length;
2. token-length SD;
3. token type/token ratio;
4. character unigram Shannon entropy;
5. character bigram conditional entropy H(C_t|C_{t-1});
6. adjacent-token repeat fraction;
7. median within-folio first-half vs second-half character-unigram JSD;
8. median consecutive-folio character-unigram JSD.

## Primary criterion
For each endpoint compute the central 99% synthetic predictive interval (0.5th–99.5th percentile) over the 999 replicas. Endpoint PASS iff the real H96 holdout statistic lies inside that interval.

H97 = **PASS** iff all 8/8 endpoints PASS. H97 = **FAIL** if execution and controls succeed but fewer than 8/8 pass. No weighted score, endpoint dropping, alternate k, alternate state assignment, or secondary endpoint can rescue a FAIL.

## Mandatory controls
- Source SHA and partition hash exactly match H96: PASS required.
- Holdout-fit firewall: PASS required.
- Exact per-folio token-count preservation: PASS required.
- Empty-token fraction <=5% and all endpoint values finite: PASS required.
- Determinism: two executions of replica 0 with seed 97001 must produce identical corpus/statistics SHA-256: PASS required.
- Cluster occupancy: all four development clusters must contain >=10 folios; otherwise H97 = **BLOCKED**.

## Output/provenance
Artifact must record executing commit, source/partition hashes, runner SHA-256, development cluster centroids and occupancies, seeds, real endpoint vector, synthetic medians and 99% intervals, endpoint mask, controls, statistics hash, and final PASS/FAIL/BLOCKED. Do not emit inferred plaintext or translations.

## Interpretation ceiling
PASS would support only that explicit latent folio-level heterogeneity materially reproduces the frozen H96 structural signature under this exact generator. It would not identify the latent state with Currier A/B, scribes, topic, page order, cipher key, language, or semantics. FAIL would reject this exact k=4 hierarchical token-Markov implementation, not all hierarchical or state-dependent models.

Semantics = **NOT_RUN**. Language = **NOT_RUN**. Translation = **NOT_RUN**. Decipherment = **NOT_RUN**.

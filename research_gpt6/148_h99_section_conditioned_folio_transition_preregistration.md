# H99 — section-conditioned folio-transition generator preregistration

Status: **PASS (preregistration only)**

## Motivation
H97 = FAIL despite passing 5/8 frozen H96 endpoints. Its clearest remaining miss is between-folio discontinuity: real consecutive-folio character-unigram JSD = 0.0439020 versus H97 synthetic 99% interval [0.0118773, 0.0204252]. H97 drew latent states independently from global development proportions, so it deliberately discarded observed manuscript-level folio grouping and adjacency structure. H99 tests one new, falsifiable mechanism: **externally observable manuscript section plus development-only state-transition dynamics** can account for the missing between-folio heterogeneity without changing the eight H96 endpoints.

H96 and H97 remain FAIL and are not rescored. H98 remains BLOCKED and is not modified.

## Frozen source and holdout
Reuse exactly the H96/H97 Takahashi source SHA-256 `32b11a0b584a75bbe9817c96a316a246f82d02d69996d789bc2cb908190bab77`, the same 200 eligible folios, and deterministic 160-development / 40-holdout partition hash `50c82d6b48da54c3e2a1b70f14743f4c41bb2112ba74976de7185147d9d1766c`. Any mismatch => **BLOCKED**.

The lexical contents of all 40 holdout folios are forbidden during fitting. Holdout folio IDs and observed token counts may be used only for section assignment and sample-size preservation.

## External section covariate
Assign each eligible folio to the repository's already-frozen manuscript section metadata used before H99 (e.g. herbal, astronomical/astrological, biological, pharmaceutical, recipes where available). H99 MUST discover and reuse an existing pre-H99 section mapping/provenance; no section boundaries may be invented, moved, merged, split, or tuned after seeing H97/H99 outcomes.

If no exact pre-H99 frozen section mapping covering all 200 eligible folios can be resolved from repository provenance, H99 = **BLOCKED**. No lexical statistics may be used to infer missing section labels.

## Development-only latent states
For each development folio compute exactly H97's four nonsemantic statistics: mean token length, token-length SD, character unigram entropy, adjacent-token repeat fraction. Standardize using development mean/SD. Any zero SD => **BLOCKED**.

Fit deterministic k-means exactly as H97: k=4, `random_state=97001`, `n_init=100`. All four clusters must contain >=10 development folios or H99 = **BLOCKED**. Fit the same additive-smoothed (`1e-6`) token Markov-1 generator separately within each latent state.

## New mechanism: section-conditioned state transitions
Using development folios only and manuscript folio order, estimate for each external section a 4x4 latent-state transition-count matrix from consecutive development folios that are adjacent in manuscript order and share that section. Apply additive smoothing `alpha=1.0` to all 16 cells before row normalization.

For each section also estimate its development-only initial-state distribution with additive smoothing `alpha=1.0`.

For a synthetic holdout replica, traverse the 40 frozen holdout folios in manuscript order. At the first holdout folio of a section, draw a latent state from that section's development initial-state distribution. For a later holdout folio in the same section, draw its state from that section's transition row conditional on the previously generated holdout state. When the section changes, reset from the new section's initial-state distribution. Generate exactly the observed token count using that state's H97 token Markov-1 model.

No holdout lexical statistic, Currier class, scribe attribution, illustration label, candidate page reordering, or semantic information may enter fitting or state assignment.

## Frozen replicas and seeds
Generate exactly 999 synthetic holdout replicas. Replica seed = `99001 + replica_index`, replica_index 0..998. No tuning after execution.

## Frozen endpoints
Reuse unchanged, in the same order, H96/H97's eight holdout endpoints:
1. mean token length;
2. token-length SD;
3. token type/token ratio;
4. character unigram Shannon entropy;
5. character bigram conditional entropy H(C_t|C_{t-1});
6. adjacent-token repeat fraction;
7. median within-folio first-half vs second-half character-unigram JSD;
8. median consecutive-folio character-unigram JSD.

For each endpoint compute the central 99% synthetic predictive interval (0.5th–99.5th percentile). Endpoint PASS iff the real frozen H96 holdout statistic lies inside the interval.

## Confirmatory criterion
H99 = **PASS** iff all 8/8 endpoints PASS.
H99 = **FAIL** if all controls/execution pass but fewer than 8/8 endpoints pass.
No endpoint dropping, alternate section taxonomy, alternate k, alternate alpha, alternate ordering, or secondary metric can rescue FAIL.

## Mandatory controls
- source SHA and partition hash identity: PASS required;
- exact pre-H99 external section mapping provenance/hash and 200/200 coverage: PASS required, otherwise BLOCKED;
- holdout lexical firewall: PASS required;
- development cluster occupancy >=10 each: PASS required;
- transition matrices derived only from development adjacency: PASS required;
- exact per-holdout-folio token-count preservation: PASS required;
- all endpoint values finite and empty-token fraction <=5%: PASS required;
- determinism: duplicate generation of replica 0 with seed 99001 must have identical corpus/statistics SHA-256: PASS required.

## Diagnostic-only report
Report section occupancies, development transition matrices, synthetic state-switch rate, and the H97→H99 change in the predictive interval for endpoint 8. These are descriptive and cannot rescue the primary result.

## Interpretation ceiling
PASS would support only the narrow claim that pre-existing manuscript section structure plus development-derived latent-state transitions can reproduce the frozen eight-dimensional holdout signature. It would not establish that sections are semantic topics, that states are cipher keys/scribes/languages, that physical folio order is original, or that any text has been deciphered.

FAIL rejects this exact section-conditioned k=4 transition generator. BLOCKED means the required independent pre-H99 section covariate/provenance could not be established without post-hoc construction.

Semantics = **NOT_RUN**. Language = **NOT_RUN**. Translation = **NOT_RUN**. Decipherment = **NOT_RUN**.

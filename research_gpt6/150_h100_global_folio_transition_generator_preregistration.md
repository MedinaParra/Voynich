# H100 — global folio-transition generator preregistration

Status: **PASS (preregistration only)**

## Motivation
H97 = FAIL with 5/8 frozen H96 endpoints. Its largest identified miss is between-folio character-unigram discontinuity: real consecutive-folio JSD = 0.0439020 versus H97 synthetic central 99% interval [0.0118773, 0.0204252]. H97 sampled latent folio states independently from development state proportions. H99 attempted an externally section-conditioned transition model but is BLOCKED because no admissible pre-H99 200/200 section table was frozen in repository provenance.

H100 therefore tests the smallest non-post-hoc extension that requires no new metadata: whether **development-only first-order transitions among H97's four latent folio states, in frozen manuscript folio order**, reproduce all eight H96 holdout endpoints.

H96/H97 remain FAIL. H98/H99 remain BLOCKED and are not rescored.

## Frozen source and holdout
Reuse exactly H96/H97 Takahashi source SHA-256 `32b11a0b584a75bbe9817c96a316a246f82d02d69996d789bc2cb908190bab77`, the same 200 eligible folios, and deterministic 160-development / 40-holdout partition hash `50c82d6b48da54c3e2a1b70f14743f4c41bb2112ba74976de7185147d9d1766c`. Any mismatch => **BLOCKED**.

The lexical contents of all 40 holdout folios are forbidden during fitting. Holdout folio IDs/order and observed token counts may be used only for traversal and sample-size preservation.

## Development-only latent states
For each development folio compute exactly H97's four nonsemantic statistics: mean token length, token-length SD, character unigram entropy, adjacent-token repeat fraction. Standardize using development mean/SD. Any zero SD => **BLOCKED**.

Fit deterministic k-means exactly as H97: k=4, `random_state=97001`, `n_init=100`. All four clusters must contain >=10 development folios or H100 = **BLOCKED**. Fit the same additive-smoothed (`1e-6`) token Markov-1 generator separately within each latent state.

## New mechanism: one global state-transition matrix
Use only consecutive pairs in the frozen 200-folio manuscript order for which **both folios are in development**. Count transitions between their H97 latent states into one 4x4 matrix. Add `alpha=1.0` to all 16 cells, then row-normalize. Estimate one development-only initial-state distribution from the 160 development state occupancies with additive smoothing `alpha=1.0`.

For each synthetic holdout replica, traverse the 40 frozen holdout folios in their inherited manuscript order. Draw the first synthetic state from the development initial-state distribution. Draw each subsequent synthetic holdout state from the transition row conditional on the previously generated synthetic holdout state. Generate exactly that holdout folio's observed token count using the corresponding H97 state-specific token Markov-1 model.

No section taxonomy, Currier class, scribe attribution, illustration information, candidate page reordering, holdout lexical statistic, semantic information, or post-H97 metadata may enter fitting or state assignment.

## Frozen replicas and seeds
Generate exactly 999 synthetic holdout replicas. Replica seed = `100001 + replica_index`, replica_index 0..998. No tuning after execution.

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
H100 = **PASS** iff all 8/8 endpoints PASS.
H100 = **FAIL** if all mandatory controls/execution pass but fewer than 8/8 endpoints pass.
No endpoint dropping, alternate k, alternate alpha, alternate folio ordering, alternate transition definition, or secondary metric can rescue FAIL.

## Mandatory controls
- source SHA and partition hash identity: PASS required;
- exact 200-folio inherited order identity with H96/H97 provenance: PASS required;
- holdout lexical firewall during fitting: PASS required;
- development cluster occupancy >=10 each: PASS required;
- transition counts use only development→development adjacent pairs: PASS required;
- transition matrix finite and every normalized row sums to 1 within 1e-12: PASS required;
- exact per-holdout-folio token-count preservation: PASS required;
- all endpoint values finite and empty-token fraction <=5%: PASS required;
- determinism: duplicate generation of replica 0 with seed 100001 must have identical corpus/statistics SHA-256: PASS required.

## Diagnostic-only report
Report development transition counts/probabilities, number of eligible development→development adjacent transitions, development initial-state distribution, synthetic state-switch rate, and H97→H100 change in endpoint-8 predictive interval. Diagnostics cannot rescue the primary result.

## Interpretation ceiling
PASS would support only the narrow claim that development-derived first-order latent-state persistence can reproduce the frozen eight-dimensional holdout signature. It would not establish that latent states are cipher keys, languages, scribes, semantic topics, or original codicological units, and it would not validate any translation.

FAIL rejects this exact global k=4 first-order state-transition generator. BLOCKED means a mandatory frozen provenance/control could not be established without changing the preregistered test.

Semantics = **NOT_RUN**. Language = **NOT_RUN**. Translation = **NOT_RUN**. Decipherment = **NOT_RUN**.

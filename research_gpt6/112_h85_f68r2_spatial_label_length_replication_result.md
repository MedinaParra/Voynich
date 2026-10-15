# H85 — f68r2 spatial ↔ label-length replication result

Status: **FAIL_EXPLORATORY**.

This records execution of the prospectively frozen exploratory protocol in `111_h85_f68r2_spatial_label_length_replication_preregistration.md`. Infrastructure and all frozen source-integrity/sample gates passed. The primary f68r2 spatial–length association was essentially zero and did not satisfy the preregistered inferential threshold.

## Execution evidence

- Workflow: `H85 f68r2 spatial label-length replication`.
- Run: **37649576312** (run number 6).
- Job: **112889072971** (`h85-f68r2-spatial-label-length-replication`).
- Experimental branch head executed: `372227926b1551d2c90444da0006bf796fb0e5c6`.
- PR merge checkout: `f656dcd2c9c34a78c288c84bad05ba14385e92a4`.
- Artifact: `h85-f68r2-spatial-label-length-replication-results`, ID **11495827226**.
- Artifact ZIP SHA-256: `2660e3b8c7ab9f9764776fe70aa88905f7987d0aa9faff1936ccf6d33f19cdee`.

Infrastructure: **PASS**.

## Source integrity

All frozen source identities matched:

- RN-Top f68r2 CSV Git blob SHA-1: `b19bbeae51334ab124f05f081b5dc6e07ef2ae42`.
- seeton f68r1 star centres SHA-256: `e7cb7787118aa71f440fbf544da5b327a6afd8eba8b2989d6e5ca71d40629d04`.
- Yale f68r1 label source Git blob SHA-1: `12c4230fdefc8c566e9bdb3626fc6009c70a7533`.

## Primary f68r2 arm

- raw rows: **23**;
- valid rows after the frozen `^[a-z]{2,}$` rule: **20**;
- excluded rows: **3** (`o@167olchchy`, `odair.chol`, `ok[eeee]or`), with no repair;
- distinct token lengths: 6 (`5,6,7,8,9,10`);
- unordered object pairs: **190**;
- all sample/variance/unique-ID gates: **PASS**.

Primary statistic:

- observed Spearman `rho`: **0.0048978237538455415**;
- null mean: **0.00019993455349039395**;
- null SD: **0.08286458320182716**;
- null range: **[-0.22768264207524616, 0.4638250797098822]**;
- permutations: **19,999 / 19,999**;
- seed: `20261018`;
- upper-tail Monte Carlo `p`: **0.4445**.

Frozen decision gates:

- `rho > 0`: PASS descriptively;
- `p <= 0.05`: **FAIL**;
- permutations complete: PASS.

Primary status: **FAIL_EXPLORATORY**.

## Frozen f68r1 discovery diagnostic

This arm was preregistered as descriptive/diagnostic only and cannot rescue the H85 decision.

- objects: **29**;
- unordered pairs: **406**;
- observed `rho`: **0.1375294416482955**;
- null mean: **0.0001240726903814827**;
- null SD: **0.06325299815726447**;
- permutations: **19,999 / 19,999**;
- seed: `20261019`;
- upper-tail `p`: **0.0219**.

Diagnostic status: `EXECUTED_DISCOVERY_DIAGNOSTIC` only.

## Conservative interpretation

The descriptive length clue previously seen on f68r1 does **not** replicate on f68r2 as the preregistered global relationship between spatial separation and absolute label-length difference. The f68r2 effect is effectively zero (`rho≈0.0049`) and its permutation p-value is 0.4445.

Therefore token length should not be promoted as a general astronomical spatial code from this route. The positive f68r1 diagnostic remains discovery-only and is not confirmatory evidence.

This result does not test or establish star identity, celestial meaning, semantics, plaintext, language, translation, or decipherment.

Semantic identification: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

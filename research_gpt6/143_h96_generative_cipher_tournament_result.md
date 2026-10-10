# H96 — Generative Cipher Tournament result

Status: **FAIL**

## Execution evidence
- Executing commit: `2d5d0bf46fad156646271b9ca21d49b6942da7a8`
- GitHub Actions run: `38085891849`
- Workflow: `H96 generative cipher tournament`, run #1
- Actions conclusion: `success`
- Artifact: `11682928895` (`h96-generative-tournament`)
- Artifact size: 4057 bytes
- Artifact SHA-256: `2d665d8b29a827b941707d21f5fc559cfa4eb948d26da14d28d5fc15e9a6326b`
- Artifact created: 2026-10-10T21:58:58Z
- Branch: `experiment/h58-strict-l-vs-p`

## Confirmatory outcome
Infrastructure = **PASS**. Mandatory controls = **PASS**. Overall H96 = **FAIL**.

No preregistered family satisfied the frozen 8/8 holdout rule. Endpoint counts passing the frozen 99% predictive intervals:
- IID unigram: **2/8 — FAIL**
- first-order token Markov: **4/8 — FAIL**
- character Markov-2: **2/8 — FAIL**
- slot resampler: **1/8 — FAIL**
- homophonic-expansion surrogate: **1/8 — FAIL**
- folio-state Markov-2: **1/8 — FAIL**

The first-order token Markov family was the strongest partial fit but still failed half of the frozen endpoints and therefore cannot be promoted or rescued post hoc.

## Design/accounting evidence
- Eligible folios: **200**
- Frozen holdout: **40 folios**
- Synthetic replicas: **200 per family**
- Source SHA-256: `32b11a0b584a75bbe9817c96a316a246f82d02d69996d789bc2cb908190bab77`
- Partition hash: `50c82d6b48da54c3e2a1b70f14743f4c41bb2112ba74976de7185147d9d1766c`
- Partition firewall: **PASS**
- Per-folio token-count preservation: **PASS**
- Degeneracy control: **PASS**

## Notable frozen multiscale discrepancy
For the strongest partial family (first-order token Markov), the real median consecutive-folio Jensen-Shannon divergence was **0.04390**, versus approximately **0.01096** for the synthetic family. The real median first-half/second-half within-folio divergence was **0.02777**, versus approximately **0.02032** for that synthetic family. These values are descriptive consequences of the frozen H96 endpoints and do not create a new confirmatory hypothesis.

## Conservative interpretation
H96 falsifies only the six exact preregistered implementations as simultaneous explanations of the frozen eight-statistic holdout signature. It does **not** falsify every possible natural-language, cipher, homophonic, Markov, slot, or state-dependent mechanism.

The partial pattern is consistent with the tested simple generators being too homogeneous across folios. This is hypothesis-generating only. A future experiment may preregister a hierarchical generator with explicit local and folio/section state, but H96 parameters/endpoints must not be altered retrospectively.

H91 object↔label geometric reproducibility remains separate evidence. H92–H95 remain prospective FAIL results for the tested simple visual↔lexical anchor mappings; H96 does not rescue them.

Semantics = **NOT_RUN**. Language = **NOT_RUN**. Translation = **NOT_RUN**. Decipherment = **NOT_RUN**.

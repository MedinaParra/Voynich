# Holistic topology H4 preregistration: leave-one-quire-out generalization

Status: **NOT_RUN**.

H1, H2 and H3 passed. H4 is an adversarial generalization test designed to determine whether the latent-topology result survives when entire codicological groups are held out rather than evaluating the same folio universe used for discovery.

## Hypothesis
A topology rule learned from all but one eligible quire should predict held-out folio similarity in an independent representation better than a matched null when applied to the omitted quire without tuning.

## Frozen data
Use the same frozen EVA corpus blob and running-text eligibility/parser rules as H1-H3. Labels and illustration semantics remain excluded.

## Folds
Use leave-one-quire-out (LOQO). A held-out quire is evaluable only if it contains at least 8 eligible folios and at least 8 folios have a valid candidate under the frozen confound policy. Report every excluded quire and reason.

## Discovery rule
For each fold, Families A and B are constructed exactly as H1/H2. Feature definitions are frozen. Any normalization/statistical quantities that require estimation must be derived from non-held-out folios only.

Within the held-out quire, construct A and B nearest-neighbor selections using the frozen feature/distance rule without looking at Family C or physical adjacency. Form the undirected A∩B consensus edge set for that held-out quire.

A fold with fewer than 3 consensus edges is unsupported and must be reported; it contributes no inferential statistic.

## Independent validation
Use Family C exactly as frozen in H3. Compute mean Family C cosine distance over the held-out consensus edges.

## Null
Exactly 999 deterministic permutations per aggregate experiment, seed `20261006`.

Within each evaluable held-out quire, replace each consensus edge with a random edge drawn from the same held-out quire and compatible frozen confound strata where possible, preserving the observed edge count. Pool validation distances across supported held-out quires to obtain one aggregate null mean per permutation.

No cross-quire replacement is permitted.

## Primary statistic
Aggregate mean Family C distance over all consensus edges from supported held-out quires.

Report additionally:
- number of evaluable quires;
- number of supported quires;
- held-out folios and consensus edges per quire;
- per-quire observed Family C mean distance;
- total pooled consensus edges.

## Decision
**PASS** iff:
1. at least 3 distinct held-out quires are supported;
2. pooled consensus graph contains at least 30 edges;
3. 999/999 null permutations complete;
4. observed aggregate Family C distance is below null expectation;
5. Monte Carlo p <= 0.05.

**FAIL** if execution is valid with >=3 supported quires and >=30 pooled edges but the inferential criterion is missed.

**BLOCKED** if fewer than 3 quires or fewer than 30 pooled consensus edges are supported, or matched null generation cannot complete.

Before execution: **NOT_RUN**.

## Anti-leakage and interpretation
No held-out Family C value, physical adjacency, illustration meaning, proposed language, or translation may influence A/B edge selection. No thresholds or features may be changed after observing H4 results.

PASS would show that the three-view topology phenomenon is not dependent solely on pooling the complete manuscript and survives codicological group holdout. It would justify subsequent external-transcription replication and only then topology-conditioned semantic experiments.

PASS would still not establish original folio order, language, plaintext, cipher, semantics, author, or translation.

Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

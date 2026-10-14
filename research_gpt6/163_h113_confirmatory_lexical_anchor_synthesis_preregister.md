# H113 — Confirmatory lexical-anchor evidence synthesis

## Purpose

H113 is a synthesis/audit experiment, not a new pattern search. It asks whether any previously frozen visual/label lexical anchor survives the full existing control chain strongly enough to justify a later semantic test.

## Frozen inputs

Only already executed hypotheses/results H90, H92, H95, H98, H105, H106, H107, H108, H109, H110, H111, H112 and the frozen `label-object-familywise` result may contribute. No new feature, threshold, folio subset, spelling normalization, visual class, or semantic interpretation may be introduced after this preregistration.

## Evidence ladder

For each candidate anchor record, where applicable:

1. original lexical/visual signal;
2. length or morphology control;
3. spatial/geometry control;
4. paragraph/folio/quire confound control;
5. independent-transcription or independent-source control;
6. held-out generalization;
7. family-wise/permutation control.

A missing required stage is `NOT_RUN`, not PASS. Infrastructure inability to retrieve an existing frozen result is `BLOCKED`.

## Decision rule

A candidate is **PASS** only if every applicable required confirmatory stage is PASS and there is no later preregistered FAIL that directly falsifies its claimed generalization. A candidate with any direct confirmatory FAIL is **FAIL**. A candidate whose required evidence was never executed is **NOT_RUN**. H113 overall is PASS only if at least one candidate is PASS under this rule; otherwise FAIL if all evaluable candidates fail, NOT_RUN if none is evaluable, or BLOCKED if evidence cannot be retrieved for infrastructure reasons.

## Prohibitions

- No translation, language identification, semantic gloss, or decipherment.
- No tuning of thresholds or selecting favorable subsets.
- No rerunning failed hypotheses with altered parameters.
- No treating GitHub Actions `conclusion=success` as scientific PASS; scientific status must come from the frozen result evidence.
- H112 remains a source-admissibility FAIL with lexical replication NOT_RUN.

## Outputs

A machine-readable evidence matrix plus a short result note containing exact source experiment IDs/statuses and the H113 classification. Semantics, language identification, translation and decipherment remain NOT_RUN regardless of H113 outcome.
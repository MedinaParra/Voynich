# H72 — Local exact label-to-paragraph recurrence result

Status: **FAIL**.

This records execution of the preregistered protocol in `86_h72_local_exact_label_recurrence_preregistration.md`. Both frozen transcription tests passed all validity gates and completed all permutations; the replicated scientific criterion was not met.

## Execution evidence

- Workflow: `H72 local exact label recurrence`.
- Run: `37616181098` (run number 1).
- Job: `112774942947` (`h72-local-exact-label-recurrence`).
- Experimental branch head executed: `5c6152dcd937363056f2991746510f03d9c67c8f` (PR merge checkout `18188abcdaa843e9e912f3d76a73d5094d006794`).
- Artifact: `h72-local-exact-label-recurrence-results`, ID `11480800165`.
- Artifact SHA256: `598336c1d068d56041ae54f3e74e6ea7d68c6ea3fe9b3d2f4f5cdbf0960f2247`.
- Seed: `20261007`.
- Permutations: **9999/9999 per source**.
- Bonferroni alpha per source: **0.025**.

## Zandbergen–Landini

- frozen blob verified: `2a4533ab9bdfa85db9bad602d590978953055df1`;
- certain unique `(folio,label_token)` rows: **512**;
- rows on folios with P text: **474**;
- exchangeable rows under exact `(Q,Currier,hand,length,P-opportunity-quartile)`: **304**;
- exchangeable strata: **31**;
- represented folios: **28**;
- observed exact same-folio P hits: **27**;
- observed local hit rate: **0.08881578947368421**;
- null mean hit rate: **0.08179008690342915**;
- observed-minus-null lift: **0.00702570257025506**;
- Monte Carlo p: **0.2713**;
- source status: **FAIL**.

## Takahashi IT2a

- frozen blob verified: `7f491b574b65e5fba6b553e57372c3fa50e10fec`;
- certain unique `(folio,label_token)` rows: **410**;
- rows on folios with P text: **371**;
- exchangeable rows: **296**;
- exchangeable strata: **33**;
- represented folios: **29**;
- observed exact same-folio P hits: **29**;
- observed local hit rate: **0.09797297297297297**;
- null mean hit rate: **0.08092701162008221**;
- observed-minus-null lift: **0.017045961352890757**;
- Monte Carlo p: **0.0311**;
- source status: **FAIL** under the preregistered Bonferroni threshold `p <= 0.025`.

The Takahashi result is not promoted as a marginal success. The threshold was fixed before execution, and the ZL source independently does not approach significance.

## Decision

H72 required both frozen transcriptions to show positive local recurrence lift with Monte Carlo `p <= 0.025`. Both tests were valid, but neither meets the replicated decision rule.

H72: **FAIL**.

## Conservative interpretation

The robust L* label-versus-P* paragraph token-form distinction established in H60-H66 does **not** extend to a preregistered claim that exact label forms preferentially recur in paragraph text on the same folio after preserving the label-token multiset, quire, Currier class, hand, token length, paragraph opportunity, and global paragraph frequency of each token through constrained permutation.

This is consistent with the external qualitative observation that many label words also occur in running text but are rarely found in the immediate vicinity of the corresponding label. The present experiment makes that locality question quantitative under frozen controls.

The result does not imply that labels lack meaning, nor does it test approximate morphological recurrence, broader manuscript regions, or translated semantics. It closes this specific exact same-folio recurrence route unless genuinely new independent evidence or a prospectively different hypothesis is introduced.

Historical visual-subtype routes remain **FAIL/BLOCKED** as already recorded.

Semantic identification: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

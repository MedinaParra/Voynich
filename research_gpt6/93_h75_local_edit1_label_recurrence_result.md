# H75 — Local edit-distance-1 label-to-paragraph recurrence result

Status: **FAIL**.

This records the completed execution of the preregistered protocol in `92_h75_local_edit1_label_recurrence_preregistration.md`. No semantic, language, plaintext, cipher, translation, or decipherment claim is made.

## Execution evidence

- Branch: `experiment/h58-strict-l-vs-p`.
- Workflow: `H75 local edit-distance-1 label recurrence`.
- Run: `37635076965`, conclusion `success`.
- Job: `112839041144` (`h75-local-edit1-label-recurrence`), conclusion `success`.
- Experimental head executed: `c6e237c94d648aa0dd16838460aa62e20dc7d06d` (PR merge checkout `f307938f38a664f6a07abc64706541b58a2cfcea`).
- Artifact: `h75-local-edit1-label-recurrence-results`, ID `11489455257`.
- Artifact SHA256: `8d307251337b030f95e2657024d8932330a1c1a5bcb7cebea3908869ad44db50`.
- Seed: `20261007`.
- Distance rule: ordinary character-level Levenshtein distance exactly 1; exact matches excluded; label and candidate paragraph tokens length >=4.
- Permutations: **9,999/9,999 per source**.
- Bonferroni alpha: **0.025 per source**.

## Zandbergen–Landini

- frozen Git blob: `2a4533ab9bdfa85db9bad602d590978953055df1` — matched expected hash;
- unique eligible label rows length >=4 before paragraph/exchangeability filtering: **477**;
- rows with paragraph text: **439**;
- exchangeable rows: **304**;
- represented folios: **29**;
- exchangeable strata: **34**;
- observed distance-1 local hits: **81**;
- observed hit rate: **0.26644736842105265**;
- null mean hit rate: **0.2571744016506893**;
- observed-minus-null lift: **+0.009272966770363378**;
- Monte Carlo p: **0.272**;
- status: **FAIL**.

## Takahashi IT2a

- frozen Git blob: `7f491b574b65e5fba6b553e57372c3fa50e10fec` — matched expected hash;
- unique eligible label rows length >=4 before paragraph/exchangeability filtering: **394**;
- rows with paragraph text: **355**;
- exchangeable rows: **285**;
- represented folios: **29**;
- exchangeable strata: **31**;
- observed distance-1 local hits: **81**;
- observed hit rate: **0.28421052631578947**;
- null mean hit rate: **0.2779692004288203**;
- observed-minus-null lift: **+0.0062413258869691846**;
- Monte Carlo p: **0.3668**;
- status: **FAIL**.

## Frozen decision

Both source tests satisfied every preregistered source-integrity, sample, exchangeability, and execution gate. Both observed rates were slightly above their null means, but neither p-value approached the frozen corrected threshold `0.025`. Therefore the conjunction required for H75 is not met.

H75: **FAIL**.

## Conservative interpretation

The H72 exact-recurrence FAIL is not rescued by the single prospectively fixed fuzzy relation tested here. Under the same documentary, token-length, opportunity, and token-multiset-preserving controls, labels do not show statistically supported enrichment for local paragraph forms at ordinary Levenshtein distance exactly 1 in either frozen transcription.

The small positive descriptive lifts in both sources are compatible with the controlled null and must not be promoted as lexical anchors. This result closes this specific one-edit local-neighbour route; it does not demonstrate that the manuscript lacks morphology or semantics.

H72 exact local recurrence: **FAIL**.
H75 one-edit local recurrence: **FAIL**.
Semantic identification: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

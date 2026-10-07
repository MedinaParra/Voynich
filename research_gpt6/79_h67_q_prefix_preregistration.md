# H67 — q-prefix counterpart enrichment in labels

Status: **NOT_RUN**

## Question
Are consensus label forms beginning with EVA `o` unusually likely to have a strict paragraph-text counterpart formed by adding a single initial EVA `q` (`t -> q+t`)?

This tests a concrete contextual-morphology hypothesis suggested by H64/H66: labels are enriched for `o/a` and strongly depleted for initial `q`.

## Frozen sources
- Source A: `cesarjz/Voynich` commit `47e6a77dc9d5cd570c375f4aff710fa4a0567278`, `corpus/voynich_eva.txt`, Git blob `2a4533ab9bdfa85db9bad602d590978953055df1`.
- Source B: `oklo/voynich_gpt` commit `2d7c61c387ad6962de730caf73c48612bc8f6957`, `IT2a-n.txt`, Git blob `7f491b574b65e5fba6b553e57372c3fa50e10fec`.

## Consensus label types
Recreate the H66 exact-agreement label locus set: identical full IVTFF locus, identical cleaned single-token L* reading, identical Currier and hand metadata between sources, and strict P controls available in both.

Collapse the retained events to unique `(token, Currier, hand)` label types.
Confirmatory types must begin with `o` and must not begin with `q`.

## Strict P vocabulary
For each source separately, construct token counts from generic `P*` loci only, grouped by `(Currier, hand)`.

For a label type `t`, define its q-counterpart indicator as 1 iff exact token `q+t` occurs at least once in strict P text in the same `(Currier, hand)` group.

## Matched control types
For each eligible label type independently in each source, select one strict-P token type `u` that:
- begins with `o`;
- has the same token length;
- belongs to the same Currier/hand group;
- is not itself an aligned label type;
- falls in the same strict-P frequency bin as the label token's strict-P frequency.

Frequency bins: `0`, `1`, `2`, `3-4`, `5-8`, `9+` occurrences. Selection is deterministic with seed `20261007` after sorting candidates lexicographically.

For each matched control `u`, define q-counterpart indicator as 1 iff `q+u` occurs in strict P in the same group.

## Sample threshold
Each source must yield at least **30 matched type pairs**. Otherwise H67 is **BLOCKED** for that source and the threshold must not be lowered.

## Statistic and null
Observed statistic per source:
`mean(q_counterpart_label) - mean(q_counterpart_control)`.

Run exactly **999** within-pair label/control identity swaps, seed `20261007`. One-sided Monte Carlo p-value tests whether labels have greater q-counterpart enrichment than matched P controls.

## PASS criterion
H67 is **PASS** iff in both frozen sources:
- >=30 matched type pairs;
- 999/999 swaps complete;
- observed enrichment > 0;
- Monte Carlo p <= 0.05.

Otherwise a valid execution is **FAIL**. Blob/sample failure is **BLOCKED**.

## Interpretation boundary
PASS would support a specific formal relation between some label forms and paragraph forms: omission of an initial `q` is unusually associated with label usage for `o...` forms. It would not establish the linguistic meaning of `q`, morpheme identity, phonetic value, semantics, language, plaintext, cipher mechanism, translation, or decipherment.

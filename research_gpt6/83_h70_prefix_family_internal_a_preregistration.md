# H70 — Prefix-family conditioned internal `a` enrichment

Status: **NOT_RUN**

Preregistration frozen before any H70 result inspection. This metadata-only freeze does not alter the hypothesis, sample rules, statistic, thresholds, or PASS criterion below.

## Question
Does the H68 internal EVA `a` enrichment survive when labels are compared only with strict paragraph-text (`P*`) controls from the **same two-character initial family**?

This is a mechanistic follow-up to H68/H69. H68 showed replicated internal `a` enrichment after removing the first two and final characters. H69 showed that additionally forcing an exact final-character match reduced the sample to 54 pairs and the effect no longer reached significance. H70 therefore isolates the initial-family question without forcing the final character.

## Frozen sources
- Source A: `cesarjz/Voynich` commit `47e6a77dc9d5cd570c375f4aff710fa4a0567278`, `corpus/voynich_eva.txt`, Git blob `2a4533ab9bdfa85db9bad602d590978953055df1`.
- Source B: `oklo/voynich_gpt` commit `2d7c61c387ad6962de730caf73c48612bc8f6957`, `IT2a-n.txt`, Git blob `7f491b574b65e5fba6b553e57372c3fa50e10fec`.

Seed: `20261007`.

## Aligned label sample
Recreate the H66 exact-agreement label locus set:
- full IVTFF locus present in both sources;
- single certain `L*` token in both;
- identical cleaned EVA token;
- identical Currier and hand metadata;
- token length >= 5.

For each aligned label event, define its initial family as the exact first two EVA characters.

## Strict-P controls
For each source independently, an eligible control must:
- come only from generic `P*` loci;
- be on the same folio;
- have the same Currier and hand metadata;
- have exactly the same token length;
- have exactly the same first two EVA characters as the label;
- have length >= 5.

An aligned label event enters H70 only if at least one eligible control exists in **both** frozen sources. Within each source, select one control deterministically after lexicographic sorting, using seed `20261007` for source A and `20261008` for source B.

## Eligible prefix families
After the common aligned/control-eligible event set is frozen, retain every initial two-character family represented by at least **15 paired events**. Family selection uses counts only, never the `a` outcome.

The confirmatory test is executable only if:
- at least **3** prefix families are eligible;
- at least **80** paired events remain across eligible families;
- at least **8** folios are represented in each source.

Otherwise H70 is **BLOCKED** and thresholds must not be lowered.

## Outcome
For token `t`, remove the first two and final EVA characters:

`body(t) = t[2:-1]`

The sole confirmatory feature is:

`internal_a(t) = count('a' in body(t)) / len(body(t))`

For each pair compute:

`d_i = internal_a(label_i) - internal_a(control_i)`.

No `o`, `q`, token-length, semantic, section, illustration, or vocabulary-identity feature is tested confirmatorily.

## Primary statistic
Within each eligible prefix family, compute the mean paired difference. The primary cross-family statistic is the **equal-family-weighted mean** of those family means, so a very large family cannot dominate the result.

Also report the ordinary pooled event-weighted mean as descriptive context.

## Null
Run exactly **999** within-pair label/control identity swaps separately in each source. Each swap multiplies the pair difference by +1 or -1 while keeping the pair and prefix family fixed.

For every permutation recompute the equal-family-weighted primary statistic. Use a one-sided Monte Carlo p-value for enrichment (`statistic > 0`).

Family-specific mean differences are reported descriptively. In addition, compute two-sided family-specific t statistics and a max-stat familywise permutation p-value across eligible families; these familywise values are secondary and do not define PASS by themselves.

## PASS criterion
H70 is **PASS** iff in both frozen sources:
- sample thresholds are met;
- 999/999 permutations complete;
- equal-family-weighted mean difference > 0;
- one-sided Monte Carlo p <= 0.05;
- at least **2 eligible prefix families** have a positive observed mean difference in both sources.

Otherwise a valid execution is **FAIL**. Blob/sample failure is **BLOCKED**.

## Interpretation boundary
PASS would support a replicated label-vs-paragraph internal `a` shift that survives conditioning on broad initial two-character morphological family. It would not establish a morpheme, phonetic value, semantics, a language, plaintext, cipher mechanism, translation, or decipherment.

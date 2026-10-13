# H69 — Boundary-conditioned internal EVA a enrichment

Status: **NOT_RUN**

## Question
Does the H68 internal EVA `a` enrichment persist when each label is compared only with strict paragraph tokens that have the **same first two EVA characters, same final EVA character, same original length, same folio, Currier and hand**?

This isolates the residual body from the strongest token-boundary differences found in H64/H66.

## Frozen sources
- Source A: `cesarjz/Voynich` commit `47e6a77dc9d5cd570c375f4aff710fa4a0567278`, blob `2a4533ab9bdfa85db9bad602d590978953055df1`.
- Source B: `oklo/voynich_gpt` commit `2d7c61c387ad6962de730caf73c48612bc8f6957`, blob `7f491b574b65e5fba6b553e57372c3fa50e10fec`.

## Consensus events
Recreate the H66 exact-agreement label locus set:
- exact same full IVTFF label locus in both sources;
- exact same cleaned label token;
- exact same Currier/hand metadata;
- original token length >=5.

## Boundary-conditioned strict-P controls
For each consensus label event and each source independently, eligible controls must be strict generic `P*` tokens from the same:
- folio;
- Currier;
- hand;
- exact original token length;
- exact first two EVA characters;
- exact final EVA character.

Control selection is deterministic after lexicographic sorting, using seed `20261007` independently in each source. A consensus label event is retained for the confirmatory test only if at least one such control exists in **both** sources, so both analyses use the same physical label loci.

Minimum valid common sample: **50 pairs across at least 8 folios**. Otherwise H69 is **BLOCKED** and the threshold must not be lowered.

## Confirmatory feature
Residual body = exactly `token[2:-1]`.

Feature = fraction of EVA `a` in the residual body.

Pair difference = residual-a(label) - residual-a(matched strict-P control).

## Null
For each source independently, run exactly **999** within-pair label/control identity swaps, seed `20261007` for A and `20261008` for B.

One-sided Monte Carlo p-value tests positive label enrichment:
`(1 + count(null_mean >= observed_mean)) / 1000`.

## PASS criterion
H69 is **PASS** iff in both sources:
1. common retained sample >=50 pairs and >=8 folios;
2. 999/999 swaps complete;
3. observed mean difference >0;
4. one-sided Monte Carlo p <=0.05.

Otherwise a valid execution is **FAIL**. Source/blob/sample failure is **BLOCKED**.

## Interpretation boundary
PASS would show that the internal EVA `a` enrichment is not explained by the label/control differences in the first two or final characters. It would support a genuine internal compositional constraint associated with label context. It would not establish semantic, phonetic, linguistic, plaintext, cipher, translation or decipherment claims.

# H73 — Q13 reported-singulion exact permutation falsification

Status before execution: **NOT_RUN**.

## Scope and provenance boundary

This experiment tests the **Q13 sequence attributed to Layfield–Fagin Davis by a reproducible secondary report**, not an exact replication of the primary Digital Medievalist article. The primary OpenEdition full text is currently inaccessible to the automated execution because of its anti-bot gate, and the exact Q20 sequence has not been recovered from a primary accessible source. Therefore:

- Q13 only is admitted here;
- Q20 remains **NOT_RUN/BLOCKED_FOR_EXACT_SEQUENCE**;
- a H73 PASS cannot be called a primary-paper replication.

The frozen secondary report gives the attributed Q13 bifolio sequence as:

1. `77|82`
2. `78|81`
3. `75|84`
4. `76|83`
5. `79|80`

The same report gives an independent Held–Karp reconstruction with the same three central units but swapped extremes, making the reported sequence suitable for adversarial testing rather than unquestioned acceptance.

## Frozen physical units

Q13 is frozen as the five physical bifolia:

- `75|84`
- `76|83`
- `77|82`
- `78|81`
- `79|80`

The current physical nesting order, outer-to-inner, is frozen as:

`75|84 -> 76|83 -> 77|82 -> 78|81 -> 79|80`.

The reported Layfield–Davis sequence is frozen as:

`77|82 -> 78|81 -> 75|84 -> 76|83 -> 79|80`.

No sequence may be changed after execution.

## Frozen transcriptions

Run the test independently in the two already admitted frozen sources:

### Zandbergen–Landini
- `cesarjz/Voynich`
- commit `47e6a77dc9d5cd570c375f4aff710fa4a0567278`
- `corpus/voynich_eva.txt`
- Git blob SHA-1 `2a4533ab9bdfa85db9bad602d590978953055df1`

### Takahashi IT2a
- `oklo/voynich_gpt`
- commit `2d7c61c387ad6962de730caf73c48612bc8f6957`
- `IT2a-n.txt`
- Git blob SHA-1 `7f491b574b65e5fba6b553e57372c3fa50e10fec`

Any blob mismatch is **BLOCKED**.

## Frozen text selection

For each transcription independently:

1. retain only `P*` paragraph loci from folios 75 through 84;
2. remove IVTFF markup with the same conservative cleaning family already used in H60–H72;
3. unresolved `?` material is split away and cannot create a token across the uncertainty;
4. retain lowercase alphabetic tokens of length >=2;
5. aggregate all P tokens from both folios belonging to each physical bifolio.

Labels and other locus types are excluded so the strong L-vs-P morphology discovered in H60–H66 cannot itself drive the ordering score.

## Frozen validity gates

For each transcription:

- all ten folio numbers 75–84 must be represented by at least one P token;
- each of the five bifolium aggregates must contain >=50 P tokens;
- at least 100 distinct token types must occur across Q13;
- all 120 permutations of the five bifolia must be scored.

Failure of any gate is **BLOCKED**.

## Frozen representation

Within each transcription independently:

1. build one token-count document per bifolio from the five frozen Q13 units;
2. vocabulary = all observed cleaned P-token types in Q13;
3. term frequency = raw count;
4. inverse-document frequency for term `t` = `log((1 + 5) / (1 + df_t)) + 1`;
5. bifolio vector = TF * IDF;
6. L2-normalize each vector;
7. adjacency similarity = cosine similarity between normalized bifolio vectors.

No LSA dimensionality, embedding model, semantic dictionary, sequence optimization, or hand-tuned feature weighting is used.

## Frozen sequence score

For an ordered sequence of five bifolia:

`score = mean(cosine(unit_i, unit_{i+1}))` for its four adjacent transitions.

Compute exactly:

- reported sequence score;
- current nested outer-to-inner sequence score;
- score for all `5! = 120` permutations.

Because cosine adjacency is symmetric, reverse sequences can tie; ties remain in the null and are not broken.

Exact one-sided permutation p:

`p = count(permutation_score >= reported_score) / 120`.

Also report exact rank, percentile, null mean, maximum score, all tied maximizers, and `reported_score - current_score`.

## Decision rule

A transcription-level test is **PASS** only if:

1. every validity gate passes;
2. reported sequence score is strictly greater than current nested score; and
3. exact permutation `p <= 0.05`.

H73 = **PASS** only if **both** ZL and Takahashi independently PASS.

H73 = **FAIL** if both source tests are valid but either fails either scientific criterion.

H73 = **BLOCKED** if either source cannot satisfy the frozen source/sample/execution gates.

Before execution H73 is **NOT_RUN**.

## Interpretation boundary

A PASS would support only the narrow statement:

> the secondary-reported Q13 sequence has unusually high P-text lexical adjacency under this frozen TF-IDF continuity metric relative to all physical-bifolio permutations, and beats the current outer-to-inner nesting order in both admitted transcriptions.

It would not prove that this is the historically correct reading order, that lexical similarity equals semantic continuity, or that the secondary report reproduces the exact primary-paper table. It would still require the deliberately shuffled-known-text calibration highlighted in the 2026 methodological critique before stronger sequence interpretation.

A FAIL would directly weaken this specific reported Q13 order under a simple preregistered lexical-continuity metric; it would not refute the broader physical singulion hypothesis.

Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

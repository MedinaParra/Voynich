# Holistic outside-the-box pivot: recover document topology before semantics

Status: **NOT_RUN**.

Frozen after the Lc-vs-Lf exact-length matched control returned FAIL. This pivot deliberately stops treating individual label classes as candidate translations.

## Core hypothesis

The manuscript may be easier to attack as a structured information system than as a flat ciphertext. If the surviving folio/quire order is not the generating order, or if text production changes continuously through the manuscript, page adjacency and document topology are latent variables that can confound lexical, topic, Currier, hand, and label analyses.

The next question is therefore not “what does token X mean?” but:

> Can manuscript-internal text statistics recover a nontrivial local topology/order that generalizes across independent feature families and is not explained by section, Currier class, hand, or token length alone?

A positive result would define a better coordinate system for later decipherment tests. A negative result would falsify this route without semantic guessing.

## Why this pivot

The Lc/Lf pilot was reproducible but collapsed under length controls. We therefore treat labels as one view among several, not privileged semantic anchors.

The holistic model separates four layers:
1. **physical/document layer** — folio, quire, recto/verso, adjacency/order;
2. **production layer** — Currier state, handwriting/orthographic state, section;
3. **text-generative layer** — glyph n-grams, token morphology, line-position effects, repetition/novelty;
4. **semantic/illustration layer** — labels and image-derived classes, held out from topology discovery whenever possible.

## Frozen experiment H1: topology-from-text

Use the same frozen EVA corpus source where available. Build one vector per eligible folio from running text only; labels are excluded from discovery.

Two independent feature families must be evaluated separately:

### Family A — character/glyph structure
- normalized EVA character unigram, bigram and trigram frequencies;
- line-initial and line-final character distributions as separate blocks;
- no semantic labels.

### Family B — token morphology
- token-length histogram;
- prefix/suffix distributions of lengths 1–3;
- vocabulary novelty/repetition rates;
- no character n-gram features shared with Family A beyond what is implicit in prefixes/suffixes.

For each family, standardize features using training folds only and compute pairwise cosine distance.

## Evaluation

Primary target is local physical adjacency within the manuscript/quire metadata available in the frozen corpus.

For every eligible folio, rank all candidate folios from the same evaluation universe by feature distance. Measure:
- reciprocal rank of the true immediate physical neighbor(s);
- Recall@1 and Recall@3 for at least one true immediate neighbor;
- mean neighbor distance versus non-neighbor distance.

Evaluate separately for Family A and Family B.

### Confound-controlled evaluation

Repeat after restricting/permuting candidates within matched metadata strata wherever sample size permits:
- same Currier class;
- same hand;
- same section/illustration class if encoded;
- token-count bin;

The implementation must report strata that cannot support evaluation rather than pooling them silently.

## Null

Exactly 999 deterministic permutations, seed `20261006`.

Permute folio identities/order within the same available confound strata while keeping each folio feature vector intact. The null therefore preserves document-level text statistics and metadata composition but destroys local topology.

## Cross-view criterion

This is deliberately stricter than a single-model discovery.

**PASS** only if:
1. Family A beats its matched null at Monte Carlo p <= 0.05 on the preregistered primary adjacency statistic;
2. Family B independently beats its matched null at p <= 0.05;
3. both effects point in the same direction (true neighbors closer / ranked better);
4. a confound-controlled evaluation remains executable rather than collapsing to unusable strata.

**FAIL** if the experiment is valid but either independent feature family fails the inferential criterion.

**BLOCKED** if corpus metadata cannot define physical adjacency or no confound-controlled evaluation has sufficient strata.

Before execution: **NOT_RUN**.

## Critical anti-leakage rule

No proposed reordering may be selected by looking at illustration meaning, modern-language hypotheses, known proposed decipherments, or the result of the other feature family. Each family is evaluated independently against the frozen physical-order target and matched null.

## Interpretation boundary

PASS would mean that local manuscript topology leaves a reproducible signal in two independent textual views after available confound controls. It would justify a second preregistered phase testing whether an alternative/reconstructed ordering improves continuity more than the physical order.

PASS would **not** identify a language, plaintext, cipher, semantic label, author, or translation.

FAIL would tell us that topology-first reconstruction is not supported by this operationalization and we should pivot to a different generative constraint rather than tuning until significance.

Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

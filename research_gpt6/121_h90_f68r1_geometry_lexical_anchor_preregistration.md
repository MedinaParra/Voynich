# H90 — f68r1 geometry→lexical-anchor preregistration

Status: **NOT_RUN**.

## Purpose

H79 established a frozen 29-object↔29-label-position mapping on f68r1 without reading label strings. H90 is the first lexical opening of that frozen mapping. It asks a narrow falsifiable question: **does manuscript-internal object geometry predict label morphology better than chance under held-out evaluation?** It does not test proposed star names, languages, plaintext, or translations.

This protocol is frozen before execution. H79 pairings may not be changed.

## Frozen inputs

1. H79 star centres: `seeton/Voynich-public` revision `8920f2e506fce4c2c5a1245fb21a312f25655f1b`, `analysis/annotations/f68r_star_centres.csv`, f68r1 `star_id=1..29`, expected SHA256 `e7cb7787118aa71f440fbf544da5b327a6afd8eba8b2989d6e5ca71d40629d04`.
2. Yale label boxes/tokens: `YaleDHLab/voynich` revision `c4d36f4595292c92da8c7428e30cb23b700a019b`, `utils/voynichese/coords/f68r1.json`, expected Git blob SHA-1 `12c4230fdefc8c566e9bdb3626fc6009c70a7533`.
3. H79 primary mapping exactly as recorded in `101_h79_star_label_geometric_pairing_result.md`: star 1..29 → Yale occurrences `[50,38,37,43,31,36,48,53,54,41,32,55,56,46,34,39,59,51,52,40,44,58,57,35,45,47,49,42,33]`.

Any source-integrity or cardinality mismatch => **BLOCKED**.

## Geometry features fixed before reading token strings

Using only the 29 frozen star centres, normalize x and y to [0,1] within the 29-star set. Let `(cx,cy)` be the arithmetic centroid. For each star compute exactly four continuous features:

- normalized x;
- normalized y;
- radial distance from `(cx,cy)`, divided by the maximum radial distance;
- circular angle represented as `sin(theta)` and `cos(theta)`.

Thus the predictor vector is `[x,y,r,sin(theta),cos(theta)]`. No visual inspection, ray count, colour, star size, or H89/H88 classification is permitted in H90.

## Lexical outcomes fixed before execution

Read only the token occupying each frozen Yale occurrence. Normalize exactly by Unicode NFC and strip surrounding whitespace; do not transliterate or edit glyphs.

For each token compute:

1. character length;
2. first character;
3. last character;
4. adjacent-equality indicator (whether any identical adjacent characters occur).

No external lexicon, language model, proposed plaintext, EVA substitution, edit-distance rescue, or semantic dictionary is permitted.

## Primary test — held-out length prediction

Primary endpoint: token character length.

Use deterministic leave-one-out cross-validation over the 29 pairs. For each held-out pair, fit ordinary least squares on the remaining 28 using an intercept plus the five frozen geometry features. Predict held-out length. Score mean absolute error (MAE) across all 29 held-out predictions.

Null: keep geometry fixed and permute the 29 complete token identities across the frozen H79 pairs; recompute the entire LOOCV pipeline for **9,999** permutations using NumPy `default_rng(20261007)`.

One-sided Monte Carlo p = `(1 + count(null_MAE <= observed_MAE)) / 10000`.

Primary PASS requires both:

- observed MAE < null median; and
- p <= 0.01.

Otherwise primary endpoint = **FAIL**.

## Secondary tests — categorical morphology

The first-character, last-character, and adjacent-equality endpoints are secondary and cannot rescue a failed primary endpoint.

For first and last character, evaluate only if every class has at least 3 observations; otherwise endpoint = **NOT_RUN**. Use leave-one-out multinomial logistic regression with L2 regularization, fixed implementation defaults documented in the artifact, scoring balanced accuracy. For adjacent equality, evaluate only if both classes have at least 5 observations; otherwise **NOT_RUN**; use leave-one-out L2 logistic regression and balanced accuracy.

For every evaluable categorical endpoint use the same 9,999 whole-token permutations and seed, rerunning the full LOOCV model. One-sided p counts null balanced accuracy >= observed. Secondary nominal signal requires p <= 0.01, but is reported as exploratory unless the primary endpoint also passes.

## Negative controls

Two mandatory controls:

1. **pair-scramble control**: one fixed derangement of token identities generated with `default_rng(90090)` must not itself satisfy the primary PASS criterion when evaluated against an independently generated 9,999-permutation null using seed `90091`;
2. **feature-ablation control**: repeat the primary endpoint using x/y only. Report effect and p; it cannot rescue H90.

Failure to execute either mandatory control => **BLOCKED**.

## Decision

- **PASS**: source/inventory gates PASS, mandatory controls execute and pair-scramble is negative, and the primary held-out length endpoint satisfies both frozen criteria.
- **FAIL**: infrastructure and controls PASS but the primary endpoint misses either criterion, or pair-scramble produces a false-positive primary PASS.
- **BLOCKED**: source mismatch, mapping/cardinality mismatch, token extraction ambiguity, dependency/runtime failure, or incomplete mandatory controls.
- **NOT_RUN**: protocol has not been executed.

No secondary endpoint can change FAIL→PASS.

## Interpretation ceiling

Even a PASS would establish only a page-internal association between f68r1 object geometry and coarse label morphology. It would **not** establish semantics, star names, a language, plaintext, translation, or decipherment. A PASS would justify a separately preregistered replication on an independent folio/object system before any semantic hypothesis is opened.

Semantic identification: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

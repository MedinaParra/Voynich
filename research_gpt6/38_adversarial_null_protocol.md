# Adversarial compositional null protocol

Status: PREREGISTERED / NOT_RUN
Branch: experiment/wild-decipherment
Corpus: frozen IVTFF Eva 2.0 M5, Git blob `2a4533ab9bdfa85db9bad602d590978953055df1`.

## Question
Do the previously observed prefix contrasts (`ch/sh`, `ok/qok`, and the frozen exploratory prefix inventory) alter immediate lexical context more than expected from sparse vocabulary, manuscript regime, line position, and stem frequency alone?

## Primary test
Use only tokens that are not first or last in their transcription line. Parse folio metadata and manuscript regimes before token analysis. For each stem that occurs with at least two frozen prefixes, construct observations `(prefix, stem, left, right, folio, quire, Currier, hand, section, line-position-bin)`.

Primary contrast: `ch` vs `sh`. Secondary confirmatory contrast: `ok` vs `qok`. All other frozen-prefix contrasts are exploratory and must be labelled as such.

For every eligible prefix pair, compute the mean Jensen-Shannon divergence between immediate-neighbour distributions for matched stems. A stem contributes only when each member of the pair has at least 3 interior occurrences. The observed statistic is the occurrence-weighted mean across eligible stems.

## Adversarial null
Permutation unit is an occurrence. Shuffle prefix labels only among observations sharing the same stem and the same available manuscript strata `(Currier, hand, section)` plus a coarse within-line position bin. If a full stratum cannot permute because only one prefix is present, progressively relax section, then hand, but never stem. Record the relaxation level for every permutation pool. Folio identity is not shuffled and is used for the independent holdout below.

Run 999 deterministic permutations with seed `20261007` for this preregistered development test. A later publication-grade confirmation must use 9,999 permutations on a newly frozen holdout without changing the statistic.

Monte Carlo p = `(1 + number(null >= observed)) / (1 + permutations)`.

## Independent folio holdout
Sort folios deterministically. Assign every fifth folio to a virgin test set using only folio identity, before inspecting the test statistic. Discovery/training folios are used to establish eligible stems. The final effect is then recomputed on test folios only, without changing prefixes, thresholds, or statistic.

## PASS rule
Primary `ch/sh` is PASS only if all conditions hold:
1. at least 5 eligible matched stems in the development set;
2. development Monte Carlo p <= 0.01 with 999 permutations;
3. observed effect is positive on the untouched folio holdout and at least 60% of eligible holdout stems have positive pairwise effect relative to their matched null expectation;
4. the effect is not solely supported by a single Currier, hand, section, or quire;
5. parser coverage and permutation-pool relaxation counts are reported.

`ok/qok` is an independent secondary result and cannot rescue a failed primary result.

## Interpretation ceiling
PASS means evidence for reproducible compositional distributional structure under this operationalization. It does **not** establish natural language, semantic meanings, plaintext, or translation. FAIL is retained as a scientific result; thresholds/prefixes may not be changed after seeing the result and called confirmatory.

# H65 — Exact-consensus locus functional replication preregistration

Status: **NOT_RUN**.

## Motivation
H60-H62 establish a reproducible functional distinction between label/object loci and running text. H64 failed the stricter zero-retraining cross-transcription transfer gate. H65 tests a different, predeclared robustness question: does the functional signal survive when analysis is restricted only to loci whose tokenization is **exactly identical in both frozen transcriptions**?

This is not a rescue of H64 and does not change any previous decision. It removes transcription-disagreement loci rather than tuning a model to either transcription.

## Frozen sources
Use only:
1. primary IVTFF blob `2a4533ab9bdfa85db9bad602d590978953055df1`;
2. Takahashi blob `7f491b574b65e5fba6b553e57372c3fa50e10fec`.

No manual harmonization, glyph repair, fuzzy matching, edit-distance matching, or locus relabeling is permitted.

## Exact-consensus construction
Parse both corpora independently using the existing conservative token cleaner.

A textual locus is **consensus-eligible** only if:
- the exact locus identifier occurs in both corpora;
- after the frozen cleaner, the complete ordered token list is exactly identical in both corpora;
- page metadata `quire`, `Currier`, and `hand` agree exactly between the two sources;
- no token on the line contains an unresolved `?` in either source.

Positive examples:
- locus annotation contains `L*`;
- exactly one cleaned token occurs at that locus;
- the locus satisfies exact consensus above.

Running-text pool:
- locus does not contain any `L*` annotation;
- locus satisfies exact consensus above;
- every eligible cleaned token is entered into the running pool indexed by `(folio, Currier, hand, token_length)`.

For every positive example, select one control token from the consensus running pool on the same folio, with identical Currier, hand, and exact token length. Selection is deterministic using seed `20261007` after lexicographic sorting. A positive with no eligible control is excluded and counted.

## Frozen representation
Use only the H62 edge-ablated representation:
- remove first and final glyph;
- compute interior fraction `o`;
- interior fraction `a`;
- interior fraction `y`.

For length-2 tokens, all three values are zero. No first/last glyph feature, token length, folio, quire, section, hand, Currier, annotation subtype, or semantic label may enter the classifier.

## Evaluation
Quire is the held-out unit.

A quire is evaluable if it contains >=10 matched consensus pairs. Require:
- >=4 evaluable quires;
- >=80 total evaluable pairs.

Perform leave-one-quire-out classification with the same nearest-class-mean classifier as H60-H64. For each fold, fit standardization using training data only.

Report:
- aggregate balanced accuracy;
- per-quire balanced accuracy;
- number of held-out quires with BA > 0.5;
- number of exact-consensus positive loci and matched pairs;
- fraction of candidate label loci surviving exact cross-transcription agreement.

## Null
Exactly 999 deterministic pairwise identity permutations, seed `20261007`.

For every permutation, independently swap positive/control identity within each matched pair with probability 0.5 and refit the complete leave-one-quire-out pipeline.

Monte Carlo p = `(1 + count(null_BA >= observed_BA))/1000`.

## Frozen decision
**PASS_CONSENSUS_FUNCTIONAL_REPLICATION** iff all hold:
1. >=4 evaluable quires;
2. >=80 evaluable matched pairs;
3. 999/999 permutations complete;
4. aggregate BA > 0.55;
5. Monte Carlo p <= 0.01;
6. >=3 held-out quires individually have BA > 0.5.

**FAIL** if execution is valid but any inferential criterion fails.

**BLOCKED** if exact-consensus filtering leaves insufficient preregistered support or the sources cannot be parsed without changing the protocol.

## Interpretation ceiling
PASS would show that the edge-ablated functional label-vs-running-text signal survives on transcription-invariant loci only. It would strengthen the claim that H60-H62 are not driven solely by transcription disagreements.

FAIL would show that the strong functional effect weakens materially when restricted to exact cross-transcription consensus and would narrow the functional claim.

Neither outcome identifies semantic class, gloss, language, cipher, plaintext, translation, or decipherment.

Semantic identity: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

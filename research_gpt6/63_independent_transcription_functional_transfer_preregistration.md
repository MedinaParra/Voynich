# H61 — Independent-transcription functional-register replication

Status: **NOT_RUN**.

## Motivation
H60 passed a strict leave-one-quire-out test: label/object-locus tokens are distinguishable from locally matched running text across 9/9 evaluable quires. H61 asks whether that functional-register signal survives an independently sourced Voynich transcription rather than depending on the discovery IVTFF file.

This is a replication of a frozen functional claim, not a new lexical or semantic search.

## Frozen independent source
Use only the already frozen Takahashi-family transcription:
- file: `IT2a-n.txt`
- upstream repository: `oklo/voynich_gpt`
- upstream commit: `2d7c61c387ad6962de730caf73c48612bc8f6957`
- expected Git blob: `7f491b574b65e5fba6b553e57372c3fa50e10fec`

Do not substitute another transcription after execution begins.

## Frozen extraction and matching
Apply the H60 construction without tuning:
- positive = a single certain token on an existing `L*` label/object locus;
- running controls exclude every `L*` locus;
- match within the same folio;
- exact token length;
- Currier/hand metadata matched when present;
- deterministic control selection with seed `20261007`.

No manual recoding of label classes or illustration content is permitted.

## Frozen predictors
Exactly the same five H60 predictors:
- fraction `o`;
- fraction `a`;
- fraction `y`;
- starts `q`;
- ends `y`.

Prohibited predictors: token length, folio, quire, section, hand, Currier class, annotation subtype, topology, illustration class, original-transcription token identity, or proposed semantics.

## Evaluation
Primary unit: quire.

Only quires with >=10 matched pairs are evaluable. Require >=4 evaluable quires and >=80 total evaluable pairs or classify **BLOCKED**.

Perform leave-one-quire-out classification with training-only standardization and the same nearest-class-mean classifier family used by H60.

Report:
- aggregate balanced accuracy;
- balanced accuracy for each held-out quire;
- number of held-out quires above 0.5.

## Null
Exactly 999 deterministic paired-label permutations, seed `20261007`.

Within each matched pair, independently swap label-locus/running-text identity with probability 0.5, preserving quire membership and pair structure, then refit the entire leave-one-quire-out pipeline.

Monte Carlo p = `(1 + count(null_BA >= observed_BA))/1000`.

## Frozen decision
**PASS_INDEPENDENT_FUNCTIONAL_REPLICATION** iff all hold:
1. independent source blob exactly matches the frozen blob;
2. >=4 evaluable quires;
3. >=80 evaluable matched pairs;
4. 999/999 permutations complete;
5. aggregate BA > 0.60;
6. Monte Carlo p <= 0.01;
7. >=3 held-out quires individually have BA > 0.5.

**FAIL** if execution is valid but any inferential criterion fails.

**BLOCKED** if the source, label-locus syntax, matching, or sample requirements cannot be used without changing the frozen protocol.

## Interpretation ceiling
PASS would independently replicate the functional-register effect across transcription files/traditions: label/object-locus tokens would retain a cross-quire token-form distinction from locally matched running text.

Because both transcriptions describe the same physical manuscript and remain EVA-family encodings, PASS would still not be independent manuscript evidence and would not identify semantics, language, plaintext, cipher, or translation.

The failed Lc/Lf semantic-anchor route remains closed regardless of H61.

Semantic identity: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

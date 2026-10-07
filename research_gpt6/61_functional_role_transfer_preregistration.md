# H60 — Functional-role transfer preregistration

Status: **NOT_RUN**.

## Motivation
The frozen program now has a reproducible distinction between annotated label/object loci and matched running text, while specific Lc/Lf lexical-semantic routes remain FAIL. H60 tests the narrower next claim: whether the already-frozen label-locus token-form signal transfers across manuscript regions rather than being driven by one local section or quire.

No semantic class, plaintext, language, or translation is assigned.

## Frozen source and positive/control construction
Use discovery blob `2a4533ab9bdfa85db9bad602d590978953055df1` and exactly the extraction/matching rules of the frozen label-locus-vs-running-text test:
- positive = existing label/object locus token;
- control = running-text token from the same folio;
- exact token length matched;
- Currier/hand matched when metadata exist;
- seed `20261007`;
- no manual relabeling.

The original five predictors are frozen unchanged:
- fraction `o`;
- fraction `a`;
- fraction `y`;
- starts `q`;
- ends `y`.

No token length, folio ID, quire ID, section, hand, Currier state, annotation subtype, topology, illustration class, or proposed semantics may enter as predictors.

## Independent transfer unit
Primary transfer unit is **quire**. Construct all eligible matched pairs first, then assign each pair to the quire of its folio.

Only quires with >=10 matched pairs are evaluable. Require >=4 evaluable quires and >=80 total evaluable pairs; otherwise **BLOCKED**.

## Evaluation
Perform leave-one-quire-out classification. For every held-out quire:
1. fit standardization on training quires only;
2. fit the same nearest-class-mean classifier used in the frozen label-locus test;
3. predict every pair in the held-out quire.

Primary statistic: aggregate balanced accuracy over all held-out predictions.

Also report per-quire BA. A transfer result dominated by a single held-out quire is not sufficient: require at least 3 evaluable held-out quires individually above 0.5.

## Null
Exactly 999 deterministic permutations, seed `20261007`.

Within each matched pair, independently swap label-locus/running-text identity with probability 0.5, then refit the complete leave-one-quire-out pipeline. Preserve quire membership and pair structure.

Monte Carlo p = `(1 + count(null_BA >= observed_BA))/1000`.

## Frozen decision
**PASS_FUNCTIONAL_TRANSFER** iff all hold:
1. >=4 evaluable quires;
2. >=80 evaluable matched pairs;
3. 999/999 permutations complete;
4. aggregate BA > 0.60;
5. Monte Carlo p <= 0.01;
6. >=3 held-out quires have BA > 0.5.

**FAIL** if the execution is valid but any inferential criterion fails.

**BLOCKED** if sample/quire requirements cannot be met without altering the frozen construction.

## Interpretation ceiling
PASS would support a manuscript-region-generalizing **functional locus distinction**: label/object-position tokens differ from locally matched running text in a way that transfers across quires. It would not establish that labels name depicted objects, distinguish specific semantic classes, identify language/cipher/plaintext, or translate any token.

The prior Lc/Lf semantic tests remain FAIL regardless of H60.

Semantic identity: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

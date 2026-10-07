# H62 — Edge-ablation functional-role replication preregistration

Status: **NOT_RUN**.

## Motivation
H60 and H61 show a reproducible label/object-locus versus running-text distinction across quires and across two transcriptions. However, the frozen predictor set contains two explicit edge cues (`starts q`, `ends y`) and three whole-token character fractions (`o`, `a`, `y`). H62 asks whether the functional signal survives when token-edge information is removed rather than merely detecting position-specific orthographic endings/beginnings.

This is an adversarial robustness test, not a semantic test.

## Frozen sources
Run the identical test independently on both already frozen corpora:
1. primary IVTFF blob `2a4533ab9bdfa85db9bad602d590978953055df1`;
2. independent Takahashi blob `7f491b574b65e5fba6b553e57372c3fa50e10fec`.

No transcription may be modified or manually harmonized.

## Frozen pair construction
For each corpus separately, reuse exactly the H60/H61 extraction and matching rules:
- positive = existing single-certain-token label/object locus;
- control = running-text token from same folio;
- exact token length matched;
- Currier/hand matched when available;
- deterministic seed `20261007`;
- no manual recoding.

Quire eligibility remains >=10 matched pairs. Require >=4 evaluable quires and >=80 evaluable pairs per corpus, else that corpus is **BLOCKED**.

## Primary edge-ablated representation
For every token of length >=2, remove the first and last glyph before feature extraction. For length 2, the interior is empty and all interior fractions are defined as zero. For length 3, the one central glyph is retained.

Primary predictors are ONLY:
- interior fraction `o`;
- interior fraction `a`;
- interior fraction `y`.

The following are prohibited in the primary model:
- original first glyph;
- original final glyph;
- starts-`q`;
- ends-`y`;
- token length;
- folio, quire, section, hand, Currier, annotation subtype, topology or proposed semantics.

## Diagnostic edge-only model
After the primary score, compute a non-gating diagnostic model using ONLY:
- starts `q`;
- ends `y`.

This diagnostic is reported to quantify how much signal is carried by token edges. It cannot rescue a failing primary test.

## Evaluation
For each corpus separately, perform the same leave-one-quire-out nearest-class-mean pipeline used in H60/H61, with training-only standardization.

Report:
- aggregate balanced accuracy;
- per-quire balanced accuracy;
- number of held-out quires above 0.5.

## Null
For each corpus independently, perform exactly 999 pairwise identity permutations, seed `20261007`, preserving pair and quire structure. Refit the entire leave-one-quire-out primary pipeline for each permutation.

Monte Carlo p = `(1 + count(null_BA >= observed_BA))/1000`.

## Frozen decision
A corpus receives **PASS_EDGE_ABLATED** iff all hold:
1. >=4 evaluable quires;
2. >=80 evaluable matched pairs;
3. 999/999 permutations complete;
4. primary edge-ablated aggregate BA > 0.55;
5. Monte Carlo p <= 0.01;
6. >=3 held-out quires individually have BA > 0.5.

Experiment-level **PASS_EDGE_ABLATED_REPLICATION** requires PASS_EDGE_ABLATED independently in **both** frozen corpora.

**FAIL** if both executions are valid but the two-corpus replication gate is not met.

**BLOCKED** if either source cannot meet frozen sample requirements or cannot be parsed without changing the protocol.

## Interpretation ceiling
PASS would show that the replicated functional-locus signal is not reducible to the original first/last glyph cues and survives in token interiors across two transcriptions. It would strengthen a functional-register/production-grammar interpretation.

FAIL would indicate that much or all of the current functional classification may depend on token-edge orthography and would prevent escalation toward semantic interpretation from H60/H61 alone.

Neither outcome identifies a semantic class, gloss, language, cipher, plaintext or translation.

Semantic identity: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

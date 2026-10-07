# H63 — Same-folio lexical-echo preregistration

Status: **NOT_RUN**.

## Motivation
H60/H61 establish a cross-quire functional distinction between label/object-locus tokens and matched running text, and H62 shows that part of this distinction survives removal of the first and last glyph in two frozen transcriptions. The next falsifiable bridge toward lexical/referential information is locality: if labels participate in the same lexical system as the prose associated with a folio, their deterministic interior cores should recur in running text on their own folio more than on carefully matched other folios.

H63 tests **local lexical coupling**, not a gloss and not translation.

## Frozen sources
Run independently on both already frozen corpora:
1. primary IVTFF blob `2a4533ab9bdfa85db9bad602d590978953055df1`;
2. independent Takahashi blob `7f491b574b65e5fba6b553e57372c3fa50e10fec`.

No manual harmonization, relabeling, or uncertain-glyph repair is permitted.

## Frozen extraction
Use the same single-certain-token label/object-locus extraction used in H60-H62. Running text excludes all annotated `L*` loci.

For every token with original length >=4 define one deterministic **interior core** by deleting exactly its first and final glyph. Tokens shorter than 4 are excluded from H63 rather than assigned an empty/one-glyph core.

For each folio:
- `L_f` = unique interior cores from eligible label tokens;
- `R_f` = unique interior cores from eligible running-text tokens.

Require at least 2 unique eligible label cores on a source folio.

## Frequency weighting
To stop ubiquitous cores from dominating, compute running-text document frequency over all parsed folios in that corpus only.

For core `c`:
`w(c) = 1 + log((N + 1) / (df(c) + 1))`,
where `N` is the number of folios with eligible running-text cores.

For source folio `f` and target folio `g`:
`echo(f,g) = sum(w(c) for c in L_f intersect R_g) / sum(w(c) for c in L_f)`.

Each core is counted once per folio. No token-frequency multiplier is allowed.

## Matched target sets
For every source folio `f`, define candidate targets as folios `g != f` having:
- identical quire;
- identical Currier state;
- identical scribal hand;
- non-empty eligible running-core set.

A source folio is evaluable only if it has at least **2** such matched control folios.

Require per corpus:
- >=20 evaluable source folios;
- sources spanning >=4 quires.
Otherwise that corpus is **BLOCKED**.

## Primary statistic
For each evaluable source folio:
`delta_f = echo(f,f) - mean_g echo(f,g)` over all frozen matched control targets.

Primary aggregate statistic is the **equal-folio-weighted mean** of `delta_f`. Label-rich folios do not receive extra weight.

Also report:
- mean own-folio echo;
- mean matched-control echo;
- median `delta_f`;
- fraction of evaluable folios with `delta_f > 0`;
- per-quire mean delta.

## Matched randomization null
Exactly 999 randomizations, seed `20261007`, independently in each corpus.

For each source folio `f`, construct the fixed candidate set `{f} union controls(f)`. In each randomization, choose one member uniformly as the pseudo-own target and calculate:
`pseudo_delta_f = echo(f,pseudo) - mean echo(f,all other fixed candidates)`.

Aggregate the equal-folio-weighted mean pseudo-delta exactly as for the observed statistic.

Monte Carlo p = `(1 + count(null >= observed))/(1000)`.

This null preserves the source label-core set, quire, Currier/hand matching, target-pool size, and core-frequency weighting.

## Non-gating diagnostic
Repeat the observed calculation using exact full tokens rather than interior cores. This is descriptive only and cannot rescue a failing primary test.

## Frozen decision
A corpus receives **PASS_LOCAL_LEXICAL_ECHO** iff all hold:
1. >=20 evaluable source folios;
2. >=4 represented quires;
3. 999/999 randomizations complete;
4. aggregate mean interior-core delta > 0;
5. Monte Carlo p <= 0.01;
6. >55% of evaluable source folios have `delta_f > 0`.

Experiment-level **PASS_REPLICATED_LOCAL_LEXICAL_ECHO** requires PASS_LOCAL_LEXICAL_ECHO independently in both frozen transcriptions.

**FAIL** if both executions are valid but the two-corpus gate is not met.

**BLOCKED** if either corpus cannot meet the frozen support requirements without changing the protocol.

## Interpretation ceiling
PASS would show that label-token interiors are preferentially echoed in running text on the same folio beyond matched quire/Currier/hand targets, and that this locality replicates across two transcriptions. This would be evidence for **local lexical/referential coupling** and would justify moving from FUNCTIONAL toward a lexical-anchor program.

PASS would still not identify what any core means, whether a label names the pictured object, the language, cipher, plaintext, or a translation. Same-manuscript production effects remain an alternative explanation.

FAIL would mean the strong functional-register result does not automatically produce same-folio lexical echo and would block escalation on this route.

Semantic gloss: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

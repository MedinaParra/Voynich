# H84 — exact-length robustness audit of astronomical-label hapax enrichment

Status before execution: **NOT_RUN**.

## Evidential role

H84 is a prospectively frozen **robustness/falsification audit of an already published external positive result**, not a fresh discovery test.

At frozen revision `2bb4437906b714c1fba26f9897f8df3e7660a0b0`, `brigadire/voinich` reports that 80/112 independently matched astronomical `LABEL` occurrences are section-local hapax, versus a panel-conditioned null mean fraction 0.611207143, with one-sided permutation `p=0.008799120` and positive direction in all 8 leave-one-panel-out exclusions.

That external null preserves label counts by panel but does **not** preserve exact token length. Longer or otherwise length-shifted token inventories can be intrinsically more likely to be section-local hapax. H84 asks whether the reported enrichment survives an exact token-length control without changing the frozen positive label inventory.

No semantic, language, plaintext, translation, or decipherment claim is permitted from H84.

## Frozen external source

Repository: `brigadire/voinich`

Revision: `2bb4437906b714c1fba26f9897f8df3e7660a0b0`

Required inputs and SHA-256:

1. `experiments/fingerprint-v2-task79-v1/canonical-out/occurrence_metadata.jsonl`
   - `ba0342e15d8c468ec4e9f741e97cdb4a11938fe1f0ae3ac4338b73aaf1bd773a`
2. `research/stolfi_label_inventory/STOLFI_ASTRO_LABEL_MATCHES.tsv`
   - `4b78659807f83ea16da872eaf29dc259393bef96a10bc96361919a79db822000`

Any hash mismatch is **BLOCKED**.

The source's own frozen manifest reports these same hashes, 901 Astronomical-section token occurrences, 112 confirmed label occurrences, and 518 section-local hapax occurrences.

## Frozen astronomical panels

Use exactly:

`f67r1, f67r2, f67v1, f68r1, f68r2, f68r3, f68v2, f68v1`.

From `occurrence_metadata.jsonl`, admit exactly rows satisfying:

- `section == "A"`;
- `folio` belongs to the frozen panel list.

Use `absolute_token_position` as the occurrence identifier and `token` as the exact token representation.

Integrity gates:

- exactly **901** admitted occurrence positions;
- all admitted absolute positions unique;
- exactly **518** positions whose exact `token` has frequency 1 within the admitted 901-position section.

Failure is **BLOCKED**.

## Frozen positive-label inventory

Read `STOLFI_ASTRO_LABEL_MATCHES.tsv`.

Use only rows with `match_status == "MATCHED"`.

For each such row, parse the comma-separated integer field `absolute_token_positions`; pool and deduplicate positions.

Required integrity gates:

- exactly **130** matched source rows;
- exactly **112** distinct matched absolute token positions;
- all 112 positions occur in the frozen 901-position Astronomical inventory;
- exactly **80/112** are section-local hapax under the frozen frequency definition.

The `object_type` field is not used for the primary H84 statistic.

Failure to reproduce these pre-existing published invariants is **BLOCKED**.

## Frozen exact token-length definition

For every occurrence define:

`token_length = len(token)`

using Python's ordinary character count on the **exact canonical `token` field as stored in the frozen metadata**.

No EVA normalization, markup cleaning, glyph equivalence, stemming, bracket repair, transliteration conversion, or semantic interpretation is allowed.

The exact raw token representation is used only because it is already the unit on which the external section-local hapax frequency was defined.

## Primary observed statistic

Let `H(position)=1` iff that occurrence's exact token is a section-local hapax among the 901 frozen Astronomical occurrences.

Primary observed statistic:

`F_obs = mean(H(position))` over the 112 frozen confirmed label positions.

The frozen integrity gate requires `F_obs = 80/112 = 0.7142857142857143` exactly as an integer ratio before permutation.

## Frozen panel × exact-length null

Use exactly **19,999** permutations with seed `20261016`.

Construct cells keyed by:

`(panel, token_length)`.

For every cell independently:

1. let `N_c` be the number of all frozen Astronomical token occurrences in that panel×length cell;
2. let `n_c` be the number of the 112 frozen confirmed label occurrences in that cell;
3. sample without replacement exactly `n_c` positions uniformly from the complete `N_c` positions in that same cell;
4. pool all sampled positions over cells;
5. compute the sampled hapax fraction `F_perm`.

Thus every null draw preserves simultaneously:

- exact panel label counts;
- the complete exact token-length distribution **within each panel**;
- the 901-token Astronomical sampling frame;
- the section-local hapax definition.

The sampling frame includes confirmed labels; the unlabeled complement is not asserted to be a validated negative class.

Upper-tail Monte Carlo p:

`p = (1 + count(F_perm >= F_obs)) / 20000`.

Use a repository-local SplitMix64 generator with deterministic rejection-sampled `randbelow` and partial Fisher-Yates sampling. No dependence on Python's `random` implementation is permitted.

## Frozen exchangeability gates

Before computing the null result, report every occupied label cell `(panel,length,n_c,N_c)`.

A label position is `movable` iff its cell has `N_c > n_c` and `n_c > 0`.

Validity requires:

- at least **80 of 112** confirmed label positions are movable;
- at least **12** occupied panel×length cells are movable;
- at least **7 of 8** panels contain at least one movable occupied cell;
- all 19,999/19,999 permutations complete.

If any gate fails, H84 = **BLOCKED**.

These thresholds are frozen before inspecting the exact-length-controlled null.

## Frozen decision

H84 = **PASS_ROBUSTNESS** only if all integrity/exchangeability gates pass and:

1. `F_obs > null_mean`;
2. one-sided `p <= 0.05`.

H84 = **FAIL_ROBUSTNESS** if all validity gates pass but either scientific criterion fails.

H84 = **BLOCKED** for source-integrity, invariant-reproduction, exchangeability, or execution failure.

No cell definition, token-length rule, label inventory, seed, permutation count, p-value direction, or threshold may be changed after viewing the output.

## Secondary STAR-family diagnostic

The external source also reports a descriptive STAR-family result. H84 will reproduce the set of positions from matched rows with `object_type == "star"` and report the same panel×exact-length-controlled hapax statistic for that set using a separate deterministic stream derived from seed `20261017`.

This STAR-family analysis is **secondary/descriptive only** and cannot change the primary H84 decision. Report:

- number of unique STAR positions;
- observed STAR hapax fraction;
- exact-length-conditioned null mean/SD and upper-tail p;
- STAR exchangeability counts.

No PASS/FAIL claim is assigned to this secondary family.

## Interpretation boundary

A `PASS_ROBUSTNESS` would establish only that the external finding — confirmed astronomical label positions are enriched for section-local hapax — cannot be explained solely by their panel distribution and exact token-length distribution under this frozen null.

It would strengthen a **structural/documentary label-specialization** claim. It would not show what any label means, whether labels are names, whether the diagrams encode a particular astronomical catalogue, what language is used, or how to translate the manuscript.

A `FAIL_ROBUSTNESS` would show that the previously reported panel-conditioned hapax enrichment does not survive exact token-length conditioning and therefore should not be treated as an independent structural signal beyond length composition.

This test reuses the same external positive inventory and manuscript tokens. It is an independent implementation/stronger-null audit, **not independent data replication**.

H79 geometric f68r1 star↔label pairing (A0): **PASS**.
H80 local f68r1 star-topology label morphology: **FAIL**.
H81 f68r1 star-label paragraph rarity: **BLOCKED** (valid ZL arm **FAIL**).
H82 f68r2 centre-mark ↔ label morphology: **FAIL_EXPLORATORY**.
H83 exact-36 f68r2 external-geometry route: **BLOCKED_DATA / BLOCKED_SELECTION**.
H84 exact-length astronomical-label hapax robustness: **NOT_RUN**.
Semantic identification A1+: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

# H67 — Richer IVTFF label-source admissibility audit

Status before execution: **NOT_RUN**.

## Purpose

Before reopening any label-object / visual-subtype hypothesis, audit whether a publicly retrievable, commit-pinned IVTFF source actually contains enough explicit `L*` subtype observations for a new multiclass experiment.

This is a **data-admissibility audit**, not a semantic test. It cannot rescue the prior `Lc` vs `Lf` FAIL results.

## Frozen candidate source

Candidate bytes are frozen to:

- repository: `noah-chelednik/voynich-data`;
- commit: `472ef7366606a799fc8f1044c037e06b413f6ddd`;
- path: `data_sources/cache/IT_ivtff_1a.txt`;
- raw URL assembled only from that commit and path.

The file header must contain both:

- `#=IVTFF`;
- `# Extracted from LSI_ivtff_0d.txt`.

A missing file or missing provenance header is **BLOCKED**.

## Scientific provenance boundary

Because the candidate explicitly declares that it was extracted from `LSI_ivtff_0d.txt`, it is **not an independent transcription tradition** for confirmation. A successful H67 gate admits it only as a richer IVTFF/LSI-derived discovery dataset.

It may not satisfy the independent-replication requirement in the original label-object protocol.

## Frozen parsing

For every IVTFF text record of the form `<folio.record,locator> text`:

1. extract the generic unit after the record comma, ignoring the leading IVTFF status marker (`@`, `+`, `*`, `=`);
2. retain units whose normalized unit begins with `L`;
3. tokenize the text after removing IVTFF angle/bracket/brace annotations, using lowercase alphabetic tokens of length >=2;
4. count both record count and known-token count by exact normalized `L*` unit;
5. a token containing unresolved `?` material is not counted as a known token;
6. do not infer, merge, rename, or semantically relabel units after seeing counts.

Also report total `L*` records, nonempty records, known tokens, distinct known token types, file byte count, Git blob SHA-1, and SHA-256.

## Frozen object-related units and eligibility

The only candidate units eligible for a later visual-subtype experiment are frozen as:

- `Lp`
- `Lc`
- `Lf`
- `Ln`
- `Lt`
- `Ls`
- `Lz`
- `La`

`L0` and bare `L` are excluded from a future semantic/object-class claim because they do not themselves encode one of the frozen explicit object-relation subtypes.

A class is sample-eligible only if it has **>=20 known tokens** in the audited candidate source.

## Admissibility decision

H67 = **PASS** only if all of the following are true:

1. the frozen source is retrievable;
2. the required provenance header is present;
3. parsing completes without source mutation;
4. at least **four** of the frozen object-related units each contain >=20 known tokens;
5. the audit emits exact source hashes and counts.

H67 = **FAIL** if the source is valid/retrievable but fewer than four frozen object-related units reach the >=20 threshold.

H67 = **BLOCKED** if bytes/provenance/parsing cannot be audited as frozen.

Before execution H67 is **NOT_RUN**.

## Interpretation boundary

A PASS merely establishes that a new multiclass visual-subtype experiment is statistically feasible on an LSI-derived IVTFF layer. It does not establish semantics, language, plaintext, translation, or decipherment, and it does not provide independent transcription replication.

Historical `Lc`-vs-`Lf`, topology-conditioned lexical-anchor, and familywise subtype tests remain **FAIL**.

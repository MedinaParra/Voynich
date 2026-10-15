# H70 — Cross-alphabet visual-label locus coverage audit result

Status: **FAIL**.

This records execution of the preregistered coverage protocol in `82_h70_cross_alphabet_label_coverage_preregistration.md`. Workflow completion was successful; the scientific/data-coverage gate failed.

## Execution evidence

- Workflow: `H70 cross-alphabet label coverage`.
- Run: `37614940364` (run number 1), conclusion `success`.
- Job: `112770900826` (`h70-cross-alphabet-label-coverage`), conclusion `success`.
- Experimental branch head executed: `b4092e2786c20e78a5de7b514423f5c36dd35a25` (PR merge checkout `f7963be61eff08f6732110ca97cc64c38dcd3433`).
- Artifact: `h70-cross-alphabet-label-coverage-results`, ID `11478583439`.
- Artifact SHA256: `6fa09f92ff0b0d1f07ca52a3b5a180cd4f3950ca371f0880d746f5b28a6467a0`.

All four frozen source SHA-256 values matched the preregistration exactly.

## IT visual-label inventory

Eligible exact IT loci under the frozen H68 documentary scope:

- `Lc`: **37** loci;
- `Lf`: **195**;
- `Ln`: **59**;
- `Lt`: **42**.

## Currier-D'Impero / Currier alphabet (`CD`)

Exact locus present:
- `Lc` 0;
- `Lf` 0;
- `Ln` 0;
- `Lt` 7.

Single-token mappable:
- `Lc` 0;
- `Lf` 0;
- `Ln` 0;
- `Lt` 5 on 1 folio.

Replication eligibility: **FAIL**.

## Friedman Study Group / FSG alphabet (`FG`)

Exact locus present:
- `Lc` 0;
- `Lf` 1;
- `Ln` 1;
- `Lt` 11.

Single-token mappable:
- `Lc` 0;
- `Lf` 1 on 1 folio;
- `Ln` 1 on 1 folio;
- `Lt` 7 on 3 folios.

Replication eligibility: **FAIL**.

## Glen Claston / v101 alphabet (`GC`)

Exact locus present:
- `Lc` 37;
- `Lf` 195;
- `Ln` 59;
- `Lt` 42.

Single-token mappable:
- `Lc` **30** on **10** folios;
- `Lf` **158** on **15** folios;
- `Ln` **53** on **8** folios;
- `Lt` **33** on **9** folios.

GC satisfies the frozen >=20 tokens and >=5 folios rule for all four classes.

Replication eligibility: **PASS for this source only**.

## Cross-source overlap

Single-token exact-locus overlaps:

- CD & FG: **5**;
- CD & GC: **5**;
- FG & GC: **9**;
- all three: **5**.

## Decision

The preregistration required at least **two** of the three non-EVA sources to be replication-eligible. Only **one** source (`GC`) qualifies.

H70: **FAIL**.

The gate is not weakened post hoc. GC may support a separately preregistered single-source experiment, but such an experiment cannot retroactively turn H70 into PASS and cannot be called a two-source cross-alphabet replication.

## Conservative interpretation

The frozen public Currier and FSG files do not contain sufficient exact-locus coverage for the H68 visual subtype family under the stringent single-token mapping rule. Glen Claston/v101 does have sufficient exact-locus coverage and therefore admits one new falsifiable single-source test.

H69 remains **FAIL**.
Semantic identification: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

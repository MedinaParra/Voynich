# H84 — exact-length robustness audit of astronomical-label hapax enrichment: result

Status: **FAIL_ROBUSTNESS**.

This records the completed execution of the prospectively frozen protocol in `109_h84_astronomical_label_hapax_length_control_preregistration.md`.

H84 re-tested an already published external positive structural result using a stronger null that preserves both panel and exact token length. All integrity, exchangeability and execution gates passed. The previously significant hapax enrichment did **not** survive this exact-length conditioning.

H84 is a robustness/falsification audit of a structural/documentary signal. It is not a semantic, language, plaintext, translation or decipherment test.

## Execution evidence

- Branch: `experiment/h58-strict-l-vs-p`.
- Workflow: `H84 astronomical label hapax exact-length robustness`.
- Run: `37648065882` (run number 2), conclusion `success`.
- Job: `112883907379` (`h84-astronomical-label-hapax-length-control`), conclusion `success`.
- Experimental head: `ae7b93db865ca7947d977f312974f09845079fe7`.
- PR merge checkout: `ae79541f82a3829ff3224f4f648ee4cc1d10a544`.
- Artifact: `h84-astronomical-label-hapax-length-control-results`, ID `11494619632`.
- Artifact SHA256: `579552c094ebf0e71fdc3527dcc5aa1eb82aa51da5655b83b5c69402dc203c9c`.
- Artifact size: 1,569 bytes.

Infrastructure: **PASS**.

## Frozen source integrity

External source: `brigadire/voinich`, revision `2bb4437906b714c1fba26f9897f8df3e7660a0b0`.

Both frozen input hashes matched exactly:

- occurrence metadata SHA256: `ba0342e15d8c468ec4e9f741e97cdb4a11938fe1f0ae3ac4338b73aaf1bd773a` — PASS;
- matched-label inventory SHA256: `4b78659807f83ea16da872eaf29dc259393bef96a10bc96361919a79db822000` — PASS.

The implementation independently reproduced all preregistered published invariants:

- Astronomical-section occurrences in the 8 frozen panels: **901**;
- section-local hapax occurrences: **518**;
- matched source rows: **130**;
- distinct confirmed label positions: **112**;
- confirmed-label hapax positions: **80**;
- STAR-family positions: **54**;
- every selected position lay inside the frozen section inventory.

Source/invariant gates: **PASS**.

## Panel × exact-length exchangeability

The stronger null preserved the exact number of selected labels separately in every `(panel, exact token length)` cell.

Observed exchangeability:

- movable confirmed-label positions: **108/112**;
- movable occupied panel×length cells: **40**;
- panels with at least one movable occupied cell: **8/8**.

Frozen gates required >=80 movable positions, >=12 movable occupied cells and >=7 panels.

Exchangeability: **PASS**.

## Primary exact-length-controlled result

Observed confirmed-label hapax fraction:

`80 / 112 = 0.7142857142857143`

Frozen panel×exact-length null, seed `20261016`:

- permutations: **19,999/19,999**;
- null mean hapax fraction: **0.6771584114920032**;
- null SD: **0.03340324692807503**;
- null minimum: **0.5267857142857143**;
- null maximum: **0.8214285714285714**;
- observed minus null mean: **+0.0371273027937111**;
- one-sided upper-tail Monte Carlo `p = 0.1651`.

Frozen criteria:

1. `F_obs > null_mean` — **PASS**;
2. `p <= 0.05` — **FAIL**;
3. 19,999/19,999 permutations — **PASS**.

Primary H84 decision: **FAIL_ROBUSTNESS**.

## What changed relative to the external positive result

The external panel-conditioned analysis had reported 80/112 hapax labels against a null mean around 0.6112 with `p≈0.0088`.

Once the null additionally preserves the exact token-length composition **within each panel**, the expected hapax fraction rises substantially to **0.6772** and the same observed 0.7143 becomes statistically unremarkable (`p=0.1651`).

Therefore a large part of the apparent astronomical-label hapax enrichment is attributable to the label inventory's panel-specific token-length composition. The previously reported significance is not robust to this frozen exact-length control.

This does not prove that length is the only structural difference between labels and other astronomical tokens. It means the specific hapax-enrichment claim cannot be treated as an independent signal beyond panel and exact length on this dataset.

## Secondary STAR-family diagnostic

The STAR subset was frozen as descriptive only and cannot alter the primary H84 decision.

- unique STAR positions: **54**;
- observed STAR hapax: **46/54 = 0.8518518518518519**;
- panel×exact-length null mean: **0.7591870334257453**;
- null SD: **0.04453183508134152**;
- one-sided upper-tail `p = 0.02755`;
- permutations: **19,999/19,999**.

STAR exchangeability:

- movable STAR positions: **52**;
- movable occupied cells: **17**;
- movable panels: **4**.

This is an interesting residual concentration, but it was prospectively secondary/descriptive and covers only four movable panels. It is **not** a confirmatory PASS and must not be promoted post hoc.

A future STAR-specific test would need a new preregistration and preferably an independent or untouched object-label inventory.

## Frozen decision

H84: **FAIL_ROBUSTNESS**.

The external astronomical-label hapax enrichment does not survive the preregistered panel × exact-token-length null.

## Conservative interpretation

The strongest defensible conclusion is now narrower:

- astronomical labels are structurally special in several previously established label-vs-running-text analyses;
- however, the specific claim that independently matched astronomical labels are unusually section-local hapax does not remain significant after exact panel and token-length conditioning;
- the STAR-family residual is hypothesis-generating only;
- none of these results identifies label meanings or an external celestial catalogue.

Do not remove length cells, redefine token length, restrict panels, or promote the STAR subset using the same output in order to rescue the primary H84 result.

## Identifier note

A separate workflow already present in the branch is also named `H84 IT-GC label transcription disagreement`. This is an experiment-number namespace collision only. The present test remains identified by its frozen protocol path and workflow/run IDs above; no scientific criterion is changed retrospectively. Future experiments should use a new unique identifier rather than silently renumbering this completed protocol.

## Current ladder

H79 geometric f68r1 star↔label pairing (A0): **PASS**.

H80 local f68r1 star-topology label morphology: **FAIL**.

H81 f68r1 star-label paragraph rarity: **BLOCKED** (valid ZL arm **FAIL**).

H82 f68r2 centre-mark ↔ label morphology: **FAIL_EXPLORATORY**.

H83 exact-36 f68r2 external-geometry route: **BLOCKED_DATA / BLOCKED_SELECTION**.

H84 exact-length astronomical-label hapax robustness: **FAIL_ROBUSTNESS**.

Semantic identification A1+: **NOT_RUN**.

Language identification: **NOT_RUN**.

Translation: **NOT_RUN**.

Decipherment: **NOT_RUN**.

# H84 — IT↔GC structural transcription-disagreement challenge result

Status: **BLOCKED**.

This records execution of the preregistered protocol in `109_h84_it_gc_label_transcription_disagreement_preregistration.md`. The workflow and frozen-source checks succeeded, but the preregistered matched-sample gate failed before any permutation test was allowed.

## Execution evidence

- Workflow: `H84 IT-GC label transcription disagreement`.
- Run: **37647629830** (run number 2).
- Job: **112882430768** (`h84-it-gc-label-transcription-disagreement`).
- Experimental branch head executed: `d3216da922be117328cfc589c1df408acc50fb5e` (PR merge checkout `c836027c87097486a8e0eb4e04a53450760e3185`).
- Frozen IT SHA-256: `db624a731114f26854bbfe3a59d40827fa8911be46d086b6c558d99e557241ee` — matched.
- Frozen GC SHA-256: `b09570cb6c993bc2d87134d115e60a978650a8a6495483ddbb1f6005a586096f` — matched.
- Artifact: `h84-it-gc-label-transcription-disagreement-results`, ID **11495510587**.
- Artifact ZIP SHA-256: `6018ca9dd64a55aa7aaa6d7ce2f9f593eea3569b86d3bff8b0d4edf9eb746257`.

Infrastructure: **PASS**.

## Exact-locus coverage

Exact IT loci also present in GC:

- generic `L*`: **548**;
- generic `P*`: **4,118**.

Under the preregistered requirement that the entire exact locus yield exactly one known token in both IT and GC:

- `L*`: **451** single-token-mappable loci across **49** folios;
- `P*`: only **24** single-token-mappable loci across **10** folios.

Thus the limiting factor is not label coverage. It is the fact that paragraph records are normally multi-token records in these frozen source files, whereas H84 required a whole P record to be single-token in both transcriptions.

## Frozen matching result

Same-folio + same-IT-token-length matching without replacement produced:

- matched L–P pairs: **3**;
- represented folios: **2** (`f67r2`, `f68r1`);
- labels excluded because no unused exact control remained: **448**.

Preregistered gates were:

- >=60 matched pairs: **FAIL**;
- >=8 represented folios: **FAIL**.

Therefore:

- permutations requested: 9,999;
- permutations executed: **0 by design after the sample gate**;
- primary `Delta`: **NOT_RUN**;
- p-value: **NOT_RUN**;
- H84 scientific status: **BLOCKED**.

## Conservative interpretation

H84 does **not** show that labels are more or less transcriptionally ambiguous than paragraph text. The test never reached its inferential stage.

The blocker is a representational mismatch between the frozen exact-locus record unit and the intended token-level P control: paragraph loci usually contain multiple tokens. Lowering the 60-pair/8-folio threshold or silently accepting multi-token P records after seeing this result would violate the preregistration.

A legitimate follow-up must be separately preregistered and must define, before execution, a deterministic token-level alignment inside exact P records. The cleanest admissible rule is ordinal alignment only for exact P records where IT and GC contain the same number of known tokens; no fuzzy token matching or content-based realignment should be allowed.

Semantic identification: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

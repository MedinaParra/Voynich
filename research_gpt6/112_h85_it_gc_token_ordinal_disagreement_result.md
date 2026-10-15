# H85 — IT↔GC exact-record ordinal-token transcription-disagreement result

Status: **FAIL**.

This records execution of the preregistered protocol in `111_h85_it_gc_token_ordinal_disagreement_preregistration.md`. Infrastructure, frozen-source verification, sample gates, and all permutations completed successfully. The preregistered nuisance prediction (`labels are more structurally unstable than matched paragraph tokens`) failed, with the observed direction reversed.

## Execution evidence

- Workflow: `H85 IT-GC ordinal-token transcription disagreement`.
- Run: **37648165970** (run number 2).
- Job: **112884253733** (`h85-it-gc-token-ordinal-disagreement`).
- Experimental branch head executed: `00e6b4cd93062ed3ef8c99a7b39263eefa0473f6` (PR merge checkout `fd9c08dc782a57276de98819d8d4b5f91c9ddf69`).
- Frozen IT SHA-256: `db624a731114f26854bbfe3a59d40827fa8911be46d086b6c558d99e557241ee` — matched.
- Frozen GC SHA-256: `b09570cb6c993bc2d87134d115e60a978650a8a6495483ddbb1f6005a586096f` — matched.
- Artifact: `h85-it-gc-token-ordinal-disagreement-results`, ID **11494991602**.
- Artifact ZIP SHA-256: `054b90c6b4743a6d26ea6f641ce03d7bde83f94c64e24df2a82ba2814e55560d`.

Infrastructure: **PASS**.

## Coverage and sample

- L exact-record single-token mappable: **451** across **49** folios.
- P exact records present in both IT and GC: **4,118**.
- P records nonempty in both: **4,116**.
- P records with exactly equal cleaned known-token counts: **2,128**.
- Ordinal P-token candidates from those equal-count records: **16,488**.

Frozen one-P-record-per-control matching produced:

- matched L–P pairs: **185**;
- represented folios: **30**;
- distinct P records used: **185**;
- unmatched labels with no unused exact control: **266**.

All preregistered sample gates passed.

## Primary result

Symbol identities were removed before comparison; the endpoint is normalized edit distance between first-occurrence equality/repetition patterns.

- mean label disagreement `D_L`: **0.12185328185328186**;
- median `D_L`: **0.0**;
- mean paragraph disagreement `D_P`: **0.20939081939081938**;
- median `D_P`: **0.2**;
- preregistered `Delta = mean(D_L - D_P)`: **-0.08753753753753754**.

Exact equality-pattern agreement between IT and GC:

- labels: **0.5621621621621622**;
- paragraphs: **0.32432432432432434**.

The preregistered nuisance prediction required `Delta > 0`; the observed value is negative.

## Frozen null

- paired sign-flip permutations: **9,999 / 9,999**;
- seed: `20261019`;
- null mean Delta: `0.00008380160195341713`;
- null SD: `0.01765256329051515`;
- preregistered upper-tail p: **1.0**.

Scientific gates:

- `Delta > 0`: **FAIL**;
- `p_upper <= 0.05`: **FAIL**;
- permutation completion: **PASS**.

H85: **FAIL**.

## Frozen diagnostics

Encoded-length stability also ran opposite to the nuisance prediction:

- labels with equal IT/GC token length: **0.6486486486486487**;
- paragraphs with equal IT/GC token length: **0.35135135135135137**;
- mean absolute IT↔GC length difference, labels: **0.4594594594594595**;
- paragraphs: **1.1567567567567567**.

The preregistered equal-source-length sensitivity retained **48 pairs across 19 folios**:

- label mean D: **0.026041666666666668**;
- paragraph mean D: **0.03402777777777778**;
- descriptive Delta: **-0.007986111111111112**.

This sensitivity is descriptive only and is not a second inferential route.

## Conservative interpretation

H85 directly weakens the specific explanation that the established strict label-vs-paragraph token-form distinction is merely caused by label loci being harder or more ambiguous to transcribe. Under exact-record alignment, same-folio/same-IT-length matching, one-control-per-P-record anti-pseudoreplication, and symbol-renaming-invariant comparison, labels were not more structurally unstable than paragraph tokens.

The observed reverse direction — greater IT↔GC structural agreement for labels — was **not preregistered as the alternative** and therefore is not promoted to a PASS here. It is a new descriptive observation requiring an independently frozen replication before interpretation.

This result does not establish semantics, plaintext, a language, or a cipher solution.

Semantic identification: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

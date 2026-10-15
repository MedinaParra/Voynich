# H68 — Visual-subtype documentary-confound identifiability audit result

Status: **PASS**.

This records execution of the preregistered data-geometry protocol in `78_h68_visual_subtype_identifiability_preregistration.md`. It is not a semantic test.

## Execution evidence

- Workflow: `H68 visual-subtype identifiability`.
- Run: `37613848918` (run number 1).
- Job: `112767340382` (`h68-visual-subtype-identifiability`).
- Experimental branch head executed: `c167e1a9ee17af5126f5b0452f6db581a9e3cd7f` (PR merge checkout `97a98347e9551a49d1fe122e9a2a43ced8cc20e9`).
- Frozen source Git blob SHA-1: `4201d762a4bd6e9014e0e796d72dd5c3efb597da`.
- Frozen source SHA-256: `db624a731114f26854bbfe3a59d40827fa8911be46d086b6c558d99e557241ee`.
- Artifact: `h68-visual-subtype-identifiability-results`, ID `11478681796`.
- Artifact SHA256: `0253cca542e52f421792fc0a93cc8d71a4eacc9b3e776d460055362f8c473b51`.

## Frozen-class inventory

The six H67 classes contained **475** known tokens in this audit:

- `Lc`: 40 tokens / 12 folios;
- `Lf`: 216 / 15;
- `Ln`: 64 / 8;
- `Lt`: 50 / 10;
- `Ls`: 68 / 4;
- `Lz`: 37 / 12.

## Documentary segregation

Currier metadata:
- Currier A: `Lc` 40, `Lf` 216;
- Currier B: `Ln` 64, `Lt` 50;
- unknown Currier: `Ls` 68, `Lz` 37.

Hand metadata:
- hand 1: `Lc` 40, `Lf` 216;
- hand 2: `Ln` 64, `Lt` 50;
- hand 4: `Ls` 68, `Lz` 37.

Quire metadata:
- I: `Ls` 68;
- J/K/L: `Lz` 9/22/6;
- M: `Ln` 64, `Lt` 50;
- O: `Lc` 19, `Lf` 78;
- S: `Lc` 21, `Lf` 138.

Thus `Ls` and `Lz` are completely non-exchangeable under the frozen exact documentary strata and must not be admitted to a confound-controlled subtype classifier on this source.

## Exact exchangeable strata

Three exact `(Q,L,H)` strata met the frozen >=5 tokens/class rule:

- `M|B|2`: `Ln` 64, `Lt` 50; **114** retained tokens;
- `O|A|1`: `Lc` 19, `Lf` 78; **97** retained tokens;
- `S|A|1`: `Lc` 21, `Lf` 138; **159** retained tokens.

Collectively:
- exchangeable strata: **3**;
- exchangeable tokens: **370**;
- exchangeable folios: **26**.

Confound-eligible classes under the frozen thresholds:
- `Lc`: 40 exchangeable tokens / 12 exchangeable folios;
- `Lf`: 216 / 15;
- `Ln`: 64 / 8;
- `Lt`: 50 / 10.

Count: **4** confound-eligible classes. The preregistered minimum was 3 classes, 60 exchangeable tokens, 8 folios and 2 strata.

H68: **PASS**.

## Conservative interpretation

A new documentary-confound-controlled subtype experiment is feasible, but only for the two frozen contrasts `Lc` vs `Lf` within A/hand-1 quires O/S and `Ln` vs `Lt` within B/hand-2 quire M. `Ls` and `Lz` cannot be interpreted independently of their documentary placement in this source.

This does not support semantics and does not alter the historical `Lc`-vs-`Lf` FAIL. It only identifies where a new properly controlled test is statistically admissible.

Semantic identification: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

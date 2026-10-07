# H81 — f68r1 star-label global paragraph-rarity result

Status: **BLOCKED**.

This records the completed execution of the preregistered protocol in `104_h81_star_label_paragraph_rarity_preregistration.md`.

The workflow completed successfully and produced a valid artifact. The family-level result is BLOCKED because the Takahashi arm failed a frozen matched-control sufficiency gate. The Zandbergen–Landini (ZL) arm was fully valid and returned a scientific FAIL in the direction opposite the preregistered rarity prediction.

H81 does not identify semantics, proper names, language, plaintext, translation, or decipherment.

## Execution evidence

- Branch: `experiment/h58-strict-l-vs-p`.
- Workflow: `H81 star-label paragraph rarity`.
- Run: `37642222263` (run number 2), conclusion `success`.
- Job: `112863898631` (`h81-star-label-paragraph-rarity`), conclusion `success`.
- Experimental head: `6867cd222aa721eadb7c03a82753ed1fc19a4b09`.
- PR merge checkout: `86e01db7ff1db5a155e328778ab4f7711421e9c3`.
- Artifact: `h81-star-label-paragraph-rarity-results`, ID `11492607525`.
- Artifact SHA256: `fe2d06bb3314175ac54b9401738eb0158e18596cde9861874f76a98b84d7115c`.
- Artifact size: 1,696 bytes.

Infrastructure: **PASS**.

## Frozen source integrity

Both frozen source blobs matched their preregistered Git blob SHA-1 values:

- ZL `voynich_eva.txt`: `2a4533ab9bdfa85db9bad602d590978953055df1` — PASS.
- Takahashi `IT2a-n.txt`: `7f491b574b65e5fba6b553e57372c3fa50e10fec` — PASS.

For both sources, f68r1 metadata resolved to `Q=I`, `Currier L=?`, `H=4`.

## Zandbergen–Landini arm

### Sample and controls

- frozen targets: 27;
- source-admitted targets: **25/27**;
- represented exact-length strata: **5**;
- unique documentary-matched label controls: **39**;
- all exact-length control-count gates: PASS;
- permutations: **9,999/9,999**.

Admitted target counts by exact length:

- length 4: 4;
- length 5: 4;
- length 6: 6;
- length 7: 6;
- length 8: 5.

### Primary statistic

- observed mean `log(1 + P_count)`: **1.1693449786959247**;
- matched-null mean: **1.07240187812025**;
- matched-null SD: **0.16314764022426176**;
- observed minus null mean: **+0.09694310057567468**;
- lower-tail Monte Carlo p: **0.7189**;
- Bonferroni alpha: **0.025**.

Frozen prediction: target star labels should be *rarer* in paragraph text, requiring `T_obs < null_mean` and `p <= 0.025`.

Observed direction was the opposite: `T_obs > null_mean`.

ZL arm: **FAIL**.

Descriptive target recurrence:

- median `P_count`: **1**;
- mean `P_count`: **7.12**;
- zero-paragraph-count fraction: **0.36**.

Therefore the f68r1 star-associated label inventory is not unusually paragraph-rare relative to exact-length, same-documentary-context label controls in the valid ZL arm.

## Takahashi IT2a arm

### Target admission

- source-admitted targets: **27/27**;
- represented exact-length strata: **5**;
- unique matched controls overall: **38**.

Target/control counts by exact length:

| Length | Targets | Controls | Gate |
|---:|---:|---:|---|
| 4 | 4 | 3 | **FAIL** |
| 5 | 4 | 8 | PASS |
| 6 | 8 | 11 | PASS |
| 7 | 6 | 7 | PASS |
| 8 | 5 | 9 | PASS |

The frozen protocol required, for every represented target length, `control_count >= target_count`. Length 4 has only 3 eligible controls for 4 targets.

No fallback to looser metadata matching, target removal, replacement sampling, or mixed-length controls was permitted after seeing the output.

Takahashi arm: **BLOCKED**.

No confirmatory Takahashi p-value is reported because the exchangeability/control-sufficiency gate failed before the matched-set null was admissible.

## Frozen family decision

H81 required both transcription arms to be valid and independently pass the rarity criterion.

- ZL: **FAIL**.
- Takahashi: **BLOCKED**.

H81 overall: **BLOCKED**.

The valid ZL arm additionally provides direct negative evidence against the preregistered panel-specific paragraph-rarity prediction.

## Conservative interpretation

H79 remains a strong spatial A0 association between the 29 f68r1 stars and the 29 stellar-label positions.

H80 showed no preregistered local topology→character-form similarity after exact-length control.

H81 now shows that a valid exact-length/documentary-matched rarity test in ZL also fails: the star-associated forms are not unusually absent or rare in running paragraph text. This weakens the narrow model that f68r1 star labels behave like a special inventory of panel-local/proper-name-like forms defined by paragraph rarity.

The result does not reject proper names generally, because proper names may recur in prose and the label inventory can mix names, categories, descriptors, and other functions. It specifically rejects the frozen rarity prediction in the valid ZL arm.

Do not loosen the Takahashi length-4 gate post hoc to manufacture a second arm.

Infrastructure: **PASS**.
H79 geometric star↔label pairing (A0): **PASS**.
H80 local star-topology label morphology: **FAIL**.
H81 star-label paragraph rarity: **BLOCKED** (ZL scientific arm = **FAIL**; Takahashi = **BLOCKED**).
Semantic identification A1+: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

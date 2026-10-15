# H113 — Confirmatory lexical-anchor evidence synthesis: result

## Status

- Infrastructure/evidence retrieval: **PASS**
- H113 confirmatory lexical-anchor synthesis: **FAIL**
- Semantics: **NOT_RUN**
- Language identification: **NOT_RUN**
- Translation: **NOT_RUN**
- Decipherment: **NOT_RUN**

## Frozen decision rule

Per `163_h113_confirmatory_lexical_anchor_synthesis_preregister.md`, a candidate can PASS only if every applicable confirmatory stage passes and no later preregistered FAIL directly falsifies its claimed generalization. Any direct confirmatory FAIL makes that candidate FAIL. Missing required evidence is NOT_RUN; retrieval failure is BLOCKED.

## Evidence matrix

| Evidence item | Frozen status | Consequence for H113 |
|---|---|---|
| H90 f68r1 geometry lexical anchor | **FAIL** | Candidate does not survive its primary preregistered criterion. |
| H92 independent geometry lexical-anchor replication | **FAIL** | Independent geometry replication does not confirm the label/object anchor. |
| H95 visual-cluster lexical coherence | **FAIL** | Visual-cluster lexical coherence is not confirmed. |
| H98 cross-transcription lexical-anchor closure | **BLOCKED** | Independent transcription closure could not be evaluated; this is neither positive nor negative lexical evidence. |
| H105 Rosettes spatial lexical anchor | **PASS** | Initial within-dataset association exists and enters the confirmatory chain. |
| H106 Rosettes feature ablation | **FAIL** | Direct confirmatory failure; H105 candidate cannot remain PASS under H113. |
| H107 Rosettes joint incremental value | **FAIL** | No confirmed incremental value beyond components. |
| H108 Rosettes paragraph-order confound | **FAIL** | Spatial interpretation does not survive the preregistered order control. |
| H109 Rosettes paragraph-identity confound | **FAIL** | Spatial interpretation does not survive paragraph-identity control. |
| H110 Rosettes leave-one-paragraph-out replication | **FAIL** | The H105 association does not generalize under held-out paragraph evaluation. |
| H111 visual-box → L* bridge admissibility | **FAIL** | No admissible exact bridge to L* classes. |
| H112 independent held-out source admissibility | **FAIL** | Source-admissibility gate fails; held-out lexical replication is **NOT_RUN**. |
| label-object familywise screen | **FAIL** | No eligible annotation-code contrast survives the frozen familywise criterion. |

## Key frozen numeric evidence

- H90: n=29; primary length MAE=1.1582621731 vs null median=1.4285492926, p=0.0187; frozen status **FAIL**.
- H92: 153 pairs / 9 folios; primary MAE=1.33461 vs null median=1.31657, p=0.897; **FAIL**.
- H105: 482 tokens / 23 paragraphs; MAE=1.59502 vs null median=1.67593, p=0.0049; **PASS**.
- H106: orientation p=0.0238 and position p=0.0128 under the frozen ablation criteria; **FAIL**.
- H107: incremental p=0.7132 vs orientation and p=0.7161 vs position; **FAIL**.
- H108: geometry-over-order p=0.4876; **FAIL**.
- H109: paragraph-identity control p=0.4423; **FAIL**.
- H110: geometry LOPO MAE=1.8178423 vs global baseline=1.6035817; p=0.8109; **FAIL**.
- H111: F_exact=0, N_exact=0, common_folio_page_count=0; **FAIL**.
- H112: workflow run `38575708202`, job `115892113494`, artifact `11899318303`; source-admissibility **FAIL**, lexical replication **NOT_RUN**.
- Familywise label-object screen: only Lc vs Lf eligible; aggregate balanced accuracy=0.4571428571; familywise Monte Carlo p=0.756 over 999 permutations; **FAIL**.

## H113 decision

**FAIL.** No candidate in the frozen H113 evidence set survives every applicable confirmatory stage. The one positive initial Rosettes signal (H105) is directly falsified as a confirmatory/generalizable lexical anchor by subsequent preregistered controls H106–H111. H98 is BLOCKED and H112's lexical stage is NOT_RUN, so neither may be counted as negative lexical evidence; neither can rescue a candidate as PASS.

## Scientific interpretation

The frozen program does not currently support a confirmatory visual/label → lexical anchor strong enough to justify semantic testing. This does **not** show that the Voynich manuscript lacks linguistic structure, meaning, or visually associated text. It rejects the tested anchor routes under their preregistered controls. No semantic gloss, language identity, plaintext, translation, or decipherment is inferred.

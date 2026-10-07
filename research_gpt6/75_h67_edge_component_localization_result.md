# H67 — Exact-consensus edge-component localization result

Status: **PASS_Q_LOCALIZED**.

Frozen preregistration: `74_h67_edge_component_localization_preregistration.md`.

## Execution evidence
- GitHub Actions run: `37615527055`
- job: `112772806072` (`edge-component-localization-h67`), conclusion `success`
- workflow head SHA tested: `477c62e90bdf971cca7ceac92f997f96307b1920`
- PR merge checkout: `f712779f5508c079091f45d6762bf931b5caa955`
- artifact: `edge-component-localization-h67-results`, ID `11479204758`
- artifact SHA-256: `56d79888ae6a77b4066002bb2029c231ad30d36241094c5840eab82ba237cc16`
- primary IVTFF blob: `2a4533ab9bdfa85db9bad602d590978953055df1`
- independent Takahashi blob: `7f491b574b65e5fba6b553e57372c3fa50e10fec`

## Frozen support
- primary pages: 227
- independent pages: 225
- common loci: 5,213
- exact-consensus loci: 2,283
- metadata disagreements: 0
- consensus positive loci: 482
- excluded without exact-length same-folio match: 231
- evaluable matched pairs: 246
- evaluable quires: H, I, M, O, S
- 999/999 permutations completed for each component
- familywise alpha: 0.01; component alpha: 0.005

## H67-Q — `starts_q`
- status: **POSITIVE**
- balanced accuracy: `0.5772357723577236`
- null mean BA: `0.5000854513049631`
- null max BA: `0.5528455284552846`
- Monte Carlo p: **`0.001`**
- quires above chance: **4/5**
- H: `0.36363636363636365`
- I: `0.5363636363636364`
- M: `0.6474358974358975`
- O: `0.6551724137931034`
- S: `0.5342465753424658`

All preregistered H67-Q gates pass.

## H67-Y — `ends_y`
- status: **NEGATIVE**
- balanced accuracy: `0.4735772357723577`
- null mean BA: `0.5007934764032314`
- null max BA: `0.5833333333333333`
- Monte Carlo p: `0.798`
- quires above chance: **0/5**
- 999/999 permutations completed

H67-Y fails the preregistered component gate.

## Frozen decision
Q is positive and Y is not. H67 therefore classifies **PASS_Q_LOCALIZED** exactly as preregistered.

## Conservative interpretation
Under the strict exact-consensus subset, the H66 edge-only label-vs-running-text distinction localizes to q-initial behavior. The y-final indicator does not independently carry the confirmatory effect. This is a functional-register / orthographic-position result. It is not lexical semantics.

Because H67 is an adaptive localization on the same exact-consensus sample used by H66, the next justified test is a direct, simpler q-initial replication constructed independently inside each frozen transcription, with paired same-folio exact-length controls and no classifier tuning.

Semantic gloss: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

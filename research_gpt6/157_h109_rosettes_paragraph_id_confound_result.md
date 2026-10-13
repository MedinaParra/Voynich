# H109 — Rosettes paragraph-identity confound test — result

Status: **FAIL**

## Execution evidence

- GitHub Actions run: `38375018060`
- Job: `115221106270`
- Infrastructure: **PASS**
- Executing PR merge SHA: `b372813fd5703dcfc78a51d35ac4eb561c028347`
- Experimental branch source HEAD: `44ca61d38891379d7c2bb0e817cb47214633a088`
- Artifact: `11801086243` (`h109-rosettes-paragraph-id-confound`)
- Artifact size: 697 bytes
- Artifact ZIP SHA-256: `66000884a3f11c0840f2465adc57fa504a758d9571ed3d8125c05768754fd904`
- Frozen source SHA-256: `ff7b779e9ff2468ca04c0e07d0bd9999110d554a962faad1d78fc99c5e7e712d`

## Frozen cohort / gate

- Rows: 482
- Paragraphs: 23
- H105 replay: **PASS**
- COMBINED MAE: `1.5950207468879667`

## Preregistered H109 test

- PARAGRAPH MAE: `1.5565408541914865`
- COMBINED+PARAGRAPH MAE: `1.5950207468879667`
- Observed `D = MAE(PARAGRAPH) - MAE(COMBINED+PARAGRAPH)`: `-0.03847989269648022`
- Null median: `-0.04096951925249703`
- Permutations: 9,999
- Seed: `20261019`
- One-sided p: `0.4423`
- Preregistered alpha: `0.005`

The preregistered PASS condition is not met: `D` is not positive and `p` is not below `0.005`. Therefore **H109 = FAIL**.

## Conservative interpretation

Paragraph identity alone predicts token length better than the frozen H105 COMBINED geometry model in this cohort, and adding COMBINED geometry to the paragraph predictor does not improve the preregistered loss. Under H109's permutation test there is no evidence that geometry contributes incremental predictive value beyond paragraph identity.

This substantially weakens a token-level geometry→lexical-length interpretation of H105. It does not prove that paragraph identity causally explains H105 and does not erase the numerical H105 association; the positive H105 result simply does not survive this stronger prospective confound test as independent geometric information.

Given H106 = FAIL, H107 = FAIL, H108 = FAIL, and H109 = FAIL, further post-hoc subdivision of this same Rosettes effect should not be used to manufacture a positive lexical anchor. A new label-object test should require a new independently auditable visual→token bridge or an independent held-out spatial dataset.

Semantics: **NOT_RUN**  
Language: **NOT_RUN**  
Translation: **NOT_RUN**  
Decipherment: **NOT_RUN**

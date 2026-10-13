# H110 — Rosettes leave-one-paragraph-out geometry→length replication — result

Status: **FAIL**

This file records the preregistered H110 result without changing the frozen analysis or its stopping rule.

## Execution evidence

- GitHub Actions run: `38402423539`
- Job: `115313161723`
- Workflow conclusion / infrastructure: **PASS** (`success`)
- Executing PR merge commit: `9b33631c0e785cede2ac76461c42bfb09e6e65e0`
- Experimental branch head tested by the PR merge: `48b2316aa6ac4fc3948394f735a068e2778c5797`
- Frozen source SHA-256: `ff7b779e9ff2468ca04c0e07d0bd9999110d554a962faad1d78fc99c5e7e712d`
- Artifact ID: `11816068302`
- Artifact size: `760` bytes
- Artifact ZIP SHA-256: `34c0683849f9e5777f9d7d89c439c793455fd72cdeb1129ad65099e7a580144d`

## Frozen cohort and controls

- Rows/tokens: `482` — **PASS**
- Paragraphs: `23` — **PASS**
- Required columns present — **PASS**
- Source SHA-256 identity — **PASS**
- Finite outputs — **PASS**
- 9,999 permutations — **PASS**
- H105 replay — **PASS**, MAE `1.5950207468879667`
- Seed: `20261020`
- alpha: `0.005`

## Preregistered result

- `MAE geometry LOPO = 1.8178423236514525`
- `MAE global LOPO = 1.6035816795841797`
- `D = -0.21426064406727274`
- null median `D = -0.1777461212456959`
- `p = 0.8109`

Therefore H110 is **FAIL** under the preregistered criterion.

## Scientific interpretation

The frozen Rosettes geometry does not generalize token length to completely held-out paragraphs under H110. In this test the geometry predictor is worse than the training-only global baseline. This does not prove that geometry has no relation to the manuscript, but it fails the specific prospective claim that the H105 geometry→length association generalizes across paragraphs.

The preregistered stopping rule is now active: do **not** continue subdividing or tuning H105 on these same 482 tokens. A subsequent lexical-anchor test must require either (a) a genuinely held-out spatial dataset not used to develop H105–H110, or (b) an independently specified visual→token bridge.

## Interpretation ceiling

- Semantics: **NOT_RUN**
- Language: **NOT_RUN**
- Translation: **NOT_RUN**
- Decipherment: **NOT_RUN**

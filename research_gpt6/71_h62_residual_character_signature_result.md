# H62 — Residual character signature — result

Status: **BLOCKED** under the preregistered quire-stability gate.

## Execution
- Branch: `experiment/h62-residual-character-signature`
- Preregistration commit: `cdfde3554b155f394383093f0c4be30009b6aed6`
- Implementation commit: `6267773a135454d174881502505135491632452c`
- Workflow commit: `36623063759dc4f60c8fb782a20c4ab55c6fdfc3`
- GitHub Actions run: `37615483784`
- Job: `112772668566`
- Artifact ID: `11478979685`
- Artifact ZIP SHA-256: `56d2beb6c8555376bf2b71e5870038d1dc65d597131d784cbbee9941a1c53fd7`

## Sample recreation
H60 was recreated exactly:
- positives: 780
- matched pairs: 495
- represented folios: 34
- unmatched positives: 285

After the frozen H61 length>=5 filter:
- retained pairs: 382
- represented folios: 33
- excluded short pairs: 113

## Quire gate
The preregistration required at least 8 quires with >=5 retained pairs.

Observed retained-pair counts by quire:
- A: 1
- H: 7
- I: 63
- M: 79
- N: 68
- O: 61
- S: 103

Only **6** quires met the >=5-pair criterion: H, I, M, N, O, S.

Because 6 < 8, the script stopped before any character-level inferential permutation test. Therefore:

**H62 = BLOCKED**.

- familywise permutations completed: 0/999
- character-level p-values: NOT_RUN
- significant characters: NOT_RUN

The frozen threshold is not lowered after observing the quire counts.

## Interpretation
This is a design/sample-support limitation, not evidence against a residual character signature. H62 cannot make a confirmatory statement about cross-quire stable individual character biases using the preregistered gate.

Language identification: **NOT_RUN**.
Semantic identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

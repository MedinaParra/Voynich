# H60 — Functional-role transfer result

Status: **PASS_FUNCTIONAL_TRANSFER**.

## Execution evidence
- Branch: `experiment/lexical-anchor-replication`
- Preregistration: `research_gpt6/61_functional_role_transfer_preregistration.md`
- Implementation commit: `a06f795c04661da0153e05256bc31d8fd8503fcd`
- Workflow head: `de88f629ae6dafcad537b390f8f7107840d1a8f1`
- GitHub Actions run: `37610210027` (run 80)
- Job: `112755381115` (`functional-role-transfer-h60`), conclusion `success`
- Artifact: `functional-role-transfer-h60-results`, ID `11478145429`
- Artifact SHA256: `bb14e4798bec775b309468d4b45d376baffadd77f4b898b7165db330bedf6858`
- Frozen source blob: `2a4533ab9bdfa85db9bad602d590978953055df1`
- Seed: `20261007`
- Permutations: `999/999`

## Frozen sample
- Matched pairs before quire eligibility: `766`
- Excluded for no local exact-length match: `14`
- Evaluable pairs: `764`
- Evaluable quires: `9` (`H, I, J, K, L, M, N, O, S`)

Pair counts by quire:
- H: 22
- I: 91
- J: 33
- K: 154
- L: 59
- M: 98
- N: 101
- O: 71
- S: 135

## Result
- Aggregate balanced accuracy: **0.6583769633507853**
- Null mean BA: **0.4997897111771447**
- Null maximum BA: **0.550392670157068**
- Monte Carlo p: **0.001**
- Held-out quires above chance: **9/9**

Per-quire BA:
- H: `0.5681818181818181`
- I: `0.6043956043956045`
- J: `0.6363636363636364`
- K: `0.6363636363636364`
- L: `0.5677966101694916`
- M: `0.7857142857142857`
- N: `0.5396039603960396`
- O: `0.7535211267605634`
- S: `0.7259259259259259`

## Frozen decision
All preregistered gates pass:
1. >=4 evaluable quires: **PASS (9)**
2. >=80 evaluable pairs: **PASS (764)**
3. 999/999 permutations: **PASS**
4. aggregate BA >0.60: **PASS (0.6584)**
5. p <=0.01: **PASS (0.001)**
6. >=3 held-out quires above 0.5: **PASS (9/9)**

Therefore H60 is **PASS_FUNCTIONAL_TRANSFER**.

## Conservative interpretation
The previously frozen label/object-locus versus running-text token-form distinction transfers across manuscript quires under exact token-length matching and local folio/Currier/hand controls. Because every evaluable held-out quire is above chance and the aggregate statistic exceeds the full 999-permutation null, the effect is not confined to a single manuscript region.

This materially strengthens a **functional-register** interpretation: tokens used at annotated label/object loci have reproducibly different form statistics from locally matched running text.

It does **not** identify the meaning of a label, prove that labels name depicted objects, rescue the failed Lc/Lf semantic-anchor route, identify language/plaintext/cipher, or constitute translation.

Semantic identity: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

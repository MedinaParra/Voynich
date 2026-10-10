# Familywise label-object / lexical-anchor screen result

Status: **FAIL**.

## Frozen execution evidence
- Branch: `experiment/lexical-anchor-replication`
- Workflow run: `37595431643` (`Voynich frozen experiments`, run 67), conclusion `success`
- Job: `112706783085` (`label-object-familywise`), conclusion `success`
- Artifact: `11469887780` (`label-object-familywise-results`)
- Artifact SHA256: `61449255391033eba12955d39f68be8e156c496e7767c6a591b837a9c5634cbb`
- Source blob: `2a4533ab9bdfa85db9bad602d590978953055df1`
- Permutations: 999/999

## Eligibility
Observed annotation-code counts under the frozen A|1 extraction were:
- `L`: 1
- `Lc`: 36
- `Lf`: 177
- `Lp`: 1

Therefore only `Lc` and `Lf` met the preregistered >=20-token eligibility threshold. The complete familywise screen consequently contained one evaluable pair: `Lc` vs `Lf`.

## Result
For `Lc` vs `Lf`:
- aggregate balanced accuracy: **0.45714285714285713**
- quire O: 18 matched examples/class, BA **0.4166666666666667**
- quire S: 17 matched examples/class, BA **0.5**
- familywise Monte Carlo p: **0.756**
- status: **FAIL**

Experiment-level status: **FAIL**.

The null max-statistic mean was `0.008774982367475502` above chance. No screened annotation-code contrast passed the frozen familywise criterion.

## Interpretation
This valid execution does not support a length-controlled lexical distinction among the annotation codes that had enough A|1 data to be tested. It independently leaves the historical `Lc/Lf` route at FAIL rather than rescuing it.

The result is also informative about coverage: the frozen A|1 corpus contains too few `L` and `Lp` examples to evaluate them under the preregistered threshold. That is a sample limitation, not evidence that those code classes are equivalent.

This does **not** show that Voynich labels as a broader locus category lack distinctive statistics; it only rejects the tested between-code lexical-anchor screen under the frozen extraction, controls and sample requirements.

Semantic identity: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

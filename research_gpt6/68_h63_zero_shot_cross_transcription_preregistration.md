# H63 — Zero-shot cross-transcription label-form transfer preregistration

Status: **NOT_RUN**.

## Motivation
H60 and H61 established a strict L* label-locus vs P* paragraph-text token-form distinction in the frozen Zandbergen-Landini transcription. H62 replicated that distinction by fitting and evaluating the same model family inside independently frozen Takahashi IT2a-n.

H63 is a harder falsification: **fit no model parameters on Takahashi**. Learn the frozen five-feature class geometry from Zandbergen-Landini only, then predict L-vs-P identities in Takahashi zero-shot. This tests whether the direction of the label-form distinction transfers across transcription traditions rather than merely reappearing after refitting within each transcription.

This is not a semantic or translation test.

## Frozen sources
Discovery/training source:
- Zandbergen-Landini frozen corpus Git blob: `2a4533ab9bdfa85db9bad602d590978953055df1`.
- public source commit already used by H60/H61: `cesarjz/Voynich@47e6a77dc9d5cd570c375f4aff710fa4a0567278`, path `corpus/voynich_eva.txt`.

Replication/test source:
- Takahashi IT2a-n Git blob: `7f491b574b65e5fba6b553e57372c3fa50e10fec`.
- `oklo/voynich_gpt@2d7c61c387ad6962de730caf73c48612bc8f6957`, path `IT2a-n.txt`.

No other transcription or manual recoding may be introduced.

## Frozen extraction and matching
Independently in each transcription, use the H60/H62 rules:
- positive: certain single-token generic `L` locus;
- control pool: generic `P` loci only;
- C*, R*, L* excluded from controls;
- same cleaning policy;
- match same folio, exact token length, and Currier/hand metadata when available;
- deterministic control selection with seed `20261007`.

The Takahashi replication set must contain >=60 matched pairs across >=8 folios, otherwise **BLOCKED**.

## Frozen predictors
Exactly:
1. fraction `o`;
2. fraction `a`;
3. fraction `y`;
4. starts `q`;
5. ends `y`.

No absolute length, folio, hand, Currier state, section, locus subtype, token identity, illustration class, semantic hypothesis, or replication-derived predictor may enter the model.

## Zero-shot evaluation
For every Takahashi test folio `f`:
1. build the Zandbergen-Landini discovery matched-pair set using frozen rules;
2. exclude every discovery pair from folio `f`;
3. fit standardization parameters on the remaining ZL training tokens only;
4. fit the same nearest-class-mean classifier used by H60 on those standardized ZL tokens only;
5. transform and classify every Takahashi matched pair from folio `f` using those frozen training parameters.

No Takahashi token may contribute to standardization, class means, hyperparameter selection, or model choice.

Primary statistic: aggregate balanced accuracy over all eligible Takahashi test pairs.

## Null
Exactly **999** deterministic within-pair identity swaps on the Takahashi test pairs with seed `20261007`.

The ZL-trained models and their predictions remain fixed under the null; only which member of each Takahashi pair is designated L versus P is randomized. This prevents refitting on the replication transcription.

Monte Carlo p = `(1 + count(null_BA >= observed_BA))/1000`.

## Negative control
Descriptive only: replace each Takahashi L item with an independently selected matched P-only token and test P-vs-P with the same ZL-trained predictions where possible. Not part of PASS.

## Decision
H63 is **PASS** iff:
1. Takahashi replication set has >=60 pairs;
2. >=8 Takahashi folios are represented;
3. 999/999 null permutations complete;
4. zero-shot observed balanced accuracy > 0.5;
5. Monte Carlo p <= 0.05.

H63 is **FAIL** if execution is valid but either inferential threshold is missed.

H63 is **BLOCKED** if either immutable source fails verification, the frozen extraction cannot be applied without protocol change, or the replication sample threshold is not met.

Before execution: **NOT_RUN**.

## Interpretation boundary
PASS would show that a label-vs-paragraph token-form classifier learned solely from the frozen ZL transcription transfers above chance to the independently frozen Takahashi transcription without fitting on Takahashi. This would materially weaken a transcription-specific refitting explanation.

Because both transcriptions describe the same manuscript and use EVA-family representations and inherited locus conventions, PASS would still not establish independent semantics or rule out every shared-encoding/annotation mechanism.

The failed Lc-vs-Lf subtype/semantic-anchor tests remain **FAIL** regardless of H63.

Semantic identification: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

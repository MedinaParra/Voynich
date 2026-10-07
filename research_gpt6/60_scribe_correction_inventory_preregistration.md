# H59 — Blind scribe-correction prediction preregistration

Status: **NOT_RUN / DATA_AUDIT_REQUIRED**.

## Motivation
The manuscript has a small published set of probable scribal emendations. Unlike lexical crib hunting, a correction is a manuscript-internal production event: an initial mark/form was apparently changed by the producer. H59 asks whether the final state is statistically preferred by manuscript-internal structure without assigning meaning to any glyph or token.

## Frozen candidate inventory
Before any predictive scoring, audit only the externally reported candidate folios:
`f16r, f20v, f24v, f39r, f42r, f50v, f79r, f80r, f83r, f102v2, f112r`.
The duplicate/second candidate reported on f39r must receive a distinct candidate ID if visually confirmed.

Primary image authority: Yale/Beinecke MS 408 high-resolution digital images. Secondary discovery/reference source may be used only to locate a candidate, never to decide its transcription.

## Blind visual audit
Each candidate must be frozen before statistical scoring with:
- candidate ID and folio;
- exact image crop coordinates or stable image reference;
- correction mechanism: stroke-addition, overwrite, erasure/scrape, insertion, deletion, other;
- visible final form;
- recoverable pre-correction form, if defensible;
- confidence: HIGH / MEDIUM / AMBIGUOUS;
- explicit reason for the reconstruction.

No invisible stroke may be invented. If the pre-correction state cannot be reconstructed from the image with HIGH confidence, that candidate is excluded from the primary prediction test but retained in the audit table.

## Primary test set
Only HIGH-confidence cases with a defensible `before -> after` reconstruction enter inference. Require at least 6 independent corrections; otherwise H59 is **BLOCKED** for confirmatory inference and may proceed only descriptively.

## Candidate alternatives
For each included event, generate only physically plausible local alternatives requiring no more pen operations than the observed correction. The alternative generator must be frozen before scoring and must not use corpus frequency, language hypotheses, plaintext hypotheses, or the observed statistical score to select alternatives.

## Predictive views
Score `before`, observed `after`, and all frozen alternatives using manuscript-internal models trained with the test folio excluded.

View A — local form grammar:
- character n-gram likelihood;
- token-initial/final compatibility;
- token-form morphology already used in frozen Voynich experiments.

View B — contextual grammar:
- compatibility with preceding/following tokens;
- line-position-conditioned statistics;
- no illustration labels, proposed semantics, translations, or external language models.

All model fitting is leave-one-folio-out. The correction itself and its folio may not contribute to training statistics for its prediction.

## Primary statistics
For each correction and each view:
1. `delta = score(after) - score(before)`;
2. rank of observed `after` among all physically plausible alternatives.

Aggregate statistic is mean normalized rank advantage of the observed correction over alternatives. Direction is preregistered: corrected forms should rank better than chance.

## Null
Exactly 999 deterministic randomizations, seed `20261007`. Within each correction event, randomly designate one frozen physically plausible candidate as the pseudo-observed correction, preserving each event's alternative-set size. Recompute the aggregate statistic. Monte Carlo p-value is `(1 + count(null >= observed))/(1000)`.

## Decision
Scientific **PASS** requires all of:
1. >=6 HIGH-confidence independent correction events;
2. complete blind inventory frozen before scoring;
3. 999/999 null randomizations;
4. observed aggregate rank advantage > 0;
5. p <= 0.05 in at least one predictive view;
6. the other view must have the same positive direction (it need not independently reach p <= 0.05).

**FAIL**: valid test with thresholds satisfied but inferential criterion missed.

**BLOCKED**: fewer than 6 defensible events, unavailable authoritative imagery, inability to reconstruct before-state, or inability to define alternatives without post-hoc statistical selection.

## Negative controls
After the primary test only:
- matched uncorrected tokens from the same folio/line-position regime;
- pseudo-corrections with identical operation counts;
- stratification by proposed scribal hand and Currier regime is exploratory only.

## Interpretation boundary
PASS would show that visible scribal corrections preferentially move forms toward independently learned manuscript-internal constraints. It would be evidence for a reproducible production grammar/error model. It would **not** identify a language, plaintext, cipher, semantics, author, or translation.

FAIL would show that this small visible correction set does not provide predictive evidence under the frozen model; it would not imply meaningless text.

Language identification: **NOT_RUN**.
Semantic identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

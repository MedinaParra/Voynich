# H78 — Major-prefix jackknife robustness — Result

Status: **PASS**

- Actions run: `37649307488`
- Job: `112888143619`
- Artifact: `h78-prefix-jackknife-results`
- Artifact ID: `11495976953`
- Artifact ZIP SHA256: `6e7c3c5526a1e977f6905bc67ae3ad3f7a412812a77bd2641cfe67eb55886324`
- aligned exact-prefix events: 122
- represented folios: 27
- major prefixes: `ch`, `ok`, `ol`, `ot`
- 999/999 randomizations per source

## Source A leave-one-prefix-out residuals at t[4]
- omit `ch`: `+0.1130751964`
- omit `ok`: `+0.1118656806`
- omit `ol`: `+0.0732737427`
- omit `ot`: `+0.1299823232`
- worst-case residual: `+0.0732737427`
- worst-case p: `0.032`

## Source B
- omit `ch`: `+0.1057613169`
- omit `ok`: `+0.1115956189`
- omit `ol`: `+0.0656752712`
- omit `ot`: `+0.1216767677`
- worst-case residual: `+0.0656752712`
- worst-case p: `0.033`

## Interpretation
The H72 fifth-character EVA-`a` residual remains positive and significant under a preregistered worst-case jackknife removing each major two-character prefix family in turn. The signal therefore cannot be attributed to any single major prefix among `ch`, `ok`, `ol`, or `ot`.

This remains a token-form result only. Language identification, semantics, translation, and decipherment are **NOT_RUN**.

# H64 — Replicated five-feature decomposition result

Scientific status: **PASS**.

Run: `37634192692`  
Job: `112835953048`  
Artifact: `11487956344` (`h64-five-feature-decomposition-results`)  
Artifact ZIP SHA-256: `78b6b59aec338e6a2b8dd89189afc042835d7e52e08adaadb0db04ab7dc9ec0d`

Both frozen samples reconstructed exactly as preregistered:
- Source A: 780 positive candidates, 495 matched pairs, 34 folios, 285 unmatched.
- Source B: 669 positive candidates, 388 matched pairs, 32 folios, 281 unmatched.
- 999/999 familywise max-stat randomizations completed for each source.

## Replicated components

| Feature | Source A mean L-P | A p_FWER | Source B mean L-P | B p_FWER | Replicated? |
|---|---:|---:|---:|---:|---|
| `frac_o` | +0.0405429 | 0.001 | +0.0496156 | 0.001 | YES |
| `frac_a` | +0.0505396 | 0.001 | +0.0367126 | 0.001 | YES |
| `frac_y` | +0.0068646 | 0.796 | +0.0184144 | 0.084 | NO |
| `starts_q` | -0.1454545 | 0.001 | -0.1829897 | 0.001 | YES |
| `ends_y` | -0.0101010 | 0.999 | +0.0335052 | 0.807 | NO |

Thus the preregistered replicated components are:
- higher within-token fraction of EVA `o` in labels;
- higher within-token fraction of EVA `a` in labels;
- substantially lower probability that a label begins with EVA `q`.

`frac_y` and `ends_y` do not survive the dual-source familywise replication criterion.

## Interpretation boundary
This result identifies reproducible token-form components of the strict L-vs-P distinction. It does not establish whether they are linguistic, orthographic, scribal, positional, generative, or semantic. It does not identify the manuscript language, plaintext, cipher, translation, or decipherment.

Language identification: **NOT_RUN**  
Semantic identification: **NOT_RUN**  
Translation: **NOT_RUN**  
Decipherment: **NOT_RUN**

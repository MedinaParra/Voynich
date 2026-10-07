# H70 — q-initial depletion against line-initial running text result

Status: **FAIL**.

Frozen preregistration: `80_h70_q_initial_line_initial_control_preregistration.md`.

## Execution evidence
- Branch: `experiment/lexical-anchor-replication`
- Experimental head tested: `866f82772042bc6610d8a0e75eb1889f47526fc5`
- PR merge checkout: `c4e6bf042139d2fa190871754f9450ae32b112c0`
- GitHub Actions run: `37657393387`
- Job: `112915863920` (`q-line-initial-h70`), conclusion `success`
- Artifact: `q-line-initial-h70-results`, ID `11500101242`
- Artifact SHA-256: `8debe4729305ba533c2092b1e7981bf9580cf2f1e64a3086b04fd567980f2da5`
- Primary IVTFF blob: `2a4533ab9bdfa85db9bad602d590978953055df1`
- Independent Takahashi blob: `7f491b574b65e5fba6b553e57372c3fa50e10fec`

## Primary IVTFF
- included exact strata: **135**
- included labels: **500**
- included line-initial running tokens: **464**
- evaluable quires: **9**
- observed conditional `D`: **`-0.04063861693861694`**
- negative quires: **4/9**
- raw label q prevalence: `0.0200`
- raw line-initial q prevalence: `0.1681034483`
- two-sided Monte Carlo p: **0.001**
- permutations: **999/999**
- transcription status under frozen gate: **NEGATIVE**

Per-quire D: H `+0.0709273`, I `-0.0075295`, J `0`, K `0`, L `0`, M `-0.1477082`, N `+0.0019841`, O `-0.0600962`, S `-0.0470747`.

## Independent Takahashi
- included exact strata: **126**
- included labels: **406**
- included line-initial running tokens: **468**
- evaluable quires: **8**
- observed conditional `D`: **`-0.04497095114364708`**
- negative quires: **4/8**
- raw label q prevalence: `0.0246305419`
- raw line-initial q prevalence: `0.1730769231`
- two-sided Monte Carlo p: **0.001**
- permutations: **999/999**
- transcription status under frozen gate: **NEGATIVE**

Per-quire D: H `+0.0966667`, I `-0.0115220`, J `0`, K `0`, L `+0.0089286`, M `-0.1470085`, O `-0.0556603`, S `-0.0443223`.

## Frozen decision
H70 required `D <= -0.05` in **both** transcriptions in addition to p <= 0.01 and support gates. Both observed effects are statistically non-null under the conditional permutation test but fall short of the preregistered magnitude gate. Therefore H70 is **FAIL**. The threshold is not relaxed post hoc.

## Conservative interpretation
The q-initial label depletion seen in H68/H69 attenuates substantially when labels are compared only with line-initial running tokens. This is evidence that running-line position explains a meaningful portion of the earlier q contrast. A residual negative contrast remains in both transcriptions (`D≈-0.041` to `-0.045`, p=.001), but under the frozen H70 criterion it is not strong enough to claim the preregistered positional-confound rejection.

Thus H69 remains a valid exact-stratum result for arbitrary running text, while H70 limits its interpretation: q-initial behavior is partly entangled with line-position grammar. This is more consistent with a structural/orthographic role than with any demonstrated lexical meaning.

No semantic rescue is permitted from the sub-threshold residual.

Semantic gloss: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.

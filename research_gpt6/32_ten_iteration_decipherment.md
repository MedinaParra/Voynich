# 32. Ten-iteration holistic decipherment pass
Date: 2026-10-06

Rule: no gloss is promoted without held-out evidence. PASS means an inference supported by the cited corpus/format evidence; HYPOTHESIS is a next falsifiable target.

## Iteration 1 — Separate communicative channels
IVTFF explicitly distinguishes paragraph text P, labels L, circular text C, and radial text R. Treating them as one corpus is therefore rejected. Result: PASS methodological correction.

## Iteration 2 — Use label subtype as weak supervision
IVTFF subtypes encode visual relation: Lp plant, Lc pharmaceutical container, Lf pharmaceutical herb fragment, Ln nymph, Lt tube/tub, Ls star, Lz zodiac, La astro/cosmological. These are not semantic translations but externally defined object classes. Result: PASS weak-label design.

## Iteration 3 — Test the naming hypothesis
If labels are object names, label distributions should differ by object class and recur with repeated object identity. Existing descriptive statistics show labels are unusually flat; this is compatible with naming but not sufficient. Result: naming = HYPOTHESIS, not conclusion.

## Iteration 4 — Reject naive frequency translation
High-frequency running-text words are scarce among labels; therefore mapping the most frequent Voynich words directly to common nouns is methodologically weak. Result: PASS rejection of naive frequency glossing.

## Iteration 5 — Identify morphological label register
Published label statistics report strong initial ok/ot enrichment and low initial qo relative to running text. Treat ok-/ot- as candidate register/morphological markers, not meanings. Result: PASS register signal; lexical meaning UNKNOWN.

## Iteration 6 — Cross-domain overlap as discriminator
Zodiac and pharmaceutical labels share only a small subset of word types despite similar label-like frequency shape. A universal 'name prefix' process is plausible; domain-specific lexical cores remain possible. Test shared prefixes separately from residual stems. Result: HYPOTHESIS.

## Iteration 7 — Internal Rosetta test
For pages where a herbal plant is explicitly cross-referenced to a pharmaceutical fragment, compare Lp/Lf label families and running-text contexts. A repeated label family associated with the same depicted plant across independent folios is a candidate semantic anchor. Result: protocol PASS; systematic execution NOT_RUN.

## Iteration 8 — Position-sensitive morphology
For every label token decompose prefix/core/suffix under several blind segmentations. Ask whether object class is predicted primarily by prefix, core, or suffix under leave-one-quire-out. This distinguishes grammatical/register morphology from lexical identity. Result: HYPOTHESIS prepared.

## Iteration 9 — Adversarial semantic test
Permute labels among objects within the same section/Currier/hand and compare real object-class prediction to null. Preserve length and initial-glyph distribution in a stricter null. Semantic-anchor promotion requires real pairing to beat >=95% nulls, preferably >=99%. Result: protocol PASS; execution NOT_RUN.

## Iteration 10 — Decipherment decision gate
Current evidence supports multiple structured textual registers and non-random relation to manuscript layout, but does not identify a natural language, cipher key, or stable lexicon. Therefore the strongest defensible target is semantic recovery by object-linked labels, not whole-text substitution. First A3 lexical candidate requires: repeated independent object association + morphological stability + held-out prediction + historical comparator support. Result: NO SOLUTION YET; search space substantially narrowed.

## Consolidated inference
The most promising attack is no longer generic character-frequency decipherment. It is a weakly supervised multimodal problem in which IVTFF label subtypes supply object classes. The next executable model should predict {Lp,Lc,Lf,Ln,Lt,Ls,Lz,La} from label morphology with grouped holdout, then use repeated-object correspondences to isolate lexical cores. Only after that should candidate historical languages/ciphers be scored.

## Stop conditions
Reject any proposed translation that cannot predict unseen labels/pages. Reject any mapping explained by Currier, hand, quire, label length, or prefix frequency alone. Do not call a prefix a word meaning. Do not call visual resemblance an identification.

# 100-iteration adversarial research matrix

Status: DESIGN_FROZEN. This file does not claim that 100 computational runs have completed. It freezes 100 distinct falsification/validation iterations to execute against the Voynich semantic-anchor hypothesis.

Primary claim under test: text/labels contain reproducible information about external visual referents beyond section, Currier, hand, quire, length and transcription artifacts.

Decision levels: STRUCTURAL -> FUNCTIONAL -> SEMANTIC_CLASS -> LEXICAL_ANCHOR -> TRANSLATION. No level may be skipped.

## Iterations 001-020: representation
001 EVA whole-token baseline
002 character unigram
003 character bigram
004 character trigram
005 character 4-gram
006 first glyph only
007 first 2 glyphs
008 first 3 glyphs
009 last glyph only
010 last 2 glyphs
011 last 3 glyphs
012 token length only negative control
013 glyph inventory only negative control
014 prefix/core/suffix deterministic split
015 train-only MDL segmentation
016 train-only BPE segmentation
017 remove ot/ok prefix families
018 mask first glyph
019 mask final glyph
020 reverse glyph order control

## Iterations 021-040: visual/label channels
021 paragraph text only
022 L labels only
023 C circular text only
024 R radial text only
025 L+C
026 L+R
027 C+R
028 L+C+R
029 labels vs paragraph discrimination
030 plant labels Lp
031 pharma fragment labels Lf
032 container labels Lc
033 human/nymph labels Ln
034 tube/bath labels Lt
035 star labels Ls
036 zodiac labels Lz
037 astro/cosmo labels La
038 herbal-to-pharma transfer
039 pharma-to-herbal transfer
040 zodiac-to-astro transfer

## Iterations 041-060: holdout and confounding
041 random-page CV diagnostic only
042 leave-one-folio-out
043 leave-one-quire-out primary
044 leave-one-hand-out
045 leave-one-Currier-out
046 leave-one-section-out transfer
047 leave-one-object-class-out transfer
048 matched Currier x hand
049 matched Currier x quire
050 matched hand x quire
051 matched Currier x hand x quire where support exists
052 page-length matched
053 token-count matched
054 label-count matched
055 illustration-density matched
056 manuscript-half temporal/physical split
057 odd/even folio negative diagnostic
058 recto/verso split
059 bifolio holdout
060 physically reconstructed-order holdout

## Iterations 061-080: adversarial nulls
061 global label permutation
062 within-section label permutation
063 within-page label permutation
064 within-quire label permutation
065 within-Currier permutation
066 within-hand permutation
067 within Currier x hand permutation primary
068 length-preserving permutation
069 prefix-family-preserving permutation
070 suffix-family-preserving permutation
071 frequency-bin-preserving permutation
072 first-glyph-preserving permutation
073 last-glyph-preserving permutation
074 shuffle token order within line
075 shuffle token interiors preserving edges
076 reverse token order within line
077 character-bigram Markov surrogate
078 page-density matched surrogate
079 wrong-image pairing hard negative
080 neighboring-page image hard negative

## Iterations 081-100: replication and decisive tests
081 alternate transcription replication
082 strict uncertain-glyph exclusion
083 permissive uncertain-glyph inclusion
084 high-confidence labels only
085 labels with single clear referent only
086 independent discovery/validation folio sets
087 discovery in pharma, blind validation herbal
088 discovery herbal, blind validation pharma
089 discovery zodiac, blind validation astro
090 family-level rather than token-level prediction
091 candidate core enrichment in correct object class
092 candidate core depletion in wrong classes
093 multiple independent anchors requirement
094 permutation p <= .001 gate
095 effect-size gate above majority baseline
096 stability across Currier conditioning on/off
097 stability across hand conditioning on/off
098 stability across quire conditioning on/off
099 preregistered blind prediction table before reveal
100 final lexical-anchor gate: held-out referent prediction + independent transcription replication + adversarial-null survival

## Publication gate
A famous or high-impact paper cannot be guaranteed. Scientific submission is justified if at least one predeclared lexical anchor passes 086-100 without post-hoc relabeling. A negative paper remains publishable if the full matrix strongly bounds semantic recoverability while reproducing known structural signals.

## Anti-hype rule
Never report decipherment from classification accuracy alone. Never assign a natural-language gloss until a candidate predicts unseen material. All failed and null iterations remain in the record.
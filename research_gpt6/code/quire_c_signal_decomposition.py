#!/usr/bin/env python3
"""Diagnostic decomposition of the influential quire C bifolio signal.

No representation is selected after seeing results. A fixed suite is evaluated
on all complete held-out quires A,C,D,E,F,G in both ZL3b and Takahashi IT2a.
Every edge representation is nuisance-residualized by absolute folio-number
distance and exact unordered Davis-hand/Currier-L folio-signature pair category,
then the physical matching is ranked among all 105 perfect matchings and the
maximum-weight matching is scored blindly.

Fixed representations:
  1. word_tfidf                  exact token identity
  2. char3_cosine                character morphology
  3. token_jaccard               binary lexical overlap
  4. word_tfidf_no_top20         remove 20 globally most frequent token types
  5. word_tfidf_no_hapax_folios  remove token types occurring in only one heldout folio
  6. shape_tfidf                 map token -> length:first:last
  7. affix_tfidf                 map token -> first2:last2

The top-20 and hapax masks are computed over the full held-out folio collection
without using physical B labels. This is diagnostic, not a new confirmatory
claim and not decipherment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

import singulion_q13_order as base
import all_quires_bifolio_holdout as aq
import bifolio_double_residual_reconstruction as dr

IT2A_SHA256=dr.IT2A_SHA256
QUIRES=dr.QUIRES
REPS=(
 'word_tfidf','char3_cosine','token_jaccard','word_tfidf_no_top20',
 'word_tfidf_no_hapax_folios','shape_tfidf','affix_tfidf'
)


def folio_tokens(pages,n):
    return list(pages[f'f{n}r'])+list(pages[f'f{n}v'])


def heldout_folios():
    return sorted({n for pairs in QUIRES.values() for p in pairs for n in p})


def global_masks(pages):
    folios=heldout_folios(); freq=Counter(); df=Counter()
    for n in folios:
        toks=folio_tokens(pages,n);freq.update(toks);df.update(set(toks))
    top20={w for w,_ in sorted(freq.items(),key=lambda kv:(-kv[1],kv[0]))[:20]}
    hapax_folio={w for w,d in df.items() if d==1}
    return top20,hapax_folio


def transform(tokens,rep,top20,hapax):
    if rep=='word_tfidf': return list(tokens)
    if rep=='word_tfidf_no_top20': return [w for w in tokens if w not in top20]
    if rep=='word_tfidf_no_hapax_folios': return [w for w in tokens if w not in hapax]
    if rep=='shape_tfidf': return [f'{len(w)}:{w[:1]}:{w[-1:]}' for w in tokens if w]
    if rep=='affix_tfidf': return [f'{w[:2]}:{w[-2:]}' for w in tokens if w]
    return list(tokens)


def tfidf_vectors(docs):
    N=len(docs);df=Counter()
    for toks in docs.values():df.update(set(toks))
    idf={w:math.log((1+N)/(1+d))+1.0 for w,d in df.items()}
    return {n:base.tfidf(toks,idf) for n,toks in docs.items()}


def edge_weights(pages,folios,rep,top20,hapax):
    docs={n:transform(folio_tokens(pages,n),rep,top20,hapax) for n in folios}
    if rep=='char3_cosine':
        vec={n:base.char_ngrams(docs[n],3) for n in folios}
        return {(a,b):base.cosine(vec[a],vec[b]) for i,a in enumerate(folios) for b in folios[i+1:]}
    if rep=='token_jaccard':
        return {(a,b):base.jaccard(docs[a],docs[b]) for i,a in enumerate(folios) for b in folios[i+1:]}
    vec=tfidf_vectors(docs)
    return {(a,b):base.cosine(vec[a],vec[b]) for i,a in enumerate(folios) for b in folios[i+1:]}


def rank_physical(residual,folios,true):
    def score(m):return base.mean([residual[(min(a,b),max(a,b))] for a,b in m])
    tv=score(true);vals=[];best=None;bs=None
    for m in aq.perfect_matchings(folios):
        m=aq.canonical_matching(m);s=score(m);vals.append(s)
        if best is None or (s,tuple(m))>(bs,tuple(best)):best=m;bs=s
    greater=sum(x>tv for x in vals);ge=sum(x>=tv for x in vals);le=sum(x<=tv for x in vals)
    return {
      'physical_score':tv,'rank_best_is_1':greater+1,'n_exact_matchings':len(vals),
      'percentile':100*le/len(vals),'exact_upper_tail_p':ge/len(vals),
      'predicted_pairs':[f'{a}|{b}' for a,b in best],
      'blind_recovered_pairs':sum(p in set(true) for p in best),
      'blind_accuracy':sum(p in set(true) for p in best)/len(true),
    }


def run(name,pages,meta):
    top20,hapax=global_masks(pages);out=[]
    for q,pairs in QUIRES.items():
        true=aq.canonical_matching(pairs);folios=sorted({n for p in true for n in p})
        sigs={n:(dr.folio_sig(meta,n,'H'),dr.folio_sig(meta,n,'L')) for n in folios}
        reps={}
        for rep in REPS:
            raw=edge_weights(pages,folios,rep,top20,hapax)
            residual,fit=dr.alternating_residualize(raw,sigs)
            reps[rep]={**rank_physical(residual,folios,true),'residualization':fit}
        out.append({'quire':q,'physical_pairs':[f'{a}|{b}' for a,b in true],'representations':reps})
    c=next(r for r in out if r['quire']=='C')
    c_summary={rep:{'rank':c['representations'][rep]['rank_best_is_1'],'p':c['representations'][rep]['exact_upper_tail_p'],'recovered':c['representations'][rep]['blind_recovered_pairs']} for rep in REPS}
    return {'transcription':name,'global_top20_removed':sorted(top20),'n_hapax_folio_types_removed':len(hapax),'results':out,'quire_C_summary':c_summary}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--zl',type=Path,required=True);ap.add_argument('--it',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    zlb=a.zl.read_bytes();itb=a.it.read_bytes()
    if base.git_blob_sha1(zlb)!=base.SOURCE_BLOB:raise SystemExit('ZL blob mismatch')
    sha=hashlib.sha256(itb).hexdigest()
    if sha!=IT2A_SHA256:raise SystemExit(f'IT2a SHA mismatch {sha}')
    zp,zm,za=base.parse_pages(zlb.decode('utf-8'));ip,_,ia=base.parse_pages(itb.decode('utf-8',errors='replace'))
    result={
      'classification':'QUIRE_C_SIGNAL_DECOMPOSITION_DIAGNOSTIC_NOT_DECIPHERMENT',
      'representations':list(REPS),
      'nuisance_control':'same double residualization by folio distance plus exact Davis-H/Currier-L metadata-pair category for every representation',
      'zl':run('ZL3b',zp,zm),'it2a':run('Takahashi IT2a',ip,zm),
      'interpretation':'A representation surviving in C identifies what information class carries the influential signal; this suite is diagnostic and not used to choose a new predictor.',
      'parser_audit':{'ZL3b':za,'IT2a':ia},
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()

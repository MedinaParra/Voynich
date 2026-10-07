#!/usr/bin/env python3
"""Condition held-out bifolio signal on hand and Currier compatibility.

For each blind held-out complete quire A,C,D,E,F,G, enumerate all perfect
matchings. A candidate matching is admitted to the conditional null only when it
has exactly the same number of same-hand and same-Currier pairs as the physical
matching. Rank the physical matching by distance-centered TF-IDF within that
conditional null.

This tests whether the bifolio effect is merely a consequence of pairing folios
with the same Davis hand or Currier language label.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
from collections import Counter
import singulion_q13_order as base
import all_quires_bifolio_holdout as aq

QUIRES = {
 'A': ((1,8),(2,7),(3,6),(4,5)),
 'C': ((17,24),(18,23),(19,22),(20,21)),
 'D': ((25,32),(26,31),(27,30),(28,29)),
 'E': ((33,40),(34,39),(35,38),(36,37)),
 'F': ((41,48),(42,47),(43,46),(44,45)),
 'G': ((49,56),(50,55),(51,54),(52,53)),
}

def folio_sig(meta,n,key):
    vals=[]
    for s in ('r','v'):
        v=meta.get(f'f{n}{s}',{}).get(key)
        if v is not None: vals.append(v)
    return tuple(sorted(set(vals)))

def compat(pair,sigs):
    a,b=pair
    ha,hb=sigs[a]['H'],sigs[b]['H']; la,lb=sigs[a]['L'],sigs[b]['L']
    return (ha==hb and bool(ha), la==lb and bool(la))

def profile(matching,sigs):
    c=Counter(compat(p,sigs) for p in matching)
    return tuple(sorted((str(k),v) for k,v in c.items()))

def rank(value,vals):
    return {
      'rank_best_is_1':1+sum(x>value for x in vals),
      'n_conditional_matchings':len(vals),
      'percentile':100*sum(x<=value for x in vals)/len(vals),
      'exact_upper_tail_p_including_observed':sum(x>=value for x in vals)/len(vals),
      'null_min':min(vals),'null_mean':base.mean(vals),'null_max':max(vals),
    }

def fisher(ps):
    import math
    x=-2*sum(math.log(max(p,1e-300)) for p in ps); k=len(ps); z=x/2
    sf=math.exp(-z)*sum(z**j/math.factorial(j) for j in range(k))
    return {'k':k,'statistic':x,'df':2*k,'p':sf}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--corpus',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args()
    data=a.corpus.read_bytes()
    if base.git_blob_sha1(data)!=base.SOURCE_BLOB: raise SystemExit('Corpus blob mismatch')
    pages,meta,audit=base.parse_pages(data.decode('utf-8'))
    rows=[]
    for q,pairs in QUIRES.items():
        true=aq.canonical_matching(pairs); folios=sorted({x for p in true for x in p})
        sigs={n:{'H':folio_sig(meta,n,'H'),'L':folio_sig(meta,n,'L')} for n in folios}
        weights=aq.build_tfidf_pair_weights(pages,folios); residual,_=aq.distance_center(weights)
        score=lambda m:base.mean([residual[(min(x,y),max(x,y))] for x,y in m])
        true_prof=profile(true,sigs); tv=score(true); vals=[]; admitted=[]
        for m in aq.perfect_matchings(folios):
            if profile(m,sigs)==true_prof:
                vals.append(score(m)); admitted.append(m)
        rows.append({
          'quire':q,'folio_metadata':{str(n):sigs[n] for n in folios},
          'physical_profile':list(true_prof),'true_adjusted_score':tv,
          'conditional_rank':rank(tv,vals),
          'conditional_fraction_of_all_matchings':len(vals)/105,
        })
    ps=[r['conditional_rank']['exact_upper_tail_p_including_observed'] for r in rows]
    result={
      'classification':'BIFOLIO_HAND_CURRIER_CONDITIONAL_CONTROL_NOT_DECIPHERMENT',
      'source_blob':base.SOURCE_BLOB,
      'conditioning':'exact multiset of pair categories defined by same/different folio-level Davis H signature and same/different Currier L signature',
      'results':rows,'fisher_conditional':fisher(ps),
      'guardrails':['Conditioning controls labeled hand/language compatibility, not all paleographic or topical covariates.','If labels are constant within a quire, the conditional null equals the full null.'],
      'parser_audit':audit,
    }
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result,indent=2))
if __name__=='__main__': main()

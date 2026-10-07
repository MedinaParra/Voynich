#!/usr/bin/env python3
"""Independent-transcription replication on Takahashi IT2a Basic EVA.

No tuning on IT2a. Reuse the exact blind rule selected on ZL/Q13/Q20:
aggregate folio (r+v) TF-IDF, center pair similarity by absolute folio-number
distance within quire, choose maximum-weight perfect matching.

Held-out complete quires are fixed as A,C,D,E,F,G and physical pairs are used
only after prediction for scoring. Source SHA256 is frozen to the independently
reported IT2a-n.txt hash.
"""
from __future__ import annotations
import argparse, hashlib, json
from collections import Counter
from pathlib import Path
import singulion_q13_order as base
import all_quires_bifolio_holdout as aq

EXPECTED_SHA256='7f27a8b0feed8f6de0a99900df6bf912dd1d295c38e5f830bac8b41c3f536fb5'
QUIRES={
 'A':((1,8),(2,7),(3,6),(4,5)),
 'C':((17,24),(18,23),(19,22),(20,21)),
 'D':((25,32),(26,31),(27,30),(28,29)),
 'E':((33,40),(34,39),(35,38),(36,37)),
 'F':((41,48),(42,47),(43,46),(44,45)),
 'G':((49,56),(50,55),(51,54),(52,53)),
}

def overlap(m,true): return sum((min(a,b),max(a,b)) in true for a,b in m)
def conv(a,b):
    o=Counter()
    for x,cx in a.items():
        for y,cy in b.items():o[x+y]+=cx*cy
    return o

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--corpus',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args()
    raw=a.corpus.read_bytes(); sha=hashlib.sha256(raw).hexdigest()
    if sha!=EXPECTED_SHA256: raise SystemExit(f'IT2a SHA256 mismatch: {sha}')
    pages,meta,audit=base.parse_pages(raw.decode('utf-8',errors='replace'))
    rows=[]; distall=Counter({0:1}); obs=0; total=0; expected=0.0
    for q,pairs in QUIRES.items():
        true=aq.canonical_matching(pairs); ts=set(true); folios=sorted({n for p in true for n in p})
        missing=[f'f{n}{s}' for n in folios for s in ('r','v') if not pages.get(f'f{n}{s}')]
        if missing: raise SystemExit(f'IT2a missing clean heldout pages in {q}: {missing}')
        weights=aq.build_tfidf_pair_weights(pages,folios); resid,_=aq.distance_center(weights)
        best=None;bs=None;od=Counter(); nm=0
        for m in aq.perfect_matchings(folios):
            nm+=1; s=base.mean([resid[(min(x,y),max(x,y))] for x,y in m]); ov=overlap(m,ts); od[ov]+=1
            if best is None or (s,tuple(m))>(bs,tuple(best)):best=m;bs=s
        rec=overlap(best,ts); obs+=rec; total+=len(true); expected+=len(true)/(2*len(true)-1); distall=conv(distall,od)
        rows.append({'quire':q,'predicted_pairs':[f'{x}|{y}' for x,y in best],'physical_pairs':[f'{x}|{y}' for x,y in true],'recovered':rec,'total':len(true),'accuracy':rec/len(true),'adjusted_score':bs,'exact_matching_count':nm})
    nnull=sum(distall.values()); ge=sum(c for k,c in distall.items() if k>=obs)
    result={
      'classification':'IT2A_INDEPENDENT_TRANSCRIPTION_BLIND_BIFOLIO_REPLICATION_NOT_DECIPHERMENT',
      'source':'Takahashi IT2a Basic EVA','sha256':sha,
      'prediction_rule':'unchanged maximum perfect matching by within-quire distance-centered aggregate-folio TF-IDF',
      'results':rows,
      'global':{'recovered_pairs':obs,'total_pairs':total,'pair_accuracy':obs/total,'random_expected_recovered_pairs':expected,'exact_joint_null_outcomes':nnull,'exact_p_random_recovers_at_least_observed':ge/nnull,'joint_overlap_distribution':{str(k):v for k,v in sorted(distall.items())}},
      'guardrails':['Independent transcription robustness, not an independent manuscript sample.','Physical pair labels are used only after prediction for scoring.'],
      'parser_audit':audit,
    }
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result,indent=2))
if __name__=='__main__':main()

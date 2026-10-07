#!/usr/bin/env python3
"""Control Quire F nesting scores for Currier language and Davis hand.

Raw boundary-continuity ranking strongly prefers grouping the two Currier-B
bifolia (41|48,43|46) and the two Currier-A bifolia (42|47,44|45), suggesting a
known language/scribe confound. This script freezes the previous boundary model
and removes group means from each directed folio-transition score under:
  (1) ordered Currier-L source/target category;
  (2) ordered exact (Davis-H, Currier-L) source/target category.

Metadata come only from the frozen ZL page headers and are reused as nuisance
labels for IT2a, exactly as in the manuscript-wide metadata control.
No physical bifolio order is used in residualization.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import re
from collections import defaultdict
from pathlib import Path
from statistics import median

import order_quire_c_nesting as base
import order_regular_quires_nesting_scan as scan

PAIRS=((41,48),(42,47),(43,46),(44,45))
FOLIOS=tuple(range(41,49))
CURRENT=tuple(scan.label(p) for p in PAIRS)
WINDOWS=base.WINDOWS


def parse_metadata(raw:str):
    meta={}
    current=None
    for line in raw.splitlines():
        m=re.match(r"^<([^>.,]+)>\s*<!",line)
        if not m: continue
        current=m.group(1)
        vals=dict(re.findall(r"\$([A-Z])=([^\s>]+)",line))
        meta[current]=vals
    return meta


def folio_sig(meta,n,key):
    vals=[]
    for side in ('r','v'):
        v=meta.get(f'f{n}{side}',{}).get(key)
        if v is not None: vals.append(v)
    return tuple(sorted(set(vals)))


def signatures(meta):
    return {n:(folio_sig(meta,n,'H'),folio_sig(meta,n,'L')) for n in FOLIOS}


def residualize(matrix,key_fn):
    groups=defaultdict(list)
    for p,v in matrix.items(): groups[key_fn(p)].append((p,v))
    out={}
    means={}
    for k,rows in groups.items():
        mu=sum(v for _,v in rows)/len(rows)
        means[repr(k)]={'mean':mu,'n_edges':len(rows)}
        for p,v in rows: out[p]=v-mu
    return out,means


def nesting_rows(matrix):
    rows=[]
    labels=tuple(scan.label(p) for p in PAIRS)
    for p in itertools.permutations(labels):
        leaves=scan.leaf_sequence(p)
        s=sum(matrix[(a,b)] for a,b in zip(leaves,leaves[1:]))
        rows.append((s,p,leaves))
    rows.sort(key=lambda x:(-x[0],x[1]))
    return rows


def one(matrix):
    rows=nesting_rows(matrix)
    idx=next(i for i,(_,p,_) in enumerate(rows) if p==CURRENT)
    best=rows[0]; cur=rows[idx]
    return {
        'current_rank':idx+1,
        'current_score':cur[0],
        'current_exact_p_ge':(idx+1)/24.0,
        'best_nesting_outer_to_inner':list(best[1]),
        'best_leaf_reading_order':best[2],
        'best_score':best[0],
    }


def analyse(pages,sigs):
    out=[]
    for w in WINDOWS:
        raw=scan.directed_transition_matrix(pages,FOLIOS,w)
        lang,lang_means=residualize(raw,lambda p:(sigs[p[0]][1],sigs[p[1]][1]))
        exact,exact_means=residualize(raw,lambda p:(sigs[p[0]],sigs[p[1]]))
        out.append({
            'boundary_tokens':'whole_page' if w==0 else w,
            'raw':one(raw),
            'currier_residual':one(lang),
            'hand_currier_residual':one(exact),
            'n_currier_transition_classes':len(lang_means),
            'n_hand_currier_transition_classes':len(exact_means),
        })
    summary={}
    for control in ('raw','currier_residual','hand_currier_residual'):
        ranks=[r[control]['current_rank'] for r in out]
        bests=[tuple(r[control]['best_nesting_outer_to_inner']) for r in out]
        summary[control]={
            'current_ranks':ranks,
            'current_median_rank':median(ranks),
            'current_top1_windows':sum(x==1 for x in ranks),
            'current_top3_windows':sum(x<=3 for x in ranks),
            'best_nestings_by_window':[list(x) for x in bests],
        }
    return {'by_window':out,'summary':summary}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--zl',type=Path,required=True)
    ap.add_argument('--it',type=Path,required=True)
    ap.add_argument('--json',type=Path)
    args=ap.parse_args()
    zlraw=args.zl.read_text(encoding='utf-8',errors='replace')
    itb=args.it.read_bytes(); itsha=hashlib.sha256(itb).hexdigest()
    if itsha!=base.IT2A_SHA256: raise SystemExit(f'IT2a SHA mismatch {itsha}')
    zlpages,_=base.parse_pages(zlraw); itpages,_=base.parse_pages(itb.decode('utf-8',errors='replace'))
    meta=parse_metadata(zlraw); sigs=signatures(meta)
    zl=analyse(zlpages,sigs); it=analyse(itpages,sigs)
    cross={}
    for control in ('raw','currier_residual','hand_currier_residual'):
        ranks=zl['summary'][control]['current_ranks']+it['summary'][control]['current_ranks']
        cross[control]={
            'current_ranks_across_10_tests':ranks,
            'median_rank':median(ranks),
            'top1_tests':sum(x==1 for x in ranks),
            'top3_tests':sum(x<=3 for x in ranks),
            'worst_rank':max(ranks),
        }
    result={
        'status':'QUIRE_F_NESTING_METADATA_CONFOUND_CONTROL',
        'physical_bifolia':[scan.label(p) for p in PAIRS],
        'current_nesting_outer_to_inner':list(CURRENT),
        'folio_metadata_signatures':{str(k):{'H':list(v[0]),'L':list(v[1])} for k,v in sigs.items()},
        'ZL3b':zl,
        'IT2a':it,
        'cross_transcription':cross,
        'interpretation_rule':'A raw alternative is not promoted if its advantage collapses materially after Currier or exact H/L transition-class centering.',
        'guardrails':[
            'Exact metadata class centering can remove genuine sequence signal that is correlated with scribal/language changes; it is a confound control, not a replacement model.',
            'Metadata labels come from ZL headers and are reused for IT2a.',
            'No physical nesting labels enter the residualization.',
            'Windows and text scoring are unchanged from the pre-existing Quire C model.',
            'This tests nesting continuity only, not semantic decoding.'
        ]
    }
    text=json.dumps(result,ensure_ascii=False,indent=2)
    print(text)
    if args.json:
        args.json.parent.mkdir(parents=True,exist_ok=True)
        args.json.write_text(text+'\n',encoding='utf-8')

if __name__=='__main__': main()

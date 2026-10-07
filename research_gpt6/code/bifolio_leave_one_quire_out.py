#!/usr/bin/env python3
"""Leave-one-quire-out robustness audit for blind bifolio reconstruction.

Recomputes two already-frozen predictors on held-out complete quires A,C,D,E,F,G:
1) distance-centered aggregate-folio TF-IDF maximum matching;
2) the stronger double-residual predictor removing additive folio-distance and
   exact Davis-hand/Currier metadata-pair effects before maximum matching.

For both ZL3b and Takahashi IT2a, inference uses the exact metadata-conditioned
physical-architecture null. We convolve per-quire overlap distributions after
omitting each quire in turn. No predictor or threshold is retuned.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

import singulion_q13_order as base
import all_quires_bifolio_holdout as aq
import blind_reconstruction_metadata_conditional as mc
import bifolio_double_residual_reconstruction as dr

IT2A_SHA256 = dr.IT2A_SHA256
QUIRES = dr.QUIRES


def convolve(a,b):
    out=Counter()
    for x,cx in a.items():
        for y,cy in b.items(): out[x+y]+=cx*cy
    return out


def summarize(selected):
    joint=Counter({0:1}); observed=0; expected=0.0
    for row in selected:
        joint=convolve(joint,row['dist'])
        observed+=row['observed']
        expected+=row['expected']
    n=sum(joint.values())
    ge=sum(c for k,c in joint.items() if k>=observed)
    return {
        'quires':[r['quire'] for r in selected],
        'observed_overlap':observed,
        'conditional_expected_overlap':expected,
        'exact_joint_null_outcomes':n,
        'exact_conditional_p_overlap_ge_observed':ge/n,
    }


def frozen_metadata_sigs(meta,folios):
    return {n:(dr.folio_sig(meta,n,'H'),dr.folio_sig(meta,n,'L')) for n in folios}


def original_row(pages,meta,q,pairs):
    true=aq.canonical_matching(pairs); folios=sorted({n for p in true for n in p})
    # Same predictor as blind_reconstruction_metadata_conditional.py.
    pred,_=mc.predict_matching(pages,folios)
    sigs_mc={n:{'H':mc.folio_sig(meta,n,'H'),'L':mc.folio_sig(meta,n,'L')} for n in folios}
    local,_=mc.conditional_distribution(folios,true,sigs_mc,pred)
    dist=Counter({int(k):v for k,v in local['overlap_distribution'].items()})
    return {'quire':q,'observed':local['observed_overlap'],'expected':local['conditional_expected_overlap'],'dist':dist}


def double_row(pages,meta,q,pairs):
    true=aq.canonical_matching(pairs); trueset=set(true); folios=sorted({n for p in true for n in p})
    sigs=frozen_metadata_sigs(meta,folios)
    raw=aq.build_tfidf_pair_weights(pages,folios)
    residual,_=dr.alternating_residualize(raw,sigs)
    pred,_=dr.predict(residual,folios)
    observed=dr.overlap(pred,trueset)
    dist=dr.null_distribution(folios,pred,true,sigs,True)
    n=sum(dist.values()); expected=sum(k*c for k,c in dist.items())/n
    return {'quire':q,'observed':observed,'expected':expected,'dist':dist}


def audit_predictor(rows):
    out={'all':summarize(rows),'leave_one_out':[]}
    for omitted in [r['quire'] for r in rows]:
        selected=[r for r in rows if r['quire']!=omitted]
        s=summarize(selected); s['omitted']=omitted
        out['leave_one_out'].append(s)
    out['all_leave_one_out_p_below_0_05']=all(x['exact_conditional_p_overlap_ge_observed']<0.05 for x in out['leave_one_out'])
    out['max_leave_one_out_p']=max(x['exact_conditional_p_overlap_ge_observed'] for x in out['leave_one_out'])
    out['most_influential_omission']=max(out['leave_one_out'],key=lambda x:x['exact_conditional_p_overlap_ge_observed'])['omitted']
    return out


def run(name,pages,meta):
    original=[]; double=[]
    for q,pairs in QUIRES.items():
        folios=sorted({n for p in pairs for n in p})
        missing=[f'f{n}{s}' for n in folios for s in ('r','v') if not pages.get(f'f{n}{s}')]
        if missing: raise SystemExit(f'{name}: missing heldout pages in {q}: {missing}')
        original.append(original_row(pages,meta,q,pairs))
        double.append(double_row(pages,meta,q,pairs))
    return {'transcription':name,'distance_centered_predictor':audit_predictor(original),'double_residual_predictor':audit_predictor(double)}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--zl',type=Path,required=True);ap.add_argument('--it',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    zlb=args.zl.read_bytes();itb=args.it.read_bytes()
    if base.git_blob_sha1(zlb)!=base.SOURCE_BLOB: raise SystemExit('ZL blob mismatch')
    itsha=hashlib.sha256(itb).hexdigest()
    if itsha!=IT2A_SHA256: raise SystemExit(f'IT2a SHA256 mismatch: {itsha}')
    zl_pages,zl_meta,zla=base.parse_pages(zlb.decode('utf-8'))
    it_pages,_,ita=base.parse_pages(itb.decode('utf-8',errors='replace'))
    result={
      'classification':'BIFOLIO_BLIND_RECONSTRUCTION_LEAVE_ONE_QUIRE_OUT_NOT_DECIPHERMENT',
      'heldout_quires':list(QUIRES),
      'inference':'exact metadata-conditioned overlap null; one whole quire omitted at a time; predictors frozen',
      'zl':run('ZL3b',zl_pages,zl_meta),
      'it2a':run('Takahashi IT2a',it_pages,zl_meta),
      'interpretation_rule':'A reconstruction claim is not leave-one-quire-out robust if omitting any single quire raises the exact conditional p-value to >=0.05.',
      'guardrails':['This is an influence/robustness audit, not a new model-selection loop.','IT2a is an independent transcription of the same manuscript, not an independent manuscript.'],
      'parser_audit':{'ZL3b':zla,'IT2a':ita},
    }
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))

if __name__=='__main__':main()

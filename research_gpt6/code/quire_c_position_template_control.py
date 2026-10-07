#!/usr/bin/env python3
"""Cross-quire positional-template control for influential quire C.

Potential confound: in every 8-folio quire, physical bifolia are mirror pairs
(1,8),(2,7),(3,6),(4,5). A generic textual similarity pattern tied to relative
position in a quire could therefore mimic a bifolio effect even after centering
by |i-j|.

For each fixed representation and transcription, learn the mean similarity for
each unordered pair of relative positions (1..8) from OTHER held-out complete
quires A,D,E,F,G, without using any physical B labels. Subtract that positional
template from every C candidate edge. Then rank C's physical matching among all
105 perfect matchings and perform blind maximum-weight reconstruction.

Two fixed variants are reported:
  - position_template_only
  - position_template_plus_nuisance: additionally residualize by absolute folio
    distance and exact Davis-H/Currier-L metadata pair class, matching the prior
    strongest nuisance control.

Diagnostic only; no representation is selected after seeing outcomes.
"""
from __future__ import annotations
import argparse, hashlib, json
from collections import defaultdict
from pathlib import Path
import singulion_q13_order as base
import all_quires_bifolio_holdout as aq
import bifolio_double_residual_reconstruction as dr
import quire_c_signal_decomposition as dec

IT2A_SHA256=dr.IT2A_SHA256
TRAIN_QUIRES=('A','D','E','F','G')
TARGET='C'
REPS=dec.REPS


def relmap(pairs):
    fs=sorted({n for p in pairs for n in p})
    return fs,{n:i+1 for i,n in enumerate(fs)}


def template_for_rep(pages,rep,top20,hapax):
    vals=defaultdict(list)
    for q in TRAIN_QUIRES:
        pairs=dr.QUIRES[q];folios,pos=relmap(pairs)
        w=dec.edge_weights(pages,folios,rep,top20,hapax)
        for (a,b),v in w.items(): vals[(pos[a],pos[b])].append(v)
    return {k:base.mean(vs) for k,vs in vals.items()}


def rank_and_predict(weights,folios,true):
    def score(m):return base.mean([weights[(min(a,b),max(a,b))] for a,b in m])
    tv=score(true);vals=[];best=None;bs=None
    for m in aq.perfect_matchings(folios):
        m=aq.canonical_matching(m);s=score(m);vals.append(s)
        if best is None or (s,tuple(m))>(bs,tuple(best)):best=m;bs=s
    return {
      'physical_score':tv,'rank_best_is_1':1+sum(x>tv for x in vals),
      'n_exact_matchings':len(vals),'percentile':100*sum(x<=tv for x in vals)/len(vals),
      'exact_upper_tail_p':sum(x>=tv for x in vals)/len(vals),
      'predicted_pairs':[f'{a}|{b}' for a,b in best],
      'blind_recovered_pairs':sum(p in set(true) for p in best),
      'blind_accuracy':sum(p in set(true) for p in best)/len(true),
    }


def run(name,pages,meta):
    top20,hapax=dec.global_masks(pages)
    true=aq.canonical_matching(dr.QUIRES[TARGET]);folios,pos=relmap(dr.QUIRES[TARGET])
    sigs={n:(dr.folio_sig(meta,n,'H'),dr.folio_sig(meta,n,'L')) for n in folios}
    out={}
    for rep in REPS:
        templ=template_for_rep(pages,rep,top20,hapax)
        raw=dec.edge_weights(pages,folios,rep,top20,hapax)
        pr={(a,b):v-templ[(pos[a],pos[b])] for (a,b),v in raw.items()}
        plus,fit=dr.alternating_residualize(pr,sigs)
        out[rep]={
          'position_template_only':rank_and_predict(pr,folios,true),
          'position_template_plus_nuisance':{**rank_and_predict(plus,folios,true),'residualization':fit},
        }
    return {'transcription':name,'training_quires':list(TRAIN_QUIRES),'target_quire':TARGET,'representations':out}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--zl',type=Path,required=True);ap.add_argument('--it',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    zlb=a.zl.read_bytes();itb=a.it.read_bytes()
    if base.git_blob_sha1(zlb)!=base.SOURCE_BLOB:raise SystemExit('ZL blob mismatch')
    sha=hashlib.sha256(itb).hexdigest()
    if sha!=IT2A_SHA256:raise SystemExit(f'IT2a SHA mismatch {sha}')
    zp,zm,za=base.parse_pages(zlb.decode('utf-8'));ip,_,ia=base.parse_pages(itb.decode('utf-8',errors='replace'))
    result={
      'classification':'QUIRE_C_CROSS_QUIRE_POSITION_TEMPLATE_CONTROL_NOT_DECIPHERMENT',
      'hypothesis':'Does C remain reconstructible after subtracting the generic pair-of-relative-positions similarity pattern learned from A,D,E,F,G?',
      'representations':list(REPS),'zl':run('ZL3b',zp,zm),'it2a':run('Takahashi IT2a',ip,zm),
      'guardrails':['Position template is learned without C and without B labels.','Same manuscript and mostly herbal material; this controls generic within-quire position, not every latent production factor.'],
      'parser_audit':{'ZL3b':za,'IT2a':ia},
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()

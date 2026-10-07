#!/usr/bin/env python3
"""Independent image-only validation of the frozen Quire G nesting candidate.

The textual/metadata-controlled adversarial test selected, independently in
ZL3b and IT2a:
    52|53 -> 50|55 -> 51|54 -> 49|56   (outer to inner)

This script was added *after* that candidate was frozen. It consumes only the
external Xenoglyph page-image semantic profiles and ranks all 4! nestings by
visual similarity along the implied leaf reading sequence a1..an,bn..b1.
No Voynich transcription, hand labels, Currier labels, or textual scores are
read here.

This is an external semantic-image negative/positive control, not physical
codicology. Similar-looking plant pages need not be historically adjacent.
"""
from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
import random
from collections import Counter
from pathlib import Path
from statistics import mean, pstdev

LENS_FILES={
    "voynich":"voynich_profiles.json",
    "archaeology":"voynich_archaeology_profiles.json",
    "cryptological":"voynich_cryptological_profiles.json",
}
PAIRS=((49,56),(50,55),(51,54),(52,53))
LABELS=tuple(f"{a}|{b}" for a,b in PAIRS)
CURRENT=LABELS
FROZEN_CANDIDATE=("52|53","50|55","51|54","49|56")


def load_metadata(path):
    with path.open(newline="",encoding="utf-8") as f:
        return {r["image_id"]:r for r in csv.DictReader(f)}


def load_lens(path, metadata):
    profiles=json.loads(path.read_text(encoding="utf-8"))
    first=next(p["archetype_scores"] for p in profiles if p.get("archetype_scores"))
    dims=sorted(first)
    pages={}
    for p in profiles:
        m=metadata.get(p.get("image_id")); scores=p.get("archetype_scores",{})
        if not m or not scores: continue
        try: folio=int(float(m["folio_num"]))
        except (ValueError,TypeError,KeyError): continue
        side=str(m.get("side","")).strip()
        if 49<=folio<=56 and side in ("r","v"):
            pages[(folio,side)]=[float(scores.get(d,0.0)) for d in dims]
    return dims,pages


def mean_vec(rows):
    return [sum(r[j] for r in rows)/len(rows) for j in range(len(rows[0]))]


def folio_vectors(pages):
    out={}
    for f in range(49,57):
        keys=[(f,"r"),(f,"v")]
        if not all(k in pages for k in keys):
            raise RuntimeError(f"missing visual profile face(s) for f{f}")
        out[f]=mean_vec([pages[k] for k in keys])
    return out


def cosine(a,b,idx=None):
    if idx is None: idx=range(len(a))
    aa=sum(a[i]*a[i] for i in idx); bb=sum(b[i]*b[i] for i in idx)
    if aa<=0 or bb<=0: return 0.0
    return sum(a[i]*b[i] for i in idx)/math.sqrt(aa*bb)


def edge_matrix(vecs,idx=None):
    raw={}
    fs=sorted(vecs)
    for i,a in enumerate(fs):
        for b in fs[i+1:]: raw[(a,b)]=cosine(vecs[a],vecs[b],idx)
    vals=list(raw.values()); mu=mean(vals); sd=pstdev(vals) or 1.0
    return {k:(v-mu)/sd for k,v in raw.items()}


def edge(a,b): return tuple(sorted((a,b)))


def parse_label(label): return tuple(int(x) for x in label.split("|"))


def leaf_sequence(nesting):
    pairs=[parse_label(x) for x in nesting]
    return tuple(a for a,_ in pairs)+tuple(b for _,b in reversed(pairs))


def score(nesting,matrix):
    leaves=leaf_sequence(nesting)
    return sum(matrix[edge(a,b)] for a,b in zip(leaves,leaves[1:]))


def rank_all(matrix):
    rows=[]
    for p in itertools.permutations(LABELS):
        rows.append((score(p,matrix),p,leaf_sequence(p)))
    rows.sort(key=lambda x:(-x[0],x[1]))
    return rows


def rank_of(rows,target):
    for i,(s,p,l) in enumerate(rows,1):
        if p==target:
            return {"rank":i,"out_of":len(rows),"score":s,"nesting_outer_to_inner":list(p),"leaf_sequence":list(l),"percentile_higher_is_better":1-(i-1)/(len(rows)-1)}
    raise KeyError(target)


def bootstrap_dims(vecs,reps,seed):
    rng=random.Random(seed); d=len(next(iter(vecs.values())))
    candidate_wins=0; current_wins=0; candidate_ranks=[]; current_ranks=[]; winners=Counter()
    for _ in range(reps):
        idx=[rng.randrange(d) for _ in range(d)]
        rows=rank_all(edge_matrix(vecs,idx))
        winners[rows[0][1]]+=1
        rc=rank_of(rows,FROZEN_CANDIDATE)["rank"]
        rr=rank_of(rows,CURRENT)["rank"]
        candidate_ranks.append(rc); current_ranks.append(rr)
        candidate_wins += rc==1
        current_wins += rr==1
    return {
        "reps":reps,
        "candidate_top1_frequency":candidate_wins/reps,
        "current_top1_frequency":current_wins/reps,
        "candidate_median_rank":sorted(candidate_ranks)[len(candidate_ranks)//2],
        "current_median_rank":sorted(current_ranks)[len(current_ranks)//2],
        "top_nesting_frequencies":[
            {"nesting_outer_to_inner":list(p),"leaf_sequence":list(leaf_sequence(p)),"count":n,"frequency":n/reps}
            for p,n in winners.most_common(10)
        ],
    }


def add_matrices(ms):
    keys=ms[0].keys()
    return {k:sum(m[k] for m in ms)/len(ms) for k in keys}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("profiles_dir",type=Path)
    ap.add_argument("--reps",type=int,default=1000)
    ap.add_argument("--seed",type=int,default=20261007)
    ap.add_argument("--json",type=Path)
    args=ap.parse_args()

    meta=load_metadata(args.profiles_dir/"corpus_metadata.csv")
    lenses={}; matrices={}; dims_out={}
    for i,(lens,fn) in enumerate(LENS_FILES.items()):
        dims,pages=load_lens(args.profiles_dir/fn,meta)
        vecs=folio_vectors(pages)
        m=edge_matrix(vecs); rows=rank_all(m)
        dims_out[lens]=dims; matrices[lens]=m
        lenses[lens]={
            "best":{"score":rows[0][0],"nesting_outer_to_inner":list(rows[0][1]),"leaf_sequence":list(rows[0][2])},
            "frozen_text_candidate":rank_of(rows,FROZEN_CANDIDATE),
            "current_nesting":rank_of(rows,CURRENT),
            "dimension_bootstrap":bootstrap_dims(vecs,args.reps,args.seed+1000*i),
        }

    consensus=add_matrices(list(matrices.values())); rows=rank_all(consensus)
    result={
        "status":"QUIRE_G_EXTERNAL_VISUAL_VALIDATION_FROZEN_CANDIDATE",
        "source":{"dataset":"xenoglyph-ai/voynich-public","profile_generation":"image-only semantic vectors; transcription not consumed"},
        "preregistered_before_loading_profiles":{
            "current_nesting_outer_to_inner":list(CURRENT),
            "frozen_candidate_outer_to_inner":list(FROZEN_CANDIDATE),
            "current_leaf_sequence":list(leaf_sequence(CURRENT)),
            "candidate_leaf_sequence":list(leaf_sequence(FROZEN_CANDIDATE)),
        },
        "lens_dimensions":dims_out,
        "by_lens":lenses,
        "equal_weight_lens_consensus":{
            "construction":"mean of three within-lens z-scored folio-pair cosine matrices; no fitted weights",
            "best":{"score":rows[0][0],"nesting_outer_to_inner":list(rows[0][1]),"leaf_sequence":list(rows[0][2])},
            "frozen_text_candidate":rank_of(rows,FROZEN_CANDIDATE),
            "current_nesting":rank_of(rows,CURRENT),
            "top10":[{"rank":i+1,"score":s,"nesting_outer_to_inner":list(p),"leaf_sequence":list(l)} for i,(s,p,l) in enumerate(rows[:10])],
        },
        "interpretation_guardrails":[
            "This test was defined only after the textual candidate was frozen, preventing visual tuning of that candidate.",
            "Visual semantic similarity is not physical codicology and cannot prove binding history.",
            "Plant illustration similarity may reflect thematic/artistic clustering rather than production adjacency.",
            "All 24 physical nestings preserve the four accepted bifolium pairings and their orientations.",
        ],
    }
    text=json.dumps(result,ensure_ascii=False,indent=2)
    print(text)
    if args.json:
        args.json.parent.mkdir(parents=True,exist_ok=True)
        args.json.write_text(text+"\n",encoding="utf-8")

if __name__=="__main__": main()

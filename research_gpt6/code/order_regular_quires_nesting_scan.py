#!/usr/bin/env python3
"""Fixed-method nesting scan across regular complete Voynich quires.

Calibration/diagnostic extension of order_quire_c_nesting.py. No parameters,
weights or windows are retuned after Quire C. The same frozen model is applied
to all complete regular four-bifolium quires available in the metadata holdout:
A, C, D, E, F and G.

For each quire, all 4! = 24 outer->inner bifolium nestings are enumerated while
holding each bifolium's internal leaf orientation fixed. Candidate reading leaf
order is a1..an,bn..b1. Seven transitions verso(prev)->recto(next) are scored.

This is a calibration scan. It does not assume that a low-ranked current order
proves historical rebinding, and it does not decode Voynichese.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from collections import Counter
from pathlib import Path
from statistics import median

import order_quire_c_nesting as base

IT2A_SHA256 = base.IT2A_SHA256
WINDOWS = base.WINDOWS

QUIRES = {
    "A_f1-f8": ((1,8),(2,7),(3,6),(4,5)),
    "C_f17-f24": ((17,24),(18,23),(19,22),(20,21)),
    "D_f25-f32": ((25,32),(26,31),(27,30),(28,29)),
    "E_f33-f40": ((33,40),(34,39),(35,38),(36,37)),
    "F_f41-f48": ((41,48),(42,47),(43,46),(44,45)),
    "G_f49-f56": ((49,56),(50,55),(51,54),(52,53)),
}


def label(pair):
    return f"{pair[0]}|{pair[1]}"


def parse_label(s):
    a,b=s.split("|")
    return int(a),int(b)


def leaf_sequence(nesting_labels):
    pairs=[parse_label(x) for x in nesting_labels]
    return [a for a,_ in pairs]+[b for _,b in reversed(pairs)]


def directed_transition_matrix(pages, folios, window):
    tails={}; heads={}
    for f in folios:
        tails[f]=base.window_tokens(pages[f"f{f}v"],"tail",window)
        heads[f]=base.window_tokens(pages[f"f{f}r"],"head",window)
    tok_docs={f"T{f}":base.token_counter(tails[f]) for f in folios}
    tok_docs.update({f"H{f}":base.token_counter(heads[f]) for f in folios})
    chr_docs={f"T{f}":base.char_counter(tails[f]) for f in folios}
    chr_docs.update({f"H{f}":base.char_counter(heads[f]) for f in folios})
    tok_vec=base.tfidf(tok_docs); chr_vec=base.tfidf(chr_docs)
    comps={"token_tfidf":{},"char35_tfidf":{},"token_jaccard":{}}
    for a in folios:
        for b in folios:
            if a==b: continue
            p=(a,b)
            comps["token_tfidf"][p]=base.cosine(tok_vec[f"T{a}"],tok_vec[f"H{b}"])
            comps["char35_tfidf"][p]=base.cosine(chr_vec[f"T{a}"],chr_vec[f"H{b}"])
            comps["token_jaccard"][p]=base.jaccard(tails[a],heads[b])
    z={k:base.znorm(v) for k,v in comps.items()}
    return {p:sum(z[k][p] for k in z)/len(z) for p in z["token_tfidf"]}


def enumerate_nestings(pair_labels, matrix):
    rows=[]
    for p in itertools.permutations(pair_labels):
        leaves=leaf_sequence(p)
        score=sum(matrix[(a,b)] for a,b in zip(leaves,leaves[1:]))
        rows.append((score,p,leaves))
    rows.sort(key=lambda x:(-x[0],x[1]))
    return rows


def analyse_one(pages, pairs):
    folios=sorted({x for p in pairs for x in p})
    pair_labels=tuple(label(p) for p in pairs)
    wanted=[f"f{f}{s}" for f in folios for s in ("r","v")]
    missing=[x for x in wanted if not pages.get(x)]
    if missing:
        raise RuntimeError(f"missing {missing}")
    out=[]
    ranks=[]
    for w in WINDOWS:
        m=directed_transition_matrix(pages,folios,w)
        rows=enumerate_nestings(pair_labels,m)
        current_index=next(i for i,(_,p,_) in enumerate(rows) if p==pair_labels)
        cs,cp,cl=rows[current_index]
        bs,bp,bl=rows[0]
        rank=current_index+1
        ranks.append(rank)
        out.append({
            "boundary_tokens":"whole_page" if w==0 else w,
            "current_rank":rank,
            "current_exact_p_ge":rank/24.0,
            "current_score":cs,
            "best_nesting_outer_to_inner":list(bp),
            "best_leaf_reading_order":bl,
            "best_score":bs,
            "current_is_best":rank==1,
        })
    return {
        "current_nesting_outer_to_inner":list(pair_labels),
        "current_leaf_reading_order":leaf_sequence(pair_labels),
        "by_window":out,
        "current_top1_windows":sum(r==1 for r in ranks),
        "current_top3_windows":sum(r<=3 for r in ranks),
        "current_median_rank":median(ranks),
        "current_worst_rank":max(ranks),
        "current_ranks":ranks,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--zl",type=Path,required=True)
    ap.add_argument("--it",type=Path,required=True)
    ap.add_argument("--json",type=Path)
    args=ap.parse_args()

    zl_pages,zl_audit=base.parse_pages(args.zl.read_text(encoding="utf-8",errors="replace"))
    it_bytes=args.it.read_bytes(); it_sha=hashlib.sha256(it_bytes).hexdigest()
    if it_sha!=IT2A_SHA256:
        raise SystemExit(f"IT2a SHA256 mismatch: {it_sha}")
    it_pages,it_audit=base.parse_pages(it_bytes.decode("utf-8",errors="replace"))

    results={}
    all_ranks=[]; top1=top3=0
    for q,pairs in QUIRES.items():
        z=analyse_one(zl_pages,pairs)
        t=analyse_one(it_pages,pairs)
        ranks=z["current_ranks"]+t["current_ranks"]
        row={
            "known_physical_bifolia":[label(p) for p in pairs],
            "ZL3b":z,
            "IT2a":t,
            "cross_transcription":{
                "current_top1_tests_out_of_10":sum(r==1 for r in ranks),
                "current_top3_tests_out_of_10":sum(r<=3 for r in ranks),
                "current_median_rank_out_of_24":median(ranks),
                "current_worst_rank_out_of_24":max(ranks),
                "all_current_ranks":ranks,
            },
        }
        results[q]=row
        all_ranks.extend(ranks)
        top1+=sum(r==1 for r in ranks); top3+=sum(r<=3 for r in ranks)

    by_test=[]
    for corpus_name in ("ZL3b","IT2a"):
        for wi,w in enumerate(WINDOWS):
            rs=[results[q][corpus_name]["current_ranks"][wi] for q in QUIRES]
            by_test.append({
                "corpus":corpus_name,
                "boundary_tokens":"whole_page" if w==0 else w,
                "current_ranks_across_6_quires":rs,
                "median_current_rank":median(rs),
                "current_top1_count":sum(r==1 for r in rs),
                "current_top3_count":sum(r<=3 for r in rs),
            })

    result={
        "status":"REGULAR_QUIRE_NESTING_CALIBRATION_SCAN_NOT_DECIPHERMENT",
        "method_frozen_from":"Quire C nesting reconstruction",
        "quires":results,
        "global_calibration":{
            "n_quires":len(QUIRES),
            "n_tests":len(all_ranks),
            "current_top1_tests":top1,
            "current_top3_tests":top3,
            "median_current_rank_out_of_24":median(all_ranks),
            "by_corpus_window":by_test,
        },
        "parser_audit":{"ZL3b":zl_audit,"IT2a":it_audit},
        "guardrails":[
            "The scoring method and windows are copied unchanged from the Quire C experiment.",
            "These are current known physical bifolia; this scan tests nesting/read-continuity compatibility, not physical pairing discovery.",
            "A low current rank is a flag for review, not proof of rebinding.",
            "Bifolium internal orientation remains fixed.",
            "The 10 tests per quire are highly correlated and must not be treated as 10 independent p-values.",
            "ZL3b and IT2a are independent transcriptions of one manuscript, not independent manuscripts."
        ],
    }
    text=json.dumps(result,ensure_ascii=False,indent=2)
    print(text)
    if args.json:
        args.json.parent.mkdir(parents=True,exist_ok=True)
        args.json.write_text(text+"\n",encoding="utf-8")

if __name__=="__main__": main()

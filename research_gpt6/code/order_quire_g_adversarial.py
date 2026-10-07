#!/usr/bin/env python3
"""Adversarial nesting test for Quire G (f49--f56).

Quire G was flagged only after a manuscript-wide calibration scan and remains
INCONCLUSIVE after ordered Davis-hand/Currier residualization.  This script does
not assume rebinding.  It asks a narrower question: is there a single alternative
nesting that replicates across two transcriptions, boundary scales, and simple
feature ablations after the metadata control is frozen?

Design:
- known physical bifolia fixed: 49|56, 50|55, 51|54, 52|53;
- enumerate all 4! = 24 outer->inner nestings;
- fixed reading model a1..an,bn..b1 and v(previous)->r(next);
- metadata nuisance classes are parsed from frozen ZL3b headers and reused for
  IT2a, exactly as in order_regular_quires_metadata_control.py;
- candidate is selected independently in ZL3b and IT2a by a frozen consensus
  rule: lowest median rank across 5 windows, then lowest sum rank, then lowest
  worst rank, then lexical order;
- feature ablations remove one of token-TFIDF, char-3/5-TFIDF, Jaccard at a time;
- no parameter is fitted to make the current or an alternative order win.

This is a diagnostic of ordering compatibility, not decipherment and not proof
of historical rebinding.
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
import order_regular_quires_nesting_scan as scan
import order_regular_quires_metadata_control as meta_ctl

PAIRS = ((49,56),(50,55),(51,54),(52,53))
LABELS = tuple(scan.label(p) for p in PAIRS)
FOLIOS = tuple(range(49,57))
WINDOWS = base.WINDOWS
IT2A_SHA256 = base.IT2A_SHA256
COMPONENTS = ("token_tfidf","char35_tfidf","token_jaccard")
ABLATIONS = {
    "all": COMPONENTS,
    "no_token_tfidf": ("char35_tfidf","token_jaccard"),
    "no_char35_tfidf": ("token_tfidf","token_jaccard"),
    "no_token_jaccard": ("token_tfidf","char35_tfidf"),
}


def component_matrices(pages, window):
    tails={}; heads={}
    for f in FOLIOS:
        tails[f]=base.window_tokens(pages[f"f{f}v"],"tail",window)
        heads[f]=base.window_tokens(pages[f"f{f}r"],"head",window)
    tok_docs={f"T{f}":base.token_counter(tails[f]) for f in FOLIOS}
    tok_docs.update({f"H{f}":base.token_counter(heads[f]) for f in FOLIOS})
    chr_docs={f"T{f}":base.char_counter(tails[f]) for f in FOLIOS}
    chr_docs.update({f"H{f}":base.char_counter(heads[f]) for f in FOLIOS})
    tok_vec=base.tfidf(tok_docs); chr_vec=base.tfidf(chr_docs)
    raw={k:{} for k in COMPONENTS}
    for a in FOLIOS:
        for b in FOLIOS:
            if a==b: continue
            p=(a,b)
            raw["token_tfidf"][p]=base.cosine(tok_vec[f"T{a}"],tok_vec[f"H{b}"])
            raw["char35_tfidf"][p]=base.cosine(chr_vec[f"T{a}"],chr_vec[f"H{b}"])
            raw["token_jaccard"][p]=base.jaccard(tails[a],heads[b])
    return {k:base.znorm(v) for k,v in raw.items()}


def combine(zcomps, keep):
    return {p:sum(zcomps[k][p] for k in keep)/len(keep) for p in zcomps[keep[0]]}


def enumerate_orders(matrix):
    rows=[]
    for nesting in itertools.permutations(LABELS):
        leaves=scan.leaf_sequence(nesting)
        score=sum(matrix[(a,b)] for a,b in zip(leaves,leaves[1:]))
        rows.append((score,nesting,leaves))
    rows.sort(key=lambda x:(-x[0],x[1]))
    return rows


def rank_map(rows):
    return {p:i+1 for i,(_,p,_) in enumerate(rows)}


def consensus_from_rank_vectors(rank_vectors):
    rows=[]
    for nesting, ranks in rank_vectors.items():
        rows.append({
            "nesting_outer_to_inner":list(nesting),
            "ranks":ranks,
            "median_rank":median(ranks),
            "sum_rank":sum(ranks),
            "worst_rank":max(ranks),
            "top1_windows":sum(r==1 for r in ranks),
            "top3_windows":sum(r<=3 for r in ranks),
        })
    rows.sort(key=lambda r:(r["median_rank"],r["sum_rank"],r["worst_rank"],r["nesting_outer_to_inner"]))
    return rows


def analyse_transcription(pages, sigs):
    by_ablation={}
    for abl,keep in ABLATIONS.items():
        vectors={p:[] for p in itertools.permutations(LABELS)}
        windows=[]
        for w in WINDOWS:
            z=component_matrices(pages,w)
            combined=combine(z,keep)
            residual,_=meta_ctl.residualize(combined,lambda p:(sigs[p[0]],sigs[p[1]]))
            rows=enumerate_orders(residual)
            ranks=rank_map(rows)
            for p in vectors: vectors[p].append(ranks[p])
            cur=next((s,p,l) for s,p,l in rows if p==LABELS)
            windows.append({
                "boundary_tokens":"whole_page" if w==0 else w,
                "best": {"nesting_outer_to_inner":list(rows[0][1]),"score":rows[0][0]},
                "current": {"rank":ranks[LABELS],"score":cur[0]},
            })
        consensus=consensus_from_rank_vectors(vectors)
        by_ablation[abl]={"consensus_top10":consensus[:10],"current":next(r for r in consensus if tuple(r["nesting_outer_to_inner"])==LABELS),"by_window":windows}
    return by_ablation


def candidate_rank_in(result, candidate, ablation="all"):
    row=next(r for r in result[ablation]["consensus_top10"] if tuple(r["nesting_outer_to_inner"])==candidate) if any(tuple(r["nesting_outer_to_inner"])==candidate for r in result[ablation]["consensus_top10"]) else None
    if row: return row
    # top10 may omit candidate; reconstruct from window rankings unavailable directly,
    # so report null rather than fabricate a rank.
    return None


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--zl",type=Path,required=True)
    ap.add_argument("--it",type=Path,required=True)
    ap.add_argument("--json",type=Path)
    args=ap.parse_args()

    zlraw=args.zl.read_text(encoding="utf-8",errors="replace")
    itbytes=args.it.read_bytes()
    if hashlib.sha256(itbytes).hexdigest()!=IT2A_SHA256:
        raise SystemExit("IT2a SHA256 mismatch")
    itraw=itbytes.decode("utf-8",errors="replace")
    zlpages,zlaudit=base.parse_pages(zlraw)
    itpages,itaudit=base.parse_pages(itraw)
    md=meta_ctl.parse_metadata(zlraw)
    sigs=meta_ctl.signatures(md,FOLIOS)

    zl=analyse_transcription(zlpages,sigs)
    it=analyse_transcription(itpages,sigs)
    zl_candidate=tuple(zl["all"]["consensus_top10"][0]["nesting_outer_to_inner"])
    it_candidate=tuple(it["all"]["consensus_top10"][0]["nesting_outer_to_inner"])

    def top_candidate_by_ablation(res):
        return {a:r["consensus_top10"][0] for a,r in res.items()}

    result={
        "status":"QUIRE_G_ADVERSARIAL_NESTING_DIAGNOSTIC_NOT_DECIPHERMENT",
        "known_physical_bifolia":list(LABELS),
        "current_nesting_outer_to_inner":list(LABELS),
        "folio_metadata_signatures":{str(n):{"H":list(sigs[n][0]),"L":list(sigs[n][1])} for n in FOLIOS},
        "selection_rule":"per transcription: minimize median rank across five windows, then sum rank, then worst rank, then lexical order; hand+Currier residual fixed",
        "ZL3b":zl,
        "IT2a":it,
        "independently_selected_candidates":{
            "ZL3b":list(zl_candidate),
            "IT2a":list(it_candidate),
            "same_candidate":zl_candidate==it_candidate,
        },
        "ablation_winners":{
            "ZL3b":top_candidate_by_ablation(zl),
            "IT2a":top_candidate_by_ablation(it),
        },
        "parser_audit":{"ZL3b":zlaudit,"IT2a":itaudit},
        "guardrails":[
            "Quire G was selected for this diagnostic after a global scan; post-selection status must be disclosed.",
            "ZL3b and IT2a are independent transcriptions of the same manuscript, not independent physical samples.",
            "Metadata residualization may remove real sequence signal correlated with hands/language, but prevents a trivial scribe/Currier explanation.",
            "A stable alternative nesting is only a candidate for physical/codicological review, never proof of rebinding.",
            "No bifolium orientation flips are allowed in this experiment.",
        ],
    }
    text=json.dumps(result,ensure_ascii=False,indent=2)
    print(text)
    if args.json:
        args.json.parent.mkdir(parents=True,exist_ok=True)
        args.json.write_text(text+"\n",encoding="utf-8")

if __name__=="__main__": main()

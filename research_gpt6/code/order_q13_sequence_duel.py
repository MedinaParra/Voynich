#!/usr/bin/env python3
"""Direct bootstrap duel: Layfield-Davis Q13 sequence vs independent ZL3b sequence.

The two candidates share the same central chain 78|81--75|84--76|83 and
differ only in how 77|82 and 79|80 attach to the two ends.  This script
therefore compares the two endpoint assignments on each bootstrap replicate,
without selecting an optimal path first.  That avoids winner-selection bias.

Published sequence (reported publicly from Layfield & Davis 2026):
  77|82 -- 78|81 -- 75|84 -- 76|83 -- 79|80
Independent ZL3b sequence:
  79|80 -- 78|81 -- 75|84 -- 76|83 -- 77|82
"""
from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

import order_bootstrap_stability as bs
import order_q13_openpath as q13
import order_q20_openpath as q20

LD = ["Q13_77|82", "Q13_78|81", "Q13_75|84", "Q13_76|83", "Q13_79|80"]
IND = ["Q13_79|80", "Q13_78|81", "Q13_75|84", "Q13_76|83", "Q13_77|82"]


def edge(sim, a, b):
    return sim.get((a,b), sim.get((b,a)))


def path_score(sim, order):
    return sum(edge(sim,a,b) for a,b in zip(order,order[1:]))


def quantile(xs, q):
    ys=sorted(xs)
    if not ys: return float('nan')
    p=(len(ys)-1)*q
    lo=int(math.floor(p)); hi=int(math.ceil(p))
    if lo==hi: return ys[lo]
    w=p-lo
    return ys[lo]*(1-w)+ys[hi]*w


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("corpus",type=Path)
    ap.add_argument("--reps",type=int,default=2000)
    ap.add_argument("--seed",type=int,default=20261007)
    ap.add_argument("--json",type=Path)
    args=ap.parse_args()

    folios=sorted({x for pair in q13.SHEETS.values() for x in pair})
    lines=bs.load_clean_lines(args.corpus,folios)
    tok_lines,chr_lines=bs.sheet_line_counters(lines,q13.SHEETS)
    names=list(q13.SHEETS)
    rng=random.Random(args.seed)

    deltas=[]
    endpoint_deltas=[]
    wins={"independent":0,"layfield_davis":0,"tie":0}
    # Endpoint terms only; shared middle cancels algebraically.
    for _ in range(args.reps):
        tc={name:bs.sum_sample(tok_lines[name],rng) for name in names}
        cc={name:bs.sum_sample(chr_lines[name],rng) for name in names}
        sim=bs.combined_sim(tc,cc)
        s_ld=path_score(sim,LD)
        s_ind=path_score(sim,IND)
        d=s_ind-s_ld
        # Explicit endpoint assignment difference as an audit check.
        de=(edge(sim,"Q13_79|80","Q13_78|81") + edge(sim,"Q13_77|82","Q13_76|83")) - \
           (edge(sim,"Q13_77|82","Q13_78|81") + edge(sim,"Q13_79|80","Q13_76|83"))
        if abs(d-de)>1e-10:
            raise AssertionError((d,de))
        deltas.append(d); endpoint_deltas.append(de)
        if d>1e-12: wins["independent"]+=1
        elif d<-1e-12: wins["layfield_davis"]+=1
        else: wins["tie"]+=1

    # Full-corpus (unresampled) direct comparison.
    tc={name:sum(tok_lines[name], q20.Counter()) if False else None for name in []}  # keep imports deterministic
    # Build full counters by summing line feature Counters.
    from collections import Counter
    full_tok={name:sum(tok_lines[name],Counter()) for name in names}
    full_chr={name:sum(chr_lines[name],Counter()) for name in names}
    full_sim=bs.combined_sim(full_tok,full_chr)
    full_ld=path_score(full_sim,LD)
    full_ind=path_score(full_sim,IND)

    result={
        "status":"Q13_SEQUENCE_DUEL",
        "seed":args.seed,
        "reps":args.reps,
        "published_layfield_davis":LD,
        "independent_zl3b":IND,
        "shared_core":["Q13_78|81","Q13_75|84","Q13_76|83"],
        "differing_endpoint_assignments":{
            "layfield_davis":[["Q13_77|82","Q13_78|81"],["Q13_76|83","Q13_79|80"]],
            "independent":[["Q13_79|80","Q13_78|81"],["Q13_76|83","Q13_77|82"]],
        },
        "full_corpus":{
            "layfield_davis_score":full_ld,
            "independent_score":full_ind,
            "delta_independent_minus_ld":full_ind-full_ld,
            "winner":"independent" if full_ind>full_ld else "layfield_davis" if full_ld>full_ind else "tie",
        },
        "bootstrap":{
            "wins":wins,
            "win_fraction_independent":wins["independent"]/args.reps,
            "win_fraction_layfield_davis":wins["layfield_davis"]/args.reps,
            "tie_fraction":wins["tie"]/args.reps,
            "delta_independent_minus_ld":{
                "mean":sum(deltas)/len(deltas),
                "q025":quantile(deltas,0.025),
                "median":quantile(deltas,0.5),
                "q975":quantile(deltas,0.975),
                "min":min(deltas),
                "max":max(deltas),
            },
        },
        "guardrails":[
            "This comparison is conditional on the ZL3b transcription and the frozen combined TF-IDF/character-ngram metric.",
            "It compares two prespecified Q13 sequences directly and does not prove historical order.",
            "The central three-singulion chain is identical in both candidates; only the two endpoint assignments are tested.",
            "Bootstrap resamples transcription lines within each physical singulion.",
        ],
    }
    text=json.dumps(result,ensure_ascii=False,indent=2)
    print(text)
    if args.json:
        args.json.parent.mkdir(parents=True,exist_ok=True)
        args.json.write_text(text+"\n",encoding="utf-8")

if __name__=="__main__":
    main()

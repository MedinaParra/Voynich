#!/usr/bin/env python3
"""Bootstrap stability of candidate singulion adjacencies in Q13 and Q20.

Resamples cleaned transcription lines with replacement within each physical
singulion, preserving each singulion's observed line count. For every
replicate it rebuilds token TF-IDF + EVA char 3-5 gram TF-IDF, combines their
z-normalized cosine edge scores, and selects the globally optimal open path.

Q20 is evaluated both raw and after subtracting mean edge-class similarity
(SS/TT/ST) to control the known Stars-Bio vs Stars-B language split.

This is a robustness test for undirected adjacency only. It cannot determine
reading direction because the edge score is symmetric.
"""
from __future__ import annotations

import argparse
import itertools
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

import order_q20_openpath as q20
import order_q20_controls as q20c
import order_q13_openpath as q13

LOCUS = re.compile(r"^<f(\d+)([rv])\.[^>]+>\s+(.*)$")


def load_clean_lines(path: Path, folios):
    out = defaultdict(list)
    wanted = set(folios)
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = LOCUS.match(raw)
        if not m:
            continue
        f = int(m.group(1))
        if f not in wanted:
            continue
        txt = q20.clean_text(m.group(3))
        if txt:
            out[f].append(txt)
    missing = sorted(wanted - set(out))
    if missing:
        raise ValueError(f"Missing folios: {missing}")
    return out


def sheet_line_counters(lines_by_folio, sheets):
    tok = {}
    ch = {}
    for name,(a,b) in sheets.items():
        lines = lines_by_folio[a] + lines_by_folio[b]
        tok[name] = [q20.token_features(x) for x in lines]
        ch[name] = [q20.char_ngram_features(x) for x in lines]
    return tok,ch


def sum_sample(counters, rng):
    n = len(counters)
    out = Counter()
    for _ in range(n):
        out.update(counters[rng.randrange(n)])
    return out


def combined_sim(tok_counts, chr_counts):
    tv = q20.tfidf(tok_counts)
    cv = q20.tfidf(chr_counts)
    return q20.zscore_edge_matrices(q20.sim_matrix(tv), q20.sim_matrix(cv))


def canonical(order):
    t=tuple(order); r=tuple(reversed(t)); return min(t,r)


def path_edges(order):
    return {tuple(sorted((a,b))) for a,b in zip(order,order[1:])}


def rank_generic(names, sim):
    best_score=None; best_path=None
    seen=set()
    for p in itertools.permutations(names):
        c=canonical(p)
        if c in seen: continue
        seen.add(c)
        s=sum(sim[(a,b)] for a,b in zip(c,c[1:]))
        if best_score is None or s>best_score or (s==best_score and c<best_path):
            best_score=s; best_path=c
    return best_score,best_path


def run_bootstrap(label, sheets, tok_lines, chr_lines, reps, rng, residualize_q20=False):
    names=list(sheets)
    edge_counts=Counter(); path_counts=Counter()
    for _ in range(reps):
        tc={name:sum_sample(tok_lines[name],rng) for name in names}
        cc={name:sum_sample(chr_lines[name],rng) for name in names}
        sim=combined_sim(tc,cc)
        if residualize_q20:
            sim,_=q20c.residualize(sim)
        _,p=rank_generic(names,sim)
        path_counts[p]+=1
        edge_counts.update(path_edges(p))
    return {
        "label":label,
        "reps":reps,
        "edge_selection_frequency":[
            {"edge":list(e),"count":n,"frequency":n/reps}
            for e,n in edge_counts.most_common()
        ],
        "top_paths":[
            {"order":list(p),"reverse":list(reversed(p)),"count":n,"frequency":n/reps}
            for p,n in path_counts.most_common(15)
        ],
    }


def candidate_frequency(result, edge):
    e=tuple(sorted(edge))
    for row in result["edge_selection_frequency"]:
        if tuple(row["edge"])==e:
            return row["frequency"]
    return 0.0


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("corpus",type=Path)
    ap.add_argument("--reps",type=int,default=1000)
    ap.add_argument("--seed",type=int,default=20261007)
    ap.add_argument("--json",type=Path)
    args=ap.parse_args()

    q13_folios=sorted({x for pair in q13.SHEETS.values() for x in pair})
    q20_folios=sorted({x for pair in q20.SHEETS.values() for x in pair})
    l13=load_clean_lines(args.corpus,q13_folios)
    l20=load_clean_lines(args.corpus,q20_folios)
    t13,c13=sheet_line_counters(l13,q13.SHEETS)
    t20,c20=sheet_line_counters(l20,q20.SHEETS)

    # Separate RNG streams make each analysis reproducible independently.
    r13=run_bootstrap("Q13_combined",q13.SHEETS,t13,c13,args.reps,random.Random(args.seed))
    r20raw=run_bootstrap("Q20_raw_combined",q20.SHEETS,t20,c20,args.reps,random.Random(args.seed+1))
    r20res=run_bootstrap("Q20_dialect_residual_combined",q20.SHEETS,t20,c20,args.reps,random.Random(args.seed+2),True)

    candidates={
        "Q13":{
            "78|81--75|84":["Q13_78|81","Q13_75|84"],
            "75|84--76|83":["Q13_75|84","Q13_76|83"],
            "76|83--77|82":["Q13_76|83","Q13_77|82"],
            "78|81--79|80":["Q13_78|81","Q13_79|80"],
        },
        "Q20_residual":{
            "103|116--108|111":["S1_103|116","S6_108|111"],
            "104|115--106|113":["S2_104|115","S4_106|113"],
            "106|113--108|111":["S4_106|113","S6_108|111"],
            "106|113--107|112":["S4_106|113","S5_107|112"],
            "103|116--104|115":["S1_103|116","S2_104|115"],
        },
    }

    result={
        "status":"BOOTSTRAP_TOPOLOGY_ONLY",
        "seed":args.seed,
        "reps":args.reps,
        "q13":r13,
        "q20_raw":r20raw,
        "q20_dialect_residual":r20res,
        "candidate_edge_frequencies":{
            "Q13":{k:candidate_frequency(r13,v) for k,v in candidates["Q13"].items()},
            "Q20_residual":{k:candidate_frequency(r20res,v) for k,v in candidates["Q20_residual"].items()},
        },
        "interpretation_guardrails":[
            "Bootstrap frequency is stability under transcription-line resampling, not posterior probability of historical adjacency.",
            "Q20 residual analysis subtracts gross S/T language-block similarity on every replicate.",
            "Direction remains unidentified.",
            "The missing Q20 bifolio 109|110 is not imputed and can alter endpoints/adjacencies if later modeled.",
        ],
    }
    text=json.dumps(result,ensure_ascii=False,indent=2)
    print(text)
    if args.json: args.json.write_text(text+"\n",encoding="utf-8")

if __name__=="__main__": main()

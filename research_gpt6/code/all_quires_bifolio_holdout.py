#!/usr/bin/env python3
"""Manuscript-wide held-out test of physical bifolio textual pairing.

Design frozen after Q13/Q20 results but before inspecting any other quire scores.
The already-inspected quires Q=M (Q13) and Q=T (Q20) are excluded from the
held-out meta-analysis. For every other quire with >=3 complete physical bifolia
identified by corpus metadata $Q and $B, test whether the known physical pairing
has unusually high aggregate-folio TF-IDF similarity among *all* perfect
matchings of exactly the same folios. Repeat after centering every pair score by
the mean score at the same absolute folio-number distance.

Only folios with usable clean EVA on both recto and verso are admitted. A
physical bifolium is admitted only if its $B group contains exactly two such
folios. Incomplete bifolia are excluded wholesale; nothing is imputed.

This is a structural/codicological replication, not decipherment.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import singulion_q13_order as base

PRIMARY = "tfidf_cosine"
EXCLUDED_SEEN_QUIRES = {"M", "T"}  # Q13 and Q20 already inspected.
MAX_EXACT_MATCHINGS = 2_100_000


def canonical_matching(pairs):
    return tuple(sorted((min(a,b), max(a,b)) for a,b in pairs))


def perfect_matchings(items):
    items = tuple(items)
    if not items:
        yield tuple(); return
    a = items[0]
    for i in range(1, len(items)):
        b = items[i]
        rest = items[1:i] + items[i+1:]
        for tail in perfect_matchings(rest):
            yield canonical_matching(((a,b),)+tail)


def double_factorial_odd(n_pairs):
    # Number of perfect matchings of 2k labeled objects: (2k-1)!!
    out=1
    for x in range(1,2*n_pairs,2): out*=x
    return out


def folio_num(page):
    m=re.fullmatch(r"f(\d+)[rv]",page)
    return int(m.group(1)) if m else None


def build_complete_bifolia(pages, meta):
    """Return quire -> list of complete physical pairs plus audit info."""
    # A complete folio needs both r and v clean text and consistent Q/B metadata.
    folios=[]
    candidate_nums=sorted({folio_num(p) for p in pages if folio_num(p) is not None})
    for n in candidate_nums:
        r,v=f"f{n}r",f"f{n}v"
        if not pages.get(r) or not pages.get(v):
            continue
        mr,mv=meta.get(r,{}),meta.get(v,{})
        q1,q2=mr.get("Q"),mv.get("Q")
        b1,b2=mr.get("B"),mv.get("B")
        if not q1 or q1!=q2 or not b1 or b1!=b2:
            continue
        if not re.fullmatch(r"\d+",b1):
            continue
        folios.append((n,q1,b1))

    qb=defaultdict(lambda:defaultdict(list))
    for n,q,b in folios:
        qb[q][b].append(n)

    out={}; audit={}
    for q,groups in sorted(qb.items()):
        complete=[]; incomplete=[]
        for b,nums in sorted(groups.items(),key=lambda kv:int(kv[0])):
            u=sorted(set(nums))
            if len(u)==2:
                complete.append((u[0],u[1]))
            else:
                incomplete.append({"B":b,"folios":u})
        out[q]=tuple(complete)
        audit[q]={"complete_pairs":[f"{a}|{b}" for a,b in complete],"nonpair_groups":incomplete}
    return out,audit


def folio_tokens(pages,n):
    return list(pages[f"f{n}r"])+list(pages[f"f{n}v"])


def build_tfidf_pair_weights(pages, folio_ids):
    docs={n:folio_tokens(pages,n) for n in folio_ids}
    df=Counter()
    for n in folio_ids: df.update(set(docs[n]))
    N=len(folio_ids)
    idf={w:math.log((1+N)/(1+d))+1.0 for w,d in df.items()}
    vec={n:base.tfidf(docs[n],idf) for n in folio_ids}
    return {(a,b):base.cosine(vec[a],vec[b]) for i,a in enumerate(folio_ids) for b in folio_ids[i+1:]}


def rank_stream(true_matching, folios, weights):
    true_score=base.mean([weights[(min(a,b),max(a,b))] for a,b in true_matching])
    n=0; greater=0; ge=0; le=0; total=0.0; mn=float('inf'); mx=float('-inf')
    for m in perfect_matchings(folios):
        s=base.mean([weights[(min(a,b),max(a,b))] for a,b in m])
        n+=1; total+=s; mn=min(mn,s); mx=max(mx,s)
        if s>true_score: greater+=1
        if s>=true_score: ge+=1
        if s<=true_score: le+=1
    return {
        "true_score":true_score,
        "rank_best_is_1":greater+1,
        "n_exact_matchings":n,
        "percentile":100.0*le/n,
        "exact_upper_tail_p_including_observed":ge/n,
        "null_min":mn,"null_mean":total/n,"null_max":mx,
    }


def distance_center(weights):
    by=defaultdict(list)
    for (a,b),v in weights.items(): by[abs(a-b)].append(v)
    means={d:base.mean(vals) for d,vals in by.items()}
    return {(a,b):v-means[abs(a-b)] for (a,b),v in weights.items()}, means


def fisher_survival(ps):
    """Fisher combined p, exact chi-square survival for df=2k (integer shape)."""
    if not ps: return None
    x=-2.0*sum(math.log(max(p,1e-300)) for p in ps)
    z=x/2.0; k=len(ps)
    sf=math.exp(-z)*sum((z**j)/math.factorial(j) for j in range(k))
    return {"k":k,"statistic":x,"df":2*k,"p":sf}


def binom_upper(n,k):
    return sum(math.comb(n,j) for j in range(k,n+1))/(2**n) if n else None


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--corpus',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); args=ap.parse_args()
    data=args.corpus.read_bytes(); blob=base.git_blob_sha1(data)
    if blob!=base.SOURCE_BLOB: raise SystemExit(f"Corpus blob mismatch: {blob}")
    pages,meta,parser_audit=base.parse_pages(data.decode('utf-8'))
    by_quire,structure_audit=build_complete_bifolia(pages,meta)

    results=[]; excluded=[]
    for q,true_pairs in sorted(by_quire.items()):
        k=len(true_pairs)
        if q in EXCLUDED_SEEN_QUIRES:
            excluded.append({"quire":q,"reason":"previously inspected Q13/Q20","complete_bifolia":k})
            continue
        if k<3:
            excluded.append({"quire":q,"reason":"fewer than 3 complete bifolia","complete_bifolia":k})
            continue
        folios=sorted({n for p in true_pairs for n in p})
        if len(folios)!=2*k:
            excluded.append({"quire":q,"reason":"folio reused across B groups","complete_bifolia":k})
            continue
        expected=double_factorial_odd(k)
        if expected>MAX_EXACT_MATCHINGS:
            excluded.append({"quire":q,"reason":f"exact null too large ({expected})","complete_bifolia":k})
            continue
        weights=build_tfidf_pair_weights(pages,folios)
        true=canonical_matching(true_pairs)
        raw=rank_stream(true,folios,weights)
        residual,distmeans=distance_center(weights)
        adjusted=rank_stream(true,folios,residual)
        results.append({
            "quire":q,"complete_bifolia":k,"folios":folios,
            "true_pairs":[f"{a}|{b}" for a,b in true],
            "expected_exact_matchings":expected,
            "raw":raw,"distance_adjusted":adjusted,
            "distance_means":{str(d):v for d,v in sorted(distmeans.items())},
        })

    adj_ps=[r['distance_adjusted']['exact_upper_tail_p_including_observed'] for r in results]
    raw_ps=[r['raw']['exact_upper_tail_p_including_observed'] for r in results]
    positive=sum(r['distance_adjusted']['true_score']>0 for r in results)
    global_summary={
        "heldout_quires":len(results),
        "adjusted_p_below_0_05":sum(p<0.05 for p in adj_ps),
        "adjusted_p_below_0_10":sum(p<0.10 for p in adj_ps),
        "positive_distance_adjusted_effects":positive,
        "one_sided_sign_test_p":binom_upper(len(results),positive),
        "fisher_raw":fisher_survival(raw_ps),
        "fisher_distance_adjusted":fisher_survival(adj_ps),
        "median_adjusted_percentile":sorted(r['distance_adjusted']['percentile'] for r in results)[len(results)//2] if results else None,
    }

    result={
        "classification":"MANUSCRIPT_WIDE_BIFOLIO_PAIRING_HOLDOUT_NOT_DECIPHERMENT",
        "source_blob":blob,
        "primary_metric":PRIMARY,
        "heldout_policy":"exclude Q=M (Q13) and Q=T (Q20), which motivated the test; analyze all other eligible quires without score-based selection",
        "eligibility":"at least 3 complete physical $B groups; each admitted folio has clean EVA on both r and v; incomplete bifolia excluded wholesale",
        "distance_adjustment":"within each quire subtract mean TF-IDF similarity of all candidate folio pairs at identical absolute folio-number distance",
        "max_exact_matchings":MAX_EXACT_MATCHINGS,
        "results":results,
        "global_summary":global_summary,
        "excluded_quires":excluded,
        "structure_audit":structure_audit,
        "parser_audit":parser_audit,
        "guardrails":[
            "This held-out analysis was designed after observing Q13 and Q20, so its per-quire outcomes are fresh but the general hypothesis is not preregistered historically.",
            "Fisher aggregation assumes sufficient independence across disjoint quires and is reported as a meta-analytic summary, not proof of semantics.",
            "A positive result supports physical bifolio textual coupling; it does not determine inter-bifolio reading order.",
        ],
    }
    args.out.parent.mkdir(parents=True,exist_ok=True); args.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8'); print(json.dumps(result,indent=2))

if __name__=='__main__': main()

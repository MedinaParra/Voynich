#!/usr/bin/env python3
"""Strict leave-one-bifolium-out placement audit for Voynich Q13/Q20.

This is a metric-generalization test, not an independent validation of historical order.

For each held-out physical bifolium:
1) its two folios are removed from IDF fitting;
2) token and character IDF are learned from all remaining manuscript pages;
3) the held-out bifolium is transformed with those frozen weights (OOV terms ignored);
4) component z-normalization is learned only from pairwise similarities among
   the remaining units in the target quire;
5) every possible insertion slot into a prespecified reference order with the
   held-out unit removed is ranked.

The test is repeated on ZL3b and Takahashi IT2a. Q20 is reported both raw and
with a training-only S/T block-pair mean residualization.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

IT2A_SHA256 = "7f27a8b0feed8f6de0a99900df6bf912dd1d295c38e5f830bac8b41c3f536fb5"

Q13 = {
    "75|84": (75,84),
    "76|83": (76,83),
    "77|82": (77,82),
    "78|81": (78,81),
    "79|80": (79,80),
}
Q20 = {
    "103|116": (103,116),
    "104|115": (104,115),
    "105|114": (105,114),
    "106|113": (106,113),
    "107|112": (107,112),
    "108|111": (108,111),
}
REFERENCES = {
    "Q13_independent": ["79|80","78|81","75|84","76|83","77|82"],
    "Q13_layfield_davis": ["77|82","78|81","75|84","76|83","79|80"],
    "Q13_current": ["75|84","76|83","77|82","78|81","79|80"],
    "Q20_principal": ["105|114","107|112","106|113","104|115","108|111","103|116"],
    "Q20_current": ["103|116","104|115","105|114","106|113","107|112","108|111"],
}
Q20_BLOCK = {
    "103|116":"S",
    "104|115":"T",
    "105|114":"T",
    "106|113":"T",
    "107|112":"S",
    "108|111":"S",
}

def physical_leaf(page: str) -> str:
    m = re.match(r"^(f[0-9]+)", page)
    return m.group(1) if m else ""

def parse_pages(raw: str):
    pages = defaultdict(list)
    audit = Counter()
    for line in raw.splitlines():
        m = re.match(r"^<([^>]+)>\s*(.*)$", line)
        if not m or "," not in m.group(1):
            continue
        locus, text = m.groups()
        if not re.search(r"P[0-9a-z]", locus.split(",",1)[1]):
            continue
        page = locus.split(".",1)[0]
        if not physical_leaf(page):
            continue
        text = re.sub(r"<[^>]*>", "", text.replace("<->","|"))
        text = re.sub(r"\s+", ".", text.strip()).replace(",",".")
        for token in re.split(r"([.|])", text):
            if not token or token == ".":
                continue
            if token != "|" and re.fullmatch(r"[a-z]{1,64}", token):
                pages[page].append(token)
            elif token == "|":
                audit["drawing_breaks"] += 1
            else:
                audit["uncertain_chunks"] += 1
        audit["paragraph_loci"] += 1
    return dict(pages), dict(audit)

def token_counter(tokens):
    return Counter(tokens)

def char_counter(tokens):
    c = Counter()
    for w in tokens:
        s = f"^{w}$"
        for n in (3,4,5):
            for i in range(max(0, len(s)-n+1)):
                c[s[i:i+n]] += 1
    return c

def fit_idf(page_docs, counter_fn, excluded_folios):
    counters = {}
    for page, toks in page_docs.items():
        leaf = physical_leaf(page)
        if not leaf:
            continue
        folio = int(leaf[1:])
        if folio in excluded_folios:
            continue
        counters[page] = counter_fn(toks)
    n = len(counters)
    df = Counter()
    for c in counters.values():
        df.update(c.keys())
    return {k: math.log((1+n)/(1+d)) + 1.0 for k,d in df.items()}, n

def vectorize(tokens, counter_fn, idf):
    c = counter_fn(tokens)
    total = sum(c.values()) or 1
    v = {k:(n/total)*idf[k] for k,n in c.items() if k in idf}
    kept = sum(n for k,n in c.items() if k in idf)
    return v, {"features_total": len(c), "features_in_vocab": len(v),
               "occurrences_total": sum(c.values()), "occurrences_in_vocab": kept}

def cosine(a,b):
    if not a or not b:
        return 0.0
    if len(a) > len(b):
        a,b = b,a
    dot = sum(v*b.get(k,0.0) for k,v in a.items())
    na = math.sqrt(sum(v*v for v in a.values()))
    nb = math.sqrt(sum(v*v for v in b.values()))
    return dot/(na*nb) if na and nb else 0.0

def jaccard_tokens(a,b):
    aa,bb=set(a),set(b)
    u=len(aa|bb)
    return len(aa&bb)/u if u else 0.0

def unit_tokens(pages, pair):
    out=[]
    for f in pair:
        out += pages.get(f"f{f}r",[])
        out += pages.get(f"f{f}v",[])
    return out

def train_stats(values):
    vals=list(values)
    mu=sum(vals)/len(vals) if vals else 0.0
    sd=math.sqrt(sum((x-mu)**2 for x in vals)/len(vals)) if vals else 1.0
    return mu, sd or 1.0

def z(v, mu, sd):
    return (v-mu)/sd

def canonical_pair(a,b):
    return tuple(sorted((a,b)))

def build_holdout_similarity(pages, units, held):
    excluded=set(units[held])
    tok_idf,n_tok_docs=fit_idf(pages, token_counter, excluded)
    chr_idf,n_chr_docs=fit_idf(pages, char_counter, excluded)

    toks={u:unit_tokens(pages,p) for u,p in units.items()}
    tokvec={}
    chrvec={}
    coverage={}
    for u in units:
        tokvec[u], tcov = vectorize(toks[u], token_counter, tok_idf)
        chrvec[u], ccov = vectorize(toks[u], char_counter, chr_idf)
        coverage[u]={"token":tcov,"char35":ccov}

    train=[u for u in units if u != held]
    comps={"token_tfidf":{}, "char35_tfidf":{}, "token_jaccard":{}}
    for a,b in itertools.combinations(units,2):
        k=canonical_pair(a,b)
        comps["token_tfidf"][k]=cosine(tokvec[a],tokvec[b])
        comps["char35_tfidf"][k]=cosine(chrvec[a],chrvec[b])
        comps["token_jaccard"][k]=jaccard_tokens(toks[a],toks[b])

    stats={}
    for cname,m in comps.items():
        training_vals=[m[canonical_pair(a,b)] for a,b in itertools.combinations(train,2)]
        stats[cname]=train_stats(training_vals)

    combined={}
    for a,b in itertools.combinations(units,2):
        k=canonical_pair(a,b)
        combined[k]=sum(z(comps[c][k], *stats[c]) for c in comps)/len(comps)

    return combined, comps, stats, coverage, {"idf_training_pages":n_tok_docs}

def q20_residualize_training_only(matrix, held):
    train=[u for u in Q20 if u != held]
    groups=defaultdict(list)
    def gkey(a,b):
        return "".join(sorted((Q20_BLOCK[a],Q20_BLOCK[b])))
    for a,b in itertools.combinations(train,2):
        groups[gkey(a,b)].append(matrix[canonical_pair(a,b)])
    global_mu=sum(v for vals in groups.values() for v in vals)/sum(len(vals) for vals in groups.values())
    means={g:(sum(vals)/len(vals) if vals else global_mu) for g,vals in groups.items()}
    out={}
    for a,b in itertools.combinations(Q20,2):
        k=canonical_pair(a,b)
        out[k]=matrix[k]-means.get(gkey(a,b),global_mu)
    return out, {"training_group_means":means,"global_training_mean":global_mu,
                 "training_group_counts":{g:len(v) for g,v in groups.items()}}

def path_score(order, matrix):
    return sum(matrix[canonical_pair(a,b)] for a,b in zip(order,order[1:]))

def insertion_rank(reference, held, matrix):
    base=[x for x in reference if x != held]
    rows=[]
    for pos in range(len(base)+1):
        p=base[:pos]+[held]+base[pos:]
        rows.append({"position_0_based":pos,"order":p,"score":path_score(p,matrix)})
    rows.sort(key=lambda r:(-r["score"],r["position_0_based"]))
    for i,r in enumerate(rows,1):
        r["rank"]=i
    true_pos=reference.index(held)
    actual=next(r for r in rows if r["position_0_based"]==true_pos)
    return {
        "held_out":held,
        "expected_position_0_based":true_pos,
        "rank":actual["rank"],
        "n_positions":len(rows),
        "reciprocal_rank":1.0/actual["rank"],
        "top1":actual["rank"]==1,
        "expected_score":actual["score"],
        "best":rows[0],
        "all_positions":rows,
    }

def summarize(rows):
    ranks=[r["rank"] for r in rows]
    return {
        "n_holdouts":len(rows),
        "top1":sum(r["top1"] for r in rows),
        "top1_fraction":sum(r["top1"] for r in rows)/len(rows),
        "mean_reciprocal_rank":sum(r["reciprocal_rank"] for r in rows)/len(rows),
        "median_rank":median(ranks),
        "mean_rank":sum(ranks)/len(ranks),
        "ranks":ranks,
    }

def analyse_reference(pages, units, reference, residualize_q20=False):
    rows=[]
    for held in reference:
        matrix, comps, stats, coverage, fitinfo = build_holdout_similarity(pages, units, held)
        residual_info=None
        if residualize_q20:
            matrix,residual_info=q20_residualize_training_only(matrix,held)
        row=insertion_rank(reference,held,matrix)
        row["heldout_fit"]={
            **fitinfo,
            "component_training_mean_sd":{k:{"mean":v[0],"sd":v[1]} for k,v in stats.items()},
            "heldout_coverage":coverage[held],
            "q20_residualization":residual_info,
        }
        rows.append(row)
    return {"summary":summarize(rows),"holdouts":rows}

def analyse_transcription(raw):
    pages,audit=parse_pages(raw)
    required=sorted({f for p in list(Q13.values())+list(Q20.values()) for f in p})
    missing=[f"f{f}{s}" for f in required for s in ("r","v") if not pages.get(f"f{f}{s}")]
    if missing:
        raise RuntimeError(f"missing required pages: {missing}")
    out={"parser_audit":audit}
    out["Q13_independent"]=analyse_reference(pages,Q13,REFERENCES["Q13_independent"])
    out["Q13_layfield_davis"]=analyse_reference(pages,Q13,REFERENCES["Q13_layfield_davis"])
    out["Q13_current"]=analyse_reference(pages,Q13,REFERENCES["Q13_current"])
    out["Q20_principal_raw"]=analyse_reference(pages,Q20,REFERENCES["Q20_principal"])
    out["Q20_principal_residual_ST"]=analyse_reference(pages,Q20,REFERENCES["Q20_principal"],True)
    out["Q20_current_raw"]=analyse_reference(pages,Q20,REFERENCES["Q20_current"])
    out["Q20_current_residual_ST"]=analyse_reference(pages,Q20,REFERENCES["Q20_current"],True)
    return out

def cross_summary(zl,it,key):
    zs=zl[key]["summary"]; ts=it[key]["summary"]
    all_ranks=zs["ranks"]+ts["ranks"]
    n=zs["n_holdouts"]+ts["n_holdouts"]
    top=zs["top1"]+ts["top1"]
    rr=sum(1/r for r in all_ranks)
    return {
        "tests":n,
        "top1":top,
        "top1_fraction":top/n,
        "mean_reciprocal_rank":rr/n,
        "median_rank":median(all_ranks),
        "mean_rank":sum(all_ranks)/n,
        "ranks_zl3b":zs["ranks"],
        "ranks_it2a":ts["ranks"],
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--zl",type=Path,required=True)
    ap.add_argument("--it",type=Path,required=True)
    ap.add_argument("--json",type=Path)
    args=ap.parse_args()

    zl_raw=args.zl.read_text(encoding="utf-8",errors="replace")
    it_bytes=args.it.read_bytes()
    it_sha=hashlib.sha256(it_bytes).hexdigest()
    if it_sha != IT2A_SHA256:
        raise SystemExit(f"IT2a SHA256 mismatch: {it_sha}")
    it_raw=it_bytes.decode("utf-8",errors="replace")

    zl=analyse_transcription(zl_raw)
    it=analyse_transcription(it_raw)
    keys=[k for k in zl if k!="parser_audit"]
    cross={k:cross_summary(zl,it,k) for k in keys}
    result={
        "status":"Q13_Q20_STRICT_LEAVE_ONE_BIFOLIUM_OUT_METRIC_GENERALIZATION",
        "method":{
            "unit":"complete physical bifolium (both folios, recto+verso)",
            "idf_fit":"all manuscript pages except both held-out folios",
            "heldout_transform":"frozen training IDF; unseen held-out features ignored",
            "component_normalization":"training target-quire pair similarities only; held-out pair scores excluded",
            "components":["token TF-IDF cosine","character 3-5gram TF-IDF cosine","token Jaccard"],
            "placement":"rank every insertion slot into each frozen reference order",
            "Q20_control":"training-only S/T block-pair mean residualization reported alongside raw scores",
        },
        "references":REFERENCES,
        "ZL3b":zl,
        "IT2a":it,
        "cross_transcription":cross,
        "guardrails":[
            "This is a leakage audit / metric-generalization test, not independent evidence for historical order.",
            "The frozen reference orders were discovered or proposed using related manuscript evidence; insertion accuracy therefore measures self-consistency under held-out fitting, not truth.",
            "ZL3b and IT2a are independent transcriptions of the same manuscript, not independent physical samples.",
            "Q20 S/T labels are external metadata and residualization is estimated from training edges only.",
            "The missing Q20 bifolium 109|110 is not imputed or scored.",
            "No folio number, current distance, image feature, or codicological defect enters the similarity metric.",
        ],
    }
    text=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
    print(text,end="")
    if args.json:
        args.json.parent.mkdir(parents=True,exist_ok=True)
        args.json.write_text(text,encoding="utf-8")

if __name__=="__main__":
    main()

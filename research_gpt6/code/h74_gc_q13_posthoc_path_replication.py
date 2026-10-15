#!/usr/bin/env python3
import argparse, hashlib, itertools, json, math, re
from collections import Counter, defaultdict
from pathlib import Path

EXPECTED_SHA256 = 'b09570cb6c993bc2d87134d115e60a978650a8a6495483ddbb1f6005a586096f'
UNITS = ('75|84', '76|83', '77|82', '78|81', '79|80')
UNIT_FOLIOS = {
    '75|84': (75,84), '76|83': (76,83), '77|82': (77,82),
    '78|81': (78,81), '79|80': (79,80),
}
CURRENT = ('75|84','76|83','77|82','78|81','79|80')
CANDIDATE = ('77|82','76|83','75|84','78|81','79|80')
MIN_TOKENS_PER_BIFOLIO = 50
MIN_VOCAB = 100
EPS = 1e-15


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def clean_tokens(payload):
    s = re.sub(r'<[^>]*>|\[[^]]*\]|\{[^}]*\}|@[0-9]+;', ' ', payload)
    pieces = re.split(r'[.\s]+', s)
    out=[]
    for p in pieces:
        p=p.strip()
        if not p or '?' in p:
            continue
        runs=re.findall(r'[A-Za-z0-9]+',p)
        if len(runs)==1 and len(runs[0])>=2:
            out.append(runs[0])
    return out


def locus_type(locator):
    loc=re.sub(r'^[@+*=]','',locator.strip())
    m=re.match(r'([PLCR])',loc)
    return m.group(1) if m else None


def parse_q13(data):
    text=data.decode('utf-8',errors='strict')
    by_folio=defaultdict(list)
    for line in text.splitlines():
        m=re.match(r'^<([^>]+)>\s*(.*)$',line)
        if not m or ',' not in m.group(1):
            continue
        locus,payload=m.groups()
        folio_id=locus.split('.')[0]
        fm=re.match(r'^f(\d+)',folio_id)
        if not fm:
            continue
        folio=int(fm.group(1))
        if not 75 <= folio <= 84:
            continue
        locator=locus.split(',',1)[1]
        if locus_type(locator)!='P':
            continue
        by_folio[folio].extend(clean_tokens(payload))
    return by_folio


def build_docs(by_folio):
    docs={}
    for u in UNITS:
        toks=[]
        for f in UNIT_FOLIOS[u]: toks.extend(by_folio.get(f,[]))
        docs[u]=Counter(toks)
    return docs


def tfidf(docs):
    vocab=sorted(set().union(*(set(d.keys()) for d in docs.values())))
    df={t:sum(t in docs[u] for u in UNITS) for t in vocab}
    idf={t:math.log(6/(1+df[t]))+1.0 for t in vocab}
    vecs={}
    for u in UNITS:
        raw={t:docs[u][t]*idf[t] for t in docs[u]}
        norm=math.sqrt(math.fsum(v*v for v in raw.values()))
        vecs[u]={t:v/norm for t,v in raw.items()} if norm else {}
    return vecs,vocab


def cosine(a,b):
    if len(a)>len(b): a,b=b,a
    return math.fsum(v*b.get(t,0.0) for t,v in a.items())


def score(seq,sim):
    vals=[sim[(seq[i],seq[i+1])] for i in range(4)]
    return math.fsum(sorted(vals))/4


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--gc',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    data=a.gc.read_bytes()
    got=sha256(data)
    out={
        'classification':'GC_V101_Q13_H73_POSTHOC_PATH_PROSPECTIVE_REPLICATION_NOT_READING_ORDER_PROOF',
        'gc_sha256':got,'expected_gc_sha256':EXPECTED_SHA256,
        'candidate_sequence':list(CANDIDATE),'current_nested_sequence':list(CURRENT),
        'physical_units':list(UNITS),
    }
    if got!=EXPECTED_SHA256:
        out.update({'status':'BLOCKED','reason':'frozen GC source hash mismatch','permutations_scored':0})
        a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2,sort_keys=True)); return

    by_folio=parse_q13(data)
    docs=build_docs(by_folio)
    folio_counts={str(f):len(by_folio.get(f,[])) for f in range(75,85)}
    bifolio_counts={u:sum(docs[u].values()) for u in UNITS}
    vecs,vocab=tfidf(docs)
    out.update({'folio_p_token_counts':folio_counts,'bifolio_p_token_counts':bifolio_counts,'vocabulary_types':len(vocab)})
    valid=(all(folio_counts[str(f)]>0 for f in range(75,85)) and all(bifolio_counts[u]>=MIN_TOKENS_PER_BIFOLIO for u in UNITS) and len(vocab)>=MIN_VOCAB)
    if not valid:
        out.update({'status':'BLOCKED','reason':'preregistered GC Q13 sample gate not met','permutations_scored':0})
        a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2,sort_keys=True)); return

    sim={}
    for x in UNITS:
        for y in UNITS:
            if x==y: sim[(x,y)]=1.0
            elif (y,x) in sim: sim[(x,y)]=sim[(y,x)]
            else: sim[(x,y)]=cosine(vecs[x],vecs[y])
    scored=[(p,score(p,sim)) for p in itertools.permutations(UNITS)]
    if len(scored)!=120:
        out.update({'status':'BLOCKED','reason':'did not score exactly 120 permutations','permutations_scored':len(scored)})
        a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2,sort_keys=True)); return
    cand=score(CANDIDATE,sim); current=score(CURRENT,sim); scores=[s for _,s in scored]
    ge=sum(s>=cand-EPS for s in scores); gt=sum(s>cand+EPS for s in scores)
    p=ge/120; rank=1+gt; mx=max(scores)
    maximizers=[list(q) for q,s in scored if abs(s-mx)<=EPS]
    status='PASS' if cand>current and p<=0.05 else 'FAIL'
    out.update({
        'candidate_score':cand,'current_nested_score':current,'candidate_minus_current':cand-current,
        'null_mean_score':math.fsum(scores)/120,'exact_permutation_p':p,'exact_rank':rank,
        'percentile_at_or_below_candidate':sum(s<=cand+EPS for s in scores)/120,
        'maximum_score':mx,'maximizing_sequences':maximizers,'permutations_scored':120,
        'pairwise_cosine':{x:{y:sim[(x,y)] for y in UNITS if y!=x} for x in UNITS},
        'status':status,
    })
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2,sort_keys=True))

if __name__=='__main__': main()

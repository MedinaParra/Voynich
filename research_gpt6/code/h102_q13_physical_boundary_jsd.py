#!/usr/bin/env python3
import argparse, hashlib, itertools, json, math, re
from collections import Counter, defaultdict
import numpy as np
EXPECTED_SHA='32b11a0b584a75bbe9817c96a316a246f82d02d69996d789bc2cb908190bab77'
CANDIDATE=[(77,82),(76,83),(75,84),(78,81),(79,80)]

def clean_tokens(text):
    clean=re.sub(r'<[^>]*>|\[[^]]*\]|\{[^}]*\]|@[0-9]+;', ' ', text).replace('?', ' ')
    return re.findall(r'(?<![a-z])[a-z]{2,}(?![a-z])', clean.lower())
def parse(raw):
    d=defaultdict(list)
    for line in raw.splitlines():
        m=re.match(r'^<([^>]+)>\s*(.*)$',line)
        if not m: continue
        fm=re.match(r'^(f\d+[rv]?)',m.group(1))
        if fm: d[fm.group(1)].extend(clean_tokens(m.group(2)))
    return {k:v for k,v in d.items() if len(v)>=20}
def js(a,b):
    keys=set(a)|set(b); sa=sum(a.values()); sb=sum(b.values())
    if not sa or not sb: return float('nan')
    pa={k:a.get(k,0)/sa for k in keys}; pb={k:b.get(k,0)/sb for k in keys}; pm={k:(pa[k]+pb[k])/2 for k in keys}
    def kl(p): return sum(v*math.log2(v/pm[k]) for k,v in p.items() if v and pm[k])
    return .5*(kl(pa)+kl(pb))
def expand(order):
    out=[]
    for a,b in order: out += [f'f{a}r',f'f{a}v',f'f{b}r',f'f{b}v']
    return out
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--takahashi',required=True); ap.add_argument('--out',required=True); a=ap.parse_args()
    raw=open(a.takahashi,'rb').read(); got=hashlib.sha256(raw).hexdigest(); seq=expand(CANDIDATE); corpus=parse(raw.decode('utf-8',errors='replace'))
    res={'experiment':'H102','source_sha256':got,'expected_source_sha256':EXPECTED_SHA,'candidate_bifolio_order':CANDIDATE,'candidate_sequence':seq}
    controls={}
    controls['source_sha_identity']='PASS' if got==EXPECTED_SHA else 'FAIL'
    controls['candidate_identity']='PASS' if CANDIDATE==[(77,82),(76,83),(75,84),(78,81),(79,80)] else 'FAIL'
    controls['coverage_20_of_20']='PASS' if all(x in corpus for x in seq) and len(seq)==20 else 'FAIL'
    rows=[]
    for i,(x,y) in enumerate(zip(seq,seq[1:])):
        if x[:-1]==y[:-1]: cls='WITHIN_LEAF'
        elif i%4==1: cls='WITHIN_BIFOLIO'
        elif i%4==3: cls='BETWEEN_BIFOLIO'
        else: cls='INTERNAL_ERROR'
        v=js(Counter(''.join(corpus.get(x,[]))),Counter(''.join(corpus.get(y,[]))))
        rows.append({'index':i,'a':x,'b':y,'class':cls,'jsd':v})
    between=[r['jsd'] for r in rows if r['class']=='BETWEEN_BIFOLIO']; internal=[r['jsd'] for r in rows if r['class'] in ('WITHIN_LEAF','WITHIN_BIFOLIO')]
    controls['adjacency_count_19']='PASS' if len(rows)==19 else 'FAIL'; controls['between_count_4']='PASS' if len(between)==4 else 'FAIL'; controls['internal_count_15']='PASS' if len(internal)==15 else 'FAIL'; controls['finite_jsd']='PASS' if all(np.isfinite(r['jsd']) for r in rows) else 'FAIL'
    combos=list(itertools.combinations(range(19),4)); controls['exact_enumeration_3876']='PASS' if len(combos)==3876 else 'FAIL'
    if any(v!='PASS' for v in controls.values()): res.update(status='BLOCKED',controls=controls,adjacencies=rows); json.dump(res,open(a.out,'w'),indent=2,sort_keys=True); return
    obs=float(np.median(between)-np.median(internal)); vals=np.array([r['jsd'] for r in rows]); ge=0
    for c in combos:
        mask=np.zeros(19,dtype=bool); mask[list(c)]=True; stat=float(np.median(vals[mask])-np.median(vals[~mask])); ge += stat>=obs-1e-15
    p=ge/len(combos); bm=float(np.median(between)); im=float(np.median(internal)); status='PASS' if bm>im and p<=0.01 else 'FAIL'
    res.update(status=status,controls=controls,adjacencies=rows,between_median_jsd=bm,internal_median_jsd=im,observed_difference=obs,exact_one_sided_p=p,extreme_or_equal_assignments=ge,total_assignments=len(combos))
    with open(a.out,'w') as f: json.dump(res,f,indent=2,sort_keys=True)
if __name__=='__main__': main()

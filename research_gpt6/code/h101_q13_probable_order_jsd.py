#!/usr/bin/env python3
# H101 preregistered implementation; this comment-only revision triggers the dedicated workflow.
import argparse, hashlib, json, re
from collections import Counter, defaultdict
import numpy as np

EXPECTED_SHA='32b11a0b584a75bbe9817c96a316a246f82d02d69996d789bc2cb908190bab77'
CURRENT=[(75,84),(76,83),(77,82),(78,81),(79,80)]
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
    def kl(p):
        import math
        return sum(v*math.log2(v/pm[k]) for k,v in p.items() if v and pm[k])
    return .5*(kl(pa)+kl(pb))

def expand(order):
    out=[]
    for a,b in order:
        out += [f'f{a}r',f'f{a}v',f'f{b}r',f'f{b}v']
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--takahashi',required=True); ap.add_argument('--out',required=True); a=ap.parse_args()
    raw=open(a.takahashi,'rb').read(); got=hashlib.sha256(raw).hexdigest()
    res={'experiment':'H101','source_sha256':got,'expected_source_sha256':EXPECTED_SHA,'current_bifolio_order':CURRENT,'candidate_bifolio_order':CANDIDATE}
    if got!=EXPECTED_SHA:
        res.update(status='BLOCKED',reason='source_sha_mismatch'); json.dump(res,open(a.out,'w'),indent=2); return
    corpus=parse(raw.decode('utf-8',errors='replace'))
    cur=expand(CURRENT); can=expand(CANDIDATE)
    common=set(cur)&set(can)&set(corpus)
    cur=[f for f in cur if f in common]; can=[f for f in can if f in common]
    res['common_folio_sides']=len(common); res['current_sequence']=cur; res['candidate_sequence']=can
    if len(common)<16 or set(cur)!=set(can):
        res.update(status='BLOCKED',reason='coverage_or_set_mismatch'); json.dump(res,open(a.out,'w'),indent=2); return
    def vec(seq):
        rows=[]
        for x,y in zip(seq,seq[1:]):
            v=js(Counter(''.join(corpus[x])),Counter(''.join(corpus[y])))
            rows.append({'a':x,'b':y,'jsd':v})
        return rows
    cv=vec(cur); pv=vec(can)
    if not all(np.isfinite(r['jsd']) for r in cv+pv):
        res.update(status='BLOCKED',reason='nonfinite_jsd'); json.dump(res,open(a.out,'w'),indent=2); return
    cm=float(np.median([r['jsd'] for r in cv])); pm=float(np.median([r['jsd'] for r in pv])); threshold=.8*cm
    status='PASS' if pm<=threshold else 'FAIL'
    res.update(status=status,current_median_jsd=cm,candidate_median_jsd=pm,candidate_minus_current=pm-cm,candidate_over_current=(pm/cm if cm else None),required_max_candidate_jsd=threshold,current_adjacencies=cv,candidate_adjacencies=pv,controls={'source_sha_identity':'PASS','candidate_identity':'PASS','current_identity':'PASS','identical_folio_side_set':'PASS','coverage_ge_16':'PASS','finite_jsd':'PASS'})
    with open(a.out,'w') as f: json.dump(res,f,indent=2,sort_keys=True)
if __name__=='__main__': main()

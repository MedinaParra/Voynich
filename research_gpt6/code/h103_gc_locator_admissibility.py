#!/usr/bin/env python3
import argparse, hashlib, json, re
from collections import Counter, defaultdict
EXPECTED='b09570cb6c993bc2d87134d115e60a978650a8a6495483ddbb1f6005a586096f'
FOLIOS=['f14v','f25v','f39r','f40r','f50v','f87r','f8v','f90r1','f95r2']

def single_token(payload):
    s=re.sub(r'<[^>]*>|\[[^]]*\]|\{[^}]*\}|@[0-9]+;',' ',payload)
    toks=[p for p in re.split(r'[.\s]+',s.strip()) if p and '?' not in p and len(re.findall(r'[A-Za-z0-9]+',p))==1]
    return len(toks)==1

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--gc',required=True); ap.add_argument('--out',required=True); a=ap.parse_args()
    raw=open(a.gc,'rb').read(); sha=hashlib.sha256(raw).hexdigest()
    out={'experiment':'H103','source_sha256':sha,'expected_source_sha256':EXPECTED,'folios':FOLIOS,'semantics':'NOT_RUN','language':'NOT_RUN','translation':'NOT_RUN','decipherment':'NOT_RUN'}
    if sha!=EXPECTED:
        out.update(status='BLOCKED',reason='source_sha_mismatch'); json.dump(out,open(a.out,'w'),indent=2,sort_keys=True); return
    counts={f:Counter() for f in FOLIOS}; singles={f:Counter() for f in FOLIOS}; totals=Counter()
    pat=re.compile(r'^<(f\d+[rv]\d*)\.(\d+),([^>]+)>\s*(.*)$')
    try: lines=raw.decode('utf-8','strict').splitlines()
    except UnicodeDecodeError:
        out.update(status='BLOCKED',reason='source_decode_error'); json.dump(out,open(a.out,'w'),indent=2,sort_keys=True); return
    for line in lines:
        m=pat.match(line)
        if not m: continue
        fol,_,loc,payload=m.groups()
        if fol not in counts: continue
        norm=re.sub(r'^[@+*=]+','',loc.strip()); mm=re.search(r'[A-Za-z]',norm)
        if not mm: continue
        prefix=mm.group(0).upper(); counts[fol][prefix]+=1; totals[fol]+=1
        if single_token(payload): singles[fol][prefix]+=1
    prefix_sets=[set(counts[f]) for f in FOLIOS]; shared=sorted(set.intersection(*prefix_sets)) if prefix_sets else []
    shared_single=[p for p in shared if all(singles[f][p]>=1 for f in FOLIOS)]
    all_present=all(totals[f]>=1 for f in FOLIOS)
    status='PASS' if all_present and bool(shared_single) else 'FAIL'
    out.update(status=status,parseable_records={f:totals[f] for f in FOLIOS},prefix_counts={f:dict(sorted(counts[f].items())) for f in FOLIOS},single_token_prefix_counts={f:dict(sorted(singles[f].items())) for f in FOLIOS},shared_prefixes=shared,shared_prefixes_with_single_token_every_folio=shared_single,controls={'source_sha_identity':'PASS','all_9_folios_parseable':'PASS' if all_present else 'FAIL','shared_prefix_all_9':'PASS' if shared else 'FAIL','shared_prefix_single_token_all_9':'PASS' if shared_single else 'FAIL'})
    with open(a.out,'w') as f: json.dump(out,f,indent=2,sort_keys=True)
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__': main()

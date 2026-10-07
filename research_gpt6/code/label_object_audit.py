#!/usr/bin/env python3
"""Audit IVTFF label subtype sample sizes before lexical-anchor modeling.
No classifier and no semantic gloss are produced by this script.
"""
import argparse, hashlib, json, re
from collections import Counter, defaultdict
from pathlib import Path

SOURCE_BLOB = '2a4533ab9bdfa85db9bad602d590978953055df1'
SUBTYPES = ('Lp','Lc','Lf','Ln','Lt','Ls','Lz','La')

def blob_sha(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--corpus',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args(); raw=a.corpus.read_bytes()
    if blob_sha(raw)!=SOURCE_BLOB: raise SystemExit('frozen corpus mismatch')
    pages={}; rows=[]
    for line in raw.decode().splitlines():
        p=re.match(r'^<([^>.,]+)>\s*<!([^>]*)>',line)
        if p:
            fol=p.group(1); m=dict(re.findall(r'\$([A-Z])=([^\s>]+)',p.group(2)))
            pages[fol]={'quire':m.get('Q','?'),'currier':m.get('L','?'),'hand':m.get('H','?')}
            continue
        m=re.match(r'^<([^>]+)>\s*(.*)$',line)
        if not m or ',' not in m.group(1): continue
        locus,text=m.groups(); fol=locus.split('.')[0]; pos=locus.split(',',1)[1]
        subtype=next((s for s in SUBTYPES if s in pos),None)
        if not subtype: continue
        clean=re.sub(r'<[^>]*>',' ',text)
        clean=re.sub(r'\[[^]]*\]|\{[^}]*\}|@[0-9]+;',' ',clean)
        uncertain='?' in clean
        toks=re.findall(r'(?<![a-z])[a-z]{2,}(?![a-z])',clean.replace('?',' '))
        md=pages.get(fol,{'quire':'?','currier':'?','hand':'?'})
        rows.append({'folio':fol,'locus':locus,'subtype':subtype,'tokens':toks,'uncertain':uncertain,**md})
    exact=[r for r in rows if len(r['tokens'])==1 and not r['uncertain']]
    by=Counter(r['subtype'] for r in exact); q=defaultdict(set); ch=defaultdict(Counter)
    for r in exact:
        q[r['subtype']].add(r['quire']); ch[r['subtype']][(r['currier'],r['hand'])]+=1
    result={'classification':'PRE_MODEL_LABEL_AUDIT','source_blob':SOURCE_BLOB,'raw_label_rows':len(rows),'primary_single_certain_labels':len(exact),'counts':{s:by[s] for s in SUBTYPES},'quires':{s:len(q[s]-{'?'}) for s in SUBTYPES},'currier_hand_strata':{s:{f'{k[0]}|{k[1]}':v for k,v in sorted(ch[s].items())} for s in SUBTYPES},'rule':'No class is removed after observing model performance. Sparse classes must be reported before classification.'}
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result,indent=2))
if __name__=='__main__': main()

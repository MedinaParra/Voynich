#!/usr/bin/env python3
"""Weak semantic section test for Voynich IVTFF.

Purpose: test whether text alone predicts coarse manuscript section after controlling
for Currier/hand/quire confounds. This is NOT translation and never assigns glosses.
Standard library only; deterministic; leave-one-quire-out evaluation.
"""
import argparse, hashlib, json, math, random, re
from collections import Counter, defaultdict
from pathlib import Path

SOURCE_BLOB='2a4533ab9bdfa85db9bad602d590978953055df1'
SEED=20261006

def blob_sha(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()

def parse(raw):
    meta={}; pages={}
    for line in raw.splitlines():
        m=re.match(r'^<([^>.,]+)>\s*<!([^>]*)>',line)
        if m:
            fol=m.group(1); meta=dict(re.findall(r'\$([A-Z])=([^\s>]+)',m.group(2)))
            pages[fol]={'folio':fol,'quire':meta.get('Q','?'),'currier':meta.get('L','?'),'hand':meta.get('H','?'),'illustration':meta.get('I','?'),'tokens':[]}
            continue
        m=re.match(r'^<([^>]+)>\s*(.*)$',line)
        if not m or ',' not in m.group(1): continue
        fol=m.group(1).split('.')[0]
        if fol not in pages: continue
        text=re.sub(r'<[^>]*>',' ',m.group(2)); text=re.sub(r'\[[^]]*\]|\{[^}]*\}|@[0-9]+;|\?',' ',text)
        pages[fol]['tokens'] += re.findall(r'(?<![a-z])[a-z]{2,}(?![a-z])',text)
    return [p for p in pages.values() if len(p['tokens'])>=20]

def section(p):
    # IVTFF illustration code, intentionally coarse. H=herbal, A=astronomical,
    # B=biological, P=pharmaceutical, S=stars/recipes; unknowns excluded.
    return {'H':'herbal','A':'astronomical','B':'biological','P':'pharmaceutical','S':'recipes'}.get(p['illustration'])

def feats(tokens):
    c=Counter()
    for w in tokens:
        c['W:'+w]+=1
        for n in (2,3):
            for i in range(len(w)-n+1): c[f'C{n}:'+w[i:i+n]]+=1
    return c

def train_nb(train, label_key):
    labs=sorted({label_key(p) for p in train}); docs=Counter(label_key(p) for p in train); counts={l:Counter() for l in labs}; totals=Counter(); vocab=set()
    for p in train:
        l=label_key(p); f=feats(p['tokens']); counts[l].update(f); totals[l]+=sum(f.values()); vocab.update(f)
    return labs,docs,counts,totals,len(vocab)

def predict(model,p):
    labs,docs,counts,totals,V=model; f=feats(p['tokens']); N=sum(docs.values()); best=None
    for l in labs:
        s=math.log((docs[l]+1)/(N+len(labs)))
        den=totals[l]+V
        for x,n in f.items(): s += n*math.log((counts[l][x]+1)/den)
        if best is None or s>best[0]: best=(s,l)
    return best[1]

def evaluate(pages,label_key):
    qs=sorted({p['quire'] for p in pages if p['quire']!='?'}); y=[]
    for q in qs:
        test=[p for p in pages if p['quire']==q]; train=[p for p in pages if p['quire']!=q]
        if len({label_key(p) for p in train})<2: continue
        m=train_nb(train,label_key)
        for p in test:
            if label_key(p) in m[0]: y.append((label_key(p),predict(m,p),p['folio'],q))
    return y

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--corpus',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args(); b=a.corpus.read_bytes()
    if blob_sha(b)!=SOURCE_BLOB: raise SystemExit('frozen corpus mismatch')
    pages=parse(b.decode()); pages=[p for p in pages if section(p)]
    obs=evaluate(pages,section); acc=sum(a==b for a,b,_,_ in obs)/len(obs) if obs else 0
    # Critical confound tests: can text predict Currier/hand under identical folds?
    cur=evaluate([p for p in pages if p['currier'] in ('A','B')],lambda p:p['currier'])
    hand=evaluate([p for p in pages if p['hand']!='?'],lambda p:p['hand'])
    result={'classification':'WEAK_SEMANTIC_SECTION_SIGNAL_NOT_TRANSLATION','source_blob':SOURCE_BLOB,'seed':SEED,'pages':len(pages),'fold_unit':'quire','section_accuracy':acc,'section_n':len(obs),'currier_accuracy':sum(a==b for a,b,_,_ in cur)/len(cur) if cur else None,'currier_n':len(cur),'hand_accuracy':sum(a==b for a,b,_,_ in hand)/len(hand) if hand else None,'hand_n':len(hand),'warning':'Section predictability is semantic evidence only if it survives Currier/hand/quire confound controls; no token gloss follows from this test.'}
    a.out.write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result,indent=2))
if __name__=='__main__': main()

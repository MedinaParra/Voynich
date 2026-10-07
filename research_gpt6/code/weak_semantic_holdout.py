#!/usr/bin/env python3
"""Weak semantic section test for Voynich IVTFF.

Tests whether text predicts coarse manuscript section with leave-one-quire-out,
and estimates a stratified permutation null preserving Currier/hand strata.
This is NOT translation and never assigns glosses.
"""
import argparse, hashlib, json, math, random, re
from collections import Counter, defaultdict
from pathlib import Path

SOURCE_BLOB='2a4533ab9bdfa85db9bad602d590978953055df1'
SEED=20261006

def blob_sha(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()

def parse(raw):
    pages={}
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
    return {'H':'herbal','A':'astronomical','B':'biological','P':'pharmaceutical','S':'recipes'}.get(p['illustration'])

def feats(tokens):
    c=Counter()
    for w in tokens:
        c['W:'+w]+=1
        for n in (2,3):
            for i in range(len(w)-n+1): c[f'C{n}:'+w[i:i+n]]+=1
    return c

def train_nb(train,label_key):
    labs=sorted({label_key(p) for p in train}); docs=Counter(label_key(p) for p in train); counts={l:Counter() for l in labs}; totals=Counter(); vocab=set()
    for p in train:
        l=label_key(p); f=feats(p['tokens']); counts[l].update(f); totals[l]+=sum(f.values()); vocab.update(f)
    return labs,docs,counts,totals,len(vocab)

def predict(model,p):
    labs,docs,counts,totals,V=model; f=feats(p['tokens']); N=sum(docs.values()); best=None
    for l in labs:
        s=math.log((docs[l]+1)/(N+len(labs))); den=totals[l]+V
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

def metrics(y):
    if not y: return {'accuracy':None,'balanced_accuracy':None,'n':0}
    acc=sum(a==b for a,b,_,_ in y)/len(y); by=defaultdict(list)
    for a,b,_,_ in y: by[a].append(a==b)
    bal=sum(sum(v)/len(v) for v in by.values())/len(by)
    return {'accuracy':acc,'balanced_accuracy':bal,'n':len(y),'classes':{k:len(v) for k,v in sorted(by.items())}}

def permute_sections(pages,rng):
    out=[dict(p) for p in pages]; strata=defaultdict(list)
    for i,p in enumerate(out): strata[(p['currier'],p['hand'])].append(i)
    for idx in strata.values():
        labels=[out[i]['illustration'] for i in idx]; rng.shuffle(labels)
        for i,l in zip(idx,labels): out[i]['illustration']=l
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--corpus',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); ap.add_argument('--permutations',type=int,default=999); a=ap.parse_args(); b=a.corpus.read_bytes()
    if blob_sha(b)!=SOURCE_BLOB: raise SystemExit('frozen corpus mismatch')
    pages=[p for p in parse(b.decode()) if section(p)]; obs=evaluate(pages,section); om=metrics(obs)
    cur=metrics(evaluate([p for p in pages if p['currier'] in ('A','B')],lambda p:p['currier']))
    hand=metrics(evaluate([p for p in pages if p['hand']!='?'],lambda p:p['hand']))
    rng=random.Random(SEED); null=[]
    for _ in range(a.permutations):
        pm=metrics(evaluate(permute_sections(pages,rng),section))['balanced_accuracy']
        if pm is not None: null.append(pm)
    p_mc=(1+sum(x>=om['balanced_accuracy'] for x in null))/(1+len(null)) if null and om['balanced_accuracy'] is not None else None
    result={'classification':'WEAK_SEMANTIC_SECTION_SIGNAL_NOT_TRANSLATION','source_blob':SOURCE_BLOB,'seed':SEED,'fold_unit':'quire','pages':len(pages),'section':om,'currier_control':cur,'hand_control':hand,'permutation_null':{'scheme':'shuffle section labels within Currier x hand strata','requested':a.permutations,'completed':len(null),'mean_balanced_accuracy':sum(null)/len(null) if null else None,'max_balanced_accuracy':max(null) if null else None,'monte_carlo_p':p_mc},'warning':'A significant section signal is evidence of topic/section association, not a token translation.'}
    a.out.write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result,indent=2))
if __name__=='__main__': main()

#!/usr/bin/env python3
"""Held-out EVA edge prediction; no semantic or language identification."""
import argparse, hashlib, json, math, random, re, sys
from collections import Counter, defaultdict
from pathlib import Path
from boundary_dependence import parse, SOURCE_BLOB

def samples(rows):
    out=[]
    for row in rows:
        w=row['words']; page=row['folio']
        leaf=re.sub(r'([rv]).*$', '', page)
        for i in range(1,len(w)):
            band=min(3,4*i//len(w))
            out.append((leaf,row['quire'] or 'UNKNOWN',band,w[i-1][-1],w[i][0]))
    return out

def train(data):
    base=Counter(); ctx=defaultdict(Counter); link=defaultdict(Counter)
    for leaf,q,b,x,y in data:
        base[y]+=1;ctx[q,b][y]+=1;link[q,b,x][y]+=1
    return base,ctx,link

def probs(model,q,b,x,y):
    base,ctx,link=model
    p=(base[y]+.5)/(sum(base.values())+13)
    c=ctx.get((q,b),{}); pc=(c.get(y,0)+20*p)/(sum(c.values())+20)
    c=link.get((q,b,x),{}); pl=(c.get(y,0)+20*pc)/(sum(c.values())+20)
    # For completely unseen quires, train a pooled position+edge distribution.
    return p,pc,pl

def fit_predict(data,scheme):
    groups=sorted(set(a[0 if scheme=='leaf5' else 1] for a in data))
    folds={g:i%5 for i,g in enumerate(groups)} if scheme=='leaf5' else {g:i for i,g in enumerate(groups)}
    agg=defaultdict(lambda:[0,0.,0.,0.])
    for fold in sorted(set(folds.values())):
        idx=0 if scheme=='leaf5' else 1
        tr=[s for s in data if folds[s[idx]]!=fold];te=[s for s in data if folds[s[idx]]==fold]
        # Pooled fallback trained exclusively on training samples.
        model=train(tr); pooled=train([(l,'POOL',b,x,y) for l,q,b,x,y in tr])
        known=set(s[1] for s in tr)
        for leaf,q,b,x,y in te:
            ps=probs(model,q,b,x,y) if q in known else probs(pooled,'POOL',b,x,y)
            a=agg[leaf if scheme=='leaf5' else q];a[0]+=1
            for j,p in enumerate(ps):a[j+1]+=-math.log2(p)
    n=sum(a[0] for a in agg.values()); losses=[sum(a[j] for a in agg.values())/n for j in (1,2,3)]
    values=list(agg.values());rng=random.Random(20261006);boot=[]
    for _ in range(999):
        draw=[rng.choice(values) for _ in values]
        boot.append(sum(a[2]-a[3] for a in draw)/sum(a[0] for a in draw))
    boot.sort()
    return {'pairs':n,'test_groups':len(agg),'loss_bits':dict(zip(['base','context','link'],losses)),
            'link_gain_over_context':losses[1]-losses[2],'bootstrap_95pct':[boot[24],boot[974]],
            'per_group':{g:{'pairs':a[0],'gain_bits':(a[2]-a[3])/a[0]} for g,a in agg.items()}}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--corpus',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    raw=args.corpus.read_bytes(); blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    assert blob==SOURCE_BLOB,(blob,SOURCE_BLOB)
    out={'classification':'HELD_OUT_EDGE_PREDICTION_NOT_TRANSLATION','python':sys.version.split()[0],'blob':blob,'sha256':hashlib.sha256(raw).hexdigest(),'smoothing':20,'seed':20261006,'results':{}}
    for mode in ('split','join'):
        rows,_,_=parse(raw.decode(),mode);data=samples(rows)
        out['results'][mode]={s:fit_predict(data,s) for s in ('leaf5','quire')}
    out['criterion_pass']=all(t['bootstrap_95pct'][0]>0 for m in out['results'].values() for t in m.values())
    args.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({m:{s:{k:v for k,v in t.items() if k!='per_group'} for s,t in tests.items()} for m,tests in out['results'].items()},indent=2));print('criterion_pass',out['criterion_pass'])
if __name__=='__main__':main()

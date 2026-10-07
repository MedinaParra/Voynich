#!/usr/bin/env python3
"""Confound-matched IVTFF label-pair lexical anchor audit.
No natural-language gloss is produced.
"""
import argparse, hashlib, json, re, random
from collections import Counter, defaultdict
from pathlib import Path

SOURCE_BLOB='2a4533ab9bdfa85db9bad602d590978953055df1'
PAIRS=[('Lc','Lf'),('Ln','Lt'),('Ls','Lz')]
SEED=20261007

def blob_sha(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def parse(raw):
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
        subtype=next((s for s in sum(([a,b] for a,b in PAIRS),[]) if s in pos),None)
        if not subtype: continue
        clean=re.sub(r'<[^>]*>',' ',text); clean=re.sub(r'\[[^]]*\]|\{[^}]*\}|@[0-9]+;',' ',clean)
        uncertain='?' in clean
        toks=re.findall(r'(?<![a-z])[a-z]{2,}(?![a-z])',clean.replace('?',' '))
        if len(toks)!=1 or uncertain: continue
        rows.append({'folio':fol,'subtype':subtype,'token':toks[0],**pages.get(fol,{'quire':'?','currier':'?','hand':'?'})})
    # collapse exact duplicate folio/subtype/token rows
    seen=set(); out=[]
    for r in rows:
        k=(r['folio'],r['subtype'],r['token'])
        if k not in seen: seen.add(k); out.append(r)
    return out

def feats(token, mode='ngram'):
    if mode=='length': return {f'LEN={min(len(token),10)}'}
    if mode=='edge': return {f'F={token[0]}',f'L={token[-1]}'}
    s=set()
    for n in (1,2,3):
        for i in range(len(token)-n+1): s.add(f'{n}:{token[i:i+n]}')
    return s

def train_nb(rows, classes, mode):
    # Bernoulli-like multinomial set-feature NB with Laplace smoothing.
    cc=Counter(r['subtype'] for r in rows); fc={c:Counter() for c in classes}; vocab=set()
    for r in rows:
        f=feats(r['token'],mode); vocab |= f
        for x in f: fc[r['subtype']][x]+=1
    return cc,fc,vocab

def predict(model, token, classes, mode):
    import math
    cc,fc,vocab=model; total=sum(cc.values()); f=feats(token,mode)
    scores={}
    for c in classes:
        score=math.log((cc[c]+1)/(total+len(classes)))
        denom=sum(fc[c].values())+len(vocab)+1
        for x in f: score += math.log((fc[c][x]+1)/denom)
        scores[c]=score
    return max(classes,key=lambda c:scores[c])

def metrics(rows, labels, classes, mode='ngram'):
    y=[]; p=[]; folds=0
    folios=sorted(set(r['folio'] for r in rows))
    for fol in folios:
        tr=[dict(r,subtype=labels[i]) for i,r in enumerate(rows) if r['folio']!=fol]
        te=[(i,r) for i,r in enumerate(rows) if r['folio']==fol]
        if set(x['subtype'] for x in tr)!=set(classes): continue
        true=[labels[i] for i,_ in te]
        if not set(true).issubset(set(classes)): continue
        model=train_nb(tr,classes,mode); folds+=1
        for i,r in te: y.append(labels[i]); p.append(predict(model,r['token'],classes,mode))
    rec={}
    for c in classes:
        ix=[i for i,v in enumerate(y) if v==c]; rec[c]=(sum(p[i]==c for i in ix)/len(ix)) if ix else None
    vals=[v for v in rec.values() if v is not None]
    ba=sum(vals)/len(vals) if vals else None
    return {'balanced_accuracy':ba,'recall':rec,'n_predictions':len(y),'evaluable_folds':folds,
            'confusion':{a:{b:sum(1 for yy,pp in zip(y,p) if yy==a and pp==b) for b in classes} for a in classes}}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--corpus',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); ap.add_argument('--permutations',type=int,default=999)
    a=ap.parse_args(); raw=a.corpus.read_bytes()
    if blob_sha(raw)!=SOURCE_BLOB: raise SystemExit('frozen corpus mismatch')
    allrows=parse(raw); rng=random.Random(SEED); results=[]
    for pair in PAIRS:
        rows=[r for r in allrows if r['subtype'] in pair]; labels=[r['subtype'] for r in rows]
        obs=metrics(rows,labels,pair,'ngram'); length=metrics(rows,labels,pair,'length'); edge=metrics(rows,labels,pair,'edge')
        byfol=defaultdict(list)
        for i,r in enumerate(rows): byfol[r['folio']].append(i)
        exch=[i for ix in byfol.values() if len(set(labels[j] for j in ix))==2 for i in ix]
        null=[]
        for _ in range(a.permutations):
            z=labels[:]
            for ix in byfol.values():
                if len(set(labels[j] for j in ix))==2:
                    vals=[z[j] for j in ix]; rng.shuffle(vals)
                    for j,v in zip(ix,vals): z[j]=v
            m=metrics(rows,z,pair,'ngram')['balanced_accuracy']
            if m is not None: null.append(m)
        pval=(1+sum(x>=obs['balanced_accuracy'] for x in null))/(1+len(null)) if null and obs['balanced_accuracy'] is not None else None
        coverage=len(exch)/len(rows) if rows else 0
        recalls=obs['recall']; gate=(obs['balanced_accuracy'] is not None and obs['balanced_accuracy']>0.60 and
             obs['balanced_accuracy']>(length['balanced_accuracy'] or 0) and obs['balanced_accuracy']>(edge['balanced_accuracy'] or 0) and
             pval is not None and pval<=0.01 and coverage>=0.25 and all((recalls[c] or 0)>0.50 for c in pair))
        status='PAIR_CANDIDATE' if gate else ('BLOCKED_CONFOUND' if coverage<0.25 else 'FAIL')
        results.append({'pair':pair,'labels':len(rows),'folios':len(set(r['folio'] for r in rows)),'counts':dict(Counter(labels)),
          'currier_hand':dict(Counter(f"{r['currier']}|{r['hand']}" for r in rows)),'primary':obs,'length_control':length,'edge_control':edge,
          'exchangeable_labels':len(exch),'exchangeable_coverage':coverage,'permutations':len(null),'null_mean_ba':sum(null)/len(null) if null else None,
          'monte_carlo_p':pval,'status':status})
    candidates=sum(r['status']=='PAIR_CANDIDATE' for r in results)
    blocked=sum(r['status']=='BLOCKED_CONFOUND' for r in results)
    classification='PASS_EXPLORATORY_LEXICAL_ANCHOR' if candidates>=2 else ('BLOCKED_CONFOUND' if blocked==len(results) else 'FAIL_EXECUTED')
    out={'classification':classification,'source_blob':SOURCE_BLOB,'seed':SEED,'pairs':results,'candidate_pairs':candidates,
         'interpretation_ceiling':'visual-class lexical-anchor candidate; not a gloss or translation'}
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__': main()

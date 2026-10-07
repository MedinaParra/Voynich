#!/usr/bin/env python3
"""Preregistered folio-level Ls/Lz null. No gloss or translation."""
import argparse, hashlib, json, math, random, re
from collections import Counter, defaultdict
from pathlib import Path

SOURCE_BLOB='2a4533ab9bdfa85db9bad602d590978953055df1'
PAIR=('Ls','Lz'); SEED=20261007

def blob_sha(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def parse(raw):
    pages={}; rows=[]
    for line in raw.decode().splitlines():
        p=re.match(r'^<([^>.,]+)>\s*<!([^>]*)>',line)
        if p:
            fol=p.group(1); m=dict(re.findall(r'\$([A-Z])=([^\s>]+)',p.group(2)))
            pages[fol]={'currier':m.get('L','?'),'hand':m.get('H','?'),'quire':m.get('Q','?')}
            continue
        m=re.match(r'^<([^>]+)>\s*(.*)$',line)
        if not m or ',' not in m.group(1): continue
        locus,text=m.groups(); fol=locus.split('.')[0]; pos=locus.split(',',1)[1]
        subtype=next((s for s in PAIR if s in pos),None)
        if not subtype: continue
        clean=re.sub(r'<[^>]*>',' ',text); clean=re.sub(r'\[[^]]*\]|\{[^}]*\}|@[0-9]+;',' ',clean)
        uncertain='?' in clean
        toks=re.findall(r'(?<![a-z])[a-z]{2,}(?![a-z])',clean.replace('?',' '))
        if len(toks)!=1 or uncertain: continue
        rows.append({'folio':fol,'subtype':subtype,'token':toks[0],**pages.get(fol,{'currier':'?','hand':'?','quire':'?'})})
    seen=set(); out=[]
    for r in rows:
        k=(r['folio'],r['subtype'],r['token'])
        if k not in seen: seen.add(k); out.append(r)
    return out

def feats(token,mode):
    if mode=='length': return {f'LEN={min(len(token),10)}'}
    if mode=='edge': return {f'F={token[0]}',f'L={token[-1]}'}
    s=set()
    for n in (1,2,3):
        for i in range(len(token)-n+1): s.add(f'{n}:{token[i:i+n]}')
    return s

def train(rows,mode):
    cc=Counter(r['subtype'] for r in rows); fc={c:Counter() for c in PAIR}; vocab=set()
    for r in rows:
        f=feats(r['token'],mode); vocab|=f
        for x in f: fc[r['subtype']][x]+=1
    return cc,fc,vocab

def pred(model,token,mode):
    cc,fc,vocab=model; total=sum(cc.values()); scores={}
    for c in PAIR:
        score=math.log((cc[c]+1)/(total+2)); den=sum(fc[c].values())+len(vocab)+1
        for x in feats(token,mode): score+=math.log((fc[c][x]+1)/den)
        scores[c]=score
    return max(PAIR,key=scores.get)

def evaluate(base_rows, folio_labels, mode):
    rows=[dict(r,subtype=folio_labels[r['folio']]) for r in base_rows]
    y=[]; p=[]; eval_fol=Counter()
    for fol in sorted(folio_labels):
        tr=[r for r in rows if r['folio']!=fol]; te=[r for r in rows if r['folio']==fol]
        if set(r['subtype'] for r in tr)!=set(PAIR) or not te: continue
        model=train(tr,mode)
        for r in te: y.append(r['subtype']); p.append(pred(model,r['token'],mode))
        eval_fol[folio_labels[fol]]+=1
    rec={}
    for c in PAIR:
        ix=[i for i,v in enumerate(y) if v==c]
        rec[c]=sum(p[i]==c for i in ix)/len(ix) if ix else None
    ba=sum(rec.values())/2 if all(rec[c] is not None for c in PAIR) else None
    return {'balanced_accuracy':ba,'recall':rec,'n_predictions':len(y),'evaluable_folios':dict(eval_fol)}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--corpus',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); ap.add_argument('--permutations',type=int,default=999)
    a=ap.parse_args(); raw=a.corpus.read_bytes()
    if blob_sha(raw)!=SOURCE_BLOB: raise SystemExit('frozen corpus mismatch')
    rows=parse(raw); byfol=defaultdict(list)
    for r in rows: byfol[r['folio']].append(r)
    mixed=sorted(f for f,rr in byfol.items() if len(set(x['subtype'] for x in rr))!=1)
    rows=[r for r in rows if r['folio'] not in mixed]; byfol=defaultdict(list)
    for r in rows: byfol[r['folio']].append(r)
    labels={f:rr[0]['subtype'] for f,rr in byfol.items()}
    fcounts=Counter(labels.values())
    obs=evaluate(rows,labels,'ngram'); length=evaluate(rows,labels,'length'); edge=evaluate(rows,labels,'edge')
    strata=defaultdict(list)
    for f,rr in byfol.items(): strata[f"{rr[0]['currier']}|{rr[0]['hand']}"].append(f)
    valid_strata={k:v for k,v in strata.items() if all(sum(labels[f]==c for f in v)>=2 for c in PAIR)}
    use_stratified=bool(valid_strata) and sum(len(v) for v in valid_strata.values())==len(labels)
    rng=random.Random(SEED); null=[]
    for _ in range(a.permutations):
        z=dict(labels)
        groups=list(valid_strata.values()) if use_stratified else [sorted(labels)]
        for fs in groups:
            vals=[labels[f] for f in fs]; rng.shuffle(vals)
            for f,v in zip(fs,vals): z[f]=v
        m=evaluate(rows,z,'ngram')['balanced_accuracy']
        if m is not None: null.append(m)
    pval=(1+sum(x>=obs['balanced_accuracy'] for x in null))/(1+len(null)) if null and obs['balanced_accuracy'] is not None else None
    enough=all(obs['evaluable_folios'].get(c,0)>=5 for c in PAIR)
    perm_ok=len(null)==a.permutations and len(labels)>=2
    gate=enough and perm_ok and obs['balanced_accuracy']>0.60 and obs['balanced_accuracy']>(length['balanced_accuracy'] or 0) and obs['balanced_accuracy']>(edge['balanced_accuracy'] or 0) and pval<=0.01 and all(obs['recall'][c]>0.50 for c in PAIR)
    status='PASS_EXPLORATORY' if gate else ('BLOCKED' if not enough or not perm_ok else 'FAIL')
    out={'classification':status,'source_blob':SOURCE_BLOB,'seed':SEED,'labels':len(rows),'folios':len(labels),'folio_class_counts':dict(fcounts),'mixed_folios_excluded':mixed,'permutation_scheme':'within Currier|hand strata' if use_stratified else 'global folio-level fallback','strata':{k:len(v) for k,v in strata.items()},'primary':obs,'length_control':length,'edge_control':edge,'permutations':len(null),'null_mean_ba':sum(null)/len(null) if null else None,'null_max_ba':max(null) if null else None,'monte_carlo_p':pval,'interpretation_ceiling':'folio-generalizing visual-class association; not a gloss or translation'}
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__': main()

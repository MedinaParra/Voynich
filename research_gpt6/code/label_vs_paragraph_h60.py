#!/usr/bin/env python3
# H60 strict L-vs-P replication. Protocol frozen in preregistration.
import argparse,hashlib,json,math,random,re
from collections import defaultdict
from pathlib import Path
SOURCE_BLOB='2a4533ab9bdfa85db9bad602d590978953055df1'
SEED=20261007

def blob_sha(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def feats(t): return [t.count('o')/len(t),t.count('a')/len(t),t.count('y')/len(t),float(t.startswith('q')),float(t.endswith('y'))]
def clean_tokens(text):
    clean=re.sub(r'<[^>]*>|\[[^]]*\]|\{[^}]*\}|@[0-9]+;',' ',text).replace('?',' ')
    return re.findall(r'(?<![a-z])[a-z]{2,}(?![a-z])',clean)

def parse(raw):
    pages={}; positives=[]; paragraph=defaultdict(list)
    for line in raw.splitlines():
        p=re.match(r'^<([^>.,]+)>\s*<!([^>]*)>',line)
        if p:
            m=dict(re.findall(r'\$([A-Z])=([^\s>]+)',p.group(2)))
            pages[p.group(1)]={'currier':m.get('L','?'),'hand':m.get('H','?')}
            continue
        m=re.match(r'^<([^>]+)>\s*(.*)$',line)
        if not m or ',' not in m.group(1): continue
        locus,text=m.groups(); fol=locus.split('.')[0]; pos=locus.split(',',1)[1]; meta=pages.get(fol,{})
        toks=clean_tokens(text)
        lm=re.search(r'(L[A-Za-z]?)',pos)
        pm=re.search(r'(P(?:[01bcrt])?)',pos)
        if lm and len(toks)==1 and '?' not in text:
            positives.append({'folio':fol,'token':toks[0],**meta}); continue
        # H60 strict control: ONLY IVTFF P* paragraph loci. C*, R*, other locus types excluded.
        if pm and not lm:
            for t in toks:
                paragraph[(fol,meta.get('currier','?'),meta.get('hand','?'),len(t))].append(t)
    return positives,paragraph

def build_pairs(pos,paragraph):
    rng=random.Random(SEED); pairs=[]; excluded=0
    for r in sorted(pos,key=lambda x:(x['folio'],x['token'],x['currier'],x['hand'])):
        key=(r['folio'],r['currier'],r['hand'],len(r['token'])); cand=paragraph.get(key,[])
        if not cand: excluded+=1; continue
        pairs.append({'folio':r['folio'],'positive':r['token'],'control':cand[rng.randrange(len(cand))]})
    return pairs,excluded

def standardize(X,T):
    d=len(X[0]); mu=[sum(x[j] for x in X)/len(X) for j in range(d)]; sd=[]
    for j in range(d):
        v=sum((x[j]-mu[j])**2 for x in X)/len(X); sd.append(math.sqrt(v) if v>0 else 1.0)
    return [[(x[j]-mu[j])/sd[j] for j in range(d)] for x in X], [[(x[j]-mu[j])/sd[j] for j in range(d)] for x in T]
def d2(a,b): return sum((x-y)**2 for x,y in zip(a,b))
def score(pairs,labels=None):
    if labels is None: labels=[1]*len(pairs)
    preds=[]; truth=[]
    for fol in sorted(set(p['folio'] for p in pairs)):
        tr=[i for i,p in enumerate(pairs) if p['folio']!=fol]; te=[i for i,p in enumerate(pairs) if p['folio']==fol]
        if not tr or not te: continue
        X=[]; y=[]; T=[]; yt=[]
        for i in tr:
            a,b=pairs[i]['positive'],pairs[i]['control']; lab=labels[i]; X.extend([feats(a),feats(b)]); y.extend([lab,1-lab])
        for i in te:
            a,b=pairs[i]['positive'],pairs[i]['control']; lab=labels[i]; T.extend([feats(a),feats(b)]); yt.extend([lab,1-lab])
        X,T=standardize(X,T); means={}
        for c in (0,1):
            z=[X[j] for j,v in enumerate(y) if v==c]; means[c]=[sum(x[k] for x in z)/len(z) for k in range(len(z[0]))]
        preds.extend([min((0,1),key=lambda c:d2(x,means[c])) for x in T]); truth.extend(yt)
    rec=[]
    for c in (0,1):
        ix=[i for i,v in enumerate(truth) if v==c]; rec.append(sum(preds[i]==c for i in ix)/len(ix))
    return sum(rec)/2

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--corpus',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); ap.add_argument('--permutations',type=int,default=999); a=ap.parse_args(); b=a.corpus.read_bytes()
    if blob_sha(b)!=SOURCE_BLOB: raise SystemExit('frozen corpus mismatch')
    pos,paragraph=parse(b.decode()); pairs,excluded=build_pairs(pos,paragraph); nfol=len(set(p['folio'] for p in pairs))
    out={'classification':'STRICT_LABEL_VS_PARAGRAPH_NOT_TRANSLATION','source_blob':SOURCE_BLOB,'seed':SEED,'positive_tokens':len(pos),'matched_pairs':len(pairs),'represented_folios':nfol,'excluded_no_match':excluded,'permutations_requested':a.permutations}
    if len(pairs)<60 or nfol<8:
        out.update({'status':'BLOCKED','permutations_completed':0,'reason':'preregistered matching/sample threshold not met'}); a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2)); return
    obs=score(pairs); rng=random.Random(SEED); null=[score(pairs,[rng.randrange(2) for _ in pairs]) for _ in range(a.permutations)]
    p=(1+sum(x>=obs for x in null))/(1+len(null)); status='PASS' if obs>0.5 and p<=0.05 and len(null)==999 else 'FAIL'
    out.update({'observed_balanced_accuracy':obs,'null_mean_balanced_accuracy':sum(null)/len(null),'monte_carlo_p':p,'permutations_completed':len(null),'status':status})
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__': main()

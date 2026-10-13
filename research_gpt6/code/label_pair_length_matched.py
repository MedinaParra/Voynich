#!/usr/bin/env python3
import argparse, hashlib, json, random, re
from collections import Counter, defaultdict
from pathlib import Path
SOURCE_BLOB='2a4533ab9bdfa85db9bad602d590978953055df1'
SEED=20261006

def blob_sha(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def feats(t): return [len(t),t.count('o')/len(t),t.count('a')/len(t),t.count('y')/len(t),t.startswith('q'),t.endswith('y')]
def dist(a,b): return sum((float(x)-float(y))**2 for x,y in zip(a,b))
def parse(raw):
 pages={}; rows=[]
 for line in raw.splitlines():
  p=re.match(r'^<([^>.,]+)>\s*<!([^>]*)>',line)
  if p:
   m=dict(re.findall(r'\$([A-Z])=([^\s>]+)',p.group(2))); pages[p.group(1)]={'quire':m.get('Q','?'),'currier':m.get('L','?'),'hand':m.get('H','?')}; continue
  m=re.match(r'^<([^>]+)>\s*(.*)$',line)
  if not m or ',' not in m.group(1): continue
  locus,text=m.groups(); fol=locus.split('.')[0]; pos=locus.split(',',1)[1]; sub=next((s for s in ('Lc','Lf') if s in pos),None)
  if not sub: continue
  clean=re.sub(r'<[^>]*>|\[[^]]*\]|\{[^}]*\}|@[0-9]+;',' ',text); uncertain='?' in clean
  toks=re.findall(r'(?<![a-z])[a-z]{2,}(?![a-z])',clean.replace('?',' '))
  meta=pages.get(fol,{})
  if len(toks)==1 and not uncertain and meta.get('currier')=='A' and meta.get('hand')=='1' and meta.get('quire') in ('O','S'):
   rows.append({'y':sub,'token':toks[0],**meta})
 return rows

def predict(train,test):
 means={}
 for c in ('Lc','Lf'):
  xs=[feats(r['token']) for r in train if r['y']==c]
  if not xs:return None
  means[c]=[sum(float(z[i]) for z in xs)/len(xs) for i in range(len(xs[0]))]
 return [min(means,key=lambda c:dist(feats(r['token']),means[c])) for r in test]
def bal(y,p):
 vals=[]
 for c in ('Lc','Lf'):
  ix=[i for i,v in enumerate(y) if v==c]
  if not ix:return None
  vals.append(sum(p[i]==c for i in ix)/len(ix))
 return sum(vals)/2

def matched_test(rows,q,seed):
 rng=random.Random(seed + ord(q[0])); groups=defaultdict(lambda:defaultdict(list))
 for r in rows:
  if r['quire']==q: groups[len(r['token'])][r['y']].append(r)
 out=[]; report={}
 for L in sorted(groups):
  a=list(groups[L]['Lc']); b=list(groups[L]['Lf'])
  if not a or not b: continue
  n=min(len(a),len(b)); rng.shuffle(a); rng.shuffle(b); out += a[:n]+b[:n]
  report[str(L)]={'Lc':n,'Lf':n}
 return out,report

def evaluate(rows):
 folds=[]
 for q in ('O','S'):
  tr=[r for r in rows if r['quire']!=q]; te,bylen=matched_test(rows,q,SEED)
  counts=Counter(r['y'] for r in te)
  if counts['Lc']<10 or counts['Lf']<10:
   folds.append({'quire':q,'matched_counts':dict(counts),'by_length':bylen,'balanced_accuracy':None,'minimum_sample_pass':False}); continue
  p=predict(tr,te); s=bal([r['y'] for r in te],p)
  folds.append({'quire':q,'matched_counts':dict(counts),'by_length':bylen,'balanced_accuracy':s,'minimum_sample_pass':True})
 valid=[f for f in folds if f['balanced_accuracy'] is not None]
 return (sum(f['balanced_accuracy'] for f in valid)/2 if len(valid)==2 else None),folds

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--corpus',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); ap.add_argument('--permutations',type=int,default=999); a=ap.parse_args(); b=a.corpus.read_bytes()
 if blob_sha(b)!=SOURCE_BLOB: raise SystemExit('frozen corpus mismatch')
 rows=parse(b.decode()); obs,folds=evaluate(rows)
 if obs is None:
  result={'classification':'LEXICAL_ANCHOR_EXACT_LENGTH_MATCHED_CONTROL_NOT_TRANSLATION','source_blob':SOURCE_BLOB,'counts':dict(Counter(r['y'] for r in rows)),'folds':folds,'balanced_accuracy':None,'permutations_completed':0,'monte_carlo_p':None,'status':'BLOCKED'}
 else:
  rng=random.Random(SEED); null=[]
  for _ in range(a.permutations):
   rr=[dict(r) for r in rows]; strata=defaultdict(list)
   for i,r in enumerate(rr): strata[(r['quire'],len(r['token']))].append(i)
   for ix in strata.values():
    ys=[rr[i]['y'] for i in ix]; rng.shuffle(ys)
    for i,y in zip(ix,ys): rr[i]['y']=y
   s,_=evaluate(rr)
   if s is not None:null.append(s)
  p=(1+sum(x>=obs for x in null))/(1+len(null)) if len(null)==a.permutations else None
  status='BLOCKED' if p is None else ('PASS' if obs>0.5 and p<=0.05 else 'FAIL')
  result={'classification':'LEXICAL_ANCHOR_EXACT_LENGTH_MATCHED_CONTROL_NOT_TRANSLATION','source_blob':SOURCE_BLOB,'counts':dict(Counter(r['y'] for r in rows)),'folds':folds,'balanced_accuracy':obs,'permutations_completed':len(null),'monte_carlo_p':p,'status':status}
 a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result,indent=2))
if __name__=='__main__': main()

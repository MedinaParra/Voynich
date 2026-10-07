#!/usr/bin/env python3
import argparse, hashlib, json, math, random, re
from collections import Counter, defaultdict
from pathlib import Path
SHA='db624a731114f26854bbfe3a59d40827fa8911be46d086b6c558d99e557241ee'
SEED=690069; NPERM=999; ALPHA=.05/3
STRATA={('O','A','1'):('Lc','Lf'),('S','A','1'):('Lc','Lf'),('M','B','2'):('Ln','Lt')}

def feats(t):
 n=len(t); c=Counter(t); k=len(c); eq=len(set(tuple(j for j,x in enumerate(t) if x==ch) for ch in c))
 return [float(n),float(k),float(sum(t[i]==t[i-1] for i in range(1,n))),float(max(c.values())),eq/n]
def clean(s):
 s=re.sub(r'<[^>]*>|\[[^]]*\]|\{[^}]*\}|@[0-9]+;',' ',s).replace('?',' ')
 return re.findall(r'(?<![a-z])[a-z]{2,}(?![a-z])',s)
def parse(raw):
 meta={}; rows=[]
 for line in raw.splitlines():
  p=re.match(r'^<([^>.,]+)>\s*<!([^>]*)>',line)
  if p:
   m=dict(re.findall(r'\$([A-Z])=([^\s>]+)',p.group(2))); meta[p.group(1)]=(m.get('Q','?'),m.get('L','?'),m.get('H','?')); continue
  m=re.match(r'^<([^>]+)>\s*(.*)$',line)
  if not m or ',' not in m.group(1): continue
  loc,text=m.groups(); fol=loc.split('.')[0]; pos=loc.split(',',1)[1]; u=re.search(r'([A-Z][a-z0-9]?)',pos)
  if not u or u.group(1) not in {'Lc','Lf','Ln','Lt'} or '?' in text: continue
  toks=clean(text)
  for t in toks: rows.append((fol,meta.get(fol,('?','?','?')),u.group(1),t))
 return rows
def centroid_fit(rows,a,b):
 X=[feats(r[3]) for r in rows]; y=[0 if r[2]==a else 1 for r in rows]; d=len(X[0]); mu=[sum(x[j] for x in X)/len(X) for j in range(d)]; sd=[]
 for j in range(d):
  v=sum((x[j]-mu[j])**2 for x in X)/len(X); sd.append(math.sqrt(v) if v else 1.)
 Z=[[(x[j]-mu[j])/sd[j] for j in range(d)] for x in X]; means=[]
 for c in (0,1):
  zz=[Z[i] for i,v in enumerate(y) if v==c]; means.append([sum(x[j] for x in zz)/len(zz) for j in range(d)])
 return mu,sd,means
def pred(t,model):
 mu,sd,means=model; x=feats(t); z=[(x[j]-mu[j])/sd[j] for j in range(len(x))]; ds=[sum((z[j]-means[c][j])**2 for j in range(len(z))) for c in (0,1)]; return 0 if ds[0]<=ds[1] else 1
def ba(truth,p):
 rs=[]
 for c in (0,1):
  ix=[i for i,v in enumerate(truth) if v==c]; rs.append(sum(p[i]==c for i in ix)/len(ix) if ix else 0)
 return sum(rs)/2
def evaluate(rows,a,b,labels=None):
 fols=sorted(set(r[0] for r in rows)); truth=[]; pp=[]; valid=[]
 labmap=labels or {r[0]:None for r in rows}
 for f in fols:
  tr=[r for r in rows if r[0]!=f]; te=[r for r in rows if r[0]==f]
  if labels:
   tr=[(r[0],r[1],labels[r[0]],r[3]) for r in tr]; te=[(r[0],r[1],labels[r[0]],r[3]) for r in te]
  if set(r[2] for r in tr)!={a,b}: continue
  model=centroid_fit(tr,a,b); valid.append(f)
  for r in te: truth.append(0 if r[2]==a else 1); pp.append(pred(r[3],model))
 return (ba(truth,pp) if truth and set(truth)=={0,1} else None),valid

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--source',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args(); b=a.source.read_bytes(); sha=hashlib.sha256(b).hexdigest()
 if sha!=SHA: raise SystemExit('frozen source mismatch '+sha)
 allrows=parse(b.decode(errors='replace')); out={'classification':'WITHIN_DOCUMENTARY_STRATUM_LABEL_SUBTYPE_FORM_NOT_SEMANTICS','sha256':sha,'seed':SEED,'permutations':NPERM,'alpha_bonferroni':ALPHA,'strata':{}}
 passes=0; executable=0
 for key,(ca,cb) in STRATA.items():
  rows=[r for r in allrows if r[1]==key and r[2] in (ca,cb)]; counts={c:sum(r[2]==c for r in rows) for c in (ca,cb)}; fols=sorted(set(r[0] for r in rows)); obs,valid=evaluate(rows,ca,cb)
  rec={'classes':[ca,cb],'counts':counts,'folios':len(fols),'valid_test_folios':len(valid),'observed_balanced_accuracy':obs,'majority_baseline_balanced_accuracy':.5}
  if obs is None or len(valid)<3:
   rec.update(status='BLOCKED',reason='insufficient valid LOFO folds'); out['strata']['|'.join(key)]=rec; continue
  executable+=1; rng=random.Random(SEED+sum(map(ord,''.join(key)))); null=[]
  orig={f:Counter(r[2] for r in rows if r[0]==f).most_common(1)[0][0] for f in fols}; labs=list(orig.values())
  for _ in range(NPERM):
   q=labs[:]; rng.shuffle(q); lm=dict(zip(fols,q)); v,_=evaluate(rows,ca,cb,lm)
   if v is not None: null.append(v)
  p=(1+sum(v>=obs for v in null))/(1+len(null)); st='PASS' if obs>=.60 and p<=ALPHA and len(null)==NPERM else 'FAIL'; passes+=st=='PASS'; rec.update(permutations_completed=len(null),null_mean=sum(null)/len(null) if null else None,monte_carlo_p=p,status=st); out['strata']['|'.join(key)]=rec
 out['status']='BLOCKED' if executable<3 else ('PASS' if passes>=2 else 'FAIL'); out['passing_strata']=passes
 a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__': main()

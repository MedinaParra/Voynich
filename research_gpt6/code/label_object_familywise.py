#!/usr/bin/env python3
import argparse,hashlib,json,math,random,re
from collections import Counter,defaultdict
from itertools import combinations
from pathlib import Path
SOURCE_BLOB='2a4533ab9bdfa85db9bad602d590978953055df1'
SEED=20261006

def blob_sha(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def feats(t): return [t.count('o')/len(t),t.count('a')/len(t),t.count('y')/len(t),float(t.startswith('q')),float(t.endswith('y'))]
def parse(raw):
 pages={}; rows=[]
 for line in raw.splitlines():
  p=re.match(r'^<([^>.,]+)>\s*<!([^>]*)>',line)
  if p:
   m=dict(re.findall(r'\$([A-Z])=([^\s>]+)',p.group(2))); pages[p.group(1)]={'quire':m.get('Q','?'),'currier':m.get('L','?'),'hand':m.get('H','?')}; continue
  m=re.match(r'^<([^>]+)>\s*(.*)$',line)
  if not m or ',' not in m.group(1): continue
  locus,text=m.groups(); fol=locus.split('.')[0]; pos=locus.split(',',1)[1]
  cm=re.search(r'(L[A-Za-z]?)',pos)
  if not cm: continue
  code=cm.group(1)
  clean=re.sub(r'<[^>]*>|\[[^]]*\]|\{[^}]*\}|@[0-9]+;',' ',text); uncertain='?' in clean
  toks=re.findall(r'(?<![a-z])[a-z]{2,}(?![a-z])',clean.replace('?',' ')); meta=pages.get(fol,{})
  if len(toks)==1 and not uncertain and meta.get('currier')=='A' and meta.get('hand')=='1' and meta.get('quire') not in (None,'?'):
   rows.append({'y':code,'token':toks[0],**meta})
 return rows

def match_fold(rows,pair,q):
 g=defaultdict(lambda:defaultdict(list))
 for i,r in enumerate(rows):
  if r['quire']==q and r['y'] in pair:g[len(r['token'])][r['y']].append(i)
 out=[]
 for L in sorted(g):
  a=sorted(g[L][pair[0]]); b=sorted(g[L][pair[1]]); n=min(len(a),len(b)); out+=a[:n]+b[:n]
 return out

def standardize(train,test):
 X=[feats(r['token']) for r in train]; T=[feats(r['token']) for r in test]; d=len(X[0]); mu=[sum(x[j] for x in X)/len(X) for j in range(d)]; sd=[]
 for j in range(d):
  v=sum((x[j]-mu[j])**2 for x in X)/len(X); sd.append(math.sqrt(v) if v>0 else 1.0)
 return [[(x[j]-mu[j])/sd[j] for j in range(d)] for x in X], [[(x[j]-mu[j])/sd[j] for j in range(d)] for x in T]
def d2(a,b):return sum((x-y)**2 for x,y in zip(a,b))
def fold_score(rows,pair,q,ix):
 train=[r for r in rows if r['quire']!=q and r['y'] in pair]; test=[rows[i] for i in ix]
 if not test or any(not any(r['y']==c for r in train) for c in pair):return None
 X,T=standardize(train,test); means={}
 for c in pair:
  z=[X[i] for i,r in enumerate(train) if r['y']==c]; means[c]=[sum(x[j] for x in z)/len(z) for j in range(len(z[0]))]
 pred=[min(pair,key=lambda c:d2(x,means[c])) for x in T]; recalls=[]
 for c in pair:
  jj=[i for i,r in enumerate(test) if r['y']==c]; recalls.append(sum(pred[i]==c for i in jj)/len(jj))
 return sum(recalls)/2

def freeze_pairs(rows):
 counts=Counter(r['y'] for r in rows); eligible=sorted(c for c,n in counts.items() if n>=20); frozen={}
 for pair in combinations(eligible,2):
  folds=[]; total=0
  for q in sorted(set(r['quire'] for r in rows)):
   ix=match_fold(rows,pair,q)
   cc=Counter(rows[i]['y'] for i in ix)
   if cc[pair[0]] and cc[pair[1]]:
    folds.append((q,ix)); total+=min(cc[pair[0]],cc[pair[1]])
  if len(folds)>=2 and total>=10:frozen[pair]=folds
 return counts,eligible,frozen

def evaluate_pair(rows,pair,folds):
 vals=[]; details=[]; correct={pair[0]:0,pair[1]:0}; totals={pair[0]:0,pair[1]:0}
 for q,ix in folds:
  s=fold_score(rows,pair,q,ix)
  if s is None:return None,[]
  # balanced fold sizes are exact matched, so aggregate BA equals weighted accuracy by matched n
  n=Counter(rows[i]['y'] for i in ix)[pair[0]]; vals.append((s,n)); details.append({'quire':q,'matched_per_class':n,'balanced_accuracy':s})
 return sum(s*n for s,n in vals)/sum(n for _,n in vals),details

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--corpus',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--permutations',type=int,default=999);a=ap.parse_args();b=a.corpus.read_bytes()
 if blob_sha(b)!=SOURCE_BLOB:raise SystemExit('frozen corpus mismatch')
 rows=parse(b.decode());counts,eligible,frozen=freeze_pairs(rows); out={'classification':'LABEL_OBJECT_FAMILYWISE_SCREEN_NOT_TRANSLATION','source_blob':SOURCE_BLOB,'label_counts':dict(sorted(counts.items())),'eligible_codes':eligible,'evaluable_pairs':len(frozen),'permutations_requested':a.permutations}
 if not frozen:
  out.update({'status':'BLOCKED','permutations_completed':0,'reason':'no evaluable pair'});a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return
 observed={}; details={}
 for pair,folds in frozen.items():
  s,d=evaluate_pair(rows,pair,folds); observed[pair]=s;details[pair]=d
 rng=random.Random(SEED); nullmax=[]
 for _ in range(a.permutations):
  rr=[dict(r) for r in rows]; strata=defaultdict(list)
  for i,r in enumerate(rr):strata[(r['quire'],len(r['token']))].append(i)
  for ix in strata.values():
   ys=[rr[i]['y'] for i in ix];rng.shuffle(ys)
   for i,y in zip(ix,ys):rr[i]['y']=y
  vals=[]
  for pair,folds in frozen.items():
   s,_=evaluate_pair(rr,pair,folds)
   if s is None:raise SystemExit('frozen pair became unevaluable under stratum-preserving permutation')
   vals.append(s-0.5)
  nullmax.append(max(vals))
 results=[]
 for pair in sorted(frozen):
  s=observed[pair];p=(1+sum(x>=s-0.5 for x in nullmax))/(1+len(nullmax));status='PASS' if s>0.5 and p<=0.05 else 'FAIL';results.append({'pair':list(pair),'balanced_accuracy':s,'familywise_p':p,'status':status,'folds':details[pair]})
 out['pairs']=results;out['permutations_completed']=len(nullmax);out['null_max_mean']=sum(nullmax)/len(nullmax);out['status']='PASS' if any(x['status']=='PASS' for x in results) else 'FAIL'
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()

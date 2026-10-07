#!/usr/bin/env python3
"""Adversarial holdout test for candidate Voynich prefix substitutions.
Discovers shared stems on training folios and asks whether the same prefix pair
continues to induce distinguishable local contexts on held-out folios.
Exploratory structural evidence only; never a translation claim.
"""
import argparse, hashlib, json, math, re
from collections import Counter, defaultdict
from pathlib import Path
BLOB='2a4533ab9bdfa85db9bad602d590978953055df1'
PREFIXES=('qok','pol','sol','ych','ysh','dsh','ch','sh','qo','ok','ot')
def gitblob(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def js(a,b):
 keys=set(a)|set(b);sa=sum(a.values());sb=sum(b.values())
 if not sa or not sb:return None
 p={k:a[k]/sa for k in keys};q={k:b[k]/sb for k in keys};m={k:(p[k]+q[k])/2 for k in keys}
 def kl(x):return sum(v*math.log2(v/m[k]) for k,v in x.items() if v and m[k])
 return (kl(p)+kl(q))/2

def parse(b):
 rows=[]
 for line in b.decode().splitlines():
  m=re.match(r'^<([^>]+)>\s*(.*)$',line)
  if not m:continue
  loc=m.group(1); text=m.group(2); clean=re.sub(r'<[^>]*>','',text)
  if ',' in text or '<->' in text or not re.fullmatch(r'[a-z.\s]+',clean):continue
  w=[x for x in re.split(r'[.\s]+',clean.strip()) if x]
  fm=re.match(r'(f\d+[rv]\d*)',loc)
  if w and fm: rows.append((fm.group(1),w))
 return rows

def collect(rows,folios):
 counts=Counter();ctx=defaultdict(Counter);stems=defaultdict(Counter)
 for folio,w in rows:
  if folio not in folios:continue
  for i,x in enumerate(w):
   p=next((p for p in PREFIXES if x.startswith(p) and len(x)>len(p)+1),None)
   if not p:continue
   stem=x[len(p):];k=(p,stem);counts[k]+=1;stems[stem][p]+=1
   if i:ctx[k]['L:'+w[i-1]]+=1
   if i+1<len(w):ctx[k]['R:'+w[i+1]]+=1
 return counts,ctx,stems

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--corpus',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--min-train',type=int,default=3);ap.add_argument('--min-test',type=int,default=2);a=ap.parse_args();b=a.corpus.read_bytes()
 if gitblob(b)!=BLOB:raise SystemExit('Corpus blob mismatch')
 rows=parse(b);folios=sorted({f for f,_ in rows},key=lambda s:(int(re.search(r'\d+',s).group()),s))
 folds=[]
 for parity in (0,1):
  test={f for i,f in enumerate(folios) if i%2==parity};train=set(folios)-test
  tc,tctx,tst=collect(rows,train);vc,vctx,vst=collect(rows,test)
  pair_train=defaultdict(list);pair_test=defaultdict(list)
  for stem,pc in tst.items():
   ps=[p for p,n in pc.items() if n>=a.min_train]
   for i,p1 in enumerate(ps):
    for p2 in ps[i+1:]:
     pair=tuple(sorted((p1,p2)));j=js(tctx[(p1,stem)],tctx[(p2,stem)])
     if j is not None:pair_train[pair].append((stem,j))
  for pair,vals in pair_train.items():
   for stem,_ in vals:
    if vc[(pair[0],stem)]>=a.min_test and vc[(pair[1],stem)]>=a.min_test:
     j=js(vctx[(pair[0],stem)],vctx[(pair[1],stem)])
     if j is not None:pair_test[pair].append((stem,j))
  out=[]
  for pair,tr in pair_train.items():
   te=pair_test.get(pair,[])
   if len(tr)>=3 and len(te)>=2:
    out.append({'prefix_pair':list(pair),'train_shared_stems':len(tr),'test_shared_stems':len(te),'train_mean_js':sum(x[1] for x in tr)/len(tr),'test_mean_js':sum(x[1] for x in te)/len(te),'test_stems':[x[0] for x in te]})
  out.sort(key=lambda z:(z['test_shared_stems'],z['test_mean_js']),reverse=True)
  folds.append({'test_parity':parity,'train_folios':len(train),'test_folios':len(test),'qualifying_pairs':out})
 # A pair replicates only if it has held-out evidence in both complementary folds.
 maps=[{tuple(x['prefix_pair']):x for x in f['qualifying_pairs']} for f in folds]
 replicated=[]
 for pair in sorted(set(maps[0])&set(maps[1])):
  a0,a1=maps[0][pair],maps[1][pair]
  replicated.append({'prefix_pair':list(pair),'fold0_test_stems':a0['test_shared_stems'],'fold1_test_stems':a1['test_shared_stems'],'fold0_test_mean_js':a0['test_mean_js'],'fold1_test_mean_js':a1['test_mean_js'],'min_test_mean_js':min(a0['test_mean_js'],a1['test_mean_js'])})
 replicated.sort(key=lambda z:(z['fold0_test_stems']+z['fold1_test_stems'],z['min_test_mean_js']),reverse=True)
 res={'classification':'ADVERSARIAL_FOLIO_HOLDOUT_COMPOSITIONALITY_NOT_TRANSLATION','source_blob':BLOB,'rows':len(rows),'folios':len(folios),'split':'alternating sorted folios; complementary two-fold holdout','min_train_per_form':a.min_train,'min_test_per_form':a.min_test,'folds':folds,'replicated_pairs':replicated,'status':'PASS_EXECUTED' if replicated else 'FAIL_NO_REPLICATED_PREFIX_PAIR','interpretation_rule':'Replication means a prefix contrast survives a folio holdout on shared stems in both complementary folds. It does not identify semantics and does not yet control Currier/hand/section.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(res,indent=2)+'\n');print(json.dumps({'status':res['status'],'rows':len(rows),'folios':len(folios),'replicated_pairs':replicated[:12]},indent=2))
if __name__=='__main__':main()

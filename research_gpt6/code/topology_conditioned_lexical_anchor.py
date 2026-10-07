#!/usr/bin/env python3
import argparse,json,math,random
from collections import Counter,defaultdict
from pathlib import Path
import label_pair_length_matched as lex
import topology_from_text as h1
import topology_crossview_h2 as h2
import topology_linegrammar_h3 as h3
SEED=20261006

def basefeat(t):
 n=len(t); return [t.count('o')/n,t.count('a')/n,t.count('y')/n,float(t.startswith('q')),float(t.endswith('y'))]

def topology_context(raw):
 pages=h1.parse(raw); fs=sorted(pages,key=h1.folio_num); prep={}
 for fam in ('A','B'):
  vec={f:h1.vector(pages[f],fam) for f in fs}; groups,cand,dist,ranked=h1.prepare(fs,pages,vec); prep[fam]=(vec,cand,dist)
 _,ea=h2.build_edges(fs,prep['A'][1],prep['A'][2]); _,eb=h2.build_edges(fs,prep['B'][1],prep['B'][2]); con=ea & eb
 adj=defaultdict(set)
 for a,b in con: adj[a].add(b); adj[b].add(a)
 vc={f:h3.vector_c(pages[f]) for f in fs}; out={}
 for f in fs:
  ns=adj[f]
  if not ns: continue
  ad=[h1.cosine(prep['A'][0][f],prep['A'][0][g]) for g in ns]
  bd=[h1.cosine(prep['B'][0][f],prep['B'][0][g]) for g in ns]
  cd=[h3.cosine(vc[f],vc[g]) for g in ns]
  out[f]=[sum(ad)/len(ad),sum(bd)/len(bd),float(len(ns)),sum(cd)/len(cd)]
 return out,len(con)

def attach(rows,ctx):
 out=[]; excluded=Counter()
 for r in rows:
  fol=r.get('folio')
  if fol not in ctx: excluded['no_topology_context']+=1; continue
  z=dict(r); z['topo']=ctx[fol]; out.append(z)
 return out,dict(excluded)

def parse_rows(raw):
 # Preserve the frozen lexical parser exactly, adding folio by independently matching token occurrences is unsafe.
 # Reproduce its logic with folio retained.
 import re
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
  toks=re.findall(r'(?<![a-z])[a-z]{2,}(?![a-z])',clean.replace('?',' ')); meta=pages.get(fol,{})
  if len(toks)==1 and not uncertain and meta.get('currier')=='A' and meta.get('hand')=='1' and meta.get('quire') in ('O','S'):
   rows.append({'y':sub,'token':toks[0],'folio':fol,**meta})
 return rows

def exact_match(rows,q,seed):
 rng=random.Random(seed+ord(q[0])); groups=defaultdict(lambda:defaultdict(list)); out=[]
 for r in rows:
  if r['quire']==q: groups[len(r['token'])][r['y']].append(r)
 for L in sorted(groups):
  a=list(groups[L]['Lc']); b=list(groups[L]['Lf']); n=min(len(a),len(b))
  if n: rng.shuffle(a); rng.shuffle(b); out+=a[:n]+b[:n]
 return out

def standardize(train,test,topo):
 def feat(r): return basefeat(r['token'])+(r['topo'] if topo else [])
 X=[feat(r) for r in train]; T=[feat(r) for r in test]; k=len(X[0]); mu=[]; sd=[]
 for j in range(k):
  vals=[x[j] for x in X]; m=sum(vals)/len(vals); s=math.sqrt(sum((v-m)**2 for v in vals)/len(vals)); mu.append(m); sd.append(s if s>0 else 1.0)
 return [[(x[j]-mu[j])/sd[j] for j in range(k)] for x in X], [[(x[j]-mu[j])/sd[j] for j in range(k)] for x in T]

def ncm(train,test,topo):
 X,T=standardize(train,test,topo); means={}
 for c in ('Lc','Lf'):
  ix=[i for i,r in enumerate(train) if r['y']==c]
  if not ix:return None
  means[c]=[sum(X[i][j] for i in ix)/len(ix) for j in range(len(X[0]))]
 pred=[]
 for x in T: pred.append(min(means,key=lambda c:sum((x[j]-means[c][j])**2 for j in range(len(x)))))
 return lex.bal([r['y'] for r in test],pred)

def evaluate(rows):
 folds=[]; ys0=[]; pb=[]; pt=[]
 for q in ('O','S'):
  te=exact_match(rows,q,SEED); tr=[r for r in rows if r['quire']!=q]
  cc=Counter(r['y'] for r in te)
  if not te or not tr or not all(any(r['y']==c for r in tr) for c in ('Lc','Lf')):
   folds.append({'quire':q,'status':'UNSUPPORTED','matched_counts':dict(cc)}); continue
  b=ncm(tr,te,False); t=ncm(tr,te,True)
  folds.append({'quire':q,'status':'SUPPORTED','matched_counts':dict(cc),'baseline_ba':b,'topology_ba':t,'delta_ba':t-b})
  # aggregate by fold-size weighted predictions are unavailable; prereg primary uses aggregate BA.
  # Since exact matching makes each fold class-balanced, weighted fold BA equals pooled BA.
  ys0.append(len(te)); pb.append((b,len(te))); pt.append((t,len(te)))
 if not ys0:return None,None,None,folds,0
 base=sum(v*n for v,n in pb)/sum(n for _,n in pb); top=sum(v*n for v,n in pt)/sum(n for _,n in pt)
 return base,top,top-base,folds,sum(n for _,n in pb)//2

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--corpus',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); ap.add_argument('--permutations',type=int,default=999); a=ap.parse_args(); b=a.corpus.read_bytes()
 if lex.blob_sha(b)!=lex.SOURCE_BLOB: raise SystemExit('frozen corpus mismatch')
 raw=b.decode(); rows0=parse_rows(raw); ctx,cedges=topology_context(raw); rows,excluded=attach(rows0,ctx)
 base,top,delta,folds,nclass=evaluate(rows); supported=sum(f['status']=='SUPPORTED' for f in folds)
 out={'classification':'TOPOLOGY_CONDITIONED_LEXICAL_ANCHOR_NOT_TRANSLATION','source_blob':lex.SOURCE_BLOB,'raw_label_rows':len(rows0),'attached_rows':len(rows),'exclusions':excluded,'consensus_edges':cedges,'folds':folds,'aggregate_matched_per_class':nclass,'permutations_requested':a.permutations}
 if supported<2 or nclass<10 or delta is None:
  out.update({'status':'BLOCKED','reason':'preregistered fold/sample requirement not met','permutations_completed':0})
 else:
  rng=random.Random(SEED); null=[]
  for _ in range(a.permutations):
   rr=[dict(r) for r in rows]; strata=defaultdict(list)
   for i,r in enumerate(rr): strata[(r['quire'],len(r['token']))].append(i)
   for ix in strata.values():
    ys=[rr[i]['y'] for i in ix]; rng.shuffle(ys)
    for i,y in zip(ix,ys): rr[i]['y']=y
   _,_,d,_,_=evaluate(rr)
   if d is not None:null.append(d)
  p=(1+sum(x>=delta for x in null))/(1+len(null)) if len(null)==a.permutations else None
  status='BLOCKED' if p is None else ('PASS' if delta>0 and p<=.05 and top>0.5 else 'FAIL')
  out.update({'baseline_balanced_accuracy':base,'topology_balanced_accuracy':top,'delta_ba':delta,'permutations_completed':len(null),'monte_carlo_p':p,'status':status})
 a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__': main()

#!/usr/bin/env python3
import argparse, hashlib, json, math, random, re
from collections import Counter, defaultdict
from pathlib import Path
SOURCE_BLOB='2a4533ab9bdfa85db9bad602d590978953055df1'; SEED=20261006

def blob_sha(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def folio_num(f):
 m=re.match(r'f?(\d+)([rv]?)',f); return (int(m.group(1)),0 if m.group(2)=='r' else 1)
def clean_text(s): return re.sub(r'<[^>]*>|\[[^]]*\]|\{[^}]*\}|@[0-9]+;|[^a-z. ]',' ',s.lower())
def parse(raw):
 pages={}; cur=None
 for line in raw.splitlines():
  p=re.match(r'^<([^>.,]+)>\s*<!([^>]*)>',line)
  if p:
   cur=p.group(1); m=dict(re.findall(r'\$([A-Z])=([^\s>]+)',p.group(2)))
   pages.setdefault(cur,{'quire':m.get('Q','?'),'currier':m.get('L','?'),'hand':m.get('H','?'),'section':m.get('I','?'),'lines':[]}); continue
  m=re.match(r'^<([^>]+)>\s*(.*)$',line)
  if not m or ',' not in m.group(1): continue
  locus,text=m.groups(); fol=locus.split('.')[0]; pos=locus.split(',',1)[1]
  if any(x in pos for x in ('L','l','C','c')): continue
  if fol in pages: pages[fol]['lines'].append(clean_text(text))
 out={}
 for f,p in pages.items():
  toks=re.findall(r'[a-z]{2,}',' '.join(p['lines']))
  if len(toks)>=40: p['tokens']=toks; out[f]=p
 return out

def addnorm(c,prefix,d):
 n=sum(c.values()) or 1
 for k,v in c.items(): d[prefix+k]=v/n
def vector(p,fam):
 toks=p['tokens']; d={}
 if fam=='A':
  chars=''.join(toks)
  for n in (1,2,3): addnorm(Counter(chars[i:i+n] for i in range(len(chars)-n+1)),f'g{n}:',d)
  ini=Counter(t[0] for t in toks); fin=Counter(t[-1] for t in toks); addnorm(ini,'ini:',d); addnorm(fin,'fin:',d)
 else:
  addnorm(Counter(str(min(len(t),15)) for t in toks),'len:',d)
  for n in (1,2,3):
   addnorm(Counter(t[:n] for t in toks if len(t)>=n),f'pre{n}:',d); addnorm(Counter(t[-n:] for t in toks if len(t)>=n),f'suf{n}:',d)
  d['repeat_rate']=1-len(set(toks))/len(toks); d['hapax_rate']=sum(v==1 for v in Counter(toks).values())/len(toks)
 return d
def cosine(a,b):
 ks=set(a)|set(b); dot=sum(a.get(k,0)*b.get(k,0) for k in ks); aa=sum(a.get(k,0)**2 for k in ks); bb=sum(b.get(k,0)**2 for k in ks)
 return 1-dot/math.sqrt(aa*bb) if aa and bb else 1.0
def neighbors(fs,pages):
 byq=defaultdict(list)
 for f in fs: byq[pages[f]['quire']].append(f)
 out={}
 for q,x in byq.items():
  x=sorted(x,key=folio_num)
  for i,f in enumerate(x): out[f]=set(([x[i-1]] if i else [])+([x[i+1]] if i+1<len(x) else []))
 return out
def strata(p):
 n=len(p['tokens']); return (p['currier'],p['hand'],p['section'],min(n//100,9))
def score(fs,pages,vecs,truth):
 rr=[]; r1=r3=0; nd=[]; non=[]; used=0
 for f in fs:
  true=truth.get(f,set())
  if not true: continue
  cand=[g for g in fs if g!=f and strata(pages[g])==strata(pages[f])]
  true=true.intersection(cand)
  if not true or len(cand)<3: continue
  ranked=sorted(cand,key=lambda g:cosine(vecs[f],vecs[g])); ranks=[ranked.index(g)+1 for g in true]; rr.append(1/min(ranks)); r1+=min(ranks)<=1; r3+=min(ranks)<=3
  nd += [cosine(vecs[f],vecs[g]) for g in true]; non += [cosine(vecs[f],vecs[g]) for g in cand if g not in true]; used+=1
 if used<10:return None
 return {'n_queries':used,'mrr':sum(rr)/used,'recall1':r1/used,'recall3':r3/used,'neighbor_distance':sum(nd)/len(nd),'nonneighbor_distance':sum(non)/len(non)}
def perm_truth(fs,pages,truth,rng):
 groups=defaultdict(list)
 for f in fs: groups[strata(pages[f])].append(f)
 mapping={}
 for xs in groups.values():
  ys=xs[:]; rng.shuffle(ys); mapping.update(zip(xs,ys))
 inv={v:k for k,v in mapping.items()}; return {f:{inv[g] for g in truth.get(mapping[f],set()) if g in inv} for f in fs}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--corpus',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); ap.add_argument('--permutations',type=int,default=999); a=ap.parse_args(); b=a.corpus.read_bytes()
 if blob_sha(b)!=SOURCE_BLOB: raise SystemExit('frozen corpus mismatch')
 pages=parse(b.decode()); fs=sorted(pages,key=folio_num); truth=neighbors(fs,pages); result={'classification':'HOLISTIC_TOPOLOGY_FROM_TEXT_NOT_TRANSLATION','source_blob':SOURCE_BLOB,'eligible_folios':len(fs),'families':{},'permutations_requested':a.permutations}
 blocked=False; passes=[]
 for fam in ('A','B'):
  vecs={f:vector(pages[f],fam) for f in fs}; obs=score(fs,pages,vecs,truth)
  if obs is None: result['families'][fam]={'status':'BLOCKED'}; blocked=True; continue
  rng=random.Random(SEED+(0 if fam=='A' else 1)); null=[]
  for _ in range(a.permutations):
   s=score(fs,pages,vecs,perm_truth(fs,pages,truth,rng))
   if s is not None:null.append(s['mrr'])
  p=(1+sum(x>=obs['mrr'] for x in null))/(1+len(null)) if len(null)==a.permutations else None
  status='BLOCKED' if p is None else ('PASS' if p<=.05 and obs['neighbor_distance']<obs['nonneighbor_distance'] else 'FAIL')
  result['families'][fam]={'status':status,'observed':obs,'permutations_completed':len(null),'monte_carlo_p':p}; passes.append(status=='PASS')
 result['status']='BLOCKED' if blocked else ('PASS' if len(passes)==2 and all(passes) else 'FAIL')
 a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result,indent=2))
if __name__=='__main__': main()

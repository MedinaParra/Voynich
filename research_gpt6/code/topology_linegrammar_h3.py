#!/usr/bin/env python3
import argparse,json,math,random,re
from collections import Counter,defaultdict
from pathlib import Path
import topology_from_text as h1
import topology_crossview_h2 as h2
SEED=20261006

def addnorm(c,prefix,d):
 n=sum(c.values()) or 1
 for k,v in c.items(): d[prefix+str(k)]=v/n

def line_tokens(line): return re.findall(r'[a-z]{2,}',line)

def vector_c(p):
 lines=[line_tokens(x) for x in p['lines']]; lines=[x for x in lines if x]
 d={}
 addnorm(Counter(min(len(x),20) for x in lines),'ntok:',d)
 addnorm(Counter(min(len(x[0]),15) for x in lines),'firstlen:',d)
 addnorm(Counter(min(len(x[-1]),15) for x in lines),'lastlen:',d)
 allc=Counter(t for x in lines for t in x); pos=Counter()
 for x in lines:
  n=len(x)
  for i,t in enumerate(x):
   if allc[t]>1:
    q=min(4,int(5*i/max(n,1))); pos[q]+=1
 addnorm(pos,'repeatpos:',d)
 if lines:
  d['first_repeat']=sum(allc[x[0]]>1 for x in lines)/len(lines)
  d['last_repeat']=sum(allc[x[-1]]>1 for x in lines)/len(lines)
 else: d['first_repeat']=d['last_repeat']=0
 return d

def cosine(a,b):
 dot=sum(v*b.get(k,0) for k,v in a.items()); aa=sum(v*v for v in a.values()); bb=sum(v*v for v in b.values())
 return 1-dot/math.sqrt(aa*bb) if aa and bb else 1.0

def mean_dist(edges,dist): return sum(dist[h2.edge(a,b)] for a,b in edges)/len(edges)

def physical_edges(fs,pages):
 truth=h1.neighbors(fs,pages); return set(h2.edge(f,g) for f,ns in truth.items() for g in ns)

def null_edges(consensus,groups,pages,rng,target):
 bystr={k:list(v) for k,v in groups.items()}; observed=set(consensus)
 for _attempt in range(100):
  out=set()
  items=list(consensus); rng.shuffle(items)
  for u,v in items:
   pool=[x for x in bystr[h1.strata(pages[v])] if x!=u and h2.edge(u,x) not in observed]
   if not pool: pool=[x for x in bystr[h1.strata(pages[v])] if x!=u]
   if pool: out.add(h2.edge(u,rng.choice(pool)))
  # top up while preserving u and partner stratum drawn from observed edges
  tries=0
  while len(out)<target and tries<target*100:
   u,v=rng.choice(items); pool=[x for x in bystr[h1.strata(pages[v])] if x!=u and h2.edge(u,x) not in observed]
   if pool: out.add(h2.edge(u,rng.choice(pool)))
   tries+=1
  if len(out)==target:return out
 return None

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--corpus',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); ap.add_argument('--permutations',type=int,default=999); a=ap.parse_args(); b=a.corpus.read_bytes()
 if h1.blob_sha(b)!=h1.SOURCE_BLOB: raise SystemExit('frozen corpus mismatch')
 pages=h1.parse(b.decode()); fs=sorted(pages,key=h1.folio_num)
 prep={}
 for fam in ('A','B'):
  vec={f:h1.vector(pages[f],fam) for f in fs}; groups,cand,dist,ranked=h1.prepare(fs,pages,vec); prep[fam]=(groups,cand,dist)
 _,ea=h2.build_edges(fs,prep['A'][1],prep['A'][2]); _,eb=h2.build_edges(fs,prep['B'][1],prep['B'][2]); consensus=ea & eb
 out={'classification':'HOLISTIC_TOPOLOGY_LINEGRAMMAR_H3_NOT_TRANSLATION','source_blob':h1.SOURCE_BLOB,'eligible_folios':len(fs),'consensus_edges':len(consensus),'permutations_requested':a.permutations}
 if len(consensus)<30:
  out['status']='BLOCKED'; out['reason']='consensus graph has fewer than 30 unique edges'
 else:
  vc={f:vector_c(pages[f]) for f in fs}; dist={h2.edge(f,g):cosine(vc[f],vc[g]) for i,f in enumerate(fs) for g in fs[i+1:]}
  obs=mean_dist(consensus,dist); phys=physical_edges(fs,pages); pd=mean_dist(phys,dist) if phys else None
  groups=defaultdict(list)
  for f in fs: groups[h1.strata(pages[f])].append(f)
  rng=random.Random(SEED); null=[]; blocked=False
  for _ in range(a.permutations):
   ne=null_edges(consensus,groups,pages,rng,len(consensus))
   if ne is None: blocked=True; break
   null.append(mean_dist(ne,dist))
  if blocked or len(null)!=a.permutations:
   out.update({'status':'BLOCKED','permutations_completed':len(null),'reason':'matched null construction incomplete'})
  else:
   nm=sum(null)/len(null); p=(1+sum(x<=obs for x in null))/(1+len(null)); status='PASS' if p<=.05 and obs<nm else 'FAIL'
   out.update({'status':status,'observed_consensus_mean_distance':obs,'null_mean_distance':nm,'monte_carlo_p':p,'permutations_completed':len(null),'physical_edges':len(phys),'physical_mean_distance':pd,'delta_vs_physical':obs-pd if pd is not None else None})
 a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
